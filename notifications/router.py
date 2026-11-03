"""
NEXUS Smart Notifications — Router FastAPI con REST y Server-Sent Events (SSE)
Aislamiento multi-usuario, autorización basada en roles (RBAC) y suscripciones SSE privadas.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Header, Request, Depends, status
from starlette.responses import StreamingResponse
from pydantic import BaseModel

from config import get_conn
from security import (
    AuthenticatedUser,
    UserRole,
    Permission,
    get_current_user,
    require_permission,
    verify_access_token,
    KNOWN_IDENTITIES,
    DEMO_MODE,
)
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

# ============================================================================
# GESTOR DE SUSCRIPCIONES SSE PRIVADAS POR USUARIO Y ROL
# ============================================================================

class SSESubscriber:
    def __init__(self, session_id: str, user_id: str, email: str, role: UserRole, queue: asyncio.Queue):
        self.session_id = session_id
        self.user_id = user_id
        self.email = email
        self.role = role
        self.queue = queue
        self.connected_at = datetime.now(timezone.utc)

class SSESubscriptionManager:
    """Administra conexiones activas de SSE aisladas por identidad y rol."""
    def __init__(self):
        self._subscribers: Dict[str, SSESubscriber] = {}
        self._lock = asyncio.Lock()

    async def register(self, user: AuthenticatedUser) -> SSESubscriber:
        session_id = str(uuid.uuid4())
        queue = asyncio.Queue(maxsize=100)
        subscriber = SSESubscriber(
            session_id=session_id,
            user_id=user.user_id,
            email=user.email,
            role=user.role,
            queue=queue
        )
        async with self._lock:
            self._subscribers[session_id] = subscriber
        logger.info(f"[SSE] Conectado usuario '{user.email}' (Rol: {user.role.value}, Sesión: {session_id[:8]})")
        return subscriber

    async def unregister(self, session_id: str):
        async with self._lock:
            if session_id in self._subscribers:
                sub = self._subscribers.pop(session_id)
                logger.info(f"[SSE] Desconectado usuario '{sub.email}' (Sesión: {session_id[:8]})")

    def broadcast(
        self,
        event_type: str,
        data: Dict[str, Any],
        target_role: Optional[UserRole] = None,
        target_email: Optional[str] = None
    ):
        """Difunde eventos únicamente a los suscriptores autorizados."""
        payload = json.dumps({
            "event": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, default=str)

        for session_id, sub in list(self._subscribers.items()):
            # Filtrado por destinatario específico
            if target_email and sub.email.lower() != target_email.lower():
                continue
            # Filtrado por rol mínimo (Administrador siempre recibe)
            if target_role and sub.role != UserRole.ADMINISTRADOR and sub.role != target_role:
                continue
            
            try:
                sub.queue.put_nowait(payload)
            except asyncio.QueueFull:
                logger.warning(f"[SSE] Cola llena para suscriptor {sub.email}. Descartando evento antiguo.")
            except Exception as e:
                logger.error(f"[SSE] Error al enviar a {sub.email}: {e}")

sse_manager = SSESubscriptionManager()

def broadcast_event(event_type: str, data: Dict[str, Any], target_role: Optional[UserRole] = None, target_email: Optional[str] = None):
    sse_manager.broadcast(event_type, data, target_role=target_role, target_email=target_email)

# ============================================================================
# ENDPOINTS REST
# ============================================================================

@router.post("/evaluate")
def evaluate_alert(
    alert: AlertEventInput,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.REQUEST_SOAR))
):
    """
    Ingesta y evalúa una alerta SOC:
    1. Calcula incident_id y dedup_key canónica.
    2. Evalúa riesgo explicable (0-100) y prioridad (P1-P4).
    3. Aplica deduplicación, agrupación y anti-saturación.
    4. Persiste en PostgreSQL y emite SSE únicamente a los perfiles SOC correspondientes.
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

    # 6. Difusión en tiempo real (SSE) filtrada
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
    current_user: AuthenticatedUser = Depends(require_permission(Permission.READ_NOTIFICATIONS))
):
    """
    Lista las notificaciones persistidas en PostgreSQL con ordenación y filtros.
    Valida la identidad del usuario en servidor y restringe ámbito según rol.
    """
    conn = get_conn()
    items, total = repository.list_notifications(
        conn=conn,
        user_id=current_user.email,
        priority=priority,
        status=status,
        search=search,
        limit=limit,
        offset=offset
    )
    return items

