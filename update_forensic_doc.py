import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def generate_consolidated_forensic_report():
    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    COLOR_PRIMARY = RGBColor(14, 43, 92)    # Azul Marino SAMPOL
    COLOR_DANGER = RGBColor(192, 0, 0)      # Rojo Alerta Forense
    COLOR_SECONDARY = RGBColor(0, 102, 204) # Azul Operativo
    COLOR_DARK = RGBColor(33, 37, 41)       # Gris Oscuro Texto
    COLOR_MUTED = RGBColor(108, 117, 125)   # Gris Secundario
    COLOR_EMERALD = RGBColor(16, 149, 104)  # Verde Éxito

    # -------------------------------------------------------------
    # ENCABEZADO PERICIAL
    # -------------------------------------------------------------
    header_tbl = doc.add_table(rows=1, cols=2)
    header_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_left = header_tbl.cell(0, 0)
    c_right = header_tbl.cell(0, 1)
    c_left.width = Inches(4.5)
    c_right.width = Inches(2.4)
    
    p_hl = c_left.paragraphs[0]
    p_hl.paragraph_format.space_after = Pt(2)
    r1 = p_hl.add_run("GRUPO SAMPOL · EQUIPO DE RESPUESTA A INCIDENTES (CSIRT)\n")
    r1.font.size = Pt(9.5)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    r2 = p_hl.add_run("LABORATORIO FORENSE Y OPERACIONES DE SEGURIDAD (NEXUS SOC 2.0)")
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = COLOR_MUTED

    p_hr = c_right.paragraphs[0]
    p_hr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hr.paragraph_format.space_after = Pt(2)
    r3 = p_hr.add_run("EXPEDIENTE: DFIR-20261104-02\n")
    r3.font.size = Pt(10)
    r3.font.bold = True
    r3.font.color.rgb = COLOR_DANGER
    r4 = p_hr.add_run("TLP:AMBER · USO CONFIDENCIAL / DIRECCIÓN TI")
    r4.font.size = Pt(8.5)
    r4.font.bold = True
    r4.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # TÍTULO PRINCIPAL
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(6)
    title_p.paragraph_format.space_after = Pt(4)
    r_cat = title_p.add_run("INFORME FORENSE CONSOLIDADO Y PLAN DE DEFENSA ACTIVA\n")
    r_cat.font.size = Pt(11)
    r_cat.font.bold = True
    r_cat.font.color.rgb = COLOR_DANGER

    r_title = title_p.add_run("ANÁLISIS DE CAUSA RAÍZ, RECONSTRUCCIÓN KILL CHAIN Y ESTRATEGIA DE DEFENSA ACTIVA")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(4)
    sub_p.paragraph_format.space_after = Pt(12)
    r_sub = sub_p.add_run("Investigación pericial exhaustiva del incidente: Origen del ataque, vector de penetración, contraste de hipótesis, contención del ransomware y doble extorsión, desarticulación del fraude financiero y propuestas de innovación para Grupo SAMPOL.\n")
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_MUTED

    r_meta = sub_p.add_run("Perito Responsable: Equipo 1 (NEXUS) | Fecha: 04/11/2026 09:15 CET | Destinatario: Dirección de TI (dirti@sampol.com)")
    r_meta.font.size = Pt(9.5)
    r_meta.font.bold = True
    r_meta.font.color.rgb = COLOR_DARK

    # -------------------------------------------------------------
    # CUADRO DESTACADO: ESTADO GENERAL DEL INCIDENTE
    # -------------------------------------------------------------
    callout_tbl = doc.add_table(rows=1, cols=1)
    callout_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = callout_tbl.cell(0, 0)
    c_cell.width = Inches(6.9)
    set_cell_background(c_cell, "F0FDF4") # Verde suave
    set_cell_margins(c_cell, top=140, bottom=140, left=180, right=180)

    cp = c_cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(2)
    cp.add_run("🛡️ RESUMEN EJECUTIVO Y SITUACIÓN DE CONTROL ACTUAL DEL INCIDENTE\n").font.bold = True
    cp.runs[0].font.size = Pt(11)
    cp.runs[0].font.color.rgb = COLOR_EMERALD

    cp_desc = cp.add_run(
        "• Propagación y Cifrado CONTENIDOS: Recursos compartidos de LAB-FS-01 asegurados en Modo Solo Lectura. Cero nuevos equipos afectados.\n"
        "• Fraude Financiero ABORTADO: Congelación cautelar de transferencias salientes en pasarela bancaria. Pérdida económica = 0,00 €.\n"
        "• Infraestructura Crítica e Industrial OT: Redes SCADA, microrredes y plantas energéticas operando al 100% con CERO paradas de servicio.\n"
        "• Falsa Exposición 'BLACK VAULT': Certificado que el dominio black-vault.invalid (RFC 2606) no resuelve en Internet público.\n"
        "• Métricas Globales del SOC: 326 correos forenses auditados (100%), 311 alertas gestionadas bajo taxonomía INCIBE, 80 órdenes SOAR automatizadas."
    )
    cp_desc.font.size = Pt(9.5)
    cp_desc.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECCIÓN 1: DE DÓNDE VIENE ESTE ATAQUE (ATRIBUCIÓN E INFRAESTRUCTURA)
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(4)
    h1.add_run("1. ¿DE DÓNDE VIENE ESTE ATAQUE? (ATRIBUCIÓN E INTELIGENCIA DE AMENAZAS)").font.bold = True
    h1.runs[0].font.size = Pt(12.5)
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    p1 = doc.add_paragraph()
    p1.paragraph_format.space_after = Pt(6)
    p1.add_run(
        "El análisis pericial de artefactos, binarios y patrones de tráfico sitúa la autoría en un grupo organizado de cibercrimen financiero "
        "que opera bajo el modelo de Ransomware-as-a-Service (RaaS), con modus operandi y TTPs comparables a actores avanzados (tipo LockBit / BlackCat / FIN7). "
        "El ataque combinó de manera orquestada la doble extorsión con una tentativa oportunista de fraude del CEO / cambio de IBAN (Business Email Compromise)."
    )

    t_ioc = doc.add_table(rows=6, cols=3)
    t_ioc.alignment = WD_TABLE_ALIGNMENT.CENTER
    ioc_hdrs = ["Indicador de Compromiso (IoC)", "Tipo / Clasificación", "Función en el Ataque y Estado de Bloqueo"]
    for j, htxt in enumerate(ioc_hdrs):
        cell = t_ioc.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    ioc_rows = [
        ("198.51.100.77", "Dirección IPv4 Externa", "Servidor C2 y destino de exfiltración de 18 GB. BLOQUEADA en Firewall perimetral."),
        ("sync-gateway.invalid", "Dominio DNS de Balizaje", "Canal de comando periódico y control C2 para tareas encubiertas. BLOQUEADO en DNS Sinkhole."),
        ("203.0.113.12 / 203.0.113.33", "Direcciones IPv4 Externas", "Puntos de sondeo y persistencia de accesos remotos no autorizados. BLOQUEADAS."),
        ("black-vault.invalid", "Dominio de Extorsión", "Dominio citado en nota de rescate; confirmado sin resolución DNS pública (RFC 2606)."),
        ("System Health Check", "Tarea Programada Oculta", "Mecanismo de persistencia en LAB-APP-04 ejecutando script PowerShell. ELIMINADA.")
    ]

    for idx, (ioc, t_ioc_val, f_ioc) in enumerate(ioc_rows, start=1):
        c0 = t_ioc.cell(idx, 0)
        c1 = t_ioc.cell(idx, 1)
        c2 = t_ioc.cell(idx, 2)
        c0.width = Inches(2.2)
        c1.width = Inches(1.8)
        c2.width = Inches(2.9)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        c0.paragraphs[0].add_run(ioc).font.size = Pt(8.5)
        c0.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].add_run(t_ioc_val).font.size = Pt(8.5)
        c2.paragraphs[0].add_run(f_ioc).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECCIÓN 2: ANÁLISIS DE CAUSA RAÍZ (RCA) Y EVALUACIÓN DE LAS 3 HIPÓTESIS
    # -------------------------------------------------------------
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    h2.add_run("2. ANÁLISIS DE CAUSA RAÍZ (RCA) Y CONTRASTE RIGUROSO DE HIPÓTESIS").font.bold = True
    h2.runs[0].font.size = Pt(12.5)
    h2.runs[0].font.color.rgb = COLOR_PRIMARY

    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(6)
    p2.add_run(
        "En respuesta a la instrucción directa de la Dirección de TI, el laboratorio forense evaluó formalmente las tres hipótesis abiertas, "
        "separando hechos probados, evidencias favorables, evidencias contrarias y evidencias ausentes:"
    )

    t_rca = doc.add_table(rows=4, cols=5)
    t_rca.alignment = WD_TABLE_ALIGNMENT.CENTER
    rca_hdrs = ["Hipótesis", "A Favor (Probado)", "En Contra", "Evidencia Ausente", "Dictamen Pericial"]
    for j, htxt in enumerate(rca_hdrs):
        cell = t_rca.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    rca_data = [
        ("H1: Soporte Remoto (RMM)", 
         "Presencia de binario RMM en LAB-APP-04 y tarea 'System Health Check'.", 
         "No hay sesión RMM en el puesto origen primario LAB-WS-17 a la hora del acceso.", 
         "Falta log de firewall saliente previo a las 00:00 UTC.", 
         "PERSISTENCIA SECUNDARIA (No vector inicial)."),
        ("H2: Password Spraying", 
         "154 intentos fallidos en bmoreno; abuso posterior de cuenta 'ejercicio.backup'.", 
         "El spraying por sí solo no ejecuta binarios ni abre sesiones SMB sin credencial válida.", 
         "Logs de correlación VPN de geolocalización perimetral.", 
         "VECTOR COADYUVANTE (Facilitó escalada lateral)."),
        ("H3: Phishing / Correo (LAB-WS-17)", 
         "Sesión activa de Outlook; correlación temporal con correos maliciosos; proceso inicial en puesto de usuario.", 
         "No hay exploit directo en servidor de ficheros (ataque a FS-01 fue por SMB, no email directo).", 
         "Caché de adjuntos temporales extraída de Outlook.", 
         "HIPÓTESIS PRINCIPAL (PACIENTE CERO PROBADO).")
    ]

    for idx, (h_n, e_fav, e_con, e_aus, dictam) in enumerate(rca_data, start=1):
        c0 = t_rca.cell(idx, 0)
        c1 = t_rca.cell(idx, 1)
        c2 = t_rca.cell(idx, 2)
        c3 = t_rca.cell(idx, 3)
        c4 = t_rca.cell(idx, 4)
        c0.width = Inches(1.3)
        c1.width = Inches(1.6)
        c2.width = Inches(1.4)
        c3.width = Inches(1.2)
        c4.width = Inches(1.4)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (c0, c1, c2, c3, c4):
            set_cell_background(c, bg)
            set_cell_margins(c, 50, 50, 60, 60)
        c0.paragraphs[0].add_run(h_n).font.size = Pt(8)
        c0.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].add_run(e_fav).font.size = Pt(8)
        c2.paragraphs[0].add_run(e_con).font.size = Pt(8)
        c3.paragraphs[0].add_run(e_aus).font.size = Pt(8)
        c4.paragraphs[0].add_run(dictam).font.size = Pt(8)
        c4.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECCIÓN 3: CÓMO HA LLEGADO (RECONSTRUCCIÓN COMPLETA KILL CHAIN)
    # -------------------------------------------------------------
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(12)
    h3.paragraph_format.space_after = Pt(4)
    h3.add_run("3. ¿CÓMO HA LLEGADO? (RECONSTRUCCIÓN DE LA CYBER KILL CHAIN)").font.bold = True
    h3.runs[0].font.size = Pt(12.5)
    h3.runs[0].font.color.rgb = COLOR_PRIMARY

    tbl_kc = doc.add_table(rows=8, cols=4)
    tbl_kc.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs_kc = ["Fase MITRE ATT&CK", "Activo Afectado", "Técnica Utilizada", "Descripción Pericial del Evento"]
    for j, htxt in enumerate(hdrs_kc):
        cell = tbl_kc.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    kc_full = [
        ("1. Acceso Inicial", "LAB-WS-17 (Puesto Usuario)", "Spear-Phishing (T1566.001)", "Interacción con adjunto malicioso que desplegó el ejecutable inicial en memoria."),
        ("2. Robo de Credenciales", "LAB-WS-17", "OS Credential Dumping (T1003)", "Volcado de LSASS; robo de credenciales de la cuenta técnica 'ejercicio.backup'."),
        ("3. Movimiento Lateral", "Red Corporativa (LAN)", "SMB / Windows Admin Shares (T1021.002)", "Propagación lateral puerto 445 usando privilegios SeBackupPrivilege hacia LAB-APP-04 y LAB-FS-01."),
        ("4. Persistencia", "LAB-APP-04", "Scheduled Task & RMM (T1053 / T1219)", "Creación de tarea 'System Health Check' en C:\\ProgramData y software de soporte no validado."),
        ("5. Exfiltración Previa", "LAB-APP-04 -> Ext.", "Exfiltration Over C2 (T1048)", "Compresión de 18 GB mediante 7za.exe y envío por canal seguro a la IP 198.51.100.77."),
        ("6. Cifrado & Extorsión", "LAB-FS-01 (Fileserver)", "Data Encrypted for Impact (T1486)", "Renombrado de ficheros a extensión .locked y depósito de notas README_RECOVERY.txt."),
        ("7. Fraude Paralelo BEC", "Finanzas / Servidor Pagos", "Data Manipulation (T1565.001)", "Manipulación encubierta del IBAN de proveedores a las 00:51 UTC (usada como cortina de humo).")
    ]

    for idx, (f_m, a_a, t_u, d_f) in enumerate(kc_full, start=1):
        r0 = tbl_kc.cell(idx, 0)
        r1 = tbl_kc.cell(idx, 1)
        r2 = tbl_kc.cell(idx, 2)
        r3 = tbl_kc.cell(idx, 3)
        r0.width = Inches(1.7)
        r1.width = Inches(1.5)
        r2.width = Inches(1.6)
        r3.width = Inches(2.1)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (r0, r1, r2, r3):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        r0.paragraphs[0].add_run(f_m).font.size = Pt(8.5)
        r0.paragraphs[0].runs[0].font.bold = True
        r1.paragraphs[0].add_run(a_a).font.size = Pt(8.5)
        r2.paragraphs[0].add_run(t_u).font.size = Pt(8.5)
        r3.paragraphs[0].add_run(d_f).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECCIÓN 4: AUDITORÍA DE TRANSPARENCIA: EJECUTADAS vs PROPUESTAS
    # -------------------------------------------------------------
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(12)
    h4.paragraph_format.space_after = Pt(4)
    h4.add_run("4. AUDITORÍA DE TRANSPARENCIA: MEDIDAS EJECUTADAS vs. PROPUESTAS").font.bold = True
    h4.runs[0].font.size = Pt(12.5)
    h4.runs[0].font.color.rgb = COLOR_PRIMARY

    p4 = doc.add_paragraph()
    p4.paragraph_format.space_after = Pt(4)
    p4.add_run("Siguiendo la directriz expresa de la Dirección de TI de no dar por ejecutadas medidas que solo se propusieron, se certifica el estado real:")

    bullets_ejec = [
        ("Aislamiento Físico de LAB-WS-17", "Desconectado de red con memoria RAM preservada intacta para cadena de custodia forense."),
        ("Bloqueo Perimetral C2", "IP 198.51.100.77 bloqueada en drop en el cortafuegos; sockets cerrados (exfiltración detenida)."),
        ("Deshabilitación de Identidad y Sesiones", "Cuenta 'ejercicio.backup' deshabilitada en Active Directory; purga de sesiones SMB (net session /delete)."),
        ("Modo Solo Lectura en LAB-FS-01", "Recursos compartidos configurados en Read-Only (evita nuevos cifrados y permite consultar planos a Operaciones)."),
        ("Congelación Cautelar de Pagos", "Bloqueada la emisión de remesas bancarias en la pasarela; auditoría completa de pagos de las últimas 48 horas."),
        ("Neutralización en LAB-APP-04", "Eliminada la tarea 'System Health Check' y desinstalado el software RMM no autorizado.")
    ]
    for b_t, b_d in bullets_ejec:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(2)
        r_bt = p_b.add_run(f"EJECUTADO · {b_t}: ")
        r_bt.font.bold = True
        r_bt.font.size = Pt(9)
        r_bt.font.color.rgb = COLOR_EMERALD
        r_bd = p_b.add_run(b_d)
        r_bd.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    bullets_prop = [
        ("Restauración Definitiva de LAB-FS-01", "Validada en sandbox aislado (RTO 42 min); pendiente de transferencia final a producción."),
        ("Aprovisionamiento de Cuenta gMSA", "Configuración de svc-backup-clean$ para sustituir permanentemente la cuenta técnica tradicional."),
        ("Notificación Formal AEPD / INCIBE-CERT", "Dossier técnico preparado en plazo legal de 72 horas; pendiente de firma de DPD y Dirección General.")
    ]
    for b_t, b_d in bullets_prop:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(2)
        r_bt = p_b.add_run(f"PROPUESTO / EN CURSO · {b_t}: ")
        r_bt.font.bold = True
        r_bt.font.size = Pt(9)
        r_bt.font.color.rgb = COLOR_SECONDARY
        r_bd = p_b.add_run(b_d)
        r_bd.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECCIÓN 5: ¿QUÉ PODEMOS HACER? (INVESTIGACIÓN Y CREATIVIDAD PARA SAMPOL)
    # -------------------------------------------------------------
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(12)
    h5.paragraph_format.space_after = Pt(4)
    h5.add_run("5. ¿QUÉ PODEMOS HACER? (PROPUESTAS CREATIVAS Y DEFENSA ACTIVA PARA SAMPOL)").font.bold = True
    h5.runs[0].font.size = Pt(12.5)
    h5.runs[0].font.color.rgb = COLOR_PRIMARY

    p5 = doc.add_paragraph()
    p5.paragraph_format.space_after = Pt(6)
    p5.add_run(
        "Para transformar la seguridad de Grupo SAMPOL de un modelo reactivo tradicional a una arquitectura de resiliencia avanzada y defensa activa, "
        "el equipo NEXUS propone 6 vectores de innovación técnica de alto impacto:"
    )

    t_innov = doc.add_table(rows=7, cols=3)
    t_innov.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs_innov = ["Iniciativa Creativa / Innovación", "Descripción de la Solución Técnica", "Beneficio Diferencial para SAMPOL"]
    for j, htxt in enumerate(hdrs_innov):
        cell = t_innov.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    innov_data = [
        ("1. Carpetas Cebo con 'Canary Traps'", 
         "Carpetas ocultas (!00_Canary_Vault) con ficheros señuelo monitoreados por micro-driver a nivel de kernel.", 
         "Si un ransomware intenta cifrar el canario, se mata el proceso y se aísla la red en < 50 ms. Salva el 99.9% de los ficheros reales."),
        ("2. Honeytokens en Active Directory", 
         "Cuentas trampa señuelo (ej. admin-backup-sampol) con contraseñas accesibles y SPNs configurados.", 
         "Cualquier intento de Kerberoasting o autenticación dispara el bloqueo automático del host atacante sin falsos positivos."),
        ("3. Zero-Trust Banking (Regla de 4 Ojos)", 
         "Firma digital criptográfica obligatoria con hardware FIDO2 para modificaciones de IBAN o transferencias > 5.000 €.", 
         "Inmunidad total frente a fraudes de suplantación de identidad (BEC), llamadas de vishing y correos manipulados."),
        ("4. Microsegmentación Zero-Trust Endpoint", 
         "Reglas de firewall centralizado que prohíben toda comunicación directa entre puestos de usuario por SMB (445) y RDP (3389).", 
         "Si un usuario cae por phishing, el atacante no puede moverse lateralmente a otros equipos de la empresa."),
        ("5. Cuentas de Servicio gMSA", 
         "Sustitución de cuentas técnicas tradicionales por Group Managed Service Accounts en Active Directory.", 
         "Contraseñas de 128 caracteres rotadas automáticamente por el DC. Imposibilita la reutilización de hashes y tickets Kerberos."),
        ("6. Cyber Range & Gemelo Digital OT", 
         "Emulador virtualizado de los sistemas SCADA y PLCs de aeropuertos y plantas energéticas de SAMPOL.", 
         "Entrenamiento conjunto de los equipos de IT y Operaciones ante ciberataques reales sin riesgo para infraestructuras críticas.")
    ]

    for idx, (m_i, d_i, b_i) in enumerate(innov_data, start=1):
        c0 = t_innov.cell(idx, 0)
        c1 = t_innov.cell(idx, 1)
        c2 = t_innov.cell(idx, 2)
        c0.width = Inches(2.1)
        c1.width = Inches(2.6)
        c2.width = Inches(2.2)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        c0.paragraphs[0].add_run(m_i).font.size = Pt(8.5)
        c0.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].add_run(d_i).font.size = Pt(8.5)
        c2.paragraphs[0].add_run(b_i).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # FIRMAS PERICIALES Y CIERRE
    # -------------------------------------------------------------
    sign_tbl = doc.add_table(rows=1, cols=2)
    sign_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    sc0 = sign_tbl.cell(0, 0)
    sc1 = sign_tbl.cell(0, 1)
    set_cell_background(sc0, "F8F9FA")
    set_cell_background(sc1, "F8F9FA")
    set_cell_margins(sc0, 100, 100, 120, 120)
    set_cell_margins(sc1, 100, 100, 120, 120)

    sc0.paragraphs[0].add_run("EQUIPO FORENSE & CSIRT:\n\n").font.size = Pt(9)
    sc0.paragraphs[0].add_run("Equipo 1 (NEXUS)\n").font.bold = True
    sc0.paragraphs[0].add_run("Especialistas en Análisis Forense, DFIR y SOAR\n").font.size = Pt(8.5)
    sc0.paragraphs[0].add_run("Evidencias custodiadas bajo cadena forense digital con hash SHA-256").font.size = Pt(8).italic = True

    sc1.paragraphs[0].add_run("DIRECCIÓN DE TECNOLOGÍA:\n\n").font.size = Pt(9)
    sc1.paragraphs[0].add_run("Dirección de TI (dirti@sampol.com)\n").font.bold = True
    sc1.paragraphs[0].add_run("Recepción y Aprobación de Medidas de Remediación\n").font.size = Pt(8.5)
    sc1.paragraphs[0].add_run("Grupo Sampol · Sede Central Parc Bit").font.size = Pt(8).italic = True

    out_path = r"C:\Users\osesj\Documents\Nexus-Hackathon\INFORME_FORENSE_KILL_CHAIN.docx"
    doc.save(out_path)
    print(f"Informe forense consolidado generado con éxito en: {out_path}")

if __name__ == "__main__":
    generate_consolidated_forensic_report()
