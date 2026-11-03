import json
from config import get_conn

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
            "user": r[6] or "N/A",
            "host": r[7] or "N/A",
            "ip": r[8] or "N/A",
            "site": r[9] or "N/A",
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

    raw_count = conn.run("SELECT count(*) FROM raw_emails")[0][0]

    out = {
        "raw_count": raw_count,
        "unique_alerts_count": len(alerts),
        "soar_count": len(soar),
        "alerts": alerts,
        "soar": soar
    }

    with open("data_export.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Exportados con éxito: {raw_count} correos, {len(alerts)} alertas únicas, {len(soar)} acciones SOAR")

if __name__ == "__main__":
    export_data()
