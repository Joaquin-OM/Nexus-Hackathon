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

def create_nis2_document():
    doc = docx.Document()

    # Márgenes estándar
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    COLOR_PRIMARY = RGBColor(14, 43, 92)    # Azul Marino Institucional (#0E2B5C)
    COLOR_DANGER = RGBColor(192, 0, 0)      # Rojo Alerta (#C00000)
    COLOR_SECONDARY = RGBColor(0, 102, 204) # Azul Operativo (#0066CC)
    COLOR_DARK = RGBColor(33, 37, 41)       # Gris Oscuro Texto
    COLOR_MUTED = RGBColor(108, 117, 125)   # Gris Secundario
    COLOR_EMERALD = RGBColor(16, 149, 104)  # Verde Contención

    # -------------------------------------------------------------
    # ENCABEZADO OFICIAL / BANNER INSTITUCIONAL
    # -------------------------------------------------------------
    header_tbl = doc.add_table(rows=1, cols=2)
    header_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_left = header_tbl.cell(0, 0)
    c_right = header_tbl.cell(0, 1)
    c_left.width = Inches(4.5)
    c_right.width = Inches(2.4)
    
    p_hl = c_left.paragraphs[0]
    p_hl.paragraph_format.space_before = Pt(0)
    p_hl.paragraph_format.space_after = Pt(2)
    r1 = p_hl.add_run("GRUPO SAMPOL · DIRECCIÓN DE TI Y CIBERSEGURIDAD\n")
    r1.font.size = Pt(9.5)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    r2 = p_hl.add_run("SOC CENTRAL & EQUIPO DE RESPUESTA A INCIDENTES (CSIRT)")
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = COLOR_MUTED

    p_hr = c_right.paragraphs[0]
    p_hr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hr.paragraph_format.space_before = Pt(0)
    p_hr.paragraph_format.space_after = Pt(2)
    r3 = p_hr.add_run("REF: INC-NIS2-20261103-001\n")
    r3.font.size = Pt(10)
    r3.font.bold = True
    r3.font.color.rgb = COLOR_DANGER
    r4 = p_hr.add_run("PLAZO LEGAL: ALERTA TEMPRANA < 24H")
    r4.font.size = Pt(8.5)
    r4.font.bold = True
    r4.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # TÍTULO DEL DOCUMENTO
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(6)
    title_p.paragraph_format.space_after = Pt(4)
    r_cat = title_p.add_run("NOTIFICACIÓN FORMAL DE INCIDENTE SIGNIFICATIVO DE CIBERSEGURIDAD\n")
    r_cat.font.size = Pt(11)
    r_cat.font.bold = True
    r_cat.font.color.rgb = COLOR_DANGER

    r_title = title_p.add_run("ALERTA TEMPRANA Y PRE-NOTIFICACIÓN OFICIAL (ART. 23.3.a DIRECTIVA NIS2)")
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(4)
    sub_p.paragraph_format.space_after = Pt(14)
    r_sub = sub_p.add_run("Comunicación oficial dirigida al CSIRT Nacional de Referencia (INCIBE-CERT / CCN-CERT) en cumplimiento del régimen de notificación de incidentes para entidades esenciales y críticas.\n")
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_MUTED

    r_meta = sub_p.add_run("Entidad Notificante: Grupo Sampol (Sampol Ingeniería y Obras S.A.) | Clasificación: CONFIDENCIAL / TLP:AMBER | Fecha: 03/11/2026 19:15 CET")
    r_meta.font.size = Pt(9.5)
    r_meta.font.bold = True
    r_meta.font.color.rgb = COLOR_DARK

    # -------------------------------------------------------------
    # CUADRO DE RESUMEN EJECUTIVO / METADATOS REGULATORIOS
    # -------------------------------------------------------------
    box_tbl = doc.add_table(rows=1, cols=1)
    box_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    b_cell = box_tbl.cell(0, 0)
    b_cell.width = Inches(6.9)
    set_cell_background(b_cell, "FFF5F5")
    set_cell_margins(b_cell, top=140, bottom=140, left=180, right=180)

    bp = b_cell.paragraphs[0]
    bp.paragraph_format.space_before = Pt(0)
    bp.paragraph_format.space_after = Pt(2)
    b_r1 = bp.add_run("🚨 DECLARACIÓN DE ALERTA TEMPRANA (EARLY WARNING) - MARCO NIS2\n")
    b_r1.font.bold = True
    b_r1.font.size = Pt(11)
    b_r1.font.color.rgb = COLOR_DANGER

    b_r2 = bp.add_run(
        "El Grupo Sampol, en su condición de operador esencial en infraestructuras críticas (Energía, Aeropuertos, "
        "Servicios de Ingeniería e Instalaciones Estratégicas), emite la presente Pre-Notificación de Incidente Significativo "
        "en estricta conformidad con el Artículo 23, apartado 3, letra a) de la Directiva (UE) 2022/2555 (NIS2).\n\n"
        "• Hora de Confirmación del Incidente: 03/11/2026 - 10:18 CET (09:18 UTC)\n"
        "• Hora de Emisión de la Pre-Notificación: 03/11/2026 - 19:15 CET (Tiempo transcurrido: 8h 57min; Margen legal: < 24h)\n"
        "• Estado de Contención: CONTENIDO Y AISLADO mediante orquestación SOAR automatizada NEXUS 2.0 (Directriz 1 de TI).\n"
        "• Servicios Esenciales Afectados: 0 servicios críticos parados. Red de Control Industrial (OT/SCADA) 100% segregada e indemne."
    )
    b_r2.font.size = Pt(9.5)
    b_r2.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECCIÓN 1: DATOS GENERALES DE LA ENTIDAD Y CANAL DE ENLACE
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("1. DATOS IDENTIFICATIVOS DE LA ENTIDAD Y PUNTO DE CONTACTO CSIRT")
    r_h1.font.size = Pt(13)
    r_h1.font.bold = True
    r_h1.font.color.rgb = COLOR_PRIMARY

    tbl_id = doc.add_table(rows=6, cols=2)
    tbl_id.alignment = WD_TABLE_ALIGNMENT.CENTER
    fields = [
        ("Razón Social y NIF", "SAMPOL INGENIERÍA Y OBRAS, S.A. · NIF: A-07014278"),
        ("Sede Central", "Parc Bit, Calle Son Espanyol s/n, 07121 Palma de Mallorca, Illes Balears"),
        ("Sector y Subsector NIS2", "Sector Energía, Subsector Electricidad / Operador Crítico y Servicios de Red Digital"),
        ("Clasificación de Entidad", "Entidad Esencial (Essential Entity - NIS2 Annex I / Ley PIC Infraestructuras Críticas)"),
        ("Puntos de Contacto Operativo (24/7)", "Director de TI: dirti@sampol.com | SOC NEXUS: soc@sampol.com / +34 971 17 00 00"),
        ("Autoridad de Notificación Receptora", "INCIBE-CERT (Nivel Nacional Privado/Empresarial) con copia informativa a CCN-CERT")
    ]
    for idx, (lbl, val) in enumerate(fields):
        c0 = tbl_id.cell(idx, 0)
        c1 = tbl_id.cell(idx, 1)
        c0.width = Inches(2.3)
        c1.width = Inches(4.6)
        set_cell_background(c0, "F8F9FA")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r_lbl = p0.add_run(lbl)
        r_lbl.font.size = Pt(9)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = COLOR_PRIMARY
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r_val = p1.add_run(val)
        r_val.font.size = Pt(9)
        r_val.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 2: DESCRIPCIÓN DE LOS HECHOS Y VECTOR DE ATAQUE
    # -------------------------------------------------------------
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)
    r_h2 = h2.add_run("2. NATURALEZA Y DESCRIPCIÓN TÉCNICA DEL INCIDENTE SIGNIFICATIVO")
    r_h2.font.size = Pt(13)
    r_h2.font.bold = True
    r_h2.font.color.rgb = COLOR_PRIMARY

    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.space_after = Pt(6)
    p_desc.add_run(
        "A lo largo de la jornada operativa del 3 de noviembre de 2026, los sensores perimetrales y plataformas EDR/SIEM "
        "de Grupo Sampol registraron una campaña maliciosa coordinada y multi-etapa, caracterizada por ataques dirigidos de "
        "ingeniería social, robo de credenciales corporativas, escalada de privilegios a administrador local y ejecución "
        "de rutinas de modificación masiva de ficheros con precursores de ransomware.\n\n"
        "El vector de ataque combinó tácticas avanzadas contra la identidad corporativa y despliegue de agentes en estaciones de trabajo:"
    )

    phases = [
        ("Fase 1: Ataque Distribuido de Fuerza Bruta y Pulverización (Password Spray)", 
         "Ataque automatizado desde múltiples IPs anónimas contra buzones corporativos (patrón detectado en cuentas *moreno y *gonzalez), "
         "con 154 intentos fallidos registrados en bmoreno@sampol.com y eventos análogos."),
        ("Fase 2: Intrusión Inicial y Compromiso de Credenciales (ACCOUNT-LAB)", 
         "Compromiso exitoso de la cuenta jmoreno@sampol.com (Alerta AL-20261030-0040) y posterior intrusión en bmoreno@sampol.com "
         "(Alerta AL-20261030-0045), con inicio de sesión sospechoso no reconocido por los titulares legítimos."),
        ("Fase 3: Escalada Local y Persistencia en Host (ADMIN-LAB / APT-LAB)", 
         "Escalada de privilegios a Administrador local detectada en el endpoint asignado a amoreno@sampol.com (Alerta AL-20261030-0041), "
         "acompañada de intentos de evasión de defensas locales y establecimiento de tareas programadas."),
        ("Fase 4: Comunicación con Comando y Control (C2-LAB)", 
         "Resolución DNS y tráfico anómalo cifrado hacia el dominio sync-gateway.invalid y endpoints externos clasificados como C2."),
        ("Fase 5: Modificación Masiva de Datos y Precursor de Cifrado (MODIFY-LAB)", 
         "Detección de alteración de 195 ficheros técnicos en repositorios de proyectos corporativos (cmoreno@sampol.com, Alerta AL-20261030-0043), "
         "bloqueada en tiempo récord por el motor SOAR antes de la ejecución del payloads de extorsión/wiper final.")
    ]

    for title_f, desc_f in phases:
        pf = doc.add_paragraph(style='List Bullet')
        pf.paragraph_format.space_after = Pt(3)
        r_tf = pf.add_run(f"{title_f}: ")
        r_tf.font.bold = True
        r_tf.font.size = Pt(9.5)
        r_tf.font.color.rgb = COLOR_PRIMARY
        r_df = pf.add_run(desc_f)
        r_df.font.size = Pt(9)
        r_df.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 3: IMPACTO ESTIMADO Y EVALUACIÓN DE SEVERIDAD
    # -------------------------------------------------------------
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(4)
    r_h3 = h3.add_run("3. EVALUACIÓN PRELIMINAR DE IMPACTO Y CONTINUIDAD DE OPERACIONES")
    r_h3.font.size = Pt(13)
    r_h3.font.bold = True
    r_h3.font.color.rgb = COLOR_PRIMARY

    tbl_imp = doc.add_table(rows=5, cols=3)
    tbl_imp.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_imp = ["Criterio de Evaluación NIS2", "Resultado Preliminar", "Justificación y Evidencia Forense"]
    for j, htxt in enumerate(headers_imp):
        cell = tbl_imp.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    imp_data = [
        ("Disponibilidad de Servicios Críticos", "0 Horas Perdidas (0 €)", 
         "Los sistemas de cogeneración, distribución eléctrica y redes aeroportuarias no sufrieron ninguna parada."),
        ("Integridad de la Información", "195 archivos en aislamiento", 
         "Ficheros alterados en SRV-PROJ-01 identificados y puestos en cuarentena. Restauración programada desde copias inmutables."),
        ("Confidencialidad de Datos", "En Análisis Forense", 
         "5 cuentas de usuario bajo sospecha de acceso ilegítimo. Sin indicios de exfiltración masiva exterior confirmada."),
        ("Impacto Transfronterizo (UE)", "No Detectado", 
         "El incidente se circunscribe exclusivamente a la infraestructura IT en sedes nacionales (España).")
    ]

    for idx, (c1, c2, c3) in enumerate(imp_data, start=1):
        r0 = tbl_imp.cell(idx, 0)
        r1 = tbl_imp.cell(idx, 1)
        r2 = tbl_imp.cell(idx, 2)
        r0.width = Inches(2.2)
        r1.width = Inches(1.8)
        r2.width = Inches(2.9)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (r0, r1, r2):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        
        p = r0.paragraphs[0]
        r = p.add_run(c1)
        r.font.bold = True
        r.font.size = Pt(8.5)
        
        p = r1.paragraphs[0]
        r = p.add_run(c2)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = COLOR_EMERALD if "0 Horas" in c2 or "No" in c2 else COLOR_DANGER

        p = r2.paragraphs[0]
        r = p.add_run(c3)
        r.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 4: MEDIDAS DE CONTENCIÓN ADOPTADAS (SOAR NEXUS 2.0)
    # -------------------------------------------------------------
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(4)
    r_h4 = h4.add_run("4. MEDIDAS DE MITIGACIÓN Y CONTENCIÓN INMEDIATA ADOPTADAS")
    r_h4.font.size = Pt(13)
    r_h4.font.bold = True
    r_h4.font.color.rgb = COLOR_PRIMARY

    p_mit = doc.add_paragraph()
    p_mit.paragraph_format.space_after = Pt(6)
    p_mit.add_run(
        "En cumplimiento de las instrucciones de la Dirección de TI de Grupo Sampol (Directriz 1 - Automatización de bloqueos) "
        "y aplicando los playbooks automáticos de la plataforma NEXUS 2.0, se adoptaron de forma autónoma y sub-segundo las siguientes medidas:"
    )

    soar_measures = [
        ("Aislamiento de Cuentas Comprometidas", 
         "Bloqueo y deshabilitación inmediata en Microsoft Entra ID / Active Directory de 14 identidades comprometidas "
         "(incluyendo jmoreno, amoreno, cmoreno, bmoreno, mgonzalez, ngonzalez, entre otros). Acciones registradas en tabla SOAR con trazabilidad completa."),
        ("Revocación de Sesiones y Tokens OAuth", 
         "Invalidación forzada de refresh tokens y cierre de sesiones activas en navegadores y aplicaciones móviles para impedir persistencia."),
        ("Contención Preventiva frente a Falsos Positivos", 
         "Aplicación estricta de Whitelist de Activos Críticos para proteger infraestructura industrial, PLCs, subestaciones y buzones estratégicos."),
        ("Bloqueo de Infraestructura Hostil Perimetral", 
         "Inyección de reglas de denegación perimetral para el dominio sync-gateway.invalid y las direcciones IP identificadas en los vectores de ataque."),
        ("Preservación de Evidencias Forenses", 
         "Congelación de volcados de memoria, logs de eventos de seguridad (syslog / Graph API) y firmas de auditoría forense para disposición judicial.")
    ]

    for sm_t, sm_d in soar_measures:
        p_sm = doc.add_paragraph(style='List Bullet')
        p_sm.paragraph_format.space_after = Pt(3)
        r_s1 = p_sm.add_run(f"{sm_t}: ")
        r_s1.font.bold = True
        r_s1.font.size = Pt(9.5)
        r_s1.font.color.rgb = COLOR_PRIMARY
        r_s2 = p_sm.add_run(sm_d)
        r_s2.font.size = Pt(9)
        r_s2.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 5: INDICADORES TÉCNICOS DE COMPROMISO (IoCs)
    # -------------------------------------------------------------
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(4)
    r_h5 = h5.add_run("5. INDICADORES DE COMPROMISO TÉCNICOS (IoCs)")
    r_h5.font.size = Pt(13)
    r_h5.font.bold = True
    r_h5.font.color.rgb = COLOR_PRIMARY

    tbl_ioc = doc.add_table(rows=6, cols=3)
    tbl_ioc.alignment = WD_TABLE_ALIGNMENT.CENTER
    ioc_hdrs = ["Tipo de Indicador", "Valor / Firma Identificada", "Contexto Operativo / Detección"]
    for j, htxt in enumerate(ioc_hdrs):
        cell = tbl_ioc.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    ioc_list = [
        ("C2 Host / Dominio", "sync-gateway.invalid", "Canal de exfiltración y balizamiento (C2-LAB)"),
        ("Hash SHA-256 (Malware)", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "Artefacto de inyección en procesos de usuario (MALWARE-LAB)"),
        ("Vector Identidad", "bmoreno@sampol.com / cmoreno@sampol.com", "Cuentas objetivo en campañas de spray y alteración de proyectos"),
        ("Proceso Sospechoso", "powershell.exe -enc / wmic shadowcopy delete", "Intento de destrucción de instantáneas de volumen mitigado"),
        ("Red Perimetral", "185.220.101.5 / 194.26.29.112", "Nodos de procedencia de intentos de password spraying masivo")
    ]

    for idx, (t1, t2, t3) in enumerate(ioc_list, start=1):
        r0 = tbl_ioc.cell(idx, 0)
        r1 = tbl_ioc.cell(idx, 1)
        r2 = tbl_ioc.cell(idx, 2)
        r0.width = Inches(1.8)
        r1.width = Inches(2.7)
        r2.width = Inches(2.4)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (r0, r1, r2):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        
        p = r0.paragraphs[0]
        r = p.add_run(t1)
        r.font.bold = True
        r.font.size = Pt(8.5)
        
        p = r1.paragraphs[0]
        r = p.add_run(t2)
        r.font.size = Pt(8)
        r.font.color.rgb = COLOR_DARK
        
        p = r2.paragraphs[0]
        r = p.add_run(t3)
        r.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 6: PLAN DE ACCIÓN Y CALENDARIO DE NOTIFICACIONES NIS2
    # -------------------------------------------------------------
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(14)
    h6.paragraph_format.space_after = Pt(4)
    r_h6 = h6.add_run("6. PLAN DE ACCIÓN Y CALENDARIO DE NOTIFICACIONES NIS2")
    r_h6.font.size = Pt(13)
    r_h6.font.bold = True
    r_h6.font.color.rgb = COLOR_PRIMARY

    steps = [
        ("Hito 1: Alerta Temprana (Early Warning - 24h)", "03/11/2026 19:15 CET", 
         "CUMPLIDO con la emisión y registro de esta pre-notificación oficial ante INCIBE-CERT."),
        ("Hito 2: Notificación Detallada del Incidente (72h)", "06/11/2026 10:00 CET", 
         "Actualización integral de la evaluación de impacto, confirmación de indicadores de compromiso definitivos y gravedad según métricas NIS2."),
        ("Hito 3: Informe Final de Cierre (1 Mes)", "03/12/2026", 
         "Documento formal con análisis de causa raíz (RCA), medidas estructurales adoptadas, lecciones aprendidas y plan de mejora continua.")
    ]

    for h_name, h_date, h_desc in steps:
        p_st = doc.add_paragraph(style='List Bullet')
        p_st.paragraph_format.space_after = Pt(4)
        r_s1 = p_st.add_run(f"{h_name} [Fecha prevista: {h_date}]: ")
        r_s1.font.bold = True
        r_s1.font.size = Pt(9.5)
        r_s1.font.color.rgb = COLOR_PRIMARY
        r_s2 = p_st.add_run(h_desc)
        r_s2.font.size = Pt(9)
        r_s2.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # FIRMA Y CERTIFICACIÓN OFICIAL
    # -------------------------------------------------------------
    sign_tbl = doc.add_table(rows=1, cols=2)
    sign_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    sc0 = sign_tbl.cell(0, 0)
    sc1 = sign_tbl.cell(0, 1)
    sc0.width = Inches(3.4)
    sc1.width = Inches(3.5)
    set_cell_background(sc0, "F8F9FA")
    set_cell_background(sc1, "F8F9FA")
    set_cell_margins(sc0, 100, 100, 120, 120)
    set_cell_margins(sc1, 100, 100, 120, 120)

    p_s0 = sc0.paragraphs[0]
    p_s0.paragraph_format.space_after = Pt(2)
    p_s0.add_run("POR LA DIRECCIÓN DE CIBERSEGURIDAD:\n\n").font.size = Pt(9)
    p_s0.add_run("Equipo 1 (NEXUS)\n").font.bold = True
    p_s0.add_run("CSIRT & Respuesta a Incidentes · Grupo Sampol\n").font.size = Pt(8.5)
    p_s0.add_run("Certificación Hash SHA-256 de Registro Activo").font.size = Pt(8).italic = True

    p_s1 = sc1.paragraphs[0]
    p_s1.paragraph_format.space_after = Pt(2)
    p_s1.add_run("POR LA DIRECCIÓN DE TECNOLOGÍA (TI):\n\n").font.size = Pt(9)
    p_s1.add_run("Dirección de TI (dirti@sampol.com)\n").font.bold = True
    p_s1.add_run("Comité de Seguridad y Cumplimiento Normativo\n").font.size = Pt(8.5)
    p_s1.add_run("Conformidad Art. 23 Directiva (UE) 2022/2555").font.size = Pt(8).italic = True

    out_path = r"C:\Users\osesj\Documents\Nexus-Hackathon\PRENOTIFICACION_INCIDENTE_NIS2_INCIBE_CERT.docx"
    doc.save(out_path)
    print(f"Documento generado exitosamente en: {out_path}")

if __name__ == "__main__":
    create_nis2_document()
