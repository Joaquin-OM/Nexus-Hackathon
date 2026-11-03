import json
from config import get_conn
from backend_api import call_sampol_soar_api

def main():
    conn = get_conn()
    # Obtener todas las órdenes SOL-B y SOL-L en el orden cronológico en que llegaron
    rows = conn.run(
        """
        SELECT id, internal_alert_id, alert_code, affected_user, source_ip, parent_alert_id, title
        FROM alerts
        WHERE internal_alert_id LIKE 'SOL-%'
        ORDER BY id ASC
        """
    )

    print(f"Procesando {len(rows)} órdenes operativas del Responsable de turno SOC...")
    for aid, sol_id, soc_code, user_val, ctx_ip, parent_id, title in rows:
        if not user_val:
            print(f"[SKIP] {sol_id} sin usuario objetivo.")
            continue

        # Comprobar idempotencia en soar_actions
        ikey = f"ORDER-{sol_id}-{user_val}"
        existing = conn.run("SELECT id, status FROM soar_actions WHERE idempotency_key = :ik", ik=ikey)
        if existing and existing[0][1] == "ejecutado":
            print(f"[IDEMPOTENT] {sol_id} ({user_val}) ya estaba ejecutado.")
            continue

        is_release = sol_id.startswith("SOL-L-")
        action = "liberar" if is_release else "bloquear"
        endpoint = "/liberar" if is_release else "/bloquear"
        reason = (
            f"[{sol_id} / {soc_code}] Liberación autorizada por Responsable de turno SOC tras confirmar falso positivo (conector con contraseña antigua)."
            if is_release
            else f"[{sol_id} / {soc_code}] Bloqueo preventivo de usuario autorizado por Responsable de turno SOC (IP en contexto {ctx_ip} excluida expresamente)."
        )

        payload = {"ip": None, "usuario": user_val}
        status_code, resp_body = call_sampol_soar_api(endpoint, "POST", payload)
        if status_code == 400 and not is_release:
            # Si ya se había bloqueado en la llamada previa antes del rollback de BD, recuperar de /bloqueos
            _, all_b = call_sampol_soar_api("/bloqueos", "GET")
            matched = [b for b in (all_b or []) if b.get("valor") == user_val or b.get("usuario") == user_val]
            if matched:
                status_code = 200
                resp_body = matched[0]

        ext_id = resp_body.get("id") if isinstance(resp_body, dict) else None
        exec_status = "ejecutado" if status_code in (200, 201) else "error_api"

        conn.run(
            """
            INSERT INTO soar_actions (
                alert_id, external_block_id, action, target_type, target_value,
                trigger_mode, status, requested_by, approved_by, idempotency_key,
                executed_by, reason, api_status_code, api_response
            ) VALUES (
                :aid, :ext, :act, 'usuario', :val,
                'orden_soc', :st, 'Responsable de turno SOC', 'Supervisor SOC (Equipo 1)', :ik,
                'Supervisor SOC (Equipo 1)', :rsn, :code, CAST(:resp AS jsonb)
            )
            """,
            aid=parent_id or aid,
            ext=ext_id,
            act=action,
            val=user_val,
            st=exec_status,
            ik=ikey,
            rsn=reason,
            code=status_code,
            resp=json.dumps(resp_body, ensure_ascii=False),
        )

        if is_release:
            conn.run(
                """
                UPDATE soar_actions
                SET status = 'liberado'
                WHERE target_type = 'usuario' AND LOWER(target_value) = LOWER(:val) AND action = 'bloquear'
                """,
                val=user_val,
            )
            conn.run("UPDATE alerts SET status = 'falsa_alarma', updated_at = NOW() WHERE id = :id", id=aid)
        else:
            conn.run("UPDATE alerts SET status = 'cerrada', updated_at = NOW() WHERE id = :id", id=aid)
            if parent_id:
                conn.run("UPDATE alerts SET status = 'cerrada', updated_at = NOW() WHERE id = :pid AND status != 'falsa_alarma'", pid=parent_id)

        conn.run(
            """
            INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
            VALUES (:aid, 'Supervisor SOC (Equipo 1)', :atype, 'soar_status', 'pendiente', :nval, :rsn)
            """,
            aid=parent_id or aid,
            atype="SOAR_LIBERAR" if is_release else "SOAR_BLOQUEAR",
            nval=f"{action.upper()}:usuario:{user_val} (HTTP {status_code})",
            rsn=reason,
        )
        print(f"[OK] {sol_id} -> {action.upper()} usuario '{user_val}' | HTTP {status_code} | ext_id={ext_id}")

    # Verificar estado final en la API de Sampol
    st_code, final_blocks = call_sampol_soar_api("/bloqueos", "GET")
    print(f"\n=== ESTADO FINAL EN GET /equipo-1/bloqueos (HTTP {st_code}) ===")
    for b in final_blocks:
        print(f" - ID #{b['id']} | {b['tipo']}: {b['valor']} | activo={b['activo']} | acciones={len(b.get('acciones', []))}")

    conn.close()

if __name__ == "__main__":
    main()
