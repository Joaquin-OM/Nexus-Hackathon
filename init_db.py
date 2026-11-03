import json
import urllib.request
from config import get_conn, SOAR_API_URL, SOAR_API_KEY, SOAR_TEAM_PREFIX

INCIBE_CATALOG = [
    ("ABU", "Contenido abusivo", "Spam", "Bajo", "Envío masivo de correo no deseado o publicitario"),
    ("ABU", "Contenido abusivo", "Contenido ofensivo / Acoso", "Bajo", "Comunicaciones difamatorias, ofensivas o ilícitas"),
    ("MAL", "Contenido dañino", "Ransomware", "Muy Alto", "Cifrado malicioso de sistemas o ficheros con exigencia de rescate"),
    ("MAL", "Contenido dañino", "Troyano / Backdoor / RAT", "Alto", "Malware que permite acceso remoto o control encubierto"),
    ("MAL", "Contenido dañino", "Spyware / Keylogger / Infostealer", "Alto", "Captura de credenciales o información sensible del sistema"),
    ("MAL", "Contenido dañino", "Malware genérico / Virus / Gusano", "Alto", "Ejecución o detección de código dañino en endpoints o servidores"),
    ("OBT", "Obtención de información", "Escaneo de redes / puertos", "Medio", "Reconocimiento técnico de servicios, puertos o topología"),
    ("OBT", "Obtención de información", "Sniffing / Monitorización de tráfico", "Alto", "Interceptación pasiva de comunicaciones o paquetes de red"),
    ("OBT", "Obtención de información", "Ingeniería social / Reconocimiento", "Medio", "Obtención de información interna mediante engaño sin fraude directo"),
    ("IIN", "Intento de intrusión", "Fuerza bruta / Diccionario", "Alto", "Intentos repetidos de autenticación contra cuentas o servicios"),
    ("IIN", "Intento de intrusión", "Explotación de vulnerabilidad (Exploit)", "Alto", "Intento de aprovechar un fallo técnico (SQLi, RCE, XSS, CVE)"),
    ("IIN", "Intento de intrusión", "Intento de acceso no autorizado", "Medio", "Intentos fallidos de acceso a recursos restringidos"),
    ("INT", "Intrusión", "Compromiso de cuenta privilegiada / Admin", "Muy Alto", "Acceso ilegítimo exitoso a una cuenta con privilegios elevados"),
    ("INT", "Intrusión", "Compromiso de cuenta de usuario", "Alto", "Acceso ilegítimo exitoso a una cuenta de usuario estándar"),
    ("INT", "Intrusión", "Compromiso de sistema / servidor / Movimiento lateral", "Muy Alto", "Control no autorizado de un servidor, host o salto entre equipos"),
    ("INT", "Intrusión", "Compromiso de aplicación", "Alto", "Toma de control o ejecución no autorizada dentro de una aplicación"),
    ("DIS", "Disponibilidad", "Denegación de servicio (DoS / DDoS)", "Alto", "Saturación intencionada de red o servicios para impedir su operación"),
    ("DIS", "Disponibilidad", "Sabotaje lógico o físico", "Muy Alto", "Acción deliberada para detener instalaciones o borrar sistemas"),
    ("DIS", "Disponibilidad", "Interrupción / Caída de servicio", "Alto", "Pérdida de disponibilidad por fallo operativo o sobrecarga"),
    ("COM", "Compromiso de la información", "Acceso o exfiltración no autorizada de datos", "Muy Alto", "Lectura o robo de información confidencial o corporativa"),
    ("COM", "Compromiso de la información", "Modificación no autorizada de datos", "Alto", "Alteración ilícita de bases de datos, registros o configuraciones"),
    ("COM", "Compromiso de la información", "Pérdida o exposición accidental de datos", "Alto", "Fuga o extravío involuntario de información sensible"),
    ("FRA", "Fraude", "Phishing / Spear Phishing", "Alto", "Suplantación por correo o web para robar credenciales o distribuir carga maliciosa"),
    ("FRA", "Fraude", "Suplantación de identidad (Spoofing / BEC)", "Alto", "Hacerse pasar por un directivo, proveedor o entidad legítima"),
    ("FRA", "Fraude", "Uso ilegítimo de recursos", "Medio", "Uso no autorizado de infraestructura corporativa (ej. criptominería)"),
    ("VUL", "Vulnerable", "Servicio o puerto expuesto indebidamente", "Medio", "Recurso accesible sin la debida protección o segmentación"),
    ("VUL", "Vulnerable", "Sistema desactualizado / CVE sin parchear", "Alto", "Software con vulnerabilidades públicas pendientes de actualización"),
    ("VUL", "Vulnerable", "Configuración insegura / Credenciales débiles", "Medio", "Fallos de bastionado, políticas débiles o certificados caducados"),
    ("OTR", "Otros", "Falsa alarma / Ruido operativo", "Bajo", "Evento benigno o falso positivo confirmado de las herramientas del SOC"),
    ("OTR", "Otros", "Directriz / Comunicación del Director de TI", "Bajo", "Instrucción o consulta interna enviada por el Director de TI"),
    ("OTR", "Otros", "Correo ajeno al SOC / Sin clasificar", "Bajo", "Mensaje que no constituye una alerta de seguridad o no encaja en otra clase"),
]

