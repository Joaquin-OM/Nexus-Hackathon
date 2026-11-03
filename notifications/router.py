"""
NEXUS Smart Notifications — Router FastAPI con REST y Server-Sent Events (SSE)
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Header, Request, Depends
from starlette.responses import StreamingResponse
from pydantic import BaseModel

from config import get_conn
from notifications.schemas import (
    AlertEventInput,
    NotificationOut,
    NotificationAcknowledgeRequest,
    NotificationPreferencesIn,
    NotificationPreferencesOut,
    UnreadCountOut,
    NoiseReductionMetricsOut,
)
from notifications.risk_engine import evaluate_risk
from notifications.deduplication_engine import (
    generate_dedup_key,
    evaluate_anti_saturation,
)
from notifications import repository

logger = logging.getLogger("smart_notifications")
router = APIRouter(prefix="/api/smart-notifications", tags=["smart-notifications"])

# Bus de eventos en memoria para transmisión SSE en tiempo real
_subscribers: List[asyncio.Queue] = []

def broadcast_event(event_type: str, data: Dict[str, Any]):
    """Envía un evento SSE a todos los navegadores conectados."""
    payload = json.dumps({"event": event_type, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()}, default=str)
    for queue in list(_subscribers):
        try:
            queue.put_nowait(payload)
        except Exception:
            pass

@router.post("/evaluate")
def evaluate_alert(alert: AlertEventInput):
    """
    Ingesta y evalúa una alerta SOC:
    1. Calcula incident_id y dedup_key.
    2. Evalúa riesgo explicable (0-100) y prioridad (P1-P4).
    3. Aplica deduplicación, agrupación y anti-saturación.
    4. Persiste en PostgreSQL y emite SSE si corresponde.
    """
    conn = get_conn()
    now = datetime.now(timezone.utc)
    inc_id, dedup_key = generate_dedup_key(alert)

    # 1. Consultar estado existente
    existing = repository.get_notification_by_dedup_key(conn, dedup_key)
    accumulated = (existing["event_count"] if existing else 0) + 1

    # 2. Motor de riesgo explicable
    risk_score, priority, reasons, requires_action = evaluate_risk(alert, accumulated_events=accumulated)

    # 3. Motor de deduplicación y anti-saturación
    should_notify, action = evaluate_anti_saturation(
        current_priority=priority,
        existing_notification=existing,
        significant_change=alert.significant_change,
        now=now
    )

    # 4. Mensaje consolidado
    if existing:
        msg = f"{accumulated} eventos correlacionados sobre {alert.affected_user or alert.affected_host or 'el activo'}. Último evento: {alert.title}"
    else:
        msg = alert.description or alert.title

    # 5. Persistencia en PostgreSQL
    notif = repository.upsert_notification_event(
        conn=conn,
        incident_id=inc_id,
        dedup_key=dedup_key,
        priority=priority,
        risk_score=risk_score,
        title=alert.title if not existing else existing["title"],
        message=msg,
        affected_asset=alert.affected_host or alert.source_ip,
        affected_user=alert.affected_user,
        reasons=reasons,
        requires_human_action=requires_action,
        should_notify=should_notify,
        now=now
    )

    # 6. Difusión en tiempo real (SSE) si corresponde notificación
    if should_notify:
        broadcast_event("NEW_NOTIFICATION", notif)
    else:
        broadcast_event("NOTIFICATION_UPDATED", {"id": notif["id"], "event_count": notif["event_count"]})

    return {
        "action": action,
        "should_notify": should_notify,
        "notification_id": notif["id"],
        "incident_id": inc_id,
        "priority": priority,
        "risk_score": risk_score,
        "event_count": notif["event_count"],
        "reasons": reasons
    }

@router.get("", response_model=List[Dict[str, Any]])
def list_notifications(
    priority: Optional[str] = Query("all", description="Filtrar por P1, P2, P3, P4 o all"),
    status: Optional[str] = Query("all", description="Filtrar por active, acknowledged o all"),
    search: Optional[str] = Query(None, description="Término de búsqueda libre"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    x_user_id: str = Header("guardia_soc@sampol.com", alias="X-User-Id")
):
    """Lista las notificaciones persistidas en PostgreSQL con ordenación y filtros."""
    conn = get_conn()
    items, total = repository.list_notifications(
        conn=conn,
        user_id=x_user_id,
        priority=priority,
        status=status,
        search=search,
        limit=limit,
        offset=offset
    )
    return items

@router.get("/unread-count", response_model=UnreadCountOut)
def get_unread_count(x_user_id: str = Header("guardia_soc@sampol.com", alias="X-User-Id")):
    """Devuelve el contador de notificaciones no reconocidas para la campana de la UI."""
    conn = get_conn()
    return repository.get_unread_count(conn, user_id=x_user_id)

@router.get("/metrics", response_model=NoiseReductionMetricsOut)
def get_metrics():
    """Devuelve las métricas de deduplicación y reducción de fatiga de alertas."""
    conn = get_conn()
    return repository.get_noise_metrics(conn)

@router.get("/{notification_id}")
def get_notification(notification_id: int):
    """Obtiene el detalle completo de una notificación por su ID."""
    conn = get_conn()
    notif = repository.get_notification_by_id(conn, notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notif

@router.post("/{notification_id}/acknowledge")
def acknowledge_notification(
    notification_id: int,
    payload: Optional[NotificationAcknowledgeRequest] = None,
    x_user_id: str = Header("guardia_soc@sampol.com", alias="X-User-Id")
):
    """Reconoce un aviso en PostgreSQL y actualiza la auditoría inmutable."""
    conn = get_conn()
    actor = payload.actor_id if (payload and payload.actor_id) else x_user_id
    comment = payload.comment if payload else None

    notif = repository.acknowledge_notification(conn, notification_id, actor_id=actor, comment=comment)
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    broadcast_event("NOTIFICATION_ACKNOWLEDGED", {"id": notification_id, "acknowledged_by": actor})
    return {"ok": True, "id": notification_id, "status": "acknowledged", "acknowledged_by": actor}

@router.get("/stream")
async def sse_notifications_stream(request: Request):
    """
    Canal Server-Sent Events (SSE) para actualizaciones en vivo:
    - Heartbeat cada 15 segundos para evitar timeouts de proxies/firewalls.
    - Reconexión automática con EventSource en el frontend.
    """
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers.append(queue)

    async def event_generator():
        try:
            # Evento inicial de bienvenida
            yield "event: connected\ndata: {\"status\": \"connected\", \"system\": \"NEXUS-Smart-Notifications\"}\n\n"
            while True:
                # Comprobar si el cliente se desconectó
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat keep-alive
                    yield ": keep-alive\n\n"
        finally:
            if queue in _subscribers:
                _subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