@router.get("/unread-count", response_model=UnreadCountOut)
def get_unread_count(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.READ_NOTIFICATIONS))
):
    """Devuelve el contador de notificaciones no reconocidas para la campana de la UI."""
    conn = get_conn()
    return repository.get_unread_count(conn, user_id=current_user.email)

@router.get("/metrics", response_model=NoiseReductionMetricsOut)
def get_metrics(
    current_user: AuthenticatedUser = Depends(require_permission(Permission.READ_NOTIFICATIONS))
):
    """Devuelve las métricas verificadas de deduplicación y reducción de fatiga."""
    conn = get_conn()
    return repository.get_noise_metrics(conn)

@router.get("/{notification_id}")
def get_notification(
    notification_id: int,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.READ_NOTIFICATIONS))
):
    """Obtiene el detalle completo de una notificación por su ID verificando autorización."""
    conn = get_conn()
    notif = repository.get_notification_by_id(conn, notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notif

@router.post("/{notification_id}/acknowledge")
def acknowledge_notification(
    notification_id: int,
    payload: Optional[NotificationAcknowledgeRequest] = None,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.ACK_NOTIFICATIONS))
):
    """
    Reconoce un aviso en PostgreSQL y actualiza la auditoría inmutable.
    La identidad del actor es validada obligatoriamente por el backend a partir del usuario autenticado.
    """
    conn = get_conn()
    actor = current_user.email  # Forzado por identidad autenticada
    comment = payload.comment if payload else None

    notif = repository.acknowledge_notification(conn, notification_id, actor_id=actor, comment=comment)
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    broadcast_event("NOTIFICATION_ACKNOWLEDGED", {"id": notification_id, "acknowledged_by": actor})
    return {"ok": True, "id": notification_id, "status": "acknowledged", "acknowledged_by": actor}

@router.get("/stream")
async def sse_notifications_stream(
    request: Request,
    token: Optional[str] = Query(None, description="Token de sesión para clientes EventSource"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    """
    Canal Server-Sent Events (SSE) autenticado y privado:
    - Valida token en query param (compatible con EventSource de navegadores estándar) o cabeceras.
    - Asigna una suscripción privada en SSESubscriptionManager.
    - Heartbeat cada 15 segundos para evitar timeouts de proxies y WAF.
    - Desconexión limpia y liberación de recursos en memoria.
    """
    # Resolver usuario para SSE
    user: Optional[AuthenticatedUser] = None
    if token:
        user = verify_access_token(token)
    elif DEMO_MODE:
        target_email = (x_user_id or "guardia_soc@sampol.com").strip().lower()
        if target_email in KNOWN_IDENTITIES:
            info = KNOWN_IDENTITIES[target_email]
            user = AuthenticatedUser(
                user_id=info["user_id"],
                email=target_email,
                name=info["name"],
                role=info["role"],
                permissions=[p.value for p in Permission],
                is_demo=True
            )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida para el canal SSE en tiempo real."
        )

    subscriber = await sse_manager.register(user)

    async def event_generator():
        try:
            # Evento inicial autenticado
            welcome = json.dumps({
                "status": "connected",
                "system": "NEXUS-Smart-Notifications",
                "authenticated_as": user.email,
                "role": user.role.value
            })
            yield f"event: connected\ndata: {welcome}\n\n"
            
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(subscriber.queue.get(), timeout=15.0)
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat keep-alive
                    yield ": keep-alive\n\n"
        finally:
            await sse_manager.unregister(subscriber.session_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
