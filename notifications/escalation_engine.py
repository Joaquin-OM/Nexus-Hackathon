"""
NEXUS Smart Notifications — Motor de Escalado Jerárquico
Supervisa notificaciones críticas no reconocidas y escala hacia supervisores y Dirección de TI.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

ESCALATION_LEVELS = [
    {"level": 1, "timeout_minutes": 15, "role": "analista_l2", "recipient": "guardia_soc@sampol.com"},
    {"level": 2, "timeout_minutes": 30, "role": "supervisor_soc", "recipient": "supervisor_soc@sampol.com"},
    {"level": 3, "timeout_minutes": 60, "role": "director_ti", "recipient": "dirti@sampol.com"},
]

def check_and_escalate_notification(
    notification: Dict[str, Any],
    now: datetime = None
) -> Dict[str, Any]:
    """
    Evalúa si una notificación P1/P2 no reconocida debe escalar al siguiente nivel.
    Retorna un diccionario con los detalles del escalado o None si no corresponde.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # Solo escalar P1 y P2 que sigan activas o escaladas (no reconocidas ni resueltas)
    if notification.get("status") in ("acknowledged", "resolved", "dismissed"):
        return None

    priority = notification.get("priority")
    if priority not in ("P1", "P2"):
        return None

    created_at = notification.get("created_at")
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except Exception:
            created_at = now
    elif created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    age_minutes = (now - created_at).total_seconds() / 60.0
    current_escalation_level = notification.get("escalation_level", 0)

    for esc in ESCALATION_LEVELS:
        if age_minutes >= esc["timeout_minutes"] and current_escalation_level < esc["level"]:
            return {
                "notification_id": notification["id"],
                "escalation_level": esc["level"],
                "new_recipient_id": esc["recipient"],
                "role": esc["role"],
                "reason": (
                    f"Incidente crítico {notification['incident_id']} ({priority}) "
                    f"sin reconocimiento tras {int(age_minutes)} minutos. Escalado automático a {esc['role']}."
                )
            }

    return None
