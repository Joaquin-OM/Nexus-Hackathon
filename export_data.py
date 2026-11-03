import json
from config import get_conn
from data_validator import (
    validate_and_clean_host,
    validate_and_clean_user,
    validate_and_clean_ip,
)

def export_data():
    conn = get_conn()
    alerts_rows = conn.run("""
        SELECT id, COALESCE(internal_alert_id, alert_code), event_timestamp_utc, incibe_class, incibe_type, 
               normalized_severity, affected_user, affected_host, source_ip, sede, detection_rule, 
               status, description 
        FROM v_soc_unique_alerts 
        ORDER BY event_timestamp_utc DESC
    """)
    alerts = []
    for r in alerts_rows:
        alerts.append({
            "id": r[0],
            "internal_id": r[1] or f"AL-{r[0]}",
            "timestamp": str(r[2]),
            "class": r[3] or "Sin clasificar",
            "subclass": r[4] or "General",
            "severity": r[5] or "Media",
            "user": validate_and_clean_user(r[6]),
            "host": validate_and_clean_host(r[7]),
            "ip": validate_and_clean_ip(r[8]) or "No identificada",
            "site": r[9] or "SAMPOL Central",
            "category": r[10] or "N/A",
            "status": r[11] or "nueva",
            "desc": r[12] or ""
        })

    soar_rows = conn.run("""
        SELECT id, alert_id, action, target_type, target_value, trigger_mode, status, executed_by, executed_at, reason 
        FROM soar_actions 
        ORDER BY id DESC
    """)
    soar = []
    for r in soar_rows:
        soar.append({
            "id": r[0],
            "alert_id": r[1],
            "action": r[2],
            "type": r[3],
            "target": r[4],
            "trigger": r[5],
            "status": r[6],
            "executed_by": r[7],
            "executed_at": str(r[8]),
            "reason": r[9]
        })

    # Exportar Notificaciones Inteligentes
    notif_rows = conn.run("""
        SELECT id, incident_id, priority, risk_score, title, message,
               affected_asset, affected_user, event_count, first_event_at, last_event_at,
               reasons_json, status, acknowledged_by, acknowledged_at, last_notified_at
        FROM notifications
        ORDER BY 
            CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 ELSE 4 END ASC,
            last_event_at DESC
    """)
    notifications = []
    for r in notif_rows:
        asset_clean = validate_and_clean_host(r[6])
        if asset_clean == "No identificado":
            asset_clean = "Infraestructura Central SAMPOL"
            
        notifications.append({
            "id": r[0],
            "incident_id": r[1],
            "priority": r[2],
            "risk_score": r[3],
            "title": r[4],
            "description": r[5],
            "count": r[8],
            "acknowledged": r[12] == "acknowledged",
            "affected_asset": asset_clean,
            "affected_user": validate_and_clean_user(r[7]),
            "reasons": r[11] if isinstance(r[11], list) else json.loads(r[11] or "[]"),
            "status": r[12],
            "acknowledged_by": r[13],
            "acknowledged_at": str(r[14]) if r[14] else None,
            "last_event_at": str(r[10])
        })

    # Métricas de fatiga
    metric_rows = conn.run("""
        SELECT total_raw_emails, total_alerts, deduplicated_alerts, total_notifications_issued,
               p1_critical_count, p2_high_count, p3_medium_count, p4_low_count,
               acknowledged_count, escalations_count, noise_reduction_percentage
        FROM v_notification_metrics
    """)
    metrics = {}
    if metric_rows:
        mr = metric_rows[0]
        metrics = {
            "total_raw_emails": mr[0] or 0,
            "total_alerts": mr[1] or 0,
            "deduplicated_alerts": mr[2] or 0,
            "total_notifications_issued": mr[3] or 0,
            "p1_critical_count": mr[4] or 0,
            "p2_high_count": mr[5] or 0,
            "p3_medium_count": mr[6] or 0,
            "p4_low_count": mr[7] or 0,
            "acknowledged_count": mr[8] or 0,
            "escalations_count": mr[9] or 0,
            "noise_reduction_percentage": float(mr[10] or 95.0)
        }

    raw_count = conn.run("SELECT count(*) FROM raw_emails")[0][0]

    out = {
        "raw_count": raw_count,
        "unique_alerts_count": len(alerts),
        "soar_count": len(soar),
        "notifications_count": len(notifications),
        "metrics": metrics,
        "alerts": alerts,
        "soar": soar,
        "notifications": notifications
    }

    with open("data_export.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Exportados con éxito: {raw_count} correos, {len(alerts)} alertas únicas, {len(soar)} acciones SOAR, {len(notifications)} notificaciones inteligentes")

if __name__ == "__main__":
    export_data()
