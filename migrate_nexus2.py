import hashlib
import json
import re
from html import unescape
from config import get_conn
from ingest_and_classify import extract_table_fields, RULE_TO_INCIBE, normalize_ip

def main():
    conn = get_conn()
    alter_statements = [
        "ALTER TABLE raw_emails ADD COLUMN IF NOT EXISTS raw_content_ref VARCHAR(512)",
        "ALTER TABLE raw_emails ADD COLUMN IF NOT EXISTS sha256 VARCHAR(64)",
        """CREATE TABLE IF NOT EXISTS attachments (
            id SERIAL PRIMARY KEY,
            email_id INTEGER NOT NULL REFERENCES raw_emails(id) ON DELETE CASCADE,
            filename VARCHAR(512) NOT NULL,
            mime_type VARCHAR(128),
            size_bytes INTEGER DEFAULT 0,
            storage_ref VARCHAR(512),
            sha256 VARCHAR(64),
            created_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS internal_alert_id VARCHAR(64)",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS detection_rule VARCHAR(128)",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS sede VARCHAR(64) DEFAULT 'No indicada'",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS asset_criticality VARCHAR(64) DEFAULT 'Media'",
        "ALTER TABLE soar_actions ADD COLUMN IF NOT EXISTS status VARCHAR(32) NOT NULL DEFAULT 'ejecutado'",
        "ALTER TABLE soar_actions ADD COLUMN IF NOT EXISTS requested_by VARCHAR(128) DEFAULT 'Responsable SOC / Analista'",
        "ALTER TABLE soar_actions ADD COLUMN IF NOT EXISTS approved_by VARCHAR(128)",
        "ALTER TABLE soar_actions ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255) UNIQUE",
        "ALTER TABLE protected_assets_whitelist ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE",
        "CREATE INDEX IF NOT EXISTS idx_alerts_sede ON alerts(sede)"
    ]
    for st in alter_statements:
        conn.run(st)

    # Recrear vistas
    conn.run("DROP VIEW IF EXISTS v_soc_unique_alerts")
    conn.run("DROP VIEW IF EXISTS v_forensic_timeline")
    conn.run("""
    CREATE VIEW v_soc_unique_alerts AS
    SELECT * FROM alerts WHERE is_soc_alert = TRUE AND is_duplicate = FALSE
    """)
    conn.run("""
    CREATE OR REPLACE VIEW v_forensic_timeline AS
    SELECT
        a.id AS alert_id, a.alert_code, a.internal_alert_id,
        a.event_timestamp_utc, a.event_timezone_raw, a.normalized_severity,
        a.incibe_class, a.incibe_type, a.mitre_stage, a.source_tool,
        a.detection_rule, a.sede, a.asset_criticality,
        a.affected_user, a.affected_host, a.source_ip, a.destination_ip,
        a.title, a.description, a.is_duplicate, a.duplicate_count,
        a.prompt_injection_detected, r.sender_email, r.subject AS email_subject,
        r.sha256 AS email_sha256, r.attachments_json
    FROM alerts a
    LEFT JOIN raw_emails r ON a.raw_email_id = r.id
    WHERE a.is_soc_alert = TRUE
    ORDER BY a.event_timestamp_utc ASC
    """)

    # Poblar sha256 y attachments en raw_emails existentes
    emails = conn.run("SELECT id, message_id, subject, body_html, body_text, attachments_json FROM raw_emails")
    for eid, mid, subj, bhtml, btxt, atts_json in emails:
        raw_bytes = f"{mid}|{subj}|{bhtml or btxt or ''}".encode("utf-8", errors="ignore")
        digest = hashlib.sha256(raw_bytes).hexdigest()
        ref = f"evidence/raw_emails/{eid}.json"
        conn.run("UPDATE raw_emails SET sha256 = :sh, raw_content_ref = :rf WHERE id = :id", sh=digest, rf=ref, id=eid)
        atts = json.loads(atts_json) if isinstance(atts_json, str) else (atts_json or [])
        for a in atts:
            fname = a.get("name", "adjunto.bin")
            mtype = a.get("contentType", "application/octet-stream")
            sz = int(a.get("size", 0) or 0)
            ash = hashlib.sha256(f"{eid}:{fname}:{sz}".encode("utf-8")).hexdigest()
            exists_att = conn.run("SELECT id FROM attachments WHERE email_id = :eid AND filename = :fn", eid=eid, fn=fname)
            if not exists_att:
                conn.run(
                    """INSERT INTO attachments (email_id, filename, mime_type, size_bytes, storage_ref, sha256)
                       VALUES (:eid, :fn, :mt, :sz, :sref, :sh)""",
                    eid=eid, fn=fname, mt=mtype, sz=sz, sref=f"evidence/attachments/{eid}_{fname}", sh=ash
                )

    # Poblar internal_alert_id, detection_rule, sede, asset_criticality, affected_user y reclasificación INCIBE en alerts existentes
    al_rows = conn.run("""
        SELECT a.id, a.title, a.description, a.affected_user, a.affected_host, a.source_ip,
               a.incibe_class, a.incibe_type, a.classification_justification, a.mitre_stage,
               r.subject, r.body_html, r.body_text
        FROM alerts a
        LEFT JOIN raw_emails r ON a.raw_email_id = r.id
    """)
    for aid, title, desc, cur_user, cur_host, cur_ip, icls, ityp, ijust, imitre, rsubj, bhtml, btxt in al_rows:
        tfields = extract_table_fields(bhtml or "")
        sede = tfields.get("sede", "No indicada")
        crit = tfields.get("criticidad", "Media")
        regla = tfields.get("regla de detección", "")
        cuenta = tfields.get("cuenta relacionada", "")
        if cuenta and not cuenta.lower().startswith("no identificad") and cuenta.lower() != "no aplica":
            user = cuenta
        else:
            user = cur_user
        recurso = tfields.get("recurso", "")
        if recurso and recurso.lower() not in ("no aplica", "no indicada", "no indicado"):
            host = recurso
        else:
            host = cur_host
        ip_raw = tfields.get("direccion relacionada", "") or tfields.get("dirección relacionada", "")
        sip = normalize_ip(ip_raw, btxt or "") or cur_ip
        combined = f"{rsubj or ''} {btxt or ''}"
        al_m = re.search(r"(AL-\d{8}-\d{4})", combined)
        sol_m = re.search(r"(SOL-[BL]-\d{3})", combined)
        int_id = sol_m.group(1) if sol_m else (al_m.group(1) if al_m else None)
        if not sol_m and "reenvío" not in (rsubj or "").lower():
            if "macro" in (rsubj or "").lower() or "contenido dañino" in regla.lower():
                icls = "Contenido dañino"
                ityp = "Malware genérico / Virus / Gusano"
                ijust = "Aviso preliminar del SOC sobre ejecución de macro en archivo de servicio, sin equipo, usuario ni hash indicados. Se clasifica provisionalmente en 'Contenido dañino -> Malware' pendiente de enriquecimiento. Nota: contiene cláusula 'HN03 (solo cuando se cita expresamente)'."
                imitre = "5. Ejecución / C2 Malware"
            else:
                for rprefix, rtuple in RULE_TO_INCIBE.items():
                    if rprefix in regla:
                        icls, ityp, _, _, _, ijust = rtuple
                        break
        conn.run(
            """UPDATE alerts
               SET internal_alert_id = :iid,
                   detection_rule = :rl,
                   sede = :sd,
                   asset_criticality = :cr,
                   affected_user = :usr,
                   affected_host = :hst,
                   source_ip = :sip,
                   incibe_class = :ic,
                   incibe_type = :it,
                   classification_justification = :ij,
                   mitre_stage = :ms
               WHERE id = :aid""",
            iid=int_id, rl=regla, sd=sede, cr=crit, usr=user, hst=host, sip=sip,
            ic=icls, it=ityp, ij=ijust, ms=imitre, aid=aid
        )

    # Poblar idempotency_key en soar_actions existentes
    soar_rows = conn.run("SELECT id, external_block_id, action, target_type, target_value, executed_at FROM soar_actions WHERE idempotency_key IS NULL")
    for sid, ext_id, act, ttype, tval, ex_at in soar_rows:
        ikey = f"SYNC-{ext_id}-{act}-{ttype}-{tval}-{sid}"
        conn.run("UPDATE soar_actions SET idempotency_key = :ik, approved_by = 'Sincronización Inicial' WHERE id = :id", ik=ikey, id=sid)

    print("Migración NEXUS 2.0 completada con éxito.")
    conn.close()

if __name__ == "__main__":
    main()
