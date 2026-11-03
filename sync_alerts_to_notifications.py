"""
Sincroniza las alertas existentes en PostgreSQL con el motor NEXUS Smart Notifications
Agrupa los 140 eventos en un puñado de incidentes consolidados con puntuación de riesgo.
"""

from config import get_conn
from notifications.schemas import AlertEventInput
from notifications.router import evaluate_alert

def sync_existing_alerts():
    conn = get_conn()
    rows = conn.run("""
        SELECT internal_alert_id, detection_rule, incibe_class, title, description, 
               normalized_severity, affected_user, affected_host, source_ip, destination_ip, 
               asset_criticality, sede
        FROM v_soc_unique_alerts
        ORDER BY event_timestamp_utc ASC
    """)
    print(f"Procesando {len(rows)} alertas únicas a través de NEXUS Smart Notifications...")

    notifs_emitted = 0
    updates_emitted = 0

    for r in rows:
        alert_in = AlertEventInput(
            alert_id=r[0] or "AL-UNKNOWN",
            detection_rule=r[1] or "",
            incibe_class=r[2] or "Otros",
            title=r[3] or "Alerta de Seguridad",
            description=r[4] or "",
            source_severity=r[5] or "Media",
            affected_user=r[6],
            affected_host=r[7],
            source_ip=r[8],
            destination_ip=r[9],
            asset_criticality=r[10] or "Media",
            sede=r[11] or "Palma",
            is_compromise_confirmed=any(c in (r[1] or "") for c in ["ACCOUNT", "ADMIN", "MODIFY", "C2", "APT", "MALWARE"])
        )
        res = evaluate_alert(alert_in)
        if res["should_notify"]:
            notifs_emitted += 1
        else:
            updates_emitted += 1

    print(f"Sincronización completada: {notifs_emitted} avisos emitidos, {updates_emitted} actualizaciones/amortiguaciones por ráfaga.")

if __name__ == "__main__":
    sync_existing_alerts()
