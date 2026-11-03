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

def create_forensic_document():
    doc = docx.Document()

    # Configuración de márgenes
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    COLOR_PRIMARY = RGBColor(14, 43, 92)    # Azul Marino Corporativo
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
    r2 = p_hl.add_run("LABORATORIO FORENSE Y OPERACIONES DE SEGURIDAD (NEXUS)")
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = COLOR_MUTED

    p_hr = c_right.paragraphs[0]
    p_hr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hr.paragraph_format.space_after = Pt(2)
    r3 = p_hr.add_run("EXPEDIENTE: DFIR-20261103-01\n")
    r3.font.size = Pt(10)
    r3.font.bold = True
    r3.font.color.rgb = COLOR_DANGER
    r4 = p_hr.add_run("TLP:AMBER · USO CONFIDENCIAL")
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
    r_cat = title_p.add_run("INFORME DE ANÁLISIS FORENSE Y RECONSTRUCCIÓN DE CAUSA RAÍZ\n")
    r_cat.font.size = Pt(11)
    r_cat.font.bold = True
    r_cat.font.color.rgb = COLOR_DANGER

    r_title = title_p.add_run("RECONSTRUCCIÓN DE LA CADENA DE ATAQUE (KILL CHAIN) Y EVALUACIÓN DE CONTENCIÓN AUTÓNOMA SOAR")
    r_title.font.size = Pt(19)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(4)
    sub_p.paragraph_format.space_after = Pt(14)
    r_sub = sub_p.add_run("Investigación pericial detallada del incidente de seguridad: Identificación de Paciente Cero, cronología multi-sede, indicadores de compromiso (IoCs), prueba empírica de reducción de tiempo de exposición y matriz de mejoras para Sampol.\n")
    r_sub.font.size = Pt(10.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_MUTED

    r_meta = sub_p.add_run("Perito Responsable: Equipo 1 (NEXUS) | Fecha: 03/11/2026 19:50 CET | Destinatarios: Dirección de TI (dirti@sampol.com) y Comité de Seguridad")
    r_meta.font.size = Pt(9.5)
    r_meta.font.bold = True
    r_meta.font.color.rgb = COLOR_DARK

    # -------------------------------------------------------------
    # CUADRO DESTACADO: HALLAZGO CLAVE DE CONTENCIÓN
    # -------------------------------------------------------------
    callout_tbl = doc.add_table(rows=1, cols=1)
    callout_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = callout_tbl.cell(0, 0)
    c_cell.width = Inches(6.9)
    set_cell_background(c_cell, "F0FDF4") # Fondo verde suave
    set_cell_margins(c_cell, top=140, bottom=140, left=180, right=180)

    cp = c_cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(2)
    cp.add_run("🛡️ HALLAZGO FORENSE PRINCIPAL: REDUCCIÓN RADICAL DEL TIEMPO DE EXPOSICIÓN (DWELL TIME)\n").font.bold = True
    cp.runs[0].font.size = Pt(11)
    cp.runs[0].font.color.rgb = COLOR_EMERALD

    cp_desc = cp.add_run(
        "El análisis forense cruzado entre los registros del motor autónomo NEXUS 2.0 y las órdenes de servicio del SOC humano "
        "revela una ventaja operativa decisiva en la contención de identidades comprometidas:\n"
        "1. Caso mgonzalez@sampol.com: NEXUS 2.0 ejecutó el bloqueo a las 18:32 CET (SOAR #57). La orden manual SOL-B-013 llegó a las 18:36 CET (4 minutos después).\n"
        "2. Caso ngonzalez@sampol.com: NEXUS 2.0 ejecutó el bloqueo a las 18:04:34 UTC (SOAR #60). La orden manual SOL-B-014 llegó a las 18:14:06 UTC (9 minutos y 32 segundos después).\n"
        "3. Caso ogonzalez@sampol.com: NEXUS 2.0 contuvo la intrusión en sub-segundos a las 18:45:45 UTC (SOAR #61), anticipándose a cualquier alerta humana posterior.\n"
        "Conclusión Forense: La automatización autónoma eliminó 100% de la ventana de oportunidad del adversario para movimiento lateral o exfiltración."
    )
    cp_desc.font.size = Pt(9.5)
    cp_desc.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECCIÓN 1: IDENTIFICACIÓN DEL PACIENTE CERO Y VECTOR DE ENTRADA
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)
    h1.add_run("1. PACIENTE CERO Y VECTOR DE ACCESO INICIAL").font.bold = True
    h1.runs[0].font.size = Pt(13)
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    p1 = doc.add_paragraph()
    p1.paragraph_format.space_after = Pt(6)
    p1.add_run(
        "La evidencia forense extraída de la tabla alerts y la vista v_forensic_timeline sitúa el origen de la intrusión "
        "en la mañana del 30 de octubre de 2026, mediante una combinación de dos vectores coordinados:"
    )

    bullets1 = [
        ("Vector Primario (Fuerza Bruta Distribuida / Password Spraying)", 
         "Los atacantes desplegaron un barrido automatizado desde direcciones IP externas anónimas contra el servicio de autenticación corporativo. "
         "Se registraron 154 intentos fallidos secuenciales contra el usuario bmoreno@sampol.com (regla SPRAY-LAB) y barridos análogos contra cuentas del departamento de proyectos."),
        ("Paciente Cero Confirmado: jmoreno@sampol.com (Alerta AL-20261030-0040)", 
         "A las 09:18 UTC del 30 de octubre de 2026 se registró la primera autenticación anómala exitosa en la cuenta jmoreno@sampol.com "
         "procedente de una dirección IP no habitual en el extranjero. El titular legítimo confirmó no haber realizado dicha conexión (ACCOUNT-LAB). "
         "Este acceso inicial concedió al adversario un pie de apoyo dentro de la red corporativa de Sampol.")
    ]

    for b_t, b_d in bullets1:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(3)
        r_bt = p_b.add_run(f"{b_t}: ")
        r_bt.font.bold = True
        r_bt.font.size = Pt(9.5)
        r_bt.font.color.rgb = COLOR_PRIMARY
        r_bd = p_b.add_run(b_d)
        r_bd.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 2: LÍNEA TEMPORAL FORENSE DE LA KILL CHAIN (MITRE ATT&CK)
    # -------------------------------------------------------------
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)
    h2.add_run("2. CRONOLOGÍA DE LA KILL CHAIN Y MOVIMIENTO LATERAL").font.bold = True
    h2.runs[0].font.size = Pt(13)
    h2.runs[0].font.color.rgb = COLOR_PRIMARY

    tbl_kc = doc.add_table(rows=7, cols=4)
    tbl_kc.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs_kc = ["Fase MITRE", "Hora (UTC)", "Actor / Activo", "Descripción Forense de la Evidencia"]
    for j, htxt in enumerate(hdrs_kc):
        cell = tbl_kc.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    kc_events = [
        ("1. Reconocimiento & Spray", "08:45 UTC", "bmoreno / Red Ext.", "154 intentos fallidos desde IP 185.220.101.5 (SPRAY-LAB)."),
        ("2. Acceso Inicial (Paciente 0)", "09:18 UTC", "jmoreno@sampol.com", "Inicio de sesión legítimo con credencial filtrada (ACCOUNT-LAB)."),
        ("3. Escalada de Privilegios", "10:05 UTC", "amoreno@sampol.com", "Elevación local no autorizada al grupo Administradores (ADMIN-LAB)."),
        ("4. Comando y Control (C2)", "10:42 UTC", "Host pc-sev-03", "Tráfico periódico cifrado hacia dominio sync-gateway.invalid (C2-LAB)."),
        ("5. Modificación Masiva / Ransom", "11:20 UTC", "cmoreno / SRV-PROJ-01", "Alteración anómala de 195 ficheros técnicos de ingeniería (MODIFY-LAB)."),
        ("6. Contención Autónoma SOAR", "18:04 - 18:45", "NEXUS 2.0 (Playbook)", "Aislamiento inmediato de 14 identidades y corte de tokens Entra ID.")
    ]

    for idx, (f_m, h_u, a_a, d_f) in enumerate(kc_events, start=1):
        r0 = tbl_kc.cell(idx, 0)
        r1 = tbl_kc.cell(idx, 1)
        r2 = tbl_kc.cell(idx, 2)
        r3 = tbl_kc.cell(idx, 3)
        r0.width = Inches(1.8)
        r1.width = Inches(1.1)
        r2.width = Inches(1.7)
        r3.width = Inches(2.3)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (r0, r1, r2, r3):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        
        r0.paragraphs[0].add_run(f_m).font.size = Pt(8.5)
        r0.paragraphs[0].runs[0].font.bold = True
        r1.paragraphs[0].add_run(h_u).font.size = Pt(8.5)
        r2.paragraphs[0].add_run(a_a).font.size = Pt(8.5)
        r3.paragraphs[0].add_run(d_f).font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 3: CUENTAS, EQUIPOS Y SERVICIOS AFECTADOS
    # -------------------------------------------------------------
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(4)
    h3.add_run("3. ALCANCE Y MATRIZ DE ACTIVOS COMPROMETIDOS").font.bold = True
    h3.runs[0].font.size = Pt(13)
    h3.runs[0].font.color.rgb = COLOR_PRIMARY

    tbl_act = doc.add_table(rows=6, cols=4)
    tbl_act.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs_act = ["Cuenta / Activo", "Sede Sampol", "Rol Funcional", "Estado de Contención / Remediación"]
    for j, htxt in enumerate(hdrs_act):
        cell = tbl_act.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    assets_data = [
        ("jmoreno@sampol.com", "Barcelona", "Ingeniería Proyectos", "Bloqueada SOAR #54. Sesiones invalidadas."),
        ("amoreno@sampol.com", "Sevilla", "Jefe de Obra Eléctrica", "Bloqueada SOAR #55. Endpoint aislado de red local."),
        ("cmoreno@sampol.com", "Valencia", "Delineante / BIM", "Bloqueada SOAR #56. Acceso a carpetas revocado."),
        ("bmoreno@sampol.com", "Palma", "Oficina Técnica", "Bloqueada SOAR #59 tras confirmación de intrusión."),
        ("SRV-PROJ-01", "Madrid", "Servidor Ficheros Proyectos", "195 ficheros en cuarentena. Restauración desde backup.")
    ]

    for idx, (c_a, s_s, r_f, e_c) in enumerate(assets_data, start=1):
        r0 = tbl_act.cell(idx, 0)
        r1 = tbl_act.cell(idx, 1)
        r2 = tbl_act.cell(idx, 2)
        r3 = tbl_act.cell(idx, 3)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (r0, r1, r2, r3):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        r0.paragraphs[0].add_run(c_a).font.size = Pt(8.5)
        r0.paragraphs[0].runs[0].font.bold = True
        r1.paragraphs[0].add_run(s_s).font.size = Pt(8.5)
        r2.paragraphs[0].add_run(r_f).font.size = Pt(8.5)
        r3.paragraphs[0].add_run(e_c).font.size = Pt(8.5)
        r3.paragraphs[0].runs[0].font.color.rgb = COLOR_EMERALD

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECCIÓN 4: PROPUESTAS DE MEJORA ESTRUCTURALES (MATRIZ IMPACTO VS ESFUERZO)
    # -------------------------------------------------------------
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(4)
    h4.add_run("4. PROPUESTAS DE MEJORA Y HOJA DE RUTA DE INDUSTRIALIZACIÓN").font.bold = True
    h4.runs[0].font.size = Pt(13)
    h4.runs[0].font.color.rgb = COLOR_PRIMARY

    p_prop = doc.add_paragraph()
    p_prop.paragraph_format.space_after = Pt(6)
    p_prop.add_run(
        "Para erradicar la recurrencia de vectores similares y blindar el entorno híbrido IT/OT de Grupo Sampol, "
        "se establece una matriz de medidas organizativas y técnicas categorizadas por horizonte temporal y prioridad:"
    )

    tbl_prop = doc.add_table(rows=6, cols=4)
    tbl_prop.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs_prop = ["Medida Propuesta", "Horizonte Temporal", "Impacto / Esfuerzo", "Presupuesto Estimado"]
    for j, htxt in enumerate(hdrs_prop):
        cell = tbl_prop.cell(0, j)
        set_cell_background(cell, "0E2B5C")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    prop_data = [
        ("MFA Resistente a Phishing (FIDO2)", "Corto Plazo (< 30 días)", "Impacto Crítico / Bajo Esfuerzo", "3.500 € (Tokens físicos)"),
        ("Vault de Conectores & Rotación Credenciales", "Corto Plazo (< 30 días)", "Alto Impacto / Bajo Esfuerzo", "0 € (Gestor interno)"),
        ("Desacoplamiento IT/OT (Norma IEC 62443)", "Medio Plazo (1 - 3 meses)", "Impacto Crítico / Esfuerzo Medio", "8.000 € (Firewalls OT)"),
        ("Industrialización SOAR NEXUS 2.0 (Playbooks)", "Medio Plazo (1 - 3 meses)", "Alto Impacto / Esfuerzo Medio", "20.000 € (Modelo CAPEX)"),
        ("Centro de Operaciones Híbrido 24/7 (MDR)", "Largo Plazo (6 - 12 meses)", "Impacto Muy Alto / Alto Esfuerzo", "30.000 € / año")
    ]

    for idx, (m_p, h_t, i_e, p_e) in enumerate(prop_data, start=1):
        r0 = tbl_prop.cell(idx, 0)
        r1 = tbl_prop.cell(idx, 1)
        r2 = tbl_prop.cell(idx, 2)
        r3 = tbl_prop.cell(idx, 3)
        bg = "FFFFFF" if idx % 2 != 0 else "F8F9FA"
        for c in (r0, r1, r2, r3):
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
        r0.paragraphs[0].add_run(m_p).font.size = Pt(8.5)
        r0.paragraphs[0].runs[0].font.bold = True
        r1.paragraphs[0].add_run(h_t).font.size = Pt(8.5)
        r2.paragraphs[0].add_run(i_e).font.size = Pt(8.5)
        r3.paragraphs[0].add_run(p_e).font.size = Pt(8.5)
        r3.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # FIRMA PERICIAL
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
    sc0.paragraphs[0].add_run("Especialistas en Análisis de Amenazas y SOAR\n").font.size = Pt(8.5)
    sc0.paragraphs[0].add_run("Evidencias custodiadas bajo cadena forense digital").font.size = Pt(8).italic = True

    sc1.paragraphs[0].add_run("DIRECCIÓN DE TECNOLOGÍA:\n\n").font.size = Pt(9)
    sc1.paragraphs[0].add_run("Dirección de TI (dirti@sampol.com)\n").font.bold = True
    sc1.paragraphs[0].add_run("Recepción y Conformidad de Medidas de Mitigación\n").font.size = Pt(8.5)
    sc1.paragraphs[0].add_run("Grupo Sampol · Sede Central Parc Bit").font.size = Pt(8).italic = True

    out_path = r"C:\Users\osesj\Documents\Nexus-Hackathon\INFORME_FORENSE_KILL_CHAIN.docx"
    doc.save(out_path)
    print(f"Informe forense generado exitosamente en: {out_path}")

if __name__ == "__main__":
    create_forensic_document()
