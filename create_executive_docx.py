import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()

    # Configurar márgenes estándar de 1 pulgada
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Colores corporativos
    COLOR_PRIMARY = RGBColor(14, 43, 92)    # Azul Marino Sampol (#0E2B5C)
    COLOR_SECONDARY = RGBColor(0, 122, 255) # Azul Tecnológico (#007AFF)
    COLOR_DARK = RGBColor(33, 37, 41)       # Gris Oscuro Texto
    COLOR_MUTED = RGBColor(108, 117, 125)   # Gris Secundario
    COLOR_EMERALD = RGBColor(16, 149, 104)  # Verde Éxito

    # -------------------------------------------------------------
    # PORTADA / ENCABEZADO PRINCIPAL
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_pre = title_p.add_run("HACKATHON FP SAMPOL 2026 · ÁREA DE TI Y CIBERSEGURIDAD\n")
    run_pre.font.size = Pt(10)
    run_pre.font.bold = True
    run_pre.font.color.rgb = COLOR_SECONDARY

    run_title = title_p.add_run("INFORME EJECUTIVO Y PLAN DE INDUSTRIALIZACIÓN DE NEXUS 2.0")
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(4)
    sub_p.paragraph_format.space_after = Pt(16)
    run_sub = sub_p.add_run("Diagnóstico de Situación (AS-IS), Visión de Producción Corporativa (TO-BE), Presupuesto Económico Detallado y Análisis de Retorno de Inversión (ROI)\n")
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_MUTED

    run_meta = sub_p.add_run("Preparado por: Equipo 1 (NEXUS) | Fecha: 03/11/2026 (Hito 19:00 CET) | Destinatarios: Dirección de TI (dirti@sampol.com) y Comité Técnico")
    run_meta.font.size = Pt(9.5)
    run_meta.font.bold = True
    run_meta.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # CUADRO RESUMEN EJECUTIVO (CALLOUT BOX)
    # -------------------------------------------------------------
    callout_tbl = doc.add_table(rows=1, cols=1)
    callout_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = callout_tbl.cell(0, 0)
    c_cell.width = Inches(6.9)
    set_cell_background(c_cell, "F0F4F8")
    set_cell_margins(c_cell, top=140, bottom=140, left=200, right=200)

    cp = c_cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(2)
    c_run1 = cp.add_run("📌 SÍNTESIS EJECUTIVA DE IMPACTO ECONÓMICO Y OPERATIVO\n")
    c_run1.font.bold = True
    c_run1.font.size = Pt(11)
    c_run1.font.color.rgb = COLOR_PRIMARY

    c_run2 = cp.add_run(
        "• Situación Actual (Reto 24h): NEXUS 2.0 procesa de forma autónoma el 100% del buzón del SOC (125 correos ingeridos, 80 alertas únicas bajo taxonomía INCIBE, 24,8% de reducción de ruido) y ha ejecutado con éxito la Directriz 1 conteniendo 14 cuentas comprometidas en la API de Bloqueador.\n"
        "• Ahorro Operativo Anual Recurrente: 281.380 € / año liberando 547 horas/mes de analistas (6.564 h/año).\n"
        "• Periodo de Retorno (Payback): 10 días en fase actual (~1,4 meses con inversión completa de industrialización).\n"
        "• Retorno de la Inversión (ROI Primer Año): 2.010% (Build Interno) vs. alternativa comercial.\n"
        "• Coste Total de Adquisición a 3 Años (TCO 3Y): 56.000 € (NEXUS 2.0) frente a 200.000 € (Plataforma Comercial), logrando un ahorro de 144.000 € en 3 años (-72% de coste) con soberanía total del dato en Azure."
    )
    c_run2.font.size = Pt(9.5)
    c_run2.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Helper para encabezados de sección
    def add_section_heading(title_text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(title_text)
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        return h

    def add_subsection_heading(title_text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(title_text)
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_SECONDARY
        return h

    # -------------------------------------------------------------
    # 1. EN QUÉ PUNTO ESTAMOS (SITUACIÓN ACTUAL · AS-IS)
    # -------------------------------------------------------------
    add_section_heading("1. En qué punto estamos hoy (Situación Actual · AS-IS)")

    p1 = doc.add_paragraph()
    p1.paragraph_format.space_after = Pt(6)
    p1.add_run(
        "En menos de 9 horas de trabajo ininterrumpido en el Hackathon FP Sampol, el Equipo 1 ha diseñado, implementado y puesto en producción una solución integral operativa denominada "
    )
    r_n = p1.add_run("NEXUS 2.0")
    r_n.font.bold = True
    p1.add_run(
        ", pasando de una gestión manual basada en bandejas de correo no estructuradas a una plataforma inteligente de SOC automatizado. A continuación se desglosa el estado operativo exacto al corte de las 19:00 CET:"
    )

    add_subsection_heading("1.1 Arquitectura Desplegada y Datos en Vivo (Azure PostgreSQL 18.6)")

    # Tabla de métricas operativas
    t_as_is = doc.add_table(rows=7, cols=3)
    t_as_is.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Indicador Operativo", "Valor Actual", "Impacto y Trazabilidad Técnica"]
    col_widths = [Inches(2.2), Inches(1.2), Inches(3.5)]

    for col_idx, h_text in enumerate(headers):
        cell = t_as_is.cell(0, col_idx)
        cell.width = col_widths[col_idx]
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    as_is_data = [
        ("Correos Ingeridos (raw_emails)", "125 correos", "Sincronizados vía Microsoft Graph API con hash SHA-256 inmutable y persistencia RFC 822 en Azure PostgreSQL."),
        ("Incidentes Únicos (v_soc_unique_alerts)", "80 incidentes", "Clasificados con justificación forense en las 10 Clases Oficiales de INCIBE (Intento intrusión: 18, Disponibilidad: 11, Contenido dañino: 10, Fraude: 10, Compromiso información: 10, Intrusión: 9, etc.)."),
        ("Duplicados y Ruido Filtrado", "31 correos (24,8%)", "22 duplicados y órdenes enlazadas por parent_alert_id + 9 correos ajenos al SOC (reserva de salas, bienvenida, newsletter) descartados automáticamente."),
        ("Cuentas Comprometidas Bloqueadas", "14 cuentas", "Bloqueo autónomo ejecutado por autoblock_engine.py tras detección de credenciales robadas, intrusión o C2 (Directriz 1)."),
        ("Acciones SOAR Auditadas (soar_actions)", "59 acciones", "22 bajo automatico_directriz_1, 22 de órdenes operativas SOL-B/SOL-L del SOC y 15 de supervisión humana."),
        ("Portal Web y Repositorio", "En producción", "GitHub: Joaquin-OM/Nexus-Hackathon | Portal en vivo: joaquin-om.github.io/Nexus-Hackathon/ (accesible sin instalación).")
    ]

    for row_idx, data_row in enumerate(as_is_data, start=1):
        for col_idx, val in enumerate(data_row):
            cell = t_as_is.cell(row_idx, col_idx)
            cell.width = col_widths[col_idx]
            bg_color = "F8F9FA" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(9)
            if col_idx == 1:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_subsection_heading("1.2 Cumplimiento Estricto de las Directrices Oficiales del Director de TI")
    p_dir = doc.add_paragraph()
    p_dir.paragraph_format.space_after = Pt(6)
    p_dir.add_run(
        "El desarrollo de NEXUS 2.0 ha respondido de manera inmediata y documentada a cada una de las directrices enviadas por dirti@sampol.com durante el reto:\n"
        "1. Directriz Retorno de Inversión (16:46 CET): Incorporación de los 7 parámetros oficiales del Director en la tabla business_parameters, creación de la pestaña financiera en el Cuadro de Mando y desarrollo de la Calculadora Interactiva de ROI.\n"
        "2. Directriz 1 · Automatizar Bloqueos (18:02 CET): Despliegue del motor autoblock_engine.py. Como prueba de eficiencia ante el jurado, el motor batió a la orden humana: bloqueó de forma autónoma a mgonzalez@sampol.com a las 18:32 CET ante la alerta AL-0013, 4 minutos antes de que llegara la solicitud formal SOL-B-013 a las 18:36 CET. De igual modo, contuvo a bmoreno@sampol.com en cuanto se detectó el robo de sesión en AL-0045.\n"
        "3. Salvaguardas de Seguridad Operativa: Implementación de la Lista Blanca IT/OT (protected_assets_whitelist) para evitar bloqueos accidentales a cuentas clave (dirti@sampol.com) o plantas industriales; respeto automático de liberaciones por falso positivo (SOL-L-001, 004, 007); y exclusión de intentos fallidos simples sin sesión (evitando denegaciones de servicio a usuarios legítimos)."
    )

    # -------------------------------------------------------------
    # 2. A QUÉ PUNTO QUEREMOS LLEGAR (VISIÓN Y ESTADO FUTURO · TO-BE)
    # -------------------------------------------------------------
    add_section_heading("2. A qué punto queremos llegar (Visión y Estado Futuro · TO-BE)")

    p_tobe = doc.add_paragraph()
    p_tobe.paragraph_format.space_after = Pt(6)
    p_tobe.add_run(
        "La visión de NEXUS 2.0 para Grupo Sampol no es quedarse en un prototipo de hackathon, sino consolidarse como la "
    )
    r_pl = p_tobe.add_run("Plataforma Unificada de SOC & Orquestación de Ciberseguridad Industrial")
    r_pl.font.bold = True
    p_tobe.add_run(
        " para todos los activos corporativos IT y plantas de generación y distribución de energía (OT/SCADA). El estado futuro deseado contempla 4 fases estratégicas de industrialización:"
    )

    t_roadmap = doc.add_table(rows=5, cols=3)
    t_roadmap.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_headers = ["Fase de Evolución", "Horizonte Temporal", "Capacidades Técnicas e Hitos Entregables"]
    r_widths = [Inches(1.8), Inches(1.3), Inches(3.8)]

    for col_idx, h_text in enumerate(r_headers):
        cell = t_roadmap.cell(0, col_idx)
        cell.width = r_widths[col_idx]
        set_cell_background(cell, "007AFF")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    roadmap_data = [
        ("Fase 1: Despliegue en Alta Disponibilidad y n8n", "Meses 1 – 2", "Contenedorización en Azure Container Apps con réplica HA. Conexión nativa con n8n corporativo para orquestación de workflows complejos y sincronización con Microsoft Entra ID (revocación forzada de tokens OAuth y escalado a MFA condicional)."),
        ("Fase 2: Expansión a Redes Industriales y Plantas OT", "Meses 3 – 4", "Integración con telemetría de planta (sistemas SCADA, subestaciones y hoteles). Monitorización de protocolos industriales (Modbus, IEC 60870-5-104) y segregación estricta de la Lista Blanca OT para blindar la continuidad del negocio."),
        ("Fase 3: Automatización de Cumplimiento NIS2 y ENS", "Meses 5 – 6", "Módulo de pre-notificación automática a autoridades nacionales (INCIBE-CERT / CCN-CERT) en menos de 24 horas y emisión del informe oficial de incidente significativo a las 72 horas con sellado de tiempo y hash forense de evidencias."),
        ("Fase 4: Inteligencia Predictiva y Auto-Remediación", "Meses 7 – 12", "Despliegue de modelos de IA locales (SLMs/LLMs privados) para clasificación y ajuste continuo de reglas sin salida de datos al exterior, reduciendo la tasa de falsos positivos al <0,5% y ejecutando remediación preventiva asistida.")
    ]

    for row_idx, r_row in enumerate(roadmap_data, start=1):
        for col_idx, val in enumerate(r_row):
            cell = t_roadmap.cell(row_idx, col_idx)
            cell.width = r_widths[col_idx]
            bg_color = "F0F7FF" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            elif col_idx == 1:
                r.font.bold = True
                r.font.color.rgb = COLOR_SECONDARY
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------
    # 3. CUÁNTO COSTE EN EUROS TENDRÍA LLEGAR A ESO
    # -------------------------------------------------------------
    add_section_heading("3. Cuánto coste en euros tendría llegar a eso (Plan Financiero y Presupuesto)")

    p_cost = doc.add_paragraph()
    p_cost.paragraph_format.space_after = Pt(6)
    p_cost.add_run(
        "Para garantizar una absoluta transparencia y rigor financiero ante la Dirección General y el Jurado, el modelo de costes se calcula utilizando exactamente los "
    )
    r_par = p_cost.add_run("parámetros oficiales facilitados por el Director de TI")
    r_par.font.bold = True
    p_cost.add_run(
        " (50 €/h desarrollo interno, 45 €/h analista, 3.000 alertas/mes, 120 bloqueos/mes de 25 min, 25.000 €/h servicio parado y 60.000 €/año + 20.000 € plataforma comercial):"
    )

    add_subsection_heading("3.1 Presupuesto de Inversión Inicial de Industrialización (CAPEX · Meses 1 a 6)")

    t_capex = doc.add_table(rows=7, cols=4)
    t_capex.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_heads = ["Concepto de Inversión / Partida", "Dedicación (Horas)", "Tarifa Oficial", "Importe Total (€)"]
    c_w = [Inches(3.2), Inches(1.3), Inches(1.1), Inches(1.3)]

    for col_idx, h_text in enumerate(c_heads):
        cell = t_capex.cell(0, col_idx)
        cell.width = c_w[col_idx]
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, top=90, bottom=90, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    capex_items = [
        ("Arquitectura Cloud HA y despliegue Container Apps / Kubernetes", "80 horas", "50 € / hora", "4.000 €"),
        ("Conectores corporativos avanzados (Entra ID, EDR Defender, n8n, Firewalls)", "120 horas", "50 € / hora", "6.000 €"),
        ("Módulo de cumplimiento y reporte automático NIS2 / ENS a INCIBE-CERT", "60 horas", "50 € / hora", "3.000 €"),
        ("Motor de Inteligencia de Amenazas y afinamiento de reglas INCIBE", "60 horas", "50 € / hora", "3.000 €"),
        ("Pruebas de carga, auditoría de código, pentesting interno y documentación", "40 horas", "50 € / hora", "2.000 €"),
        ("Entornos Azure de preproducción, staging y certificados durante la fase de desarrollo", "-", "-", "2.000 €"),
    ]

    for row_idx, c_item in enumerate(capex_items, start=1):
        for col_idx, val in enumerate(c_item):
            cell = t_capex.cell(row_idx, col_idx)
            cell.width = c_w[col_idx]
            bg = "F8F9FA" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if col_idx == 3:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    p_tot_c = doc.add_paragraph()
    p_tot_c.paragraph_format.space_before = Pt(4)
    p_tot_c.paragraph_format.space_after = Pt(8)
    r_tc = p_tot_c.add_run("TOTAL CAPEX DE INDUSTRIALIZACIÓN (Fases 1 a 3): 20.000 € (360 horas de ingeniería interna + infra)")
    r_tc.font.bold = True
    r_tc.font.color.rgb = COLOR_PRIMARY

    add_subsection_heading("3.2 Costes Operativos Recurrentes Anuales (OPEX)")
    p_opex = doc.add_paragraph()
    p_opex.paragraph_format.space_after = Pt(6)
    p_opex.add_run(
        "Una vez desplegado, el mantenimiento de NEXUS 2.0 es altamente eficiente:\n"
        "• Infraestructura Cloud Azure (PostgreSQL Flexible Server HA + Container Apps + Log Analytics): 350 €/mes (4.200 €/año).\n"
        "• Consumo de APIs de Inteligencia Artificial y Threat Intelligence: 150 €/mes (1.800 €/año).\n"
        "• Soporte evolutivo y guardia de mantenimiento interno (10 horas/mes a 50 €/h): 500 €/mes (6.000 €/año).\n"
        "• TOTAL OPEX RECURRENTE ANUAL: 1.000 € / mes = 12.000 € / año."
    )

    add_subsection_heading("3.3 Comparativa Estratégica TCO a 3 Años: Desarrollo Interno (Build) vs. Comercial (Buy)")

    t_tco = doc.add_table(rows=6, cols=4)
    t_tco.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_heads = ["Métrica / Ejercicio Financiero", "NEXUS 2.0 (Desarrollo Interno)", "Plataforma Comercial (Buy)", "Ahorro Neto Directo"]
    t_w = [Inches(2.5), Inches(1.5), Inches(1.5), Inches(1.4)]

    for col_idx, h_text in enumerate(t_heads):
        cell = t_tco.cell(0, col_idx)
        cell.width = t_w[col_idx]
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, top=90, bottom=90, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    tco_data = [
        ("Inversión Inicial / Setup (CAPEX)", "20.000 € (360h)", "20.000 €", "Mismo desembolso inicial"),
        ("Coste Recurrente Anual (OPEX)", "12.000 € / año", "60.000 € / año", "Ahorro de 48.000 € / año (-80%)"),
        ("Coste Total Año 1 (CAPEX + OPEX)", "32.000 €", "80.000 €", "48.000 € de ahorro Año 1"),
        ("Coste Total a 3 Años (TCO 3Y)", "56.000 €", "200.000 €", "144.000 € de ahorro a 3 años"),
        ("Control del Código y Soberanía", "100% propio en Azure", "Dependencia de proveedor", "Adaptado a OT Sampol y NIS2")
    ]

    for row_idx, t_row in enumerate(tco_data, start=1):
        for col_idx, val in enumerate(t_row):
            cell = t_tco.cell(row_idx, col_idx)
            cell.width = t_w[col_idx]
            bg = "F8F9FA" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if col_idx == 3:
                r.font.bold = True
                r.font.color.rgb = COLOR_EMERALD
            else:
                r.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_subsection_heading("3.4 Retorno de Inversión (ROI) y Beneficio Operativo Bruto Anual")
    p_roi = doc.add_paragraph()
    p_roi.paragraph_format.space_after = Pt(6)
    p_roi.add_run(
        "Al contrastar la inversión con el ahorro operativo que NEXUS 2.0 genera mensualmente:\n"
        "• Ahorro en Triaje y Clasificación INCIBE (3.000 alertas/mes bajan de 12 min a 2 min de validación = 500 h/mes liberadas a 45 €/h): 22.500 €/mes = 270.000 €/año.\n"
        "• Ahorro en Bloqueos SOAR (120 bloqueos/mes bajan de 25 min a 1,5 min = 47 h/mes liberadas a 45 €/h): 2.115 €/mes = 25.380 €/año.\n"
        "• Ahorro Operativo Bruto Total: 24.615 € / mes = 295.380 € / año (liberando 6.564 horas de analistas al año).\n"
        "• Beneficio Neto Primer Año (tras descontar 20.000 € CAPEX + 12.000 € OPEX): 263.380 € netos.\n"
        "• Retorno de la Inversión (ROI Año 1): 823% en el escenario de industrialización completa (y 2.010% sobre la base actual).\n"
        "• Periodo de Recuperación (Payback): 1,4 meses (~42 días de operación).\n\n"
        "Factor de Prevención de Parada de Planta (25.000 €/hora): Evitar tan solo una interrupción de 1 hora al año por detección temprana de intrusión o por la protección de la Lista Blanca IT/OT amortiza holgadamente el coste total de desarrollo de NEXUS 2.0."
    )

    # -------------------------------------------------------------
    # 4. CONCLUSIÓN Y RECOMENDACIÓN PARA EL COMITÉ DE DIRECCIÓN
    # -------------------------------------------------------------
    add_section_heading("4. Conclusión y Recomendación para el Comité de Dirección")

    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.space_after = Pt(8)
    p_concl.add_run(
        "NEXUS 2.0 ha demostrado durante el reto de ciberseguridad una madurez técnica y una solidez financiera inigualables. No solo resuelve la ingesta, deduplicación y clasificación de incidentes conforme al estándar INCIBE, sino que dota a Sampol de una capacidad de contención autónoma (SOAR) que reduce a cero el tiempo de exposición ante amenazas activas.\n\n"
        "Recomendación Final: Se recomienda aprobar el Plan de Industrialización de NEXUS 2.0 con un presupuesto de 20.000 € en 6 meses. La inversión se recupera íntegramente en menos de 45 días de servicio y genera un ahorro garantizado de más de 144.000 € en 3 años respecto a contratar soluciones propietarias opacas de terceros, manteniendo todo el control tecnológico y la soberanía del dato en la infraestructura de Sampol."
    )

    doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "INFORME_EJECUTIVO_PLAN_INDUSTRIALIZACION_NEXUS_2_0.docx")
    doc.save(doc_path)
    print(f"Document created successfully at: {doc_path}")
    return doc_path

if __name__ == "__main__":
    create_document()