WHITELIST_SEED = [
    ("usuario", "director.ti@sampol.com", "VIP_DIRECCION", "Cuenta del Director de TI de Sampol (No bloquear automáticamente)", True),
    ("usuario", "equipo_1_hackaton@sampol.com", "INFRA_CRITICA", "Buzón oficial del SOC Equipo 1 (No bloquear)", True),
    ("ip", "127.0.0.1", "INFRA_CRITICA", "Loopback / Localhost", True),
    ("ip", "10.0.0.1", "OT_PLANTA", "Gateway Principal SCADA / Planta Energética Sampol", True),
]

BUSINESS_PARAMS_SEED = [
    ("manual_minutes_per_alert", 10.0, "minutos/alerta", "Tiempo medio dedicado hoy a revisar y clasificar cada alerta a mano"),
    ("with_solution_minutes_per_alert", 1.5, "minutos/alerta", "Tiempo medio con el sistema NEXUS para revisar casos propuestos"),
    ("manual_minutes_per_block", 15.0, "minutos/bloqueo", "Tiempo manual para tramitar y ejecutar un bloqueo de IP/usuario sin SOAR"),
    ("with_solution_minutes_per_block", 0.5, "minutos/bloqueo", "Tiempo con la automatización API del Bloqueador"),
    ("hourly_cost_eur", 32.0, "€/hora", "Coste empresa por hora del técnico/analista de TI/SOC"),
    ("initial_investment_eur", 6500.0, "€", "Inversión inicial de desarrollo y puesta en marcha (horas de ingeniería + configuración)"),
    ("monthly_maintenance_eur", 220.0, "€/mes", "Costes recurrentes mensuales (Azure PostgreSQL, hosting web, consumo API IA y mantenimiento)"),
    ("plant_downtime_cost_per_hour_eur", 18000.0, "€/hora", "Coste estimado por hora de parada en una planta energética de alta eficiencia"),
    ("commercial_siem_annual_eur", 36000.0, "€/año", "Coste anual estimado de una herramienta SIEM/SOAR comercial equivalente (Comparativa Buy vs Build)"),
]

def main():
    conn = get_conn()
    with open(r"C:\Users\osesj\Documents\Nexus-Hackathon\schema.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    # Ejecutar schema.sql sentencia por sentencia
    for statement in sql_script.split(";"):
        stmt = statement.strip()
        if stmt:
            conn.run(stmt)
    print("Esquema SQL creado correctamente.")

    # Poblar catálogo INCIBE
    for code, cname, sname, danger, desc in INCIBE_CATALOG:
        conn.run(
            """
            INSERT INTO incibe_taxonomy (class_code, class_name, subtype_name, default_danger_level, description)
            VALUES (:code, :cname, :sname, :danger, :desc)
            ON CONFLICT (class_name, subtype_name) DO UPDATE
            SET default_danger_level = EXCLUDED.default_danger_level,
                description = EXCLUDED.description
            """,
            code=code, cname=cname, sname=sname, danger=danger, desc=desc
        )
    print(f"Catálogo INCIBE poblado: {len(INCIBE_CATALOG)} subtipos en 10 clases.")

    # Poblar Whitelist
    for atype, aval, acat, desc, req in WHITELIST_SEED:
        conn.run(
            """
            INSERT INTO protected_assets_whitelist (asset_type, asset_value, asset_category, description, requires_manual_approval)
            VALUES (:atype, :aval, :acat, :desc, :req)
            ON CONFLICT (asset_value) DO NOTHING
            """,
            atype=atype, aval=aval, acat=acat, desc=desc, req=req
        )
    print("Lista blanca de activos críticos OT/IT inicializada.")

    # Poblar parámetros de negocio
    for pkey, pval, unit, desc in BUSINESS_PARAMS_SEED:
        conn.run(
            """
            INSERT INTO business_parameters (param_key, param_value, unit, description)
            VALUES (:pkey, :pval, :unit, :desc)
            ON CONFLICT (param_key) DO NOTHING
            """,
            pkey=pkey, pval=pval, unit=unit, desc=desc
        )
    print("Parámetros de negocio (ROI) inicializados.")

    # Sincronizar bloqueos actuales desde la API del Bloqueador (/equipo-1/bloqueos)
    try:
        req = urllib.request.Request(
            f"{SOAR_API_URL}{SOAR_TEAM_PREFIX}/bloqueos",
            headers={"X-API-Key": SOAR_API_KEY}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            bloqueos = json.loads(resp.read().decode())
        existing = conn.run("SELECT COUNT(*) FROM soar_actions WHERE trigger_mode = 'sincronizado'")
        if existing[0][0] == 0:
            for b in bloqueos:
                for acc in b.get("acciones", []):
                    conn.run(
                        """
                        INSERT INTO soar_actions (external_block_id, action, target_type, target_value, trigger_mode, api_status_code, api_response, reason, executed_by, executed_at)
                        VALUES (:bid, :act, :ttype, :tval, 'sincronizado', 200, :resp, 'Historial previo en API Bloqueador Sampol', 'Sincronización Inicial API', :fecha)
                        """,
                        bid=b["id"],
                        act=acc["accion"],
                        ttype=b["tipo"],
                        tval=b["valor"],
                        resp=json.dumps(b),
                        fecha=acc["fecha"]
                    )
            print(f"Sincronizados {len(bloqueos)} bloqueos previos desde la API de Sampol.")
    except Exception as e:
        print("Aviso sincronizando API:", e)

    tables = conn.run("SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
    print("Tablas y vistas en PostgreSQL:", tables)
    conn.close()

if __name__ == "__main__":
    main()
