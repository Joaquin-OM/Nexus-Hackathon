import json
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from config import get_conn
from ingest_and_classify import main as run_graph_ingest
from backend_api import (
    call_sampol_soar_api,
    soar_approve,
    soar_release,
    SoarApprovePayload,
    SoarReleasePayload,
)

st.set_page_config(
    page_title="NEXUS 2.0 · SOC Cuadro de Mando | SAMPOL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo corporativo Sampol / SOC
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(90deg, #0b1f3a 0%, #153e75 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 10px;
        margin-bottom: 16px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 26px; }
    .main-header p { color: #cbd5e1; margin: 4px 0 0 0; font-size: 14px; }
    .badge-crit { background:#dc2626; color:white; padding:3px 8px; border-radius:4px; font-weight:bold; }
    .badge-high { background:#ea580c; color:white; padding:3px 8px; border-radius:4px; font-weight:bold; }
    .badge-med  { background:#ca8a04; color:white; padding:3px 8px; border-radius:4px; font-weight:bold; }
    .badge-low  { background:#2563eb; color:white; padding:3px 8px; border-radius:4px; font-weight:bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

_SHARED_CONN = None

def query_df(sql: str, **params) -> pd.DataFrame:
    global _SHARED_CONN
    try:
        if _SHARED_CONN is None:
            _SHARED_CONN = get_conn()
        res = _SHARED_CONN.run(sql, **params)
        cols = [c["name"] for c in _SHARED_CONN.columns] if _SHARED_CONN.columns else []
    except Exception:
        _SHARED_CONN = get_conn()
        res = _SHARED_CONN.run(sql, **params)
        cols = [c["name"] for c in _SHARED_CONN.columns] if _SHARED_CONN.columns else []
    if not res:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(res, columns=cols)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("### 🛡️ NEXUS 2.0 · Equipo 1")
    st.caption("Hackathon FP Sampol · Reto SOC 24h")
    if st.button("🔄 Sincronizar Buzón Outlook (Graph)", use_container_width=True, type="primary"):
        with st.spinner("Conectando a Microsoft Graph y clasificando correos nuevos..."):
            run_graph_ingest()
        st.success("¡Buzón sincronizado y clasificado!")
        st.rerun()

    st.divider()
    st.markdown("**Filtros Globales del Cuadro de Mando**")
    incibe_classes_df = query_df("SELECT DISTINCT class_name FROM incibe_taxonomy ORDER BY class_name")
    all_classes = incibe_classes_df["class_name"].tolist() if not incibe_classes_df.empty else []

    sedes_df = query_df("SELECT DISTINCT sede FROM alerts WHERE is_soc_alert = TRUE AND sede IS NOT NULL ORDER BY sede")
    all_sedes = sedes_df["sede"].tolist() if not sedes_df.empty else []

    sel_class = st.selectbox("Clase INCIBE", ["Todas"] + all_classes)
    sel_sev = st.selectbox("Gravedad", ["Todas", "CRITICA", "ALTA", "MEDIA", "BAJA", "INFO"])
    sel_sede = st.selectbox("Sede Sampol", ["Todas"] + all_sedes)
    sel_status = st.selectbox("Estado", ["Todos", "nueva", "en_revision", "cerrada", "falsa_alarma"])
    show_duplicates = st.checkbox("Mostrar también duplicados / órdenes SOL", value=False)
    show_non_soc = st.checkbox("Mostrar correos ajenos al SOC / Directrices", value=False)

# ============================================================================
# CABECERA Y KPIS EN VIVO
# ============================================================================
st.markdown(
    """
    <div class="main-header">
        <h1>🛡️ SAMPOL SOC · Cuadro de Mando Ejecutivo y Consola SOAR (NEXUS 2.0)</h1>
        <p>From Alert to Action · Clasificación Guía Nacional INCIBE · Trazabilidad Forense SHA-256 · Protección Activos IT/OT</p>
    </div>
    """,
    unsafe_allow_html=True,
)

kpi_conn = get_conn()
total_emails = kpi_conn.run("SELECT COUNT(*) FROM raw_emails")[0][0]
unique_alerts = kpi_conn.run("SELECT COUNT(*) FROM v_soc_unique_alerts")[0][0]
crit_alerts = kpi_conn.run("SELECT COUNT(*) FROM v_soc_unique_alerts WHERE normalized_severity IN ('CRITICA', 'ALTA')")[0][0]
dup_count = kpi_conn.run("SELECT COUNT(*) FROM alerts WHERE is_duplicate = TRUE")[0][0]
nonsoc_count = kpi_conn.run("SELECT COUNT(*) FROM alerts WHERE is_soc_alert = FALSE")[0][0]
pi_count = kpi_conn.run("SELECT COUNT(*) FROM alerts WHERE prompt_injection_detected = TRUE")[0][0]
soar_count = kpi_conn.run("SELECT COUNT(*) FROM soar_actions")[0][0]
kpi_conn.close()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("📬 Correos Íntegros (BD)", total_emails, "SHA-256 verificado")
c2.metric("🚨 Alertas SOC Únicas", unique_alerts, f"{crit_alerts} Críticas/Altas")
c3.metric("🔁 Duplicados / Órdenes", dup_count, "Enlazados sin contar x2")
c4.metric("🧹 Ruido / No-SOC Filtrado", nonsoc_count, "Excluidos de KPIs")
c5.metric("🛡️ Trampas IA / Canary", pi_count, "Prompt Injection cazados")
c6.metric("⚡ Operaciones SOAR API", soar_count, "Auditadas en BD")

# ============================================================================
# PESTAÑAS PRINCIPALES
# ============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 1. Cuadro de Mando (Director TI)",
    "🔎 2. Buscador, Evidencia Original y Edición INCIBE",
    "⚡ 3. Consola SOAR y API Bloqueador",
    "🕵️ 4. Investigación Forense y NIS2",
    "💶 5. Caso de Negocio (ROI) y Directrices",
    "🗄️ 6. Explorador BBDD (PostgreSQL)",
])

# ----------------------------------------------------------------------------
# TAB 1: CUADRO DE MANDO EJECUTIVO
# ----------------------------------------------------------------------------
with tab1:
    st.subheader("Visión Ejecutiva en 1 Minuto (Excluyendo duplicados y ruido no-SOC)")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### Distribución por Clase de la Guía Nacional de INCIBE")
        df_cls = query_df(
            """
            SELECT incibe_class AS "Clase INCIBE", COUNT(*) AS "Alertas Únicas"
            FROM v_soc_unique_alerts
            GROUP BY incibe_class
            ORDER BY "Alertas Únicas" DESC
            """
        )
        if not df_cls.empty:
            st.bar_chart(df_cls.set_index("Clase INCIBE"))
            st.dataframe(df_cls, use_container_width=True, hide_index=True)

    with col_g2:
        st.markdown("#### Evolución Temporal de Incidentes (Normalizada a UTC)")
        df_time = query_df(
            """
            SELECT DATE_TRUNC('hour', event_timestamp_utc) AS "Hora (UTC)", COUNT(*) AS "Alertas"
            FROM v_soc_unique_alerts
            GROUP BY 1
            ORDER BY 1 ASC
            """
        )
        if not df_time.empty:
            st.line_chart(df_time.set_index("Hora (UTC)"))

        st.markdown("#### Reparto por Nivel de Gravedad y por Sede de Sampol")
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            df_sev = query_df(
                """
                SELECT normalized_severity AS "Gravedad", COUNT(*) AS "Total"
                FROM v_soc_unique_alerts
                GROUP BY normalized_severity
                ORDER BY "Total" DESC
                """
            )
            st.dataframe(df_sev, use_container_width=True, hide_index=True)
        with sub_c2:
            df_sede = query_df(
                """
                SELECT sede AS "Sede", COUNT(*) AS "Total"
                FROM v_soc_unique_alerts
                GROUP BY sede
                ORDER BY "Total" DESC
                """
            )
            st.dataframe(df_sede, use_container_width=True, hide_index=True)

    st.divider()
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown("#### 👤 Usuarios más afectados")
        df_usr = query_df(
            """
            SELECT COALESCE(affected_user, 'No identificado') AS "Usuario", COUNT(*) AS "Alertas"
            FROM v_soc_unique_alerts
            WHERE affected_user IS NOT NULL
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
            """
        )
        st.dataframe(df_usr, use_container_width=True, hide_index=True)

    with col_t2:
        st.markdown("#### 🖥️ Equipos / Recursos más afectados")
        df_hst = query_df(
            """
            SELECT COALESCE(affected_host, 'No indicado') AS "Recurso / Host", sede AS "Sede", COUNT(*) AS "Alertas"
            FROM v_soc_unique_alerts
            WHERE affected_host IS NOT NULL
            GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 10
            """
        )
        st.dataframe(df_hst, use_container_width=True, hide_index=True)

    with col_t3:
        st.markdown("#### 🌐 Fuentes de Detección del SOC")
        df_src = query_df(
            """
            SELECT source_tool AS "Herramienta / Fuente", COUNT(*) AS "Alertas"
            FROM v_soc_unique_alerts
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
            """
        )
        st.dataframe(df_src, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB 2: BUSCADOR, EVIDENCIA ORIGINAL Y EDICIÓN INCIBE
# ----------------------------------------------------------------------------
with tab2:
    st.subheader("Explorador de Alertas, Correo Original (`SHA-256`) y Revisión Humana")
    search_q = st.text_input("🔍 Buscar por código (AL-..., SOC-..., SOL-...), usuario, IP, equipo, regla o texto:", "")

    where_clauses = ["1=1"]
    qparams = {}
    if not show_non_soc:
        where_clauses.append("a.is_soc_alert = TRUE")
    if not show_duplicates:
        where_clauses.append("a.is_duplicate = FALSE")
    if sel_class != "Todas":
        where_clauses.append("a.incibe_class = :icls")
        qparams["icls"] = sel_class
    if sel_sev != "Todas":
        where_clauses.append("a.normalized_severity = :sev")
        qparams["sev"] = sel_sev
    if sel_sede != "Todas":
        where_clauses.append("a.sede = :sd")
        qparams["sd"] = sel_sede
    if sel_status != "Todos":
        where_clauses.append("a.status = :st")
        qparams["st"] = sel_status
    if search_q.strip():
        where_clauses.append(
            "(a.title ILIKE :q OR a.description ILIKE :q OR COALESCE(a.affected_user,'') ILIKE :q "
            "OR COALESCE(a.affected_host,'') ILIKE :q OR COALESCE(a.source_ip,'') ILIKE :q "
            "OR a.alert_code ILIKE :q OR COALESCE(a.internal_alert_id,'') ILIKE :q)"
        )
        qparams["q"] = f"%{search_q.strip()}%"

    df_alerts = query_df(
        f"""
        SELECT
            a.id AS "ID",
            a.internal_alert_id AS "ID Alerta",
            a.alert_code AS "Código SOC",
            a.event_timestamp_utc AS "Fecha Evento (UTC)",
            a.event_timezone_raw AS "TZ Orig",
            a.normalized_severity AS "Gravedad",
            a.incibe_class AS "Clase INCIBE",
            a.incibe_type AS "Subtipo INCIBE",
            a.sede AS "Sede",
            a.affected_user AS "Usuario",
            a.affected_host AS "Equipo",
            a.source_ip AS "IP",
            a.source_tool AS "Fuente",
            a.status AS "Estado",
            a.duplicate_count AS "Reps",
            a.title AS "Título"
        FROM alerts a
        WHERE {' AND '.join(where_clauses)}
        ORDER BY a.event_timestamp_utc DESC
        """,
        **qparams,
    )

    st.caption(f"Mostrando **{len(df_alerts)}** alertas según los filtros activos.")
    st.dataframe(df_alerts, use_container_width=True, hide_index=True)

    if not df_alerts.empty:
        st.divider()
        selected_id = st.selectbox(
            "Selecciona una Alerta para inspeccionar su correo original, historial o editar su categoría INCIBE:",
            options=df_alerts["ID"].tolist(),
            format_func=lambda x: f"#{x} — {df_alerts.loc[df_alerts['ID']==x, 'ID Alerta'].values[0] or ''} | {df_alerts.loc[df_alerts['ID']==x, 'Clase INCIBE'].values[0]} | {df_alerts.loc[df_alerts['ID']==x, 'Título'].values[0]}",
        )

        det_df = query_df(
            """
            SELECT a.*, r.subject AS email_subject, r.sender_email, r.received_at_utc,
                   r.original_timezone, r.sha256 AS email_sha256, r.body_text, r.body_html, r.attachments_json
            FROM alerts a
            LEFT JOIN raw_emails r ON a.raw_email_id = r.id
            WHERE a.id = :aid
            """,
            aid=int(selected_id),
        )
        if not det_df.empty:
            row = det_df.iloc[0]
            d_col1, d_col2 = st.columns([3, 2])
            with d_col1:
                st.markdown(f"### 📋 Detalle de Alerta `{row['alert_code']}` ({row['internal_alert_id'] or 'N/A'})")
                st.markdown(f"- **Título:** {row['title']}")
                st.markdown(f"- **Descripción extraída:** {row['description']}")
                st.markdown(f"- **Clase INCIBE:** `{row['incibe_class']}` $\\rightarrow$ `{row['incibe_type']}` (Secundaria: `{row['secondary_incibe_class'] or 'N/A'}`)")
                st.markdown(f"- **Peligrosidad / Impacto:** `{row['incibe_danger_level']}` / `{row['incibe_impact_level']}` | **Clasificado por:** `{row['classified_by']}`")
                st.info(f"**Justificación INCIBE:** {row['classification_justification']}")
                st.markdown(
                    f"- **Entidades:** Usuario: `{row['affected_user'] or 'N/A'}` | Host: `{row['affected_host'] or 'N/A'}` | IP normalizada: `{row['source_ip'] or 'N/A'}` | Sede: `{row['sede']}` | Regla: `{row['detection_rule'] or 'N/A'}`"
                )
                if row["prompt_injection_detected"]:
                    st.error(f"⚠️ **Trampa / Prompt Injection Detectado:** {row['prompt_injection_evidence']}")

                # Duplicados / órdenes vinculadas
                dup_children = query_df(
                    "SELECT id, alert_code, internal_alert_id, title, status, event_timestamp_utc FROM alerts WHERE parent_alert_id = :pid ORDER BY event_timestamp_utc ASC",
                    pid=int(selected_id),
                )
                if not dup_children.empty:
                    st.markdown("##### 🔗 Reenvíos Duplicados y Órdenes Operativas (`SOL-B` / `SOL-L`) vinculadas a esta alerta:")
                    st.dataframe(dup_children, use_container_width=True, hide_index=True)

                with st.expander("📩 Ver Correo Original Íntegro y Evidencia Forense (SHA-256)", expanded=True):
                    st.code(
                        f"Remitente: {row['sender_email']}\n"
                        f"Asunto Original: {row['email_subject']}\n"
                        f"Fecha Recepción Buzón (UTC): {row['received_at_utc']}\n"
                        f"Fecha Evento Reportado (UTC): {row['event_timestamp_utc']} (Zona original en correo: {row['event_timezone_raw']})\n"
                        f"SHA-256 Evidencia Inmutable: {row['email_sha256']}",
                        language="yaml",
                    )
                    st.text_area("Cuerpo del Correo Original (Texto extraído):", value=row["body_text"] or "", height=220, disabled=True)

            with d_col2:
                st.markdown("### ✏️ Revisión Humana y Corrección INCIBE")
                with st.form(key=f"edit_alert_{selected_id}"):
                    new_cls = st.selectbox(
                        "Clase INCIBE",
                        options=all_classes if all_classes else [row["incibe_class"]],
                        index=all_classes.index(row["incibe_class"]) if row["incibe_class"] in all_classes else 0,
                    )
                    subtypes_df = query_df("SELECT subtype_name FROM incibe_taxonomy WHERE class_name = :cn", cn=new_cls)
                    sub_opts = subtypes_df["subtype_name"].tolist() if not subtypes_df.empty else [row["incibe_type"]]
                    new_sub = st.selectbox("Subtipo INCIBE", options=sub_opts)
                    new_sev = st.selectbox(
                        "Gravedad Normalizada",
                        options=["CRITICA", "ALTA", "MEDIA", "BAJA", "INFO"],
                        index=["CRITICA", "ALTA", "MEDIA", "BAJA", "INFO"].index(row["normalized_severity"])
                        if row["normalized_severity"] in ["CRITICA", "ALTA", "MEDIA", "BAJA", "INFO"] else 2,
                    )
                    new_st = st.selectbox(
                        "Estado de la Alerta",
                        options=["nueva", "en_revision", "cerrada", "falsa_alarma"],
                        index=["nueva", "en_revision", "cerrada", "falsa_alarma"].index(row["status"])
                        if row["status"] in ["nueva", "en_revision", "cerrada", "falsa_alarma"] else 0,
                    )
                    analyst_name = st.text_input("Revisado por (Analista / Rol):", value="Analista SOC Equipo 1 (NEXUS)")
                    change_reason = st.text_area("Motivo / Justificación de la revisión:", value=row["classification_justification"] or "")
                    if st.form_submit_button("💾 Guardar Cambios y Registrar en Auditoría", use_container_width=True, type="primary"):
                        conn = get_conn()
                        conn.run(
                            """
                            UPDATE alerts
                            SET incibe_class = :cls, incibe_type = :typ, normalized_severity = :sev,
                                status = :st, classification_justification = :just,
                                classified_by = :cby, reviewed_by_human = TRUE, updated_at = NOW()
                            WHERE id = :aid
                            """,
                            cls=new_cls, typ=new_sub, sev=new_sev, st=new_st, just=change_reason, cby=analyst_name, aid=int(selected_id),
                        )
                        conn.run(
                            """
                            INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
                            VALUES (:aid, :cby, 'REVISION_HUMANA', 'incibe_class/status', :oldv, :newv, :rsn)
                            """,
                            aid=int(selected_id),
                            cby=analyst_name,
                            oldv=f"{row['incibe_class']} ({row['status']})",
                            newv=f"{new_cls} / {new_sub} ({new_st})",
                            rsn=change_reason,
                        )
                        conn.close()
                        st.success("¡Categoría y estado actualizados con registro en el historial de auditoría!")
                        st.rerun()

                st.markdown("#### 📜 Historial de Cambios de esta Alerta (`alert_audit_log`)")
                df_aud = query_df(
                    "SELECT changed_at AS \"Fecha\", changed_by AS \"Autor\", action_type AS \"Acción\", old_value AS \"Anterior\", new_value AS \"Nuevo\", reason AS \"Motivo\" FROM alert_audit_log WHERE alert_id = :aid ORDER BY changed_at DESC",
                    aid=int(selected_id),
                )
                st.dataframe(df_aud, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB 3: CONSOLA SOAR Y API BLOQUEADOR
# ----------------------------------------------------------------------------
with tab3:
    st.subheader("⚡ Orquestación SOAR Supervisada · API Bloqueador Sampol (`/equipo-1`)")
    st.markdown(
        "Las alertas técnicas indican *'No ejecutar una contención sin autorización del responsable'*, mientras que el **Responsable de turno SOC** emite órdenes explícitas de bloqueo (`SOL-B-XXX`) y de liberación por falso positivo (`SOL-L-XXX`)."
    )

    # Consultar órdenes SOL-B / SOL-L en la BD
    df_sols = query_df(
        """
        SELECT id, internal_alert_id AS "Orden SOC", alert_code AS "Código Correo",
               event_timestamp_utc AS "Fecha Orden (UTC)", affected_user AS "Usuario Objetivo",
               source_ip AS "IP Contexto (No bloquear)", status AS "Estado", title AS "Detalle"
        FROM alerts
        WHERE internal_alert_id LIKE 'SOL-%'
        ORDER BY id ASC
        """
    )
    st.markdown("#### 📋 Órdenes Operativas del Responsable de Turno SOC (`SOL-B` y `SOL-L`) recibidas en el buzón")
    st.dataframe(df_sols, use_container_width=True, hide_index=True)

    col_auto_soar, col_manual_soar = st.columns([1, 1])
    with col_auto_soar:
        st.markdown("#### 🤖 Ejecución Inteligente de Órdenes Oficiales `SOL-B` / `SOL-L`")
        st.caption(
            "Procesa en orden cronológico todas las solicitudes oficiales `SOL-B-XXX` (bloqueando exclusivamente el usuario indicado, nunca la IP de contexto) y aplica las liberaciones `SOL-L-XXX` por falso positivo confirmado."
        )
        if st.button("🚀 Sincronizar y Ejecutar Órdenes Oficiales SOL-B / SOL-L en la API", type="primary", use_container_width=True):
            conn = get_conn()
            sol_rows = conn.run(
                "SELECT id, internal_alert_id, affected_user, title FROM alerts WHERE internal_alert_id LIKE 'SOL-%' ORDER BY id ASC"
            )
            executed_msgs = []
            for sid, sol_code, usr, stitle in sol_rows:
                if not usr:
                    continue
                ikey = f"AUTO-ORDER-{sol_code}-{usr.lower()}"
                already = conn.run("SELECT id FROM soar_actions WHERE idempotency_key = :ik", ik=ikey)
                if already:
                    continue
                if sol_code.startswith("SOL-B-"):
                    soar_approve(
                        SoarApprovePayload(
                            target_type="usuario",
                            target_value=usr,
                            alert_id=sid,
                            approved_by=f"Responsable Turno SOC ({sol_code})",
                            reason=f"Contención temporal autorizada por orden {sol_code}",
                        )
                    )
                    conn.run("UPDATE soar_actions SET idempotency_key = :ik WHERE alert_id = :aid AND action = 'bloquear'", ik=ikey, aid=sid)
                    conn.run("UPDATE alerts SET status = 'cerrada' WHERE id = :aid", aid=sid)
                    executed_msgs.append(f"🔒 Bloqueado usuario `{usr}` ({sol_code})")
                elif sol_code.startswith("SOL-L-"):
                    soar_release(
                        SoarReleasePayload(
                            target_type="usuario",
                            target_value=usr,
                            alert_id=sid,
                            executed_by=f"Responsable Turno SOC ({sol_code})",
                            reason=f"Liberación por falso positivo verificado ({sol_code})",
                        )
                    )
                    conn.run("UPDATE soar_actions SET idempotency_key = :ik WHERE alert_id = :aid AND action = 'liberar'", ik=ikey, aid=sid)
                    executed_msgs.append(f"🔓 Liberado usuario `{usr}` por falso positivo ({sol_code})")
            conn.close()
            if executed_msgs:
                for m in executed_msgs:
                    st.success(m)
            else:
                st.info("Todas las órdenes oficiales SOL-B / SOL-L actuales ya estaban ejecutadas (Idempotencia activa).")
            st.rerun()

        st.markdown("---")
        st.markdown("##### ⚡ Directriz 1 (18:00 CET): Bloqueo Autónomo de Cuentas Comprometidas")
        st.caption("Contención automática ante robo de credenciales, intrusión o malware (ACCOUNT-LAB, ADMIN-LAB, APP-LAB, APT-LAB, C2, READ, MODIFY).")
        if st.button("🚨 Ejecutar Barrido de Bloqueo Autónomo (Directriz 1)", use_container_width=True):
            try:
                from autoblock_engine import run_autoblock_sweep
                run_autoblock_sweep()
                st.success("Barrido de bloqueo autónomo completado según la Directriz 1.")
                st.rerun()
            except Exception as e:
                st.error(f"Error en barrido autónomo: {e}")

    with col_manual_soar:
        st.markdown("#### 🛠️ Control Manual Supervisado (`Bloquear` / `Liberar`)")
        with st.form("manual_soar_form"):
            m_act = st.radio("Acción SOAR", ["bloquear", "liberar"], horizontal=True)
            m_type = st.radio("Tipo de Objetivo", ["usuario", "ip"], horizontal=True)
            m_val = st.text_input("Valor (ej. usuario@sampol.com o IP):")
            m_reason = st.text_input("Motivo de la operación:", value="Intervención supervisada desde Cuadro de Mando")
            if st.form_submit_button("Ejecutar en API Sampol", use_container_width=True):
                if m_val.strip():
                    try:
                        if m_act == "bloquear":
                            res = soar_approve(
                                SoarApprovePayload(
                                    target_type=m_type,
                                    target_value=m_val.strip(),
                                    approved_by="Director TI / Analista SOC",
                                    reason=m_reason,
                                )
                            )
                        else:
                            res = soar_release(
                                SoarReleasePayload(
                                    target_type=m_type,
                                    target_value=m_val.strip(),
                                    executed_by="Director TI / Analista SOC",
                                    reason=m_reason,
                                )
                            )
                        st.success(f"Respuesta API (HTTP {res['http_code']}): {res['api_response']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Operación rechazada: {e}")

    st.divider()
    col_live_api, col_wl = st.columns([3, 2])
    with col_live_api:
        st.markdown("#### 🌐 Estado en Vivo en la API de Sampol (`GET /equipo-1/bloqueos`)")
        code, live_blocks = call_sampol_soar_api("/bloqueos", method="GET")
        if code == 200 and isinstance(live_blocks, list):
            df_lb = pd.DataFrame(live_blocks)
            if not df_lb.empty:
                st.dataframe(
                    df_lb[["id", "tipo", "valor", "activo", "creado_en", "bloqueado_en", "liberado_en"]],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No hay bloqueos registrados actualmente en la API.")
        else:
            st.warning(f"No se pudo leer `/equipo-1/bloqueos` (HTTP {code})")

    with col_wl:
        st.markdown("#### 🛡️ Lista Blanca IT/OT (`protected_assets_whitelist`)")
        df_wl = query_df("SELECT asset_type AS \"Tipo\", asset_value AS \"Activo Protegido\", asset_category AS \"Categoría\", description AS \"Descripción\" FROM protected_assets_whitelist WHERE active = TRUE")
        st.dataframe(df_wl, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 📜 Registro y Trazabilidad de Acciones SOAR (`soar_actions`)")
    st.caption("Historial de bloqueos y liberaciones ejecutadas por el Motor Autónomo (Directriz 1), órdenes SOL-B/L y supervisión humana.")
    df_actions = query_df(
        """
        SELECT id AS "ID", action AS "Acción", target_type AS "Tipo", target_value AS "Objetivo",
               trigger_mode AS "Modo Disparo", status AS "Estado", requested_by AS "Solicitante",
               api_status_code AS "HTTP API", executed_at AS "Fecha Ejecución (UTC)", reason AS "Motivo Forense"
        FROM soar_actions
        ORDER BY id DESC
        """
    )
    st.dataframe(df_actions, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB 4: INVESTIGACIÓN FORENSE Y NIS2
# ----------------------------------------------------------------------------
with tab4:
    st.subheader("🕵️ Investigación Forense, Correlación de Ataques y Pre-Notificación NIS2")

    st.markdown("#### 🚨 1. Escudo Anti-Prompt Injection y Correos Sospechosos Fuera de Formato")
    df_traps = query_df(
        """
        SELECT id AS "ID", alert_code AS "Código", event_timestamp_utc AS "Fecha (UTC)",
               incibe_class AS "Clase INCIBE", title AS "Título",
               prompt_injection_detected AS "Trampa IA", prompt_injection_evidence AS "Evidencia Trampa / Anomalía",
               description AS "Resumen"
        FROM alerts
        WHERE prompt_injection_detected = TRUE OR alert_code LIKE 'PHISH-EXT-%' OR detection_rule LIKE 'APT-%'
        ORDER BY event_timestamp_utc ASC
        """
    )
    st.dataframe(df_traps, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### ⏱️ 2. Línea Temporal Forense Unificada en UTC (`v_forensic_timeline`)")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        filter_stage = st.selectbox(
            "Filtrar por Fase de Kill Chain / MITRE:",
            ["Todas", "1. Reconocimiento", "2. Superficie Expuesta", "3. Acceso Inicial / Fraude", "4. Intento de Intrusión", "5. Ejecución / C2 Malware", "6. Intrusión / Escalada", "7. Compromiso / Impacto en Datos", "8. Impacto en Disponibilidad"],
        )
    with f_col2:
        filter_entity = st.text_input("Filtrar Timeline por Usuario, Host, IP o Sede (ej. barcelona, rperez, 198.51.100):", "")

    tl_clauses = ["1=1"]
    tl_params = {}
    if filter_stage != "Todas":
        tl_clauses.append("mitre_stage = :ms")
        tl_params["ms"] = filter_stage
    if filter_entity.strip():
        tl_clauses.append("(COALESCE(affected_user,'') ILIKE :fe OR COALESCE(affected_host,'') ILIKE :fe OR COALESCE(source_ip,'') ILIKE :fe OR COALESCE(sede,'') ILIKE :fe OR title ILIKE :fe)")
        tl_params["fe"] = f"%{filter_entity.strip()}%"

    df_tl = query_df(
        f"""
        SELECT event_timestamp_utc AS "Timestamp UTC", event_timezone_raw AS "TZ Orig",
               mitre_stage AS "Fase Kill Chain", normalized_severity AS "Gravedad",
               internal_alert_id AS "ID Alerta", incibe_class AS "Clase INCIBE",
               sede AS "Sede", affected_user AS "Usuario", affected_host AS "Host",
               source_ip AS "IP Origen", detection_rule AS "Regla", title AS "Evento"
        FROM v_forensic_timeline
        WHERE is_duplicate = FALSE AND {' AND '.join(tl_clauses)}
        ORDER BY event_timestamp_utc ASC
        """,
        **tl_params,
    )
    st.dataframe(df_tl, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 📜 3. Generador Automático de Pre-Notificación Directiva NIS2 / INCIBE-CERT")
    crit_df = query_df(
        "SELECT alert_id AS id, internal_alert_id, alert_code, title, incibe_class, incibe_type, sede, affected_host, affected_user, source_ip, event_timestamp_utc, description, email_sha256 FROM v_forensic_timeline WHERE normalized_severity = 'CRITICA' AND is_duplicate = FALSE ORDER BY event_timestamp_utc DESC"
    )
    if not crit_df.empty:
        sel_nis = st.selectbox(
            "Selecciona un Incidente Crítico para generar el Borrador Oficial NIS2 (<24h):",
            options=crit_df["id"].tolist(),
            format_func=lambda x: f"{crit_df.loc[crit_df['id']==x, 'internal_alert_id'].values[0]} — {crit_df.loc[crit_df['id']==x, 'title'].values[0]}",
        )
        nrow = crit_df.loc[crit_df["id"] == sel_nis].iloc[0]
        nis2_text = f"""========================================================================
BORRADOR DE ALERTA TEMPRANA NIS2 (24H) / NOTIFICACIÓN INCIBE-CERT
Entidad Esencial (Sector Energía): GRUPO SAMPOL INGENIERÍA Y OBRAS S.A.
Generado por: Sistema NEXUS 2.0 (Equipo 1) — Requiere validación humana antes de envío
========================================================================
1. IDENTIFICACIÓN DEL INCIDENTE
   - Código Interno / SOC: {nrow['internal_alert_id']} / {nrow['alert_code']}
   - Fecha/Hora Detección (UTC): {nrow['event_timestamp_utc']}
   - Huella Forense Correo Evidencia (SHA-256): {nrow['email_sha256']}

2. TAXONOMÍA NACIONAL INCIBE
   - Clase de Incidente: {nrow['incibe_class']}
   - Tipo Específico: {nrow['incibe_type']}
   - Severidad Estimada: CRÍTICA (P4)

3. ACTIVOS Y ALCANCE PRELIMINAR
   - Sede afectada: {nrow['sede']}
   - Sistema / Recurso: {nrow['affected_host']}
   - Cuenta implicada: {nrow['affected_user'] or 'No aplica / No identificada'}
   - Dirección IP relacionada: {nrow['source_ip']}

4. RESUMEN DE HECHOS CONFIRMADOS
   {nrow['description']}

5. MEDIDAS DE CONTENCIÓN Y MITIGACIÓN
   - Evento registrado y correlacionado en plataforma central PostgreSQL con cadena de custodia SHA-256.
   - Verificación contra Lista Blanca de activos críticos OT/IT antes de aplicar bloqueo SOAR.
========================================================================"""
        st.code(nis2_text, language="markdown")
        st.download_button(
            "📥 Descargar Pre-Informe NIS2 (.txt)",
            data=nis2_text,
            file_name=f"PreInforme_NIS2_{nrow['internal_alert_id'] or nrow['alert_code']}.txt",
            mime="text/plain",
        )

# ----------------------------------------------------------------------------
# TAB 5: CASO DE NEGOCIO (ROI) Y DIRECTRICES
# ----------------------------------------------------------------------------
with tab5:
    st.subheader("💶 Análisis de Rentabilidad (ROI, Payback, 3 Escenarios y Build vs. Buy) — Datos Oficiales del Director de TI")
    st.caption("Modelo financiero alineado con los parámetros oficiales enviados por el Director de TI (`dirti@sampol.com` · correo 'Retorno') y las métricas reales de nuestra base de datos.")

    with st.expander("📩 Ver Tabla Oficial enviada por el Director de TI (`DATOS DEL DIRECTOR`)", expanded=True):
        dir_table = pd.DataFrame([
            {"Dato Oficial (Director TI)": "Alertas al mes", "Valor Propuesto": "3.000 alertas / mes", "Impacto Actual (AS-IS)": "600 h/mes en revisión manual (27.000 €/mes)"},
            {"Dato Oficial (Director TI)": "Tiempo medio de revisión manual", "Valor Propuesto": "12 min / alerta", "Impacto Actual (AS-IS)": "Con NEXUS 2.0 baja a ~2,0 min (24% filtrado automático de duplicados/ruido + IA INCIBE)"},
            {"Dato Oficial (Director TI)": "Coste de la hora de analista", "Valor Propuesto": "45 € / hora", "Impacto Actual (AS-IS)": "Base salarial para cálculo de ahorro operativo"},
            {"Dato Oficial (Director TI)": "Bloqueos manuales al mes", "Valor Propuesto": "120 bloqueos / mes, de 25 min", "Impacto Actual (AS-IS)": "50 h/mes en bloqueos manuales (2.250 €/mes)"},
            {"Dato Oficial (Director TI)": "Hora de servicio parado", "Valor Propuesto": "25.000 € / hora", "Impacto Actual (AS-IS)": "Coste evitado por disponibilidad IT/OT y prevención de falsos bloqueos"},
            {"Dato Oficial (Director TI)": "Hora de desarrollo interno", "Valor Propuesto": "50 € / hora", "Impacto Actual (AS-IS)": "Base para CAPEX interno (160h = 8.000 €) y mantenimiento mensual"},
            {"Dato Oficial (Director TI)": "Plataforma comercial", "Valor Propuesto": "60.000 €/año + 20.000 € implantación", "Impacto Actual (AS-IS)": "80.000 € el Año 1 (Referencia Buy vs. Build)"},
        ])
        st.dataframe(dir_table, use_container_width=True, hide_index=True)

    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        vol_mensual = st.number_input("Alertas al mes (Dato Director: 3.000):", min_value=100, max_value=50000, value=3000, step=100)
        min_manual_alerta = st.number_input("Tiempo medio de revisión manual (min/alerta — Director: 12):", min_value=1.0, max_value=60.0, value=12.0, step=0.5)
        min_nexus_alerta = st.number_input("Tiempo medio con NEXUS 2.0 (min/alerta):", min_value=0.2, max_value=30.0, value=2.0, step=0.2)
    with b_col2:
        bloqueos_mes = st.number_input("Bloqueos manuales al mes (Dato Director: 120):", min_value=10, max_value=5000, value=120, step=10)
        min_manual_soar = st.number_input("Tiempo manual por bloqueo (min — Director: 25):", min_value=1.0, max_value=60.0, value=25.0, step=1.0)
        min_nexus_soar = st.number_input("Tiempo por bloqueo/liberación con SOAR NEXUS (min):", min_value=0.2, max_value=15.0, value=1.5, step=0.5)
    with b_col3:
        coste_hora = st.number_input("Coste hora de analista (€/h — Director: 45 €):", min_value=15.0, max_value=150.0, value=45.0, step=1.0)
        coste_hora_dev = st.number_input("Coste hora desarrollo interno (€/h — Director: 50 €):", min_value=20.0, max_value=150.0, value=50.0, step=5.0)
        horas_desarrollo = st.number_input("Horas de desarrollo interno inicial (Build):", min_value=40, max_value=2000, value=160, step=20)

    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        mantenimiento_mes = st.number_input("Coste recurrente mensual NEXUS (Azure + IA + 6h soporte a 50€/h):", min_value=50.0, max_value=5000.0, value=500.0, step=50.0)
    with c_col2:
        coste_parada_planta = st.number_input("Coste por hora de servicio parado (€/h — Director: 25.000 €):", min_value=1000.0, max_value=200000.0, value=25000.0, step=1000.0)
    with c_col3:
        comercial_anual = st.number_input("Plataforma comercial licencia anual (€/año — Director: 60.000 €):", min_value=5000.0, max_value=300000.0, value=60000.0, step=5000.0)
        comercial_setup = 20000.0

    inversion_inicial = horas_desarrollo * coste_hora_dev

    # 1. Separación exigida por el enunciado: Seguimiento/Triaje vs Automatización SOAR
    horas_triaje_actual = (vol_mensual * min_manual_alerta) / 60.0
    coste_triaje_actual = horas_triaje_actual * coste_hora
    horas_triaje_nexus = (vol_mensual * min_nexus_alerta) / 60.0
    coste_triaje_nexus = horas_triaje_nexus * coste_hora
    ahorro_triaje_mes = coste_triaje_actual - coste_triaje_nexus

    horas_soar_actual = (bloqueos_mes * min_manual_soar) / 60.0
    coste_soar_actual = horas_soar_actual * coste_hora
    horas_soar_nexus = (bloqueos_mes * min_nexus_soar) / 60.0
    coste_soar_nexus = horas_soar_nexus * coste_hora
    ahorro_soar_mes = coste_soar_actual - coste_soar_nexus

    # Totales escenario realista
    horas_actual_mes = horas_triaje_actual + horas_soar_actual
    coste_actual_mes = coste_triaje_actual + coste_soar_actual

    horas_nexus_mes = horas_triaje_nexus + horas_soar_nexus
    coste_operativo_nexus_mes = coste_triaje_nexus + coste_soar_nexus

    ahorro_bruto_mes = coste_actual_mes - coste_operativo_nexus_mes
    ahorro_neto_mes = ahorro_bruto_mes - mantenimiento_mes
    payback_meses = inversion_inicial / ahorro_neto_mes if ahorro_neto_mes > 0 else 999.0

    beneficio_anual = ahorro_bruto_mes * 12
    coste_total_anual = inversion_inicial + (mantenimiento_mes * 12)
    roi_anual = ((beneficio_anual - coste_total_anual) / coste_total_anual) * 100.0

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Coste Operativo Actual (AS-IS)", f"{coste_actual_mes:,.0f} € / mes", f"{horas_actual_mes:,.0f} h/mes ({coste_actual_mes*12:,.0f} €/año)")
    r2.metric("Ahorro Neto Mensual (NEXUS 2.0)", f"{ahorro_neto_mes:,.0f} € / mes", f"{horas_actual_mes - horas_nexus_mes:,.1f} h/mes liberadas")
    r3.metric("Periodo de Recuperación (Payback)", f"{payback_meses:.2f} meses (~{int(payback_meses*30)} días)", f"CAPEX Interno: {inversion_inicial:,.0f} € ({horas_desarrollo}h)")
    r4.metric("ROI Primer Año (Build Interno)", f"{roi_anual:,.0f} %", f"Coste Total Año 1: {coste_total_anual:,.0f} €")

    st.markdown("#### 🔍 1. Desglose Separado: Retorno del Seguimiento (Triaje/Clasificación) vs. Retorno de la Automatización (API SOAR)")
    df_split = pd.DataFrame([
        {
            "Línea de Valor": "A) Seguimiento, Deduplicación y Clasificación INCIBE (3.000 alertas/mes)",
            "Horas Actuales / mes": round(horas_triaje_actual, 1),
            "Coste Actual / mes (€)": round(coste_triaje_actual, 2),
            "Horas con NEXUS / mes": round(horas_triaje_nexus, 1),
            "Coste con NEXUS / mes (€)": round(coste_triaje_nexus, 2),
            "Horas Liberadas / mes": round(horas_triaje_actual - horas_triaje_nexus, 1),
            "Ahorro Bruto Mensual (€)": round(ahorro_triaje_mes, 2),
            "Ahorro Bruto Anual (€)": round(ahorro_triaje_mes * 12, 2),
        },
        {
            "Línea de Valor": "B) Automatización Supervisada de Bloqueos/Liberaciones SOAR (120/mes)",
            "Horas Actuales / mes": round(horas_soar_actual, 1),
            "Coste Actual / mes (€)": round(coste_soar_actual, 2),
            "Horas con NEXUS / mes": round(horas_soar_nexus, 1),
            "Coste con NEXUS / mes (€)": round(coste_soar_nexus, 2),
            "Horas Liberadas / mes": round(horas_soar_actual - horas_soar_nexus, 1),
            "Ahorro Bruto Mensual (€)": round(ahorro_soar_mes, 2),
            "Ahorro Bruto Anual (€)": round(ahorro_soar_mes * 12, 2),
        },
        {
            "Línea de Valor": "TOTAL COMBINADO (A + B)",
            "Horas Actuales / mes": round(horas_actual_mes, 1),
            "Coste Actual / mes (€)": round(coste_actual_mes, 2),
            "Horas con NEXUS / mes": round(horas_nexus_mes, 1),
            "Coste con NEXUS / mes (€)": round(coste_operativo_nexus_mes, 2),
            "Horas Liberadas / mes": round(horas_actual_mes - horas_nexus_mes, 1),
            "Ahorro Bruto Mensual (€)": round(ahorro_bruto_mes, 2),
            "Ahorro Bruto Anual (€)": round(ahorro_bruto_mes * 12, 2),
        },
    ])
    st.dataframe(df_split, use_container_width=True, hide_index=True)

    st.markdown("#### 📊 2. Comparativa de los 3 Escenarios (Prudente, Realista y Optimista)")
    scenarios = []
    for s_name, mult in [
        ("1. Escenario Prudente (Conservador: 65% eficiencia)", 0.75),
        ("2. Escenario Realista (Base con datos del Director)", 1.00),
        ("3. Escenario Optimista (Escalado / Mayor automatización)", 1.15),
    ]:
        ah_bruto = ahorro_bruto_mes * mult
        ah_neto = ah_bruto - mantenimiento_mes
        pb = inversion_inicial / ah_neto if ah_neto > 0 else 99.0
        ben_1y = ah_bruto * 12
        roi_1y = ((ben_1y - coste_total_anual) / coste_total_anual) * 100.0
        scenarios.append({
            "Escenario": s_name,
            "Ahorro Bruto Mensual (€)": round(ah_bruto, 2),
            "Coste Mantenimiento Mensual (€)": round(mantenimiento_mes, 2),
            "Ahorro Neto Mensual (€)": round(ah_neto, 2),
            "Payback (Meses)": round(pb, 2),
            "Beneficio Bruto Año 1 (€)": round(ben_1y, 2),
            "Coste Total Año 1 (€)": round(coste_total_anual, 2),
            "ROI Año 1 (%)": round(roi_1y, 1),
        })
    st.dataframe(pd.DataFrame(scenarios), use_container_width=True, hide_index=True)

    st.markdown("#### ⚖️ 3. Comparativa Estratégica: Desarrollo Interno NEXUS 2.0 (Build) vs. Plataforma Comercial (Buy)")
    coste_comercial_1y = comercial_anual + comercial_setup
    coste_comercial_3y = (comercial_anual * 3) + comercial_setup
    coste_nexus_3y = inversion_inicial + (mantenimiento_mes * 36)
    df_buy_build = pd.DataFrame([
        {
            "Alternativa": "Desarrollo Interno NEXUS 2.0 (Build)",
            "Implantación / CAPEX Inicial (€)": round(inversion_inicial, 2),
            "Coste Anual Recurrente / OPEX (€/año)": round(mantenimiento_mes * 12, 2),
            "Coste Total Año 1 (€)": round(coste_total_anual, 2),
            "TCO a 3 Años (€)": round(coste_nexus_3y, 2),
            "Beneficio Neto Año 1 (€)": round(beneficio_anual - coste_total_anual, 2),
            "ROI Año 1 (%)": round(roi_anual, 1),
        },
        {
            "Alternativa": "Plataforma Comercial (Buy: 60.000 €/año + 20.000 €)",
            "Implantación / CAPEX Inicial (€)": round(comercial_setup, 2),
            "Coste Anual Recurrente / OPEX (€/año)": round(comercial_anual, 2),
            "Coste Total Año 1 (€)": round(coste_comercial_1y, 2),
            "TCO a 3 Años (€)": round(coste_comercial_3y, 2),
            "Beneficio Neto Año 1 (€)": round(beneficio_anual - coste_comercial_1y, 2),
            "ROI Año 1 (%)": round(((beneficio_anual - coste_comercial_1y) / coste_comercial_1y) * 100.0, 1),
        },
    ])
    st.dataframe(df_buy_build, use_container_width=True, hide_index=True)

    st.info(
        f"**Nota de Prudencia Financiera y Riesgo Operativo Evitado:** Además del ahorro operativo directo de **{ahorro_neto_mes*12:,.0f} €/año** y de ahorrar **{coste_comercial_1y - coste_total_anual:,.0f} € en el primer año** frente a la plataforma comercial (**{coste_comercial_3y - coste_nexus_3y:,.0f} € en 3 años**), las **{horas_actual_mes - horas_nexus_mes:,.0f} horas/mes** liberadas se dedican a investigación profunda y caza de amenazas. Con un coste de **{coste_parada_planta:,.0f} € por cada hora de servicio parado**, evitar una sola interrupción de **2 horas** al año por detección temprana o por nuestro control de **Lista Blanca IT/OT** añade otros **{coste_parada_planta*2:,.0f} €** de retorno directo."
    )

    st.divider()
    st.markdown("#### 🎯 4. Cuadro de Directrices Oficiales del Director de TI (`director_directives`)")
    st.caption("Seguimiento y trazabilidad de los encargos y directrices emitidas durante el reto por `dirti@sampol.com`.")
    df_dirs = query_df(
        """
        SELECT directive_number AS "Nº Directriz", subject AS "Asunto", received_at_utc AS "Fecha Recepción (UTC)",
               request_summary AS "Petición del Director", team_response AS "Respuesta / Solución NEXUS 2.0",
               implemented_features AS "Capacidades Técnicas Desplegadas", status AS "Estado"
        FROM director_directives
        ORDER BY id DESC
        """
    )
    st.dataframe(df_dirs, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB 6: EXPLORADOR DIRECTO DE LA BASE DE DATOS (AZURE POSTGRESQL)
# ----------------------------------------------------------------------------
with tab6:
    st.subheader("🗄️ Explorador en Vivo de la Base de Datos Azure PostgreSQL (`alertas-soc-1.postgres.database.azure.com`)")
    st.caption("Inspecciona cualquiera de las tablas y vistas del esquema NEXUS 2.0 o ejecuta consultas SQL en tiempo real.")

    tables_summary = query_df(
        """
        SELECT
            table_name AS "Tabla / Vista",
            table_type AS "Tipo"
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_type, table_name
        """
    )

    col_db1, col_db2 = st.columns([1, 3])
    with col_db1:
        st.markdown("#### Objetos en `public`")
        st.dataframe(tables_summary, use_container_width=True, hide_index=True)

        available_objects = [
            "alerts",
            "v_soc_unique_alerts",
            "v_forensic_timeline",
            "raw_emails",
            "attachments",
            "incibe_taxonomy",
            "soar_actions",
            "alert_audit_log",
            "protected_assets_whitelist",
            "business_parameters",
            "director_directives",
            "attack_campaigns",
        ]
        sel_table = st.selectbox("Seleccionar Tabla o Vista para inspeccionar:", available_objects)
        row_limit = st.slider("Límite de filas a mostrar:", min_value=10, max_value=500, value=100, step=10)

    with col_db2:
        st.markdown(f"#### Contenido de `{sel_table}`")
        df_table = query_df(f"SELECT * FROM {sel_table} ORDER BY 1 DESC LIMIT {int(row_limit)}")
        st.caption(f"Mostrando {len(df_table)} filas de `{sel_table}`")
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        if not df_table.empty:
            csv_bytes = df_table.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"⬇️ Descargar {sel_table}.csv",
                data=csv_bytes,
                file_name=f"{sel_table}.csv",
                mime="text/csv",
            )

        st.markdown("##### Estructura de Columnas (`information_schema.columns`)")
        df_cols = query_df(
            """
            SELECT column_name AS "Columna", data_type AS "Tipo de Dato", is_nullable AS "Nullable", column_default AS "Valor por Defecto"
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = :tname
            ORDER BY ordinal_position
            """,
            tname=sel_table,
        )
        st.dataframe(df_cols, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 💻 Consola SQL Interactiva (Solo Lectura `SELECT`)")
    default_sql = "SELECT id, alert_code, internal_alert_id, event_timestamp_utc, incibe_class, incibe_type, normalized_severity, sede, affected_user, source_ip FROM v_soc_unique_alerts ORDER BY event_timestamp_utc DESC;"
    custom_sql = st.text_area("Escribe cualquier consulta SELECT sobre PostgreSQL:", value=default_sql, height=90)
    if st.button("▶️ Ejecutar Consulta SQL"):
        if not custom_sql.strip().lower().startswith("select"):
            st.error("Por seguridad, desde esta consola rápida solo se permiten consultas que comiencen por SELECT.")
        else:
            try:
                df_custom = query_df(custom_sql)
                st.success(f"Consulta ejecutada correctamente ({len(df_custom)} filas devueltas).")
                st.dataframe(df_custom, use_container_width=True, hide_index=True)
            except Exception as ex:
                st.error(f"Error en consulta SQL: {ex}")

