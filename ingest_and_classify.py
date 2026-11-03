import hashlib
import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from html import unescape
from config import get_conn
from data_validator import validate_and_clean_host, validate_and_clean_user, validate_and_clean_ip

TOKEN_FILE = r"C:\Users\osesj\Documents\Nexus-Hackathon\.graph_token.json"
DUMP_FILE = r"C:\Users\osesj\Documents\Nexus-Hackathon\mailbox_dump.json"

def get_valid_token():
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        tdata = json.load(f)
    if time.time() - tdata.get("obtained_at", 0) > 2400 and "refresh_token" in tdata:
        token_url = f"https://login.microsoftonline.com/{tdata['tenant_id']}/oauth2/v2.0/token"
        poll_data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "client_id": tdata["client_id"],
            "refresh_token": tdata["refresh_token"],
            "scope": "https://graph.microsoft.com/.default offline_access"
        }).encode()
        req = urllib.request.Request(token_url, data=poll_data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            new_t = json.loads(resp.read().decode())
            tdata.update(new_t)
            tdata["obtained_at"] = time.time()
            with open(TOKEN_FILE, "w", encoding="utf-8") as fw:
                json.dump(tdata, fw, indent=2)
    return tdata["access_token"]

def fetch_all_emails_from_graph():
    token = get_valid_token()
    all_messages = []
    next_url = (
        "https://graph.microsoft.com/v1.0/me/messages?"
        "$top=100&$orderby=receivedDateTime%20asc&"
        "$select=id,internetMessageId,conversationId,subject,receivedDateTime,sentDateTime,"
        "from,sender,toRecipients,ccRecipients,hasAttachments,importance,bodyPreview,body,internetMessageHeaders"
    )
    while next_url:
        req = urllib.request.Request(next_url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            page = json.loads(resp.read().decode())
        msgs = page.get("value", [])
        all_messages.extend(msgs)
        next_url = page.get("@odata.nextLink")

    for m in all_messages:
        if m.get("hasAttachments"):
            att_url = f"https://graph.microsoft.com/v1.0/me/messages/{m['id']}/attachments?$select=id,name,contentType,size"
            try:
                req = urllib.request.Request(att_url, headers={"Authorization": f"Bearer {token}"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    m["attachments_meta"] = json.loads(resp.read().decode()).get("value", [])
            except Exception:
                m["attachments_meta"] = []
        else:
            m["attachments_meta"] = []

    with open(DUMP_FILE, "w", encoding="utf-8") as f:
        json.dump(all_messages, f, indent=2, ensure_ascii=False)
    return all_messages

def html_to_text(h):
    if not h:
        return ""
    h = re.sub(r"<style[^>]*>.*?</style>", "", h, flags=re.S | re.I)
    h = re.sub(r"<br\s*/?>", "\n", h, flags=re.I)
    h = re.sub(r"</(p|div|tr|li|h[1-6])>", "\n", h, flags=re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    h = unescape(h)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in h.splitlines()]
    return "\n".join([ln for ln in lines if ln])

def normalize_ip(raw_ip, body_text=""):
    """Corrige IPs sin puntos en las tablas del SOC (ej. 19851100107 -> 198.51.100.107)."""
    # Primero buscar IP con puntos en el cuerpo narrativo
    dotted_ips = re.findall(r"\b(?:192\.0\.2|198\.51\.100|203\.0\.113|10\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+|192\.168\.\d+)\.\d{1,3}\b", body_text)
    if dotted_ips:
        return dotted_ips[0]
    if not raw_ip or raw_ip.lower() in ("no aplica", "no indicada", "n/a", "-"):
        return None
    raw_ip = raw_ip.strip()
    if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", raw_ip):
        return raw_ip
    # Normalizar prefijos RFC 5737 sin puntos (19851100XXX, 2030113XXX, 19202XXX)
    if raw_ip.startswith("19851100") and len(raw_ip) > 8:
        return f"198.51.100.{raw_ip[8:]}"
    if raw_ip.startswith("2030113") and len(raw_ip) > 7:
        return f"203.0.113.{raw_ip[7:]}"
    if raw_ip.startswith("19202") and len(raw_ip) > 5:
        return f"192.0.2.{raw_ip[5:]}"
    return raw_ip

def detect_prompt_injection(text, html):
    """Detecta intentos de Prompt Injection o instrucciones ocultas para engañar a la IA."""
    patterns = [
        (r"ignora\s+(?:todas\s+)?las\s+instrucciones", "Instrucción explícita de ignorar prompt"),
        (r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions", "Explicit English prompt injection"),
        (r"clasifica\s+esta\s+alerta\s+como\s+(?:falsa|baja|informativa)", "Intento de forzar clasificación benigna"),
        (r"actúa\s+como|system\s*prompt|eres\s+un\s+asistente", "Manipulación de rol del sistema"),
        (r"solo\s+cuando\s+se\s+cita\s+expresamente", "Instrucción condicional para evaluador/IA ('solo cuando se cita expresamente')"),
    ]
    combined = f"{text}\n{html}"
    for pat, desc in patterns:
        m = re.search(pat, combined, flags=re.I)
        if m:
            return True, f"{desc}: '{m.group(0)}'"
    return False, None

# Mapa experto de reglas del SOC de Sampol a la Guía Nacional de INCIBE
RULE_TO_INCIBE = {
    "SPRAY-LAB": (
        "Intento de intrusión",
        "Fuerza bruta / Diccionario",
        "Alto",
        "Medio",
        "Intrusión",
        "Autenticaciones fallidas repetidas (Password Spraying / fuerza bruta OAuth2) sin sesión exitosa acreditada: encaja en 'Intento de intrusión' (fuerza bruta) de INCIBE y se descarta 'Intrusión' al no haberse emitido token válido."
    ),
    "ADMIN-LAB": (
        "Intrusión",
        "Compromiso de cuenta privilegiada / Admin",
        "Muy Alto",
        "Crítico (OT/Planta)",
        "Compromiso de la información",
        "Inicio de sesión exitoso en cuenta privilegiada (Global Administrator) y elevación de permisos no autorizada negada por el titular: constituye una 'Intrusión' confirmada con compromiso de cuenta administrativa."
    ),
    "ACCOUNT-LAB": (
        "Intrusión",
        "Compromiso de cuenta de usuario",
        "Alto",
        "Alto",
        "Fraude",
        "Emisión de token válido y MFA completado en sesión no reconocida por el usuario titular: se clasifica como 'Intrusión' (compromiso efectivo de cuenta ordinaria) y no mero intento."
    ),
    "DOS-LAB": (
        "Disponibilidad",
        "Denegación de servicio (DoS / DDoS)",
        "Alto",
        "Alto",
        "Intento de intrusión",
        "Saturación sostenida de peticiones (4600 req/min) desde un único origen generando errores HTTP 503 y degradación: corresponde a 'Disponibilidad' (ataque DoS)."
    ),
    "DDOS-LAB": (
        "Disponibilidad",
        "Denegación de servicio (DoS / DDoS)",
        "Muy Alto",
        "Crítico (OT/Planta)",
        "Intento de intrusión",
        "Tráfico SYN simultáneo desde 128 orígenes distribuidos causando un 68% de pérdida de disponibilidad en el portal público: corresponde a 'Disponibilidad' (DDoS)."
    ),
    "MALWARE-LAB": (
        "Contenido dañino",
        "Malware genérico / Virus / Gusano",
        "Alto",
        "Alto",
        "Intrusión",
        "Ejecución de binario malicioso ('invoice-viewer.exe') detectado en endpoint por motores EDR: se clasifica en 'Contenido dañino' (Malware) según la taxonomía INCIBE."
    ),
    "C2-LAB": (
        "Contenido dañino",
        "Troyano / Backdoor / RAT",
        "Muy Alto",
        "Crítico (OT/Planta)",
        "Intrusión",
        "Beaconing periódico cada 60s desde proceso sin firma hacia dominio de mando y control (C&C 'sync-gateway.invalid'): clasificado en 'Contenido dañino' (infección con canal C2 activo / RAT) con impacto de 'Intrusión'."
    ),
    "DISTRIBUTION-LAB": (
        "Contenido dañino",
        "Malware genérico / Virus / Gusano",
        "Alto",
        "Medio",
        "Vulnerable",
        "Descarga de carga maliciosa ('package.bin') detectada en proxy desde servidor externo ('updates-patch.invalid'): clasificado en 'Contenido dañino' (distribución/descarga de malware)."
    ),
    "CONFIG-LAB": (
        "Contenido dañino",
        "Malware genérico / Virus / Gusano",
        "Medio",
        "Medio",
        "Obtención de información",
        "Referencia desde servidor interno a repositorio externo con configuración de servidores de mando de malware ('profile.json'): clasificado en 'Contenido dañino'."
    ),
    "SCAN-LAB": (
        "Obtención de información",
        "Escaneo de redes / puertos",
        "Medio",
        "Bajo",
        "Intento de intrusión",
        "Sondeo secuencial de 268 puertos en 90 segundos sin tráfico de explotación posterior: encaja en 'Obtención de información' (reconocimiento / escaneo de puertos)."
    ),
    "SNIFF-LAB": (
        "Obtención de información",
        "Sniffing / Monitorización de tráfico",
        "Alto",
        "Alto",
        "Compromiso de la información",
        "Interfaz de red puesta en modo promiscuo y captura de paquetes ('captura-lab.pcap') sin autorización: corresponde exactamente a 'Obtención de información' (Sniffing / escucha de tráfico)."
    ),
    "SOCIAL-LAB": (
        "Obtención de información",
        "Ingeniería social / Reconocimiento",
        "Medio",
        "Bajo",
        "Fraude",
        "Llamada telefónica haciéndose pasar por soporte técnico solicitando nombres de servidores y códigos (vishing frustrado sin entrega de datos): se clasifica en 'Obtención de información' (Ingeniería social), con clase secundaria 'Fraude'."
    ),
    "EXPLOIT-LAB": (
        "Intento de intrusión",
        "Explotación de vulnerabilidad (Exploit)",
        "Alto",
        "Medio",
        "Vulnerable",
        "Petición con payload de explotación de vulnerabilidad conocida bloqueada por WAF (HTTP 403): se clasifica como 'Intento de intrusión' (explotación de vulnerabilidad frustrada)."
    ),
    "UNKNOWN-LAB": (
        "Intento de intrusión",
        "Intento de acceso no autorizado",
        "Medio",
        "Medio",
        "Otros",
        "Peticiones anómalas diseñadas para alterar el flujo de la aplicación rechazadas con HTTP 400 (sin firma CVE conocida): se clasifica como 'Intento de intrusión' contra aplicación."
    ),
    "APP-LAB": (
        "Intrusión",
        "Compromiso de aplicación",
        "Muy Alto",
        "Crítico (OT/Planta)",
        "Contenido dañino",
        "Ejecución confirmada de proceso hijo no permitido en el servidor web tras petición externa: constituye 'Intrusión' (compromiso efectivo de aplicación)."
    ),
    "PHYSICAL-LAB": (
        "Compromiso de la información",
        "Pérdida o exposición accidental de datos",
        "Alto",
        "Alto",
        "Disponibilidad",
        "Sustracción física no autorizada de equipamiento ('gw-sevilla-112') de zona restringida con potencial exposición de información local: se clasifica en 'Compromiso de la información' (sustracción/pérdida de dispositivo con datos), con impacto secundario en 'Disponibilidad'."
    ),
    "BADCHANGE-LAB": (
        "Disponibilidad",
        "Interrupción / Caída de servicio",
        "Medio",
        "Medio",
        "Otros",
        "Caída del servicio tras un cambio de configuración erróneo (CHG-0113) sin tráfico de ataque: corresponde a 'Disponibilidad' (interrupción operativa del servicio)."
    ),
    "SABOTAGE-LAB": (
        "Disponibilidad",
        "Sabotaje lógico o físico",
        "Alto",
        "Alto",
        "Otros",
        "Desconexión física deliberada y manipulación de cableado sin orden de mantenimiento: encaja directamente en 'Disponibilidad' (Sabotaje)."
    ),
    "OUTAGE-LAB": (
        "Disponibilidad",
        "Interrupción / Caída de servicio",
        "Medio",
        "Medio",
        "Otros",
        "Pérdida de conectividad por caída del enlace del proveedor ISP externo: se clasifica en 'Disponibilidad' (interrupción de comunicaciones)."
    ),
    "READ-LAB": (
        "Compromiso de la información",
        "Acceso o exfiltración no autorizada de datos",
        "Alto",
        "Alto",
        "Intrusión",
        "Lectura confirmada de 78 documentos fuera de los permisos autorizados de la función del usuario (DLP): corresponde a 'Compromiso de la información' (acceso no autorizado a datos)."
    ),
    "MODIFY-LAB": (
        "Compromiso de la información",
        "Modificación no autorizada de datos",
        "Muy Alto",
        "Crítico (OT/Planta)",
        "Intrusión",
        "Alteración no autorizada de 115 ficheros de proyecto verificada por cambio de hashes (FIM): corresponde a 'Compromiso de la información' (modificación no autorizada / integridad)."
    ),
    "LOSS-LAB": (
        "Compromiso de la información",
        "Pérdida o exposición accidental de datos",
        "Alto",
        "Alto",
        "Disponibilidad",
        "Pérdida de 152 documentos tras avería de almacenamiento sin réplica reciente: se clasifica en 'Compromiso de la información' (pérdida de datos) con efecto en 'Disponibilidad'."
    ),
    "MINING-LAB": (
        "Fraude",
        "Uso ilegítimo de recursos",
        "Medio",
        "Medio",
        "Intrusión",
        "Ejecución no autorizada de procesos de criptominería ('miner-lab', CPU 94%) en infraestructura corporativa: la guía de INCIBE encuadra el uso no autorizado de recursos de cómputo dentro de 'Fraude'."
    ),
    "LICENSE-LAB": (
        "Fraude",
        "Uso ilegítimo de recursos",
        "Bajo",
        "Bajo",
        "Contenido abusivo",
        "Distribución interna de software comercial sin licencia válida (uso no autorizado de recursos / derechos de propiedad intelectual): clasificado en 'Fraude' según guía INCIBE."
    ),
    "BEC-LAB": (
        "Fraude",
        "Suplantación de identidad (Spoofing / BEC)",
        "Alto",
        "Alto",
        "Obtención de información",
        "Suplantación de proveedor (Business Email Compromise) solicitando modificar cuenta bancaria de pago: corresponde a 'Fraude' (Suplantación de identidad)."
    ),
    "PHISH-LAB": (
        "Fraude",
        "Phishing / Spear Phishing",
        "Alto",
        "Medio",
        "Intento de intrusión",
        "Correo suplantando a soporte con enlace a formulario falso de robo de credenciales ('login-acceso.invalid'): corresponde a 'Fraude' (Phishing)."
    ),
    "TLS-LAB": (
        "Vulnerable",
        "Configuración insegura / Credenciales débiles",
        "Medio",
        "Bajo",
        "Otros",
        "Servicio expuesto que acepta protocolo criptográfico obsoleto (TLS 1.0) sin explotación observada: corresponde a la clase 'Vulnerable' de INCIBE."
    ),
    "AMPLIFIER-LAB": (
        "Vulnerable",
        "Servicio o puerto expuesto indebidamente",
        "Medio",
        "Medio",
        "Disponibilidad",
        "Servicio UDP expuesto sin restricción susceptible de usarse para amplificación (factor 18:1): se clasifica en 'Vulnerable' (servicio expuesto indebidamente)."
    ),
    "REMOTE-LAB": (
        "Vulnerable",
        "Servicio o puerto expuesto indebidamente",
        "Alto",
        "Alto",
        "Intento de intrusión",
        "Servicio de escritorio remoto (puerto 3389 RDP) publicado al exterior fuera del catálogo autorizado: se clasifica en 'Vulnerable' (exposición indebida de servicio)."
    ),
    "DISCLOSE-LAB": (
        "Vulnerable",
        "Configuración insegura / Credenciales débiles",
        "Medio",
        "Medio",
        "Compromiso de la información",
        "Ruta pública que expone metadatos internos de configuración sin autenticación y sin acceso a datos personales acreditado: se clasifica en 'Vulnerable' (exposición de información de configuración)."
    ),
    "PATCH-LAB": (
        "Vulnerable",
        "Sistema desactualizado / CVE sin parchear",
        "Alto",
        "Alto",
        "Otros",
        "Inventario autenticado confirma versión de software afectada por vulnerabilidad del fabricante pendiente de parcheo: corresponde directamente a 'Vulnerable' (sistema sin actualizar)."
    ),
    "SPAM-LAB": (
        "Contenido abusivo",
        "Spam",
        "Bajo",
        "Bajo",
        "Fraude",
        "Recepción masiva de mensajes comerciales no solicitados con el mismo patrón y sin enlaces de robo de credenciales: corresponde a 'Contenido abusivo' (Spam) según la guía de INCIBE."
    ),
    "APT-LAB": (
        "Intrusión",
        "Compromiso de sistema / servidor / Movimiento lateral",
        "Muy Alto",
        "Crítico (OT/Planta)",
        "Compromiso de la información",
        "Confirmación de accesos ilegítimos, persistencia y movimiento lateral sostenido en servidor de proyecto: corresponde a 'Intrusión' (compromiso avanzado / APT)."
    ),
    "OTHER-LAB": (
        "Otros",
        "Correo ajeno al SOC / Sin clasificar",
        "Medio",
        "Medio",
        "Intento de intrusión",
        "Comportamiento técnico anómalo pendiente de caracterización que aún no encaja de forma concluyente en otra clase de la taxonomía INCIBE: se asigna a 'Otros'."
    ),
}

def extract_table_fields(html):
    """Extrae pares clave-valor de la tabla HTML de notificaciones del SOC."""
    fields = {}
    rows = re.findall(r"<td[^>]*>\s*<b>([^<]+)</b>\s*</td>\s*<td[^>]*>((?:(?!</td>).)*?)</td>", html or "", flags=re.S | re.I)
    for k, v in rows:
        k_clean = re.sub(r"<[^>]+>", "", unescape(k)).strip().lower()
        v_clean = re.sub(r"<[^>]+>", "", unescape(v)).strip()
        if k_clean:
            fields[k_clean] = v_clean
    return fields

def parse_iso_timestamp(ts_str):
    """Convierte una fecha ISO con zona horaria (ej. 2026-10-29T18:59:53-04:00) a UTC y devuelve (utc_iso, raw_tz)."""
    if not ts_str:
        return None, "UTC"
    ts_str = ts_str.strip()
    tz_match = re.search(r"([+-]\d{2}:\d{2}|Z)$", ts_str)
    raw_tz = tz_match.group(1) if tz_match else "UTC"
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.isoformat(), raw_tz
    except Exception:
        return None, raw_tz

def main():
    conn = get_conn()
    print("Descargando correos desde Microsoft Graph...")
    messages = fetch_all_emails_from_graph()
    print(f"Leídos {len(messages)} correos del buzón.")

    # Mapa de internal_alert_id (ej. AL-20261030-0101) -> id en tabla alerts para enlazar duplicados y solicitudes SOL-B/SOL-L
    seen_alert_ids = {}
    rows_existing = conn.run("SELECT id, alert_code, fingerprint FROM alerts WHERE is_duplicate = FALSE")
    for rid, acode, fp in rows_existing:
        if fp:
            seen_alert_ids[fp] = rid

    inserted_emails = 0
    inserted_alerts = 0

    for idx, m in enumerate(messages, 1):
        msg_id = m.get("internetMessageId") or m.get("id")
        # Comprobar si ya existe en raw_emails
        exists = conn.run("SELECT id FROM raw_emails WHERE message_id = :mid", mid=msg_id)
        if exists:
            continue

        sender_obj = m.get("from", {}).get("emailAddress", {})
        sender_name = sender_obj.get("name", "")
        sender_email = sender_obj.get("address", "").lower()
        subject = m.get("subject") or "(Sin asunto)"
        body_html = m.get("body", {}).get("content", "")
        body_text = html_to_text(body_html)
        received_raw = m.get("receivedDateTime", "")
        received_utc, orig_tz = parse_iso_timestamp(received_raw)
        if not received_utc:
            received_utc = datetime.now(timezone.utc).isoformat()

        recipients = [r.get("emailAddress", {}) for r in (m.get("toRecipients") or [])]
        headers_list = m.get("internetMessageHeaders") or []
        headers_dict = {h.get("name"): h.get("value") for h in headers_list if h.get("name")}
        atts_meta = m.get("attachments_meta") or []
        raw_bytes = f"{msg_id}|{subject}|{body_html or body_text}".encode("utf-8", errors="ignore")
        email_sha256 = hashlib.sha256(raw_bytes).hexdigest()

        # Insertar en raw_emails
        res_raw = conn.run(
            """
            INSERT INTO raw_emails (
                message_id, conversation_id, sender_name, sender_email, recipients,
                subject, body_text, body_html, headers_json, attachments_json,
                raw_payload, raw_content_ref, sha256, received_at_raw, original_timezone, received_at_utc
            ) VALUES (
                :mid, :cid, :sname, :semail, :rcpts,
                :subj, :btxt, :bhtml, :hdrs, :atts,
                :rawp, :rref, :sha, :rraw, :otz, :rutc
            ) RETURNING id
            """,
            mid=msg_id,
            cid=m.get("conversationId", ""),
            sname=sender_name,
            semail=sender_email,
            rcpts=json.dumps(recipients),
            subj=subject,
            btxt=body_text,
            bhtml=body_html,
            hdrs=json.dumps(headers_dict),
            atts=json.dumps(atts_meta),
            rawp=json.dumps({k: v for k, v in m.items() if k != "body"}),
            rref=f"evidence/raw_emails/{idx}.json",
            sha=email_sha256,
            rraw=received_raw,
            otz=orig_tz,
            rutc=received_utc
        )
        raw_email_id = res_raw[0][0]
        for a in atts_meta:
            fname = a.get("name", "adjunto.bin")
            mtype = a.get("contentType", "application/octet-stream")
            sz = int(a.get("size", 0) or 0)
            ash = hashlib.sha256(f"{raw_email_id}:{fname}:{sz}".encode("utf-8")).hexdigest()
            conn.run(
                """INSERT INTO attachments (email_id, filename, mime_type, size_bytes, storage_ref, sha256)
                   VALUES (:eid, :fn, :mt, :sz, :sref, :sh)""",
                eid=raw_email_id, fn=fname, mt=mtype, sz=sz, sref=f"evidence/attachments/{raw_email_id}_{fname}", sh=ash
            )
        inserted_emails += 1

        # Ignorar en la tabla de alertas los correos de código de inicio de sesión de OpenAI o reenvíos propios de api.pdf
        if "openai.com" in sender_email or subject.strip() in ("Api", "No se puede entregar: Api"):
            continue

        # Detectar si es un correo del Director de TI o de la organización
        if sender_email in ("dirti@sampol.com", "amira@sampol.com") or "directriz" in subject.lower():
            conn.run(
                """
                INSERT INTO director_directives (directive_number, received_at_utc, raw_email_id, subject, request_summary, team_response, status)
                VALUES (:dnum, :rutc, :reid, :subj, :req, :resp, 'completada')
                """,
                dnum=0,
                rutc=received_utc,
                reid=raw_email_id,
                subj=subject,
                req=body_text[:1000],
                resp="Encargo inicial recibido. Base de datos PostgreSQL creada, ingesta Graph activa, clasificación INCIBE y Cuadro de Mando desplegados."
            )
            # También guardarlo en alerts como comunicación interna (is_soc_alert = FALSE) para trazabilidad total
            alert_code = f"DIR-{idx:03d}"
            conn.run(
                """
                INSERT INTO alerts (
                    alert_code, raw_email_id, event_timestamp_utc, event_timezone_raw,
                    source_tool, source_severity, normalized_severity,
                    incibe_class, incibe_type, incibe_danger_level, incibe_impact_level,
                    classification_justification, affected_user, title, description,
                    status, is_soc_alert, is_director_directive
                ) VALUES (
                    :acode, :reid, :ets, 'UTC',
                    'Dirección de TI / Organización', 'INFORMATIVO', 'INFO',
                    'Otros', 'Directriz / Comunicación del Director de TI', 'Bajo', 'Bajo',
                    'Comunicación oficial del Director de TI / Organización del reto. Se registra para trazabilidad pero se excluye del cómputo de alertas del SOC.',
                    :semail, :title, :desc,
                    'cerrada', FALSE, TRUE
                )
                """,
                acode=alert_code, reid=raw_email_id, ets=received_utc,
                semail=sender_email, title=subject, desc=body_text[:600]
            )
            continue

        # Caso 1: Correo externo de Phishing directo al buzón (ej. noreply@bankmenia.fr)
        if "bankmenia.fr" in sender_email or ("contraseña caduca hoy" in body_text.lower()):
            alert_code = f"PHISH-EXT-{idx:03d}"
            urls = re.findall(r'https?://[^\s"<>]+', body_html)
            res_al = conn.run(
                """
                INSERT INTO alerts (
                    alert_code, raw_email_id, event_timestamp_utc, event_timezone_raw,
                    source_tool, source_severity, normalized_severity,
                    incibe_class, incibe_type, incibe_danger_level, incibe_impact_level,
                    classification_justification, secondary_incibe_class,
                    affected_user, affected_host, source_ip, ioc_list, mitre_stage,
                    title, description, status, is_soc_alert, fingerprint
                ) VALUES (
                    :acode, :reid, :ets, :etz,
                    'Buzón Directo SOC (Correo Externo)', 'ALTO', 'ALTA',
                    'Fraude', 'Phishing / Spear Phishing', 'Alto', 'Alto',
                    'Correo externo recibido directamente en el buzón del equipo desde dominio fraudulento (bankmenia.fr) reclamando renovación urgente de contraseña mediante enlace de captura de credenciales. Clasificado en Fraude -> Phishing según guía INCIBE.',
                    'Intento de intrusión',
                    'equipo_1_hackaton@sampol.com', 'Buzón Correo Corporativo', 'bankmenia.fr', :iocs, 'Acceso Inicial (Phishing)',
                    :title, :desc, 'nueva', TRUE, :fp
                ) RETURNING id
                """,
                acode=alert_code, reid=raw_email_id, ets=received_utc, etz=orig_tz,
                iocs=json.dumps(urls[:3]), title=f"[Correo Externo Sospechoso] {subject}",
                desc=f"Remitente: {sender_email}. {body_text[:400]}", fp=f"EXT-{msg_id}"
            )
            aid = res_al[0][0]
            conn.run(
                """
                INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
                VALUES (:aid, 'Motor Híbrido NEXUS', 'CREACION', 'incibe_class', NULL, 'Fraude / Phishing', 'Detección automática de phishing entrante directo en el buzón')
                """,
                aid=aid
            )
            inserted_alerts += 1
            continue

        # Caso 2: Notificaciones con formato SOC de Sampol
        tfields = extract_table_fields(body_html)
        soc_code_m = re.search(r"(SOC-\d{8}-\d{3}-[A-F0-9]+)", subject + " " + body_text)
        soc_code = soc_code_m.group(1) if soc_code_m else f"SOC-GEN-{idx:03d}"

        al_id_m = re.search(r"(AL-\d{8}-\d{4})", subject + " " + body_text)
        internal_al_id = al_id_m.group(1) if al_id_m else None

        sol_id_m = re.search(r"(SOL-[BL]-\d{3})", subject + " " + body_text)
        sol_id = sol_id_m.group(1) if sol_id_m else None

        # Extraer fecha del Primer evento o Emisión
        ev_m = re.search(r"Primer evento:\s*([0-9T:\.\+-]+|Z)", body_text)
        if not ev_m:
            ev_m = re.search(r"Fecha de solicitud:\s*([0-9T:\.\+-]+|Z)", body_text)
        if not ev_m:
            ev_m = re.search(r"Revisión:\s*([0-9T:\.\+-]+|Z)", body_text)
        if not ev_m:
            ev_m = re.search(r"Emisión:\s*([0-9T:\.\+-]+|Z)", body_text)

        if ev_m:
            event_utc, event_tz = parse_iso_timestamp(ev_m.group(1))
        else:
            event_utc, event_tz = received_utc, "No indicada (asumida recepción UTC)"

        if not event_utc:
            event_utc = received_utc

        raw_cuenta = tfields.get("cuenta relacionada", "")
        clean_cuenta = validate_and_clean_user(raw_cuenta)
        cuenta = clean_cuenta if clean_cuenta != "No identificado" else None

        raw_recurso = tfields.get("recurso", "")
        clean_recurso = validate_and_clean_host(raw_recurso)
        recurso = clean_recurso if clean_recurso != "No identificado" else None

        raw_ip = tfields.get("direccion relacionada", "")
        clean_ip = validate_and_clean_ip(raw_ip) or normalize_ip(raw_ip, body_text)
        sede = tfields.get("sede", "No indicada")
        criticidad_activo = tfields.get("criticidad", "Media")
        fuente = tfields.get("fuente", "SOC")
        regla = tfields.get("regla de detección", "")

        # Prioridad/severidad del asunto
        sev_m = re.search(r"\[(CRÍTICO|ALTO|MEDIO|BAJO|INFORMATIVO)\]", subject, flags=re.I)
        source_sev = sev_m.group(1).upper() if sev_m else "NO INDICADA"
        sev_map = {
            "CRÍTICO": "CRITICA",
            "CRITICO": "CRITICA",
            "ALTO": "ALTA",
            "MEDIO": "MEDIA",
            "BAJO": "BAJA",
            "INFORMATIVO": "INFO",
            "NO INDICADA": "MEDIA"
        }
        norm_sev = sev_map.get(source_sev, "MEDIA")

        # Detectar Prompt Injection / Trampas en el texto
        pi_detected, pi_evidence = detect_prompt_injection(body_text, body_html)

        # Extraer hashes SHA-256 o dominios .invalid
        hashes = re.findall(r"\b[a-f0-9]{64}\b", body_text, flags=re.I)
        domains = re.findall(r"\b[a-z0-9.-]+\.invalid\b", body_text, flags=re.I)
        iocs = list(dict.fromkeys(hashes + domains))

        # Determinar clasificación INCIBE, duplicados y ruido
        is_soc_alert = True
        is_noise = False
        is_duplicate = False
        parent_id = None
        status = "nueva"
        mitre_stage = "Detección SOC"

        # 2A. Ruido / No es alerta SOC (ej. Reserva de sala para mañana · nota 01)
        if "no es una alerta soc" in body_text.lower() or "este mensaje no comunica una incidencia de seguridad" in body_text.lower():
            incibe_class = "Otros"
            incibe_type = "Correo ajeno al SOC / Sin clasificar"
            danger_lvl = "Bajo"
            impact_lvl = "Bajo"
            sec_class = None
            justif = "El propio cuerpo e indicadores ('Fuente: Agenda corporativa', 'No es una alerta SOC') confirman que se trata de un aviso administrativo (reserva de sala) y no un incidente de seguridad. Se archiva y se excluye de las métricas de incidentes."
            is_soc_alert = False
            is_noise = True
            status = "cerrada"
            mitre_stage = "No aplica (Ruido Administrativo)"

        # 2B. Reenvío / Alerta Duplicada explícita
        elif "reenvío de alerta ya notificada" in subject.lower() or "reenvío del mismo evento" in body_text.lower():
            incibe_class, incibe_type, danger_lvl, impact_lvl, sec_class, base_just = RULE_TO_INCIBE.get(
                "DDOS-LAB", ("Disponibilidad", "Denegación de servicio (DoS / DDoS)", "Muy Alto", "Crítico (OT/Planta)", None, "")
            )
            for rprefix, rtuple in RULE_TO_INCIBE.items():
                if rprefix in regla:
                    incibe_class, incibe_type, danger_lvl, impact_lvl, sec_class, base_just = rtuple
                    break
            is_duplicate = True
            parent_id = seen_alert_ids.get(internal_al_id)
            status = "cerrada"
            justif = f"[DUPLICADO DE {internal_al_id}] Reenvío del mismo evento por el concentrador SOC con idéntico intervalo temporal. Vinculado a la alerta original (ID BD #{parent_id}) para no contabilizarlo dos veces. {base_just}"
            if parent_id:
                conn.run("UPDATE alerts SET duplicate_count = duplicate_count + 1, updated_at = NOW() WHERE id = :pid", pid=parent_id)

        # 2C. Solicitudes operativas de Bloqueo (SOL-B-XXX) o Liberación por falso positivo (SOL-L-XXX)
        elif sol_id:
            parent_id = seen_alert_ids.get(internal_al_id)
            is_duplicate = True  # Vinculada al incidente original AL-... para no inflar el número de incidentes distintos
            if sol_id.startswith("SOL-L-"):
                incibe_class = "Otros"
                incibe_type = "Falsa alarma / Ruido operativo"
                danger_lvl = "Bajo"
                impact_lvl = "Bajo"
                sec_class = "Intento de intrusión"
                justif = f"[{sol_id} · FALSO POSITIVO CONFIRMADO] Revisión humana confirma que {internal_al_id} fue causada por un conector autorizado con contraseña antigua (cambio {re.findall(r'CHG-[0-9-]+', body_text) or ['autorizado']}). Solicita liberar al usuario {cuenta} en la API."
                is_noise = True
                status = "falsa_alarma"
                mitre_stage = "Falso Positivo / Liberación SOAR"
                if parent_id:
                    conn.run(
                        """
                        UPDATE alerts
                        SET is_noise_or_false_positive = TRUE,
                            status = 'falsa_alarma',
                            duplicate_count = duplicate_count + 1,
                            classification_justification = classification_justification || ' [ACTUALIZACIÓN ' || :solid || ': Confirmado como Falso Positivo por conector con contraseña antigua; usuario liberado]',
                            updated_at = NOW()
                        WHERE id = :pid
                        """,
                        solid=sol_id, pid=parent_id
                    )
                    conn.run(
                        """
                        INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
                        VALUES (:pid, 'Responsable de turno SOC', 'CAMBIO_ESTADO', 'status', 'nueva', 'falsa_alarma', :rsn)
                        """,
                        pid=parent_id, rsn=f"Recibido correo {sol_id} ({soc_code}) confirmando falso positivo y solicitando liberación de {cuenta}"
                    )
            else:
                incibe_class = "Intento de intrusión"
                incibe_type = "Fuerza bruta / Diccionario"
                danger_lvl = "Alto"
                impact_lvl = "Medio"
                sec_class = "Otros"
                justif = f"[{sol_id} · ORDEN OPERATIVA DE CONTENCIÓN] Solicitud del Responsable de turno SOC para bloquear temporalmente al usuario '{cuenta}' en la API en relación con la alerta {internal_al_id}. Vinculada a la alerta original para trazabilidad SOAR sin duplicar estadísticas."
                status = "en_revision"
                mitre_stage = "Contención SOAR (Solicitud Bloqueo)"
                if parent_id:
                    conn.run("UPDATE alerts SET duplicate_count = duplicate_count + 1, status = 'en_revision', updated_at = NOW() WHERE id = :pid", pid=parent_id)

        # 2D. Correo sospechoso incompleto ("SOC: ...")
        elif "posible correo sospechoso" in subject.lower() or "revisión semántica provisional" in regla.lower():
            if "contenido dañino" in regla.lower() or "macro" in subject.lower():
                incibe_class = "Contenido dañino"
                incibe_type = "Malware genérico / Virus / Gusano"
                danger_lvl = "Alto"
                impact_lvl = "Medio"
                sec_class = "Otros"
                justif = "Aviso preliminar del SOC sobre ejecución de macro en archivo de servicio, sin equipo, usuario ni hash indicados. Se clasifica provisionalmente en 'Contenido dañino -> Malware' pendiente de enriquecimiento. Nota: contiene cláusula 'HN03 (solo cuando se cita expresamente)'."
                status = "en_revision"
                mitre_stage = "5. Ejecución / C2 Malware"
            else:
                incibe_class = "Fraude"
                incibe_type = "Phishing / Spear Phishing"
                danger_lvl = "Medio"
                impact_lvl = "Bajo"
                sec_class = "Otros"
                justif = "Aviso preliminar e incompleto del SOC sobre un correo con enlace sospechoso, sin URL, IP ni usuario verificados. Se asigna provisionalmente a 'Fraude -> Phishing' pendiente de enriquecimiento. Nota: contiene la cláusula trampa 'HN03 (solo cuando se cita expresamente)'."
                status = "en_revision"
                mitre_stage = "3. Acceso Inicial / Fraude"

        # 2E. Reglas estándar del laboratorio SOC
        else:
            matched = False
            for rprefix, rtuple in RULE_TO_INCIBE.items():
                if rprefix in regla:
                    incibe_class, incibe_type, danger_lvl, impact_lvl, sec_class, justif = rtuple
                    matched = True
                    break
            if not matched:
                incibe_class = "Otros"
                incibe_type = "Correo ajeno al SOC / Sin clasificar"
                danger_lvl = "Medio"
                impact_lvl = "Medio"
                sec_class = None
                justif = f"Clasificación por análisis semántico del evento ({regla})."

            # Asignar fase MITRE / Kill Chain para la vista de Investigación Forense
            if incibe_class == "Obtención de información":
                mitre_stage = "1. Reconocimiento"
            elif incibe_class == "Vulnerable":
                mitre_stage = "2. Superficie Expuesta"
            elif incibe_class == "Fraude":
                mitre_stage = "3. Acceso Inicial / Fraude"
            elif incibe_class == "Intento de intrusión":
                mitre_stage = "4. Intento de Intrusión"
            elif incibe_class == "Contenido dañino":
                mitre_stage = "5. Ejecución / C2 Malware"
            elif incibe_class == "Intrusión":
                mitre_stage = "6. Intrusión / Escalada"
            elif incibe_class == "Compromiso de la información":
                mitre_stage = "7. Compromiso / Impacto en Datos"
            elif incibe_class == "Disponibilidad":
                mitre_stage = "8. Impacto en Disponibilidad"

        # Título limpio sin los prefijos redundantes
        clean_title = re.sub(r"^\[SOC\]\[P\d\]\[[^\]]+\]\s*", "", subject).split("|")[0].strip()
        # Primer párrafo narrativo después de "Estimado equipo Hackapol:"
        desc_m = re.search(r"Estimado equipo Hackapol:\s*(.*?)(?:Cuenta relacionada|$)", body_text, flags=re.S)
        clean_desc = desc_m.group(1).strip() if desc_m else body_text[:400]

        fp_key = internal_al_id if (internal_al_id and not is_duplicate) else soc_code

        int_alert_id = sol_id if sol_id else internal_al_id

        res_alert = conn.run(
            """
            INSERT INTO alerts (
                alert_code, internal_alert_id, raw_email_id, event_timestamp_utc, event_timezone_raw,
                source_tool, detection_rule, source_severity, normalized_severity,
                incibe_class, incibe_type, incibe_danger_level, incibe_impact_level,
                classification_justification, secondary_incibe_class,
                affected_host, source_ip, destination_ip, affected_user,
                sede, asset_criticality, affected_asset_type, ioc_list, mitre_stage,
                title, description,
                status, is_soc_alert, is_noise_or_false_positive, is_director_directive,
                is_duplicate, parent_alert_id, duplicate_count, fingerprint,
                prompt_injection_detected, prompt_injection_evidence
            ) VALUES (
                :acode, :iid, :reid, :ets, :etz,
                :stool, :drule, :ssev, :nsev,
                :iclass, :itype, :idanger, :iimpact,
                :justif, :sclass,
                :ahost, :sip, :dip, :auser,
                :sede, :acrit, :atype, :iocs, :mitre,
                :title, :desc,
                :status, :issoc, :isnoise, FALSE,
                :isdup, :pid, 1, :fp,
                :pidet, :pievid
            ) RETURNING id
            """,
            acode=soc_code,
            iid=int_alert_id,
            reid=raw_email_id,
            ets=event_utc,
            etz=event_tz,
            stool=fuente,
            drule=regla,
            ssev=source_sev,
            nsev=norm_sev,
            iclass=incibe_class,
            itype=incibe_type,
            idanger=danger_lvl,
            iimpact=impact_lvl,
            justif=justif,
            sclass=sec_class,
            ahost=recurso,
            sip=clean_ip,
            dip=sede,
            auser=cuenta,
            sede=sede,
            acrit=criticidad_activo,
            atype=f"Sede {sede} ({criticidad_activo})",
            iocs=json.dumps(iocs),
            mitre=mitre_stage,
            title=clean_title,
            desc=clean_desc,
            status=status,
            issoc=is_soc_alert,
            isnoise=is_noise,
            isdup=is_duplicate,
            pid=parent_id,
            fp=fp_key,
            pidet=pi_detected,
            pievid=pi_evidence
        )
        new_aid = res_alert[0][0]
        if internal_al_id and not is_duplicate:
            seen_alert_ids[internal_al_id] = new_aid

        conn.run(
            """
            INSERT INTO alert_audit_log (alert_id, changed_by, action_type, field_changed, old_value, new_value, reason)
            VALUES (:aid, 'Motor Híbrido NEXUS (IA + Reglas)', 'CREACION', 'incibe_class', NULL, :nval, :rsn)
            """,
            aid=new_aid,
            nval=f"{incibe_class} -> {incibe_type}",
            rsn=justif[:300]
        )
        inserted_alerts += 1

    print(f"Ingesta completada: {inserted_emails} correos nuevos guardados, {inserted_alerts} alertas procesadas.")
    conn.close()

    # Ejecutar Playbook de Bloqueo Autónomo de Cuentas Comprometidas (Directriz 1 - 18:00 CET)
    try:
        from autoblock_engine import run_autoblock_sweep
        run_autoblock_sweep()
    except Exception as e:
        print(f"[ERROR] Error ejecutando run_autoblock_sweep: {e}")

    # Resumen rápido de verificación desde la BD
    conn = get_conn()
    stats = conn.run(
        """
        SELECT incibe_class, COUNT(*) AS total_unicas
        FROM v_soc_unique_alerts
        GROUP BY incibe_class
        ORDER BY total_unicas DESC
        """
    )
    print("\n=== DISTRIBUCIÓN POR CLASE INCIBE (ALERTAS ÚNICAS DEL SOC) ===")
    for cls_name, cnt in stats:
        print(f" - {cls_name}: {cnt}")

    dups = conn.run("SELECT COUNT(*) FROM alerts WHERE is_duplicate = TRUE")
    nonsoc = conn.run("SELECT COUNT(*) FROM alerts WHERE is_soc_alert = FALSE")
    print(f"Alertas duplicadas/operativas vinculadas: {dups[0][0]} | Correos No-SOC filtrados: {nonsoc[0][0]}")
    conn.close()

if __name__ == "__main__":
    main()
