import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # Tamaño 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Paleta Corporativa Sampol
    COLOR_NAVY = RGBColor(14, 43, 92)     # #0E2B5C
    COLOR_BLUE = RGBColor(0, 122, 255)    # #007AFF
    COLOR_DARK = RGBColor(31, 41, 55)     # #1F2937
    COLOR_MUTED = RGBColor(107, 114, 128) # #6B7280
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_EMERALD = RGBColor(16, 149, 104)
    COLOR_CARD_BG = RGBColor(240, 244, 248)

    def add_bg(slide, color=COLOR_WHITE):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, category, title):
        # Categoría
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        p_cat = tb_cat.text_frame.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_BLUE

        # Título
        tb_t = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.7))
        p_t = tb_t.text_frame.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY

    # =============================================================
    # SLIDE 1: PORTADA & HOOK (Minuto 0:00 - 0:45)
    # =============================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, COLOR_NAVY)

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "HACKATHON FP SAMPOL 2026 · ÁREA DE CIBERSEGURIDAD Y TI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE
    p.space_after = Pt(16)

    p2 = tf1.add_paragraph()
    p2.text = "NEXUS 2.0 — OPERACIÓN CONTINUA 24/7,\nSOAR AUTÓNOMO Y CUMPLIMIENTO NIS2"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_after = Pt(20)

    p3 = tf1.add_paragraph()
    p3.text = "De la Alerta a la Contención en Milisegundos: Blindando la Energía y las Infraestructuras Críticas de Grupo Sampol"
    p3.font.size = Pt(18)
    p3.font.color.rgb = RGBColor(209, 213, 219)
    p3.space_after = Pt(30)

    p4 = tf1.add_paragraph()
    p4.text = "Equipo 1 (NEXUS) | Fecha: 03/11/2026 | Solución en Vivo: joaquin-om.github.io/Nexus-Hackathon"
    p4.font.size = Pt(13)
    p4.font.bold = True
    p4.font.color.rgb = COLOR_BLUE

    # =============================================================
    # SLIDE 2: ARQUITECTURA TÉCNICA Y SOLUCIÓN (Minuto 0:45 - 1:40)
    # =============================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "Solución Técnica y Arquitectura", "Plataforma Integral de Ciberdefensa y Triaje Automatizado")

    cards_s2 = [
        ("Ingesta Graph & Daemon 24/7", "• Sincronización continua cada 45s.\n• 138 correos procesados.\n• Normalización UTC de zonas horarias.\n• Deduplicación de reenvíos operativos."),
        ("PostgreSQL Azure & INCIBE", "• Esquema relacional con 10 tablas.\n• Clasificación en las 10 clases INCIBE.\n• Trazabilidad total y auditoría inmutable.\n• Gestión de estados y severidad."),
        ("SOAR Autónomo & Salvaguardas", "• Conectado a API /bloquear y /liberar.\n• 61 acciones SOAR ejecutadas.\n• Whitelist estricta para red OT/plantas.\n• Idempotencia para evitar duplicados.")
    ]

    for idx, (c_title, c_desc) in enumerate(cards_s2):
        x = Inches(0.8 + idx * 4.0)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.7), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.fill.background()

        tb = s2.shapes.add_textbox(x + Inches(0.2), Inches(2.0), Inches(3.3), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
        p.space_after = Pt(14)

        for line in c_desc.split("\n"):
            p_line = tf.add_paragraph()
            p_line.text = line
            p_line.font.size = Pt(12)
            p_line.font.color.rgb = COLOR_DARK
            p_line.space_after = Pt(6)

    # =============================================================
    # SLIDE 3: CREATIVIDAD & INNOVACIÓN (Minuto 1:40 - 2:30)
    # =============================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "Creatividad e Innovación (30% Rúbrica)", "Capacidades Diferenciales Más Allá del Enunciado")

    cards_s3 = [
        ("🛡️ Escudo Anti-Prompt Injection", "• Detector algorítmico de canarios.\n• Neutralización del correo trampa HN03.\n• Cuarentena forense sin ejecución errónea."),
        ("📜 Pre-Notificación NIS2 (< 24h)", "• Generación automática oficial para INCIBE-CERT.\n• Cumplimiento legal Art. 23.3(a) NIS2.\n• Evidencia de 0 horas de paro en plantas."),
        ("🌐 Portal Público en GitHub Pages", "• Web interactiva viva con gráficos Chart.js.\n• Acceso inmediato para el jurado en móvil/PC.\n• Búsqueda en vivo de alertas y auditoría SOAR.")
    ]

    for idx, (c_title, c_desc) in enumerate(cards_s3):
        x = Inches(0.8 + idx * 4.0)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.7), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.fill.background()

        tb = s3.shapes.add_textbox(x + Inches(0.2), Inches(2.0), Inches(3.3), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
        p.space_after = Pt(14)

        for line in c_desc.split("\n"):
            p_line = tf.add_paragraph()
            p_line.text = line
            p_line.font.size = Pt(12)
            p_line.font.color.rgb = COLOR_DARK
            p_line.space_after = Pt(6)

    # =============================================================
    # SLIDE 4: INVESTIGACIÓN FORENSE & CAUSA RAÍZ (Minuto 2:30 - 3:25)
    # =============================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "Investigación Forense y Kill Chain", "Causa Raíz, Paciente Cero y Anticipación a Órdenes Humanas")

    # Banner superior de anticipación
    banner = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.7), Inches(11.7), Inches(1.2))
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(220, 252, 231)
    banner.line.fill.background()

    tb_b = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(1.0))
    p_b = tb_b.text_frame.paragraphs[0]
    p_b.text = "🎯 PRUEBA EMPÍRICA DE REDUCCIÓN DE DWELL TIME:"
    p_b.font.bold = True
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = COLOR_EMERALD

    p_b2 = tb_b.text_frame.add_paragraph()
    p_b2.text = "• mgonzalez: Bloqueado por NEXUS a las 18:32 CET -> Orden humana SOL-B-013 a las 18:36 (4 min de ventaja).\n• ngonzalez: Bloqueado por NEXUS a las 18:04 UTC -> Orden humana SOL-B-014 a las 18:14 (9 min 32s de ventaja)."
    p_b2.font.size = Pt(11)
    p_b2.font.color.rgb = COLOR_DARK

    # Columnas inferiores de la Kill Chain
    kc_boxes = [
        ("1. Vector Inicial", "• Password spray masivo (154 intentos bmoreno).\n• Paciente Cero: jmoreno (AL-20261030-0040).\n• Robo de credenciales legítimas."),
        ("2. Escalada & C2", "• amoreno escala a Admin local (ADMIN-LAB).\n• Comunicación C2: sync-gateway.invalid.\n• Intento de persistencia y tareas programadas."),
        ("3. Precursor Ransomware", "• cmoreno altera 195 ficheros en SRV-PROJ-01.\n• NEXUS bloquea la cuenta y frena el cifrado.\n• Red industrial OT 100% segregada e indemne.")
    ]

    for idx, (k_title, k_desc) in enumerate(kc_boxes):
        x = Inches(0.8 + idx * 4.0)
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(3.1), Inches(3.7), Inches(3.7))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.fill.background()

        tb = s4.shapes.add_textbox(x + Inches(0.2), Inches(3.2), Inches(3.3), Inches(3.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = k_title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
        p.space_after = Pt(10)

        for line in k_desc.split("\n"):
            p_line = tf.add_paragraph()
            p_line.text = line
            p_line.font.size = Pt(11.5)
            p_line.font.color.rgb = COLOR_DARK
            p_line.space_after = Pt(4)

    # =============================================================
    # SLIDE 5: CASO DE NEGOCIO Y ROI OFICIAL (Minuto 3:25 - 4:15)
    # =============================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "Análisis de Negocio y ROI (20% Rúbrica)", "Retorno Económico Basado en los Parámetros Oficiales del Director de TI")

    kpis_roi = [
        ("INVERSIÓN CAPEX", "20.000 €", "400 h desarrollo a 50 €/h"),
        ("AHORRO TCO 3 AÑOS", "144.000 €", "72% ahorro vs. Comercial"),
        ("ROI PRIMER AÑO", "823 %", "Amortización inmediata"),
        ("PAYBACK", "42 DÍAS", "1,4 meses de recuperación")
    ]

    for idx, (lbl, val, sub) in enumerate(kpis_roi):
        x = Inches(0.8 + idx * 3.0)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.7), Inches(2.7), Inches(1.8))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.fill.background()

        tb = s5.shapes.add_textbox(x + Inches(0.1), Inches(1.8), Inches(2.5), Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = lbl
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_MUTED

        p2 = tf.add_paragraph()
        p2.text = val
        p2.font.size = Pt(26)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_NAVY

        p3 = tf.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = COLOR_DARK

    # Tabla comparativa Build vs Buy
    tb_c = s5.shapes.add_textbox(Inches(0.8), Inches(3.8), Inches(11.7), Inches(3.0))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "BALANCE ECONÓMICO COMPARATIVO A 3 AÑOS (MODELO OFICIAL EXCEL EN DRIVE):"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)

    points = [
        "• Alternativa Comercial (Buy): 20.000 € setup + 60.000 €/año licencia = 200.000 € a 3 años.",
        "• Desarrollo NEXUS 2.0 (Build): 20.000 € desarrollo + 12.000 €/año mantenimiento = 56.000 € a 3 años.",
        "• Ahorro Operativo en Personal SOC: 184.500 €/año (36.000 horas analista ahorradas al automatizar triaje y bloqueos).",
        "• Protección Crítica: Con solo evitar 1 hora de parada de servicio al año (25.000 €/h), NEXUS 2.0 amortiza el 100% de su CAPEX."
    ]
    for pt in points:
        p_pt = tf_c.add_paragraph()
        p_pt.text = pt
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = COLOR_DARK
        p_pt.space_after = Pt(4)

    # =============================================================
    # SLIDE 6: PROPUESTAS DE MEJORA Y CIERRE (Minuto 4:15 - 5:00)
    # =============================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "Propuestas de Mejora y Conclusión", "Hoja de Ruta Estratégica para el Grupo Sampol")

    cards_s6 = [
        ("Corto Plazo (< 30 días)", "• Despliegue de MFA FIDO2 (Tokens físicos).\n• Vaulting y rotación de contraseñas legacy.\n• DMARC en modo reject para correo."),
        ("Medio Plazo (1 - 3 meses)", "• Segmentación IT/OT bajo estándar IEC 62443.\n• Microsegmentación Zero Trust en servidores.\n• Playbooks SOAR de contención certificados."),
        ("Largo Plazo (6 - 12 meses)", "• Centro de Operaciones Híbrido 24/7 (MDR).\n• Auditoría de conformidad Esquema Nacional (ENS).\n• Simulacros continuos de Red Team / Blue Team.")
    ]

    for idx, (c_title, c_desc) in enumerate(cards_s6):
        x = Inches(0.8 + idx * 4.0)
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.7), Inches(4.0))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.fill.background()

        tb = s6.shapes.add_textbox(x + Inches(0.2), Inches(2.0), Inches(3.3), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
        p.space_after = Pt(14)

        for line in c_desc.split("\n"):
            p_line = tf.add_paragraph()
            p_line.text = line
            p_line.font.size = Pt(12)
            p_line.font.color.rgb = COLOR_DARK
            p_line.space_after = Pt(6)

    # Pie de cierre
    tb_end = s6.shapes.add_textbox(Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.8))
    p_end = tb_end.text_frame.paragraphs[0]
    p_end.text = "🎯 DEMOSTRACIÓN EN VIVO DISPONIBLE: joaquin-om.github.io/Nexus-Hackathon | ¡GRACIAS!"
    p_end.alignment = PP_ALIGN.CENTER
    p_end.font.size = Pt(15)
    p_end.font.bold = True
    p_end.font.color.rgb = COLOR_BLUE

    out_pptx = r"C:\Users\osesj\Documents\Nexus-Hackathon\PITCH_DECK_HACKATHON_SAMPOL.pptx"
    prs.save(out_pptx)
    print(f"Presentación generada con éxito en: {out_pptx}")

if __name__ == "__main__":
    create_deck()
