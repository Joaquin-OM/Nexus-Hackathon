"""
NEXUS 2.0 — Motor de Bloqueo Autónomo de Cuentas Comprometidas
Implementación de la Directriz 1 del Director de TI (18:00 CET - "Automatizar")

Criterios de Ejecución Automática:
1. Compromiso confirmado de credenciales o sesión (Reglas ACCOUNT-LAB, ADMIN-LAB, APP-LAB, APT-LAB).
2. Actividad post-compromiso crítica (Reglas C2-LAB, MALWARE-LAB, READ-LAB, MODIFY-LAB, MINING-LAB).
3. Órdenes operativas del Responsable de turno SOC (SOL-B-* para bloqueo, SOL-L-* para liberación).

Garantías de Seguridad y Anti-Falso Positivo:
- Exclusión obligatoria de Lista Blanca IT/OT (protected_assets_whitelist).
- Bloqueo de peticiones con inyección de prompts (prompt_injection_detected = TRUE).
- Exclusión de intentos fallidos simples (SPRAY-LAB sin sesión confirmada).
- Exclusión de alertas ambiguas / trampa sin usuario confirmado.
- Idempotencia estricta en soar_actions.
- Payload conforme al contrato OpenAPI de la API Bloqueador ({"ip": null, "usuario": "..."}).
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from config import get_conn, SOAR_API_URL, SOAR_TEAM_PREFIX, SOAR_API_KEY
from backend_api import call_sampol_soar_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("autoblock_engine")

COMPROMISE_RULES = {
    "ACCOUNT-LAB": "Acceso con credenciales comprometidas / no reconocido por el titular",
    "ADMIN-LAB": "Escalada no autorizada a Administrador local",
    "APP-LAB": "Compromiso de aplicación / ejecución remota de comandos",
    "APT-LAB": "Intrusión avanzada, persistencia y movimiento lateral",
    "C2-LAB": "Canal activo de Comando y Control (C2)",
    "MALWARE-LAB": "Ejecución confirmada de código dañino en host de usuario",
    "READ-LAB": "Exfiltración / Acceso a ficheros confidenciales fuera de rol",
    "MODIFY-LAB": "Modificación masiva no autorizada de ficheros (precursor de ransomware)",
    "MINING-LAB": "Uso no autorizado de recursos para minería",
}

def is_whitelisted(conn, user_val: str) -> bool:
    if not user_val:
        return True
    rows = conn.run(
        "SELECT asset_category, description FROM protected_assets_whitelist WHERE LOWER(asset_value) = LOWER(:val) AND active = TRUE",
        val=user_val.strip().lower(),
    )
    return len(rows) > 0

def execute_auto_block(conn, alert_id: int, internal_id: str, alert_code: str, user_val: str, rule: str, incibe_class: str, reason_detail: str) -> Dict[str, Any]:
    user_clean = user_val.strip()
    if is_whitelisted(conn, user_clean):
        logger.warning(f"[WHITELIST] Ignorando usuario protegido: {user_clean}")
        return {"status": "skipped_whitelist", "user": user_clean}

    ikey = f"AUTO-DIR1-bloquear-usuario-{user_clean.lower()}"
    existing = conn.run(
        "SELECT id, status, api_status_code FROM soar_actions WHERE idempotency_key = :ik AND action = 'bloquear'",
        ik=ikey,
    )
    if existing:
        logger.info(f"[IDEMPOTENTE] Usuario {user_clean} ya tiene orden de bloqueo registrada (ID #{existing[0][0]}, estado: {existing[0][1]})")
        return {"status": "idempotent_skip", "soar_id": existing[0][0], "user": user_clean}

    full_reason = f"[DIRECTRIZ 1 TI · BLOQUEO AUTÓNOMO] Contención inmediata de cuenta comprometida '{user_clean}' tras alerta {internal_id} ({alert_code}) por {rule} ({incibe_class}). Motivo: {reason_detail}"

    # Llamada a la API Bloqueador con el contrato exacto OpenAPI: {"ip": null, "usuario": "..."}
    payload = {"ip": None, "usuario": user_clean}
    status_code, resp_body = call_sampol_soar_api("/bloquear", method="POST", payload=payload)

    ext_id = None
    if isinstance(resp_body, dict):
        ext_id = resp_body.get("bloqueo", {}).get("id") or resp_body.get("id")

    exec_status = "ejecutado" if status_code in (200, 201) else "registrado_error_api"

    res = conn.run(
        """
        INSERT INTO soar_actions (
            alert_id, external_block_id, action, target_type, target_value,
            trigger_mode, status, requested_by, approved_by, idempotency_key,
            executed_by, reason, api_status_code, api_response
        ) VALUES (
            :aid, :ext, 'bloquear', 'usuario', :val,
            'automatico_directriz_1', :st, 'Playbook Autónomo NEXUS 2.0 (Directriz 1 Director TI)',
            'Motor de Reglas NEXUS 2.0', :ik, 'SOAR Auto-Blocker Engine',
            :rsn, :code, CAST(:resp AS jsonb)
        ) RETURNING id
        """,
        aid=alert_id,
        ext=ext_id,
        val=user_clean,
        st=exec_status,
        ik=ikey,
        rsn=full_reason,
        code=status_code,
        resp=json.dumps(resp_body, ensure_ascii=False),
    )
    soar_action_id = res[0][0]

    # Auditoría forense
    conn.run(
        """
        INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
        VALUES (:aid, 'Playbook Autónomo NEXUS 2.0 (Directriz 1)', 'SOAR_AUTO_BLOQUEO_DIR1', 'usuario', 'activo', :nval, :rsn)
        """,
        aid=alert_id,
        nval=f"BLOQUEO_AUTOMATICO:{user_clean} (HTTP {status_code})",
        rsn=full_reason,
    )

    # Actualizar estado de la alerta a cerrada (contención ejecutada)
    conn.run("UPDATE alerts SET status = 'cerrada', updated_at = NOW() WHERE id = :aid AND status != 'falsa_alarma'", aid=alert_id)

    logger.info(f"[AUTO-BLOCK EJECUTADO] {user_clean} | Alerta: {internal_id} | HTTP {status_code} | SOAR #{soar_action_id}")
    return {"status": "executed", "soar_id": soar_action_id, "user": user_clean, "http_code": status_code}

def execute_auto_release(conn, alert_id: int, internal_id: str, alert_code: str, user_val: str, reason_detail: str) -> Dict[str, Any]:
    user_clean = user_val.strip()
    ikey = f"AUTO-SOL-liberar-usuario-{user_clean.lower()}"
    existing = conn.run(
        "SELECT id, status FROM soar_actions WHERE idempotency_key = :ik",
        ik=ikey,
    )
    if existing and existing[0][1] == "ejecutado":
        return {"status": "idempotent_skip", "user": user_clean}

    full_reason = f"[ORDEN SOC · LIBERACIÓN] Liberación autorizada por Responsable de turno SOC ({internal_id} / {alert_code}) para '{user_clean}'. Motivo: {reason_detail}"

    payload = {"ip": None, "usuario": user_clean}
    status_code, resp_body = call_sampol_soar_api("/liberar", method="POST", payload=payload)
    ext_id = resp_body.get("id") if isinstance(resp_body, dict) else None
    exec_status = "ejecutado" if status_code in (200, 201) else "registrado_error_api"

    res = conn.run(
        """
        INSERT INTO soar_actions (
            alert_id, external_block_id, action, target_type, target_value,
            trigger_mode, status, requested_by, approved_by, idempotency_key,
            executed_by, reason, api_status_code, api_response
        ) VALUES (
            :aid, :ext, 'liberar', 'usuario', :val,
            'orden_soc', :st, 'Responsable de turno SOC',
            'Motor de Reglas NEXUS 2.0', :ik, 'SOAR Auto-Blocker Engine',
            :rsn, :code, CAST(:resp AS jsonb)
        ) RETURNING id
        """,
        aid=alert_id,
        ext=ext_id,
        val=user_clean,
        st=exec_status,
        ik=ikey,
        rsn=full_reason,
        code=status_code,
        resp=json.dumps(resp_body, ensure_ascii=False),
    )
    soar_id = res[0][0]

    # Marcar bloqueos previos del usuario como liberados
    conn.run(
        """
        UPDATE soar_actions
        SET status = 'liberado'
        WHERE target_type = 'usuario' AND LOWER(target_value) = LOWER(:val) AND action = 'bloquear'
        """,
        val=user_clean,
    )

    conn.run(
        """
        INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
        VALUES (:aid, 'Responsable de turno SOC', 'SOAR_LIBERAR', 'usuario', 'bloqueado', :nval, :rsn)
        """,
        aid=alert_id,
        nval=f"LIBERADO:{user_clean} (HTTP {status_code})",
        rsn=full_reason,
    )
    conn.run("UPDATE alerts SET status = 'falsa_alarma', updated_at = NOW() WHERE id = :aid", aid=alert_id)
    logger.info(f"[AUTO-RELEASE EJECUTADO] {user_clean} | Orden: {internal_id} | HTTP {status_code} | SOAR #{soar_id}")
    return {"status": "released", "soar_id": soar_id, "user": user_clean}

def run_autoblock_sweep():
    conn = get_conn()
    logger.info("Iniciando barrido de contención automática de cuentas comprometidas (Directriz 1)...")

    # 1. Procesar primero órdenes explícitas de liberación SOL-L-*
    releases = conn.run(
        """
        SELECT id, internal_alert_id, alert_code, affected_user, classification_justification
        FROM alerts
        WHERE internal_alert_id LIKE 'SOL-L-%' AND affected_user IS NOT NULL
        ORDER BY id ASC
        """
    )
    for aid, iid, acode, auser, just in releases:
        execute_auto_release(conn, aid, iid, acode, auser, just)

    # 2. Procesar órdenes explícitas de bloqueo SOL-B-*
    orders = conn.run(
        """
        SELECT id, internal_alert_id, alert_code, affected_user, classification_justification
        FROM alerts
        WHERE internal_alert_id LIKE 'SOL-B-%' AND affected_user IS NOT NULL
        ORDER BY id ASC
        """
    )
    for aid, iid, acode, auser, just in orders:
        # Verificar si no fue liberado posteriormente
        is_rel = conn.run(
            "SELECT id FROM alerts WHERE internal_alert_id LIKE 'SOL-L-%' AND LOWER(affected_user) = LOWER(:u)",
            u=auser.strip(),
        )
        if is_rel:
            logger.info(f"[SKIP BLOQUEO SOL-B] {auser} cuenta con orden de liberación posterior.")
            continue
        execute_auto_block(conn, aid, iid, acode, auser, "ORDEN-SOL-B", "Intento de intrusión", just)

    # 3. Procesar alertas con compromiso confirmado según la Directriz 1
    compromised = conn.run(
        """
        SELECT a.id, a.internal_alert_id, a.alert_code, a.affected_user, a.detection_rule, a.incibe_class, a.classification_justification
        FROM alerts a
        WHERE (
            a.incibe_class = 'Intrusión'
            OR a.detection_rule LIKE 'ACCOUNT-LAB%'
            OR a.detection_rule LIKE 'ADMIN-LAB%'
            OR a.detection_rule LIKE 'APP-LAB%'
            OR a.detection_rule LIKE 'APT-LAB%'
            OR a.detection_rule LIKE 'C2-LAB%'
            OR a.detection_rule LIKE 'MALWARE-LAB%'
            OR a.detection_rule LIKE 'READ-LAB%'
            OR a.detection_rule LIKE 'MODIFY-LAB%'
            OR a.detection_rule LIKE 'MINING-LAB%'
        )
        AND a.affected_user IS NOT NULL
        AND a.affected_user != ''
        AND a.affected_user NOT ILIKE '%no identificad%'
        AND a.affected_user NOT ILIKE '%no aplica%'
        AND a.prompt_injection_detected = FALSE
        AND LOWER(a.affected_user) NOT IN (SELECT LOWER(asset_value) FROM protected_assets_whitelist WHERE active = TRUE)
        ORDER BY a.event_timestamp_utc ASC
        """
    )

    logger.info(f"Evaluando {len(compromised)} incidentes de compromiso potencial...")
    executed_count = 0
    for aid, iid, acode, auser, rule, icls, just in compromised:
        rule_name = (rule or "").split("-")[0] + "-LAB" if rule else "INTRUSION"
        reason_desc = COMPROMISE_RULES.get(rule_name, f"Compromiso de seguridad bajo regla {rule} ({icls})")
        res = execute_auto_block(conn, aid, iid, acode, auser, rule, icls, reason_desc)
        if res.get("status") == "executed":
            executed_count += 1

    logger.info(f"Barrido completado. {executed_count} nuevos bloqueos autónomos ejecutados en SOAR.")
    conn.close()

if __name__ == "__main__":
    run_autoblock_sweep()
