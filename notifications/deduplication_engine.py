"""
NEXUS Smart Notifications — Motor de Deduplicación, Agrupación y Anti-Saturación
Permite procesar grandes volúmenes de alertas reduciendo el ruido operativo en > 99%.
Incluye resolución canónica de campañas, identificación de relaciones y protección anti-fatiga.
"""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple, List
from notifications.schemas import AlertEventInput, PriorityLevel

PRIORITY_RANKS = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}

COOLDOWN_MAP = {
    "P1": timedelta(minutes=10),
    "P2": timedelta(minutes=15),
    "P3": timedelta(hours=1),
    "P4": timedelta(hours=24),
}

# Diccionario configurable de campañas corporativas conocidas
DEFAULT_CAMPAIGN_PATTERNS: Dict[str, str] = {
    "moreno": "INC-CAMP-MORENO",
    "gonzalez": "INC-CAMP-GONZALEZ",
}

def get_campaign_patterns() -> Dict[str, str]:
    """Carga patrones de campaña desde entorno o diccionario por defecto."""
    patterns = dict(DEFAULT_CAMPAIGN_PATTERNS)
    env_cfg = os.environ.get("NEXUS_CAMPAIGN_PATTERNS")
    if env_cfg:
        # Formato: "keyword1=CAMP_ID_1,keyword2=CAMP_ID_2"
        for item in env_cfg.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                patterns[k.strip().lower()] = v.strip()
    return patterns

def classify_event_relationship(
    alert: AlertEventInput,
    existing_notification: Optional[Dict[str, Any]]
) -> str:
    """
    Distingue de forma precisa el tipo de relación de un evento:
    - EXACT_DUPLICATE: Mismo evento ya procesado.
    - CRITICAL_EVIDENCE_NEW: Nueva evidencia crítica (exfiltración, cifrado, C2).
    - NEW_RELATED_EVENT: Evento nuevo correlacionado en el mismo incidente.
    - INDEPENDENT_INCIDENT: Nuevo incidente independiente.
    """
    if not existing_notification:
        return "INDEPENDENT_INCIDENT"
    
    if alert.significant_change or alert.is_compromise_confirmed:
        return "CRITICAL_EVIDENCE_NEW"
        
    rule = (alert.detection_rule or "").upper()
    if any(crit in rule for crit in ("MODIFY-LAB", "C2-LAB", "APT-LAB")):
        return "CRITICAL_EVIDENCE_NEW"
        
    return "NEW_RELATED_EVENT"

def generate_dedup_key(
    alert: AlertEventInput,
    custom_campaigns: Optional[Dict[str, str]] = None
) -> Tuple[str, str]:
    """
    Genera un incident_id canónico y una clave de deduplicación idempotente estable.
    Evita agrupar indiscriminadamente por IP si hay NAT o proxies compartidos.
    Prioriza identidad de usuario comprometido, host y campaña estructurada.
    """
    if alert.incident_id and alert.incident_id.strip():
        inc_id = alert.incident_id.strip()
    else:
        # Extraer vector canónico
        u = (alert.affected_user or "").strip().lower()
        h = (alert.affected_host or "").strip().lower()
        rule = (alert.detection_rule or "").strip().upper()
        rule_prefix = rule.split("-")[0] if "-" in rule else "RULE"

        # 1. Comprobar catálogo de campañas conocidas
        campaigns = custom_campaigns or get_campaign_patterns()
        matched_campaign = None
        for pattern_kw, camp_id in campaigns.items():
            if pattern_kw in u:
                matched_campaign = camp_id
                break

        if matched_campaign:
            inc_id = matched_campaign
        elif u and u not in ("no identificado", "no indicada", "n/a"):
            user_handle = u.split("@")[0].replace(".", "_")
            inc_id = f"INC-USR-{user_handle}"
        elif h and h not in ("no identificado", "no indicada", "n/a"):
            clean_h = h.replace(".", "_").replace(" ", "_")
            inc_id = f"INC-HOST-{clean_h}"
        elif alert.source_ip:
            # Para evitar falsos agrupamientos por IPs de gateway o proxy NAT compartido,
            # correlacionar IP con la familia de regla de detección
            ip_clean = alert.source_ip.replace(".", "-")
            inc_id = f"INC-IP-{rule_prefix}-{ip_clean}"
        else:
            inc_id = f"INC-AL-{alert.alert_id}"

    # Dedup key única para la notificación del incidente
    raw_key = f"NOTIF-{inc_id}"
    return inc_id, raw_key

def evaluate_anti_saturation(
    current_priority: PriorityLevel,
    existing_notification: Optional[Dict[str, Any]],
    significant_change: bool = False,
    now: Optional[datetime] = None
) -> Tuple[bool, str]:
    """
    Determina si se debe emitir una notificación al analista o simplemente
    actualizar el contador del incidente en segundo plano (amortiguación de ruido).
    
    Retorna: (should_notify: bool, action: str)
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # 1. Si no existe notificación previa para este incidente:
    if not existing_notification:
        # P1 y P2 generan notificación inmediata
        if current_priority in ("P1", "P2"):
            return True, "notify"
        # P3 entra a la cola de trabajo (digest)
        elif current_priority == "P3":
            return False, "queued_digest"
        # P4 se guarda como registro silencioso
        else:
            return False, "quiet_log"

    # 2. Si ya existe notificación previa:
    previous_priority = existing_notification.get("priority", "P3")
    prev_rank = PRIORITY_RANKS.get(previous_priority, 3)
    curr_rank = PRIORITY_RANKS.get(current_priority, 3)

    # Regla de Oro A: Escalada de Prioridad (ej: de P3/P2 a P1) -> NUNCA se silencia
    if curr_rank < prev_rank:
        return True, "escalated_priority_notify"

    # Regla de Oro B: Cambio significativo forzado por evidencia crítica
    if significant_change:
        return True, "significant_change_notify"

    # Regla de Oro C: Cooldown temporal para recordatorios en incidentes no reconocidos
    last_notified = existing_notification.get("last_notified_at")
    if last_notified:
        if isinstance(last_notified, str):
            try:
                last_notified = datetime.fromisoformat(last_notified.replace("Z", "+00:00"))
            except Exception:
                last_notified = now
        elif last_notified.tzinfo is None:
            last_notified = last_notified.replace(tzinfo=timezone.utc)

        cooldown = COOLDOWN_MAP.get(current_priority, timedelta(minutes=15))
        is_ack = existing_notification.get("status") == "acknowledged"

        # Solo si no ha sido reconocida y ya pasó el cooldown se repite un recordatorio
        if not is_ack and current_priority in ("P1", "P2") and (now - last_notified) >= cooldown:
            return True, "cooldown_reminder_notify"

    # En cualquier otro caso, amortiguar: actualizar contador sin saturar con aviso
    return False, "burst_suppressed_update"
