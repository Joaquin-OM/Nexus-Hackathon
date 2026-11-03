import hashlib
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import get_conn, SOAR_API_URL, SOAR_API_KEY, SOAR_TEAM_PREFIX
from ingest_and_classify import (
    RULE_TO_INCIBE,
    detect_prompt_injection,
    normalize_ip,
    main as run_graph_ingest,
)
from notifications.router import router as smart_notifications_router

app = FastAPI(
    title="NEXUS 2.0 — SOC API (Equipo 1)",
    description="API interna para ingesta, clasificación INCIBE, auditoría, investigación forense y orquestación SOAR supervisada.",
    version="2.0.0",
)

app.include_router(smart_notifications_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELOS PYDANTIC (Contratos Sección 6.8 NEXUS 2.0)
# ============================================================================

class IngestEventPayload(BaseModel):
    provider_message_id: Optional[str] = None
    received_at: Optional[str] = None
    original_timezone: Optional[str] = "UTC"
    sender_email: Optional[str] = "soc-hackaton@sampol.com"
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = ""
    raw_content_ref: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = []
    sync_from_graph: Optional[bool] = False

class ClassifyRequest(BaseModel):
    subject: str
    body_text: str
    detection_rule: Optional[str] = ""

class AlertPatchRequest(BaseModel):
    incibe_class: Optional[str] = None
    incibe_type: Optional[str] = None
    normalized_severity: Optional[str] = None
    status: Optional[str] = None
    classification_justification: Optional[str] = None
    changed_by: str = "Analista SOC (Equipo 1)"
    reason: str = "Revisión manual desde Cuadro de Mando"

class SoarRequestPayload(BaseModel):
    alert_id: Optional[int] = None
    target_type: str  # "ip" o "usuario"
    target_value: str
    requested_by: str = "Responsable SOC / Analista"
    reason: str = "Contención solicitada"
    idempotency_key: Optional[str] = None
    auto_approve: bool = False
    approved_by: Optional[str] = None

class SoarApprovePayload(BaseModel):
    soar_action_id: Optional[int] = None
    target_type: Optional[str] = None
    target_value: Optional[str] = None
    alert_id: Optional[int] = None
    approved_by: str = "Director TI / Supervisor SOC"
    reason: str = "Contención autorizada tras verificar whitelist"

class SoarReleasePayload(BaseModel):
    target_type: str  # "ip" o "usuario"
    target_value: str
    alert_id: Optional[int] = None
    executed_by: str = "Supervisor SOC (Equipo 1)"
    reason: str = "Liberación controlada / Falso positivo verificado"

# ============================================================================
# HELPERS DE CLASIFICACIÓN Y LLAMADAS SOAR
# ============================================================================

def semantic_classify(subject: str, body_text: str, detection_rule: str = ""):
    pi_detected, pi_evidence = detect_prompt_injection(body_text, "")
    for rprefix, rtuple in RULE_TO_INCIBE.items():
        if rprefix in (detection_rule or "").upper():
            c, t, d, imp, sec, just = rtuple
            return {
                "incibe_class": c,
                "incibe_type": t,
                "danger_level": d,
                "impact_level": imp,
                "secondary_class": sec,
                "confidence": 96.0,
                "justification": just,
                "prompt_injection_detected": pi_detected,
                "prompt_injection_evidence": pi_evidence,
            }
    txt = f"{subject} {body_text}".lower()
    if any(w in txt for w in ("ransomware", "cifrad", "malware", "ejecutable malicioso", "c&c", "mando", "troyano")):
        return {
            "incibe_class": "Contenido dañino",
            "incibe_type": "Malware genérico / Virus / Gusano",
            "danger_level": "Muy Alto",
            "impact_level": "Crítico (OT/Planta)",
            "secondary_class": "Intrusión",
            "confidence": 89.0,
            "justification": "Detección semántica de indicadores de código dañino / C2 / ransomware.",
            "prompt_injection_detected": pi_detected,
            "prompt_injection_evidence": pi_evidence,
        }
    if any(w in txt for w in ("phishing", "suplantación", "formulario falso", "minería", "licencia")):
        return {
            "incibe_class": "Fraude",
            "incibe_type": "Phishing / Spear Phishing",
            "danger_level": "Alto",
            "impact_level": "Medio",
            "secondary_class": "Intento de intrusión",
            "confidence": 88.0,
            "justification": "Detección semántica de suplantación, phishing o uso ilegítimo de recursos.",
            "prompt_injection_detected": pi_detected,
            "prompt_injection_evidence": pi_evidence,
        }
    if any(w in txt for w in ("accesos fallidos", "fuerza bruta", "explotación", "waf")):
        return {
            "incibe_class": "Intento de intrusión",
            "incibe_type": "Fuerza bruta / Diccionario",
            "danger_level": "Alto",
            "impact_level": "Medio",
            "secondary_class": "Intrusión",
            "confidence": 90.0,
            "justification": "Detección semántica de intentos de autenticación fallidos o explotación bloqueada.",
            "prompt_injection_detected": pi_detected,
            "prompt_injection_evidence": pi_evidence,
        }
    if any(w in txt for w in ("spam", "correo masivo", "publicidad no deseada", "abusivo")):
        return {
            "incibe_class": "Contenido abusivo",
            "incibe_type": "Spam",
            "danger_level": "Bajo",
            "impact_level": "Bajo",
            "secondary_class": "Otros",
            "confidence": 88.0,
            "justification": "Detección de envío masivo no deseado o contenido abusivo según guía INCIBE.",
            "prompt_injection_detected": pi_detected,
            "prompt_injection_evidence": pi_evidence,
        }
    return {
        "incibe_class": "Otros",
        "incibe_type": "Correo ajeno al SOC / Sin clasificar",
        "danger_level": "Bajo",
        "impact_level": "Bajo",
        "secondary_class": None,
        "confidence": 75.0,
        "justification": "Sin coincidencia determinista con reglas de amenaza activas; clasificado en Otros.",
        "prompt_injection_detected": pi_detected,
        "prompt_injection_evidence": pi_evidence,
    }

def call_sampol_soar_api(endpoint_suffix: str, method: str = "GET", payload: Optional[dict] = None):
    url = f"{SOAR_API_URL}{SOAR_TEAM_PREFIX}{endpoint_suffix}"
    headers = {"X-API-Key": SOAR_API_KEY, "Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        err_txt = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_txt)
        except Exception:
            err_json = {"error": err_txt}
        return e.code, err_json

# ============================================================================
# ENDPOINTS FASTAPI
# ============================================================================

@app.get("/health")
def health():
    conn = get_conn()
    total_emails = conn.run("SELECT COUNT(*) FROM raw_emails")[0][0]
    total_alerts = conn.run("SELECT COUNT(*) FROM v_soc_unique_alerts")[0][0]
    conn.close()
    return {
        "status": "ok",
        "service": "NEXUS 2.0 FastAPI",
        "raw_emails_count": total_emails,
        "unique_soc_alerts": total_alerts,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/classify")
def classify_endpoint(req: ClassifyRequest):
    return semantic_classify(req.subject, req.body_text, req.detection_rule or "")

@app.post("/ingest")
def ingest_endpoint(payload: IngestEventPayload):
    if payload.sync_from_graph or not payload.provider_message_id:
        run_graph_ingest()
        conn = get_conn()
        total_emails = conn.run("SELECT COUNT(*) FROM raw_emails")[0][0]
        total_alerts = conn.run("SELECT COUNT(*) FROM v_soc_unique_alerts")[0][0]
        conn.close()
        return {"status": "synced_from_graph", "raw_emails": total_emails, "unique_alerts": total_alerts}

    conn = get_conn()
    existing = conn.run("SELECT id FROM raw_emails WHERE message_id = :mid", mid=payload.provider_message_id)
    if existing:
        conn.close()
        return {"status": "idempotent_skip", "raw_email_id": existing[0][0]}

    raw_bytes = f"{payload.provider_message_id}|{payload.subject}|{payload.body_html or payload.body_text}".encode("utf-8", errors="ignore")
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
    rec_utc = payload.received_at or datetime.now(timezone.utc).isoformat()
    res_raw = conn.run(
        """INSERT INTO raw_emails (message_id, sender_email, subject, body_text, body_html, raw_content_ref, sha256, original_timezone, received_at_utc)
           VALUES (:mid, :sem, :subj, :btxt, :bhtml, :rref, :sha, :otz, :rutc) RETURNING id""",
        mid=payload.provider_message_id,
        sem=payload.sender_email,
        subj=payload.subject or "(Sin asunto)",
        btxt=payload.body_text or "",
        bhtml=payload.body_html or "",
        rref=payload.raw_content_ref or f"evidence/webhook/{sha256_hex[:12]}.eml",
        sha=sha256_hex,
        otz=payload.original_timezone or "UTC",
        rutc=rec_utc,
    )
    raw_id = res_raw[0][0]
    cls_res = semantic_classify(payload.subject or "", payload.body_text or "")
    acode = f"SOC-WH-{raw_id:04d}"
    res_al = conn.run(
        """INSERT INTO alerts (
               alert_code, raw_email_id, event_timestamp_utc, event_timezone_raw,
               source_tool, normalized_severity, incibe_class, incibe_type,
               incibe_danger_level, incibe_impact_level, classification_justification,
               confidence_score, title, description, prompt_injection_detected, prompt_injection_evidence
           ) VALUES (
               :acode, :reid, :ets, :otz, 'Webhook / n8n', 'MEDIA', :icls, :ityp,
               :idng, :iimp, :just, :conf, :title, :desc, :pidet, :piev
           ) RETURNING id""",
        acode=acode,
        reid=raw_id,
        ets=rec_utc,
        otz=payload.original_timezone or "UTC",
        icls=cls_res["incibe_class"],
        ityp=cls_res["incibe_type"],
        idng=cls_res["danger_level"],
        iimp=cls_res["impact_level"],
        just=cls_res["justification"],
        conf=cls_res["confidence"],
        title=payload.subject or "Alerta Ingerida",
        desc=(payload.body_text or "")[:500],
        pidet=cls_res["prompt_injection_detected"],
        piev=cls_res["prompt_injection_evidence"],
    )
    conn.close()
    return {"status": "ingested", "raw_email_id": raw_id, "alert_id": res_al[0][0], "sha256": sha256_hex}

@app.get("/alerts")
def list_alerts(
    incibe_class: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    sede: Optional[str] = None,
    include_duplicates: bool = False,
    only_soc: bool = True,
    search: Optional[str] = None,
    limit: int = Query(200, ge=1, le=500),
):
    conn = get_conn()
    clauses = ["1=1"]
    params: Dict[str, Any] = {"lim": limit}
    if only_soc:
        clauses.append("a.is_soc_alert = TRUE")
    if not include_duplicates:
        clauses.append("a.is_duplicate = FALSE")
    if incibe_class:
        clauses.append("a.incibe_class = :icls")
        params["icls"] = incibe_class
    if severity:
        clauses.append("a.normalized_severity = :sev")
        params["sev"] = severity
    if status:
        clauses.append("a.status = :st")
        params["st"] = status
    if sede:
        clauses.append("a.sede = :sd")
        params["sd"] = sede
    if search:
        clauses.append("(a.title ILIKE :q OR a.description ILIKE :q OR a.affected_user ILIKE :q OR a.affected_host ILIKE :q OR a.source_ip ILIKE :q OR a.alert_code ILIKE :q OR a.internal_alert_id ILIKE :q)")
        params["q"] = f"%{search}%"

    sql = f"""
        SELECT
            a.id, a.alert_code, a.internal_alert_id, a.event_timestamp_utc, a.event_timezone_raw,
            a.source_tool, a.detection_rule, a.normalized_severity,
            a.incibe_class, a.incibe_type, a.incibe_danger_level, a.incibe_impact_level,
            a.classification_justification, a.affected_host, a.source_ip, a.affected_user,
            a.sede, a.asset_criticality, a.status, a.is_duplicate, a.duplicate_count,
            a.prompt_injection_detected, a.title, r.sha256
        FROM alerts a
        LEFT JOIN raw_emails r ON a.raw_email_id = r.id
        WHERE {' AND '.join(clauses)}
        ORDER BY a.event_timestamp_utc DESC
        LIMIT :lim
    """
    rows = conn.run(sql, **params)
    conn.close()
    cols = [
        "id", "alert_code", "internal_alert_id", "event_timestamp_utc", "event_timezone_raw",
        "source_tool", "detection_rule", "normalized_severity",
        "incibe_class", "incibe_type", "incibe_danger_level", "incibe_impact_level",
        "classification_justification", "affected_host", "source_ip", "affected_user",
        "sede", "asset_criticality", "status", "is_duplicate", "duplicate_count",
        "prompt_injection_detected", "title", "email_sha256"
    ]
    return [dict(zip(cols, [str(v) if isinstance(v, datetime) else v for v in r])) for r in rows]

@app.get("/alerts/{alert_id}")
def get_alert_detail(alert_id: int):
    conn = get_conn()
    rows = conn.run(
        """SELECT a.id, a.alert_code, a.internal_alert_id, a.raw_email_id,
                  a.event_timestamp_utc, a.event_timezone_raw, a.source_tool, a.detection_rule,
                  a.normalized_severity, a.incibe_class, a.incibe_type, a.incibe_danger_level,
                  a.incibe_impact_level, a.classification_justification, a.secondary_incibe_class,
                  a.affected_host, a.source_ip, a.affected_user, a.sede, a.asset_criticality,
                  a.ioc_list, a.mitre_stage, a.title, a.description, a.status,
                  a.is_duplicate, a.parent_alert_id, a.duplicate_count,
                  a.prompt_injection_detected, a.prompt_injection_evidence,
                  r.subject, r.sender_email, r.received_at_utc, r.original_timezone,
                  r.sha256, r.body_text, r.body_html
           FROM alerts a
           LEFT JOIN raw_emails r ON a.raw_email_id = r.id
           WHERE a.id = :aid""",
        aid=alert_id,
    )
    if not rows:
        conn.close()
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    r = rows[0]
    audit = conn.run(
        "SELECT changed_by, action_type, field_changed, old_value, new_value, reason, changed_at FROM alert_audit_log WHERE alert_id = :aid ORDER BY changed_at DESC",
        aid=alert_id,
    )
    children = conn.run(
        "SELECT id, alert_code, internal_alert_id, title, status, event_timestamp_utc FROM alerts WHERE parent_alert_id = :aid ORDER BY event_timestamp_utc ASC",
        aid=alert_id,
    )
    conn.close()
    return {
        "id": r[0],
        "alert_code": r[1],
        "internal_alert_id": r[2],
        "raw_email_id": r[3],
        "event_timestamp_utc": str(r[4]),
        "event_timezone_raw": r[5],
        "source_tool": r[6],
        "detection_rule": r[7],
        "normalized_severity": r[8],
        "incibe_class": r[9],
        "incibe_type": r[10],
        "incibe_danger_level": r[11],
        "incibe_impact_level": r[12],
        "classification_justification": r[13],
        "secondary_incibe_class": r[14],
        "affected_host": r[15],
        "source_ip": r[16],
        "affected_user": r[17],
        "sede": r[18],
        "asset_criticality": r[19],
        "ioc_list": r[20],
        "mitre_stage": r[21],
        "title": r[22],
        "description": r[23],
        "status": r[24],
        "is_duplicate": r[25],
        "parent_alert_id": r[26],
        "duplicate_count": r[27],
        "prompt_injection_detected": r[28],
        "prompt_injection_evidence": r[29],
        "raw_email": {
            "subject": r[30],
            "sender_email": r[31],
            "received_at_utc": str(r[32]),
            "original_timezone": r[33],
            "sha256": r[34],
            "body_text": r[35],
            "body_html": r[36],
        },
        "audit_log": [
            {
                "changed_by": a[0],
                "action_type": a[1],
                "field_changed": a[2],
                "old_value": a[3],
                "new_value": a[4],
                "reason": a[5],
                "changed_at": str(a[6]),
            }
            for a in audit
        ],
        "linked_duplicates_or_orders": [
            {"id": c[0], "alert_code": c[1], "internal_alert_id": c[2], "title": c[3], "status": c[4], "timestamp": str(c[5])}
            for c in children
        ],
    }

@app.patch("/alerts/{alert_id}")
def patch_alert(alert_id: int, req: AlertPatchRequest):
    conn = get_conn()
    curr = conn.run(
        "SELECT incibe_class, incibe_type, normalized_severity, status, classification_justification FROM alerts WHERE id = :aid",
        aid=alert_id,
    )
    if not curr:
        conn.close()
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    old_cls, old_typ, old_sev, old_st, old_just = curr[0]

    new_cls = req.incibe_class or old_cls
    new_typ = req.incibe_type or old_typ
    new_sev = req.normalized_severity or old_sev
    new_st = req.status or old_st
    new_just = req.classification_justification or old_just

    conn.run(
        """UPDATE alerts
           SET incibe_class = :cls, incibe_type = :typ, normalized_severity = :sev,
               status = :st, classification_justification = :just,
               classified_by = :cby, reviewed_by_human = TRUE, updated_at = NOW()
           WHERE id = :aid""",
        cls=new_cls, typ=new_typ, sev=new_sev, st=new_st, just=new_just, cby=req.changed_by, aid=alert_id,
    )

    if new_cls != old_cls or new_typ != old_typ:
        conn.run(
            """INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
               VALUES (:aid, :cby, 'CAMBIO_CATEGORIA', 'incibe_class', :oldv, :newv, :rsn)""",
            aid=alert_id, cby=req.changed_by, oldv=f"{old_cls} / {old_typ}", newv=f"{new_cls} / {new_typ}", rsn=req.reason,
        )
    if new_st != old_st:
        conn.run(
            """INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
               VALUES (:aid, :cby, 'CAMBIO_ESTADO', 'status', :oldv, :newv, :rsn)""",
            aid=alert_id, cby=req.changed_by, oldv=old_st, newv=new_st, rsn=req.reason,
        )
    conn.close()
    return {"status": "updated", "alert_id": alert_id}

@app.post("/soar/request")
def soar_request(req: SoarRequestPayload):
    conn = get_conn()
    # Verificar Whitelist IT/OT
    wl = conn.run(
        "SELECT asset_category, description FROM protected_assets_whitelist WHERE LOWER(asset_value) = LOWER(:val) AND active = TRUE",
        val=req.target_value.strip(),
    )
    if wl:
        conn.close()
        raise HTTPException(
            status_code=403,
            detail=f"BLOQUEADO POR WHITELIST IT/OT ({wl[0][0]}): '{req.target_value}' es un activo protegido ({wl[0][1]}). No se permite bloqueo automático.",
        )

    ikey = req.idempotency_key or f"REQ-bloquear-{req.target_type}-{req.target_value.lower()}"
    existing = conn.run("SELECT id, status, api_response FROM soar_actions WHERE idempotency_key = :ik", ik=ikey)
    if existing:
        conn.close()
        return {"status": "idempotent_existing", "soar_action_id": existing[0][0], "current_status": existing[0][1]}

    if not req.auto_approve:
        res = conn.run(
            """INSERT INTO soar_actions (alert_id, action, target_type, target_value, trigger_mode, status, requested_by, idempotency_key, reason)
               VALUES (:aid, 'bloquear', :ttype, :tval, 'solicitud_supervisada', 'pendiente_aprobacion', :rby, :ik, :rsn) RETURNING id""",
            aid=req.alert_id, ttype=req.target_type, tval=req.target_value.strip(), rby=req.requested_by, ik=ikey, rsn=req.reason,
        )
        conn.close()
        return {"status": "pendiente_aprobacion", "soar_action_id": res[0][0], "idempotency_key": ikey}

    conn.close()
    return soar_approve(
        SoarApprovePayload(
            target_type=req.target_type,
            target_value=req.target_value,
            alert_id=req.alert_id,
            approved_by=req.approved_by or req.requested_by,
            reason=req.reason,
        )
    )

@app.post("/soar/approve")
def soar_approve(req: SoarApprovePayload):
    conn = get_conn()
    if req.soar_action_id:
        row = conn.run("SELECT target_type, target_value, alert_id, reason FROM soar_actions WHERE id = :id", id=req.soar_action_id)
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Solicitud SOAR no encontrada")
        ttype, tval, aid, rsn = row[0]
    else:
        ttype = req.target_type or "usuario"
        tval = (req.target_value or "").strip()
        aid = req.alert_id
        rsn = req.reason

    # Verificar Whitelist IT/OT
    wl = conn.run(
        "SELECT asset_category, description FROM protected_assets_whitelist WHERE LOWER(asset_value) = LOWER(:val) AND active = TRUE",
        val=tval,
    )
    if wl:
        conn.close()
        raise HTTPException(
            status_code=403,
            detail=f"BLOQUEADO POR WHITELIST IT/OT ({wl[0][0]}): '{tval}' ({wl[0][1]}).",
        )

    body = {"ip": tval if ttype == "ip" else None, "usuario": tval if ttype == "usuario" else None}
    http_code, api_resp = call_sampol_soar_api("/bloquear", method="POST", payload=body)
    ext_id = api_resp.get("bloqueo", {}).get("id") if isinstance(api_resp, dict) else None
    ikey = f"EXEC-bloquear-{ttype}-{tval.lower()}-{int(datetime.now().timestamp())}"

    if req.soar_action_id:
        conn.run(
            """UPDATE soar_actions
               SET status = 'ejecutado', approved_by = :aby, external_block_id = :eid,
                   api_status_code = :code, api_response = :resp, executed_at = NOW()
               WHERE id = :id""",
            aby=req.approved_by, eid=ext_id, code=http_code, resp=json.dumps(api_resp), id=req.soar_action_id,
        )
        action_id = req.soar_action_id
    else:
        res = conn.run(
            """INSERT INTO soar_actions (external_block_id, alert_id, action, target_type, target_value, trigger_mode, status, requested_by, approved_by, idempotency_key, api_status_code, api_response, reason, executed_by)
               VALUES (:eid, :aid, 'bloquear', :ttype, :tval, 'aprobado_humano', 'ejecutado', :aby, :aby, :ik, :code, :resp, :rsn, :aby) RETURNING id""",
            eid=ext_id, aid=aid, ttype=ttype, tval=tval, aby=req.approved_by, ik=ikey, code=http_code, resp=json.dumps(api_resp), rsn=rsn,
        )
        action_id = res[0][0]

    if aid:
        conn.run(
            """INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
               VALUES (:aid, :aby, 'ACCION_SOAR', :ttype, 'activo', :nval, :rsn)""",
            aid=aid, aby=req.approved_by, ttype=ttype, nval=f"BLOQUEADO: {tval} (HTTP {http_code})", rsn=rsn,
        )
    conn.close()
    return {"status": "ejecutado", "soar_action_id": action_id, "http_code": http_code, "api_response": api_resp}

@app.post("/soar/release")
def soar_release(req: SoarReleasePayload):
    conn = get_conn()
    ttype = req.target_type
    tval = req.target_value.strip()
    body = {"ip": tval if ttype == "ip" else None, "usuario": tval if ttype == "usuario" else None}
    http_code, api_resp = call_sampol_soar_api("/liberar", method="POST", payload=body)
    ext_id = api_resp.get("bloqueo", {}).get("id") if isinstance(api_resp, dict) else None
    ikey = f"REL-liberar-{ttype}-{tval.lower()}-{int(datetime.now().timestamp())}"

    res = conn.run(
        """INSERT INTO soar_actions (external_block_id, alert_id, action, target_type, target_value, trigger_mode, status, requested_by, approved_by, idempotency_key, api_status_code, api_response, reason, executed_by)
           VALUES (:eid, :aid, 'liberar', :ttype, :tval, 'liberacion_controlada', 'liberado', :eby, :eby, :ik, :code, :resp, :rsn, :eby) RETURNING id""",
        eid=ext_id, aid=req.alert_id, ttype=ttype, tval=tval, eby=req.executed_by, ik=ikey, code=http_code, resp=json.dumps(api_resp), rsn=req.reason,
    )
    if req.alert_id:
        conn.run(
            """INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
               VALUES (:aid, :eby, 'ACCION_SOAR', :ttype, 'bloqueado', :nval, :rsn)""",
            aid=req.alert_id, eby=req.executed_by, ttype=ttype, nval=f"LIBERADO: {tval} (HTTP {http_code})", rsn=req.reason,
        )
    conn.close()
    return {"status": "liberado", "soar_action_id": res[0][0], "http_code": http_code, "api_response": api_resp}

@app.get("/soar/status")
def soar_status():
    http_code, live_blocks = call_sampol_soar_api("/bloqueos", method="GET")
    conn = get_conn()
    local_actions = conn.run(
        "SELECT id, action, target_type, target_value, status, requested_by, approved_by, reason, api_status_code, executed_at FROM soar_actions ORDER BY executed_at DESC LIMIT 50"
    )
    whitelist = conn.run("SELECT asset_type, asset_value, asset_category, description FROM protected_assets_whitelist WHERE active = TRUE")
    conn.close()
    return {
        "live_api_http_code": http_code,
        "live_api_blocks": live_blocks if isinstance(live_blocks, list) else [],
        "audit_actions": [
            {
                "id": a[0], "action": a[1], "target_type": a[2], "target_value": a[3],
                "status": a[4], "requested_by": a[5], "approved_by": a[6],
                "reason": a[7], "api_status_code": a[8], "executed_at": str(a[9])
            }
            for a in local_actions
        ],
        "whitelist": [
            {"asset_type": w[0], "asset_value": w[1], "asset_category": w[2], "description": w[3]}
            for w in whitelist
        ],
    }

@app.get("/metrics")
def get_metrics():
    conn = get_conn()
    total_raw = conn.run("SELECT COUNT(*) FROM raw_emails")[0][0]
    unique_soc = conn.run("SELECT COUNT(*) FROM v_soc_unique_alerts")[0][0]
    duplicates = conn.run("SELECT COUNT(*) FROM alerts WHERE is_duplicate = TRUE")[0][0]
    non_soc = conn.run("SELECT COUNT(*) FROM alerts WHERE is_soc_alert = FALSE")[0][0]
    prompt_inj = conn.run("SELECT COUNT(*) FROM alerts WHERE prompt_injection_detected = TRUE")[0][0]
    soar_ops = conn.run("SELECT COUNT(*) FROM soar_actions")[0][0]

    by_class = conn.run("SELECT incibe_class, COUNT(*) FROM v_soc_unique_alerts GROUP BY incibe_class ORDER BY COUNT(*) DESC")
    by_sev = conn.run("SELECT normalized_severity, COUNT(*) FROM v_soc_unique_alerts GROUP BY normalized_severity ORDER BY COUNT(*) DESC")
    by_sede = conn.run("SELECT sede, COUNT(*) FROM v_soc_unique_alerts GROUP BY sede ORDER BY COUNT(*) DESC")
    by_source = conn.run("SELECT source_tool, COUNT(*) FROM v_soc_unique_alerts GROUP BY source_tool ORDER BY COUNT(*) DESC")

    params_rows = conn.run("SELECT param_key, param_value FROM business_parameters")
    bparams = {k: float(v) for k, v in params_rows}
    conn.close()

    return {
        "kpis": {
            "total_raw_emails": total_raw,
            "unique_soc_alerts": unique_soc,
            "duplicates_and_orders_linked": duplicates,
            "non_soc_filtered": non_soc,
            "prompt_injections_caught": prompt_inj,
            "soar_operations_logged": soar_ops,
        },
        "by_incibe_class": [{"incibe_class": r[0], "count": r[1]} for r in by_class],
        "by_severity": [{"severity": r[0], "count": r[1]} for r in by_sev],
        "by_sede": [{"sede": r[0], "count": r[1]} for r in by_sede],
        "by_source_tool": [{"source_tool": r[0], "count": r[1]} for r in by_source],
        "business_parameters": bparams,
    }
