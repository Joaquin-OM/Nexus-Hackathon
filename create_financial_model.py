import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_financial_model():
    wb = openpyxl.Workbook()
    # Eliminar hoja por defecto
    default_sheet = wb.active
    
    # -------------------------------------------------------------
    # ESTILOS Y COLORES CORPORATIVOS
    # -------------------------------------------------------------
    NAVY_HEADER = PatternFill(start_color="0E2B5C", end_color="0E2B5C", fill_type="solid")
    BLUE_ACCENT = PatternFill(start_color="007AFF", end_color="007AFF", fill_type="solid")
    LIGHT_BG = PatternFill(start_color="F0F4F8", end_color="F0F4F8", fill_type="solid")
    CARD_BG = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
    INPUT_CELL = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid") # Amarillo suave editable
    SUCCESS_BG = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Verde suave KPI

    FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    FONT_TITLE = Font(name="Calibri", size=16, bold=True, color="0E2B5C")
    FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="555555")
    FONT_BOLD = Font(name="Calibri", size=11, bold=True, color="1F2937")
    FONT_REGULAR = Font(name="Calibri", size=11, color="1F2937")
    FONT_KPI_VAL = Font(name="Calibri", size=18, bold=True, color="0E2B5C")
    FONT_KPI_LBL = Font(name="Calibri", size=9, bold=True, color="4B5563")

    THIN_BORDER_SIDE = Side(border_style="thin", color="D1D5DB")
    DOUBLE_BORDER_SIDE = Side(border_style="double", color="0E2B5C")
    CELL_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)
    TOTAL_BORDER = Border(top=THIN_BORDER_SIDE, bottom=DOUBLE_BORDER_SIDE, left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE)

    ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
    ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
    ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")

    CURRENCY_FORMAT = '"€"#,##0'
    PERCENT_FORMAT = '0.0%'
    NUMBER_FORMAT = '#,##0'

    # =============================================================
    # PESTAÑA 1: RESUMEN EJECUTIVO & CUADRO DE MANDO FINANCIERO
    # =============================================================
    ws1 = wb.create_sheet(title="Resumen Ejecutivo")
    ws1.views.sheetView[0].showGridLines = True

    ws1["B2"] = "GRUPO SAMPOL · CASO DE NEGOCIO Y RETORNO DE INVERSIÓN (ROI)"
    ws1["B2"].font = FONT_TITLE
    ws1["B3"] = "Industrialización NEXUS 2.0 frente a Plataforma Comercial de Mercado | Hackathon FP Sampol 2026"
    ws1["B3"].font = FONT_SUBTITLE

    # TARJETAS KPI (Filas 5 a 7)
    kpi_cards = [
        ("B", "C", "INVERSIÓN INICIAL (CAPEX)", "='Parámetros Director'!C12", CURRENCY_FORMAT, "Desarrollo interno (400 h)"),
        ("D", "E", "AHORRO TCO A 3 AÑOS", "='TCO 3 Años (Build vs Buy)'!F15", CURRENCY_FORMAT, "Ahorro vs. Comercial"),
        ("F", "G", "RETORNO INVERSIÓN (ROI AÑO 1)", "='Escenarios'!D22", PERCENT_FORMAT, "Escenario Realista"),
        ("H", "I", "PAYBACK (AMORTIZACIÓN)", "='Escenarios'!D23", "0.0", "Meses recuperación")
    ]

    for c1, c2, label, formula, num_fmt, subtext in kpi_cards:
        # Fila 5: Label
        ws1.merge_cells(f"{c1}5:{c2}5")
        ws1[f"{c1}5"] = label
        ws1[f"{c1}5"].font = FONT_KPI_LBL
        ws1[f"{c1}5"].fill = LIGHT_BG
        ws1[f"{c1}5"].alignment = ALIGN_CENTER

        # Fila 6: Valor
        ws1.merge_cells(f"{c1}6:{c2}6")
        ws1[f"{c1}6"] = formula
        ws1[f"{c1}6"].font = FONT_KPI_VAL
        ws1[f"{c1}6"].fill = LIGHT_BG
        ws1[f"{c1}6"].alignment = ALIGN_CENTER
        ws1[f"{c1}6"].number_format = num_fmt

        # Fila 7: Subtexto
        ws1.merge_cells(f"{c1}7:{c2}7")
        ws1[f"{c1}7"] = subtext
        ws1[f"{c1}7"].font = FONT_SUBTITLE
        ws1[f"{c1}7"].fill = LIGHT_BG
        ws1[f"{c1}7"].alignment = ALIGN_CENTER

    # Tabla de Síntesis Comparativa (Filas 9 a 17)
    ws1["B9"] = "MÉTRICA / INDICADOR CLAVE"
    ws1["C9"] = "MODELO MANUAL (AS-IS)"
    ws1["D9"] = "PLATAFORMA MERCADO (BUY)"
    ws1["E9"] = "NEXUS 2.0 (BUILD)"
    ws1["F9"] = "BENEFICIO / DIFERENCIAL"

    for col in ["B", "C", "D", "E", "F"]:
        cell = ws1[f"{col}9"]
        cell.fill = NAVY_HEADER
        cell.font = FONT_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = CELL_BORDER

    synth_rows = [
        (10, "Coste de Adquisición / Puesta en marcha", "0 €", "='Parámetros Director'!C14", "='Parámetros Director'!C12", "=D10-E10", CURRENCY_FORMAT),
        (11, "Coste Anual de Mantenimiento / Licencia", "0 €", "='Parámetros Director'!C13", "='Parámetros Director'!C16", "=D11-E11", CURRENCY_FORMAT),
        (12, "TCO Acumulado a 3 Años", "0 €", "='TCO 3 Años (Build vs Buy)'!F9", "='TCO 3 Años (Build vs Buy)'!F13", "='TCO 3 Años (Build vs Buy)'!F15", CURRENCY_FORMAT),
        (13, "Tiempo Medio de Revisión de Alerta", "12,0 min", "5,0 min", "0,1 min (< 5s)", "11,9 min ahorrados", "@"),
        (14, "Coste Anual Horas Analista (Triaje)", "='Escenarios'!C15", "='Escenarios'!C15*0.4", "='Escenarios'!D16", "='Escenarios'!D17", CURRENCY_FORMAT),
        (15, "Tiempo Medio de Contención de Cuenta", "25,0 min", "15,0 min", "< 1 segundo (SOAR)", "24,9 min ahorrados", "@"),
        (16, "Ahorro Operativo Anual en Personal", "0 €", "90.000 €", "='Escenarios'!D19", "='Escenarios'!D19", CURRENCY_FORMAT),
        (17, "Cobertura de Parada de Planta Crítica", "Sin salvaguarda", "Parcial (IT)", "Integrado con Whitelist OT", "25.000 €/h evitada", "@")
    ]

    for r_idx, m_name, as_is, buy, build, diff, fmt in synth_rows:
        ws1[f"B{r_idx}"] = m_name
        ws1[f"C{r_idx}"] = as_is
        ws1[f"D{r_idx}"] = buy
        ws1[f"E{r_idx}"] = build
        ws1[f"F{r_idx}"] = diff

        ws1[f"B{r_idx}"].font = FONT_BOLD if r_idx in [12, 16] else FONT_REGULAR
        ws1[f"B{r_idx}"].alignment = ALIGN_LEFT
        ws1[f"B{r_idx}"].border = CELL_BORDER

        for col in ["C", "D", "E", "F"]:
            c = ws1[f"{col}{r_idx}"]
            c.font = FONT_BOLD if r_idx in [12, 16] else FONT_REGULAR
            c.alignment = ALIGN_RIGHT if fmt != "@" else ALIGN_CENTER
            c.border = CELL_BORDER
            if fmt != "@":
                c.number_format = fmt
        
        if r_idx in [12, 16]:
            ws1[f"F{r_idx}"].fill = SUCCESS_BG
            ws1[f"F{r_idx}"].font = Font(name="Calibri", size=11, bold=True, color="166534")

    # =============================================================
    # PESTAÑA 2: PARÁMETROS OFICIALES DEL DIRECTOR DE TI
    # =============================================================
    ws2 = wb.create_sheet(title="Parámetros Director")
    ws2.views.sheetView[0].showGridLines = True

    ws2["B2"] = "PARÁMETROS ECONÓMICOS OFICIALES COMUNICADOS POR DIRECCIÓN DE TI"
    ws2["B2"].font = FONT_TITLE
    ws2["B3"] = "Valores proporcionados en la tabla oficial del Director (Foto 'DATOS DEL DIRECTOR')"
    ws2["B3"].font = FONT_SUBTITLE

    ws2["B5"] = "PARÁMETRO"
    ws2["C5"] = "VALOR PROPUESTO"
    ws2["D5"] = "UNIDAD"
    ws2["E5"] = "DESCRIPCIÓN / IMPACTO EN EL MODELO"

    for col in ["B", "C", "D", "E"]:
        c = ws2[f"{col}5"]
        c.fill = NAVY_HEADER
        c.font = FONT_HEADER
        c.alignment = ALIGN_CENTER
        c.border = CELL_BORDER

    params_data = [
        (6, "Alertas al mes", 3000, "Alertas / mes", "Volumen mensual de alertas generadas por los sensores del SOC", NUMBER_FORMAT),
        (7, "Tiempo medio de revisión manual", 12, "Minutos / alerta", "Tiempo que dedica un analista de Nivel 1 a revisar cada alerta en el modelo AS-IS", NUMBER_FORMAT),
        (8, "Coste de la hora de analista", 45, "€ / hora", "Coste horario medio imputado al personal de análisis del SOC", CURRENCY_FORMAT),
        (9, "Bloqueos manuales al mes", 120, "Bloqueos / mes", "Número mensual de solicitudes de contención y aislamiento de cuentas", NUMBER_FORMAT),
        (10, "Tiempo por bloqueo manual", 25, "Minutos / bloqueo", "Tiempo de dedicación operativa por cada orden de bloqueo manual", NUMBER_FORMAT),
        (11, "Hora de servicio parado (Planta)", 25000, "€ / hora", "Coste empresarial estimado por hora de parada en plantas de cogeneración/críticas", CURRENCY_FORMAT),
        (12, "Inversión inicial NEXUS 2.0 (Build)", 20000, "€ (CAPEX)", "Coste de industrialización interna: 400 horas de desarrollo a 50 €/h", CURRENCY_FORMAT),
        (13, "Plataforma comercial - Licencia anual", 60000, "€ / año", "Coste recurrente de suscripción de la alternativa comercial evaluada", CURRENCY_FORMAT),
        (14, "Plataforma comercial - Implantación inicial", 20000, "€ (Setup)", "Coste único de consultoría, despliegue y puesta en marcha de la solución comercial", CURRENCY_FORMAT),
        (15, "Coste hora de desarrollo interno", 50, "€ / hora", "Tarifa de hora técnica interna de desarrollo e ingeniería en Sampol", CURRENCY_FORMAT),
        (16, "Mantenimiento anual NEXUS 2.0 (OPEX)", 12000, "€ / año", "20 horas/mes de soporte y evolución a 50 €/h (240 h/año)", CURRENCY_FORMAT)
    ]

    for r_idx, name, val, unit, desc, fmt in params_data:
        ws2[f"B{r_idx}"] = name
        ws2[f"C{r_idx}"] = val
        ws2[f"D{r_idx}"] = unit
        ws2[f"E{r_idx}"] = desc

        ws2[f"B{r_idx}"].font = FONT_BOLD
        ws2[f"B{r_idx}"].border = CELL_BORDER

        c_val = ws2[f"C{r_idx}"]
        c_val.font = FONT_BOLD
        c_val.alignment = ALIGN_RIGHT
        c_val.border = CELL_BORDER
        c_val.fill = INPUT_CELL # Marcar como variable de entrada
        c_val.number_format = fmt

        ws2[f"D{r_idx}"].alignment = ALIGN_CENTER
        ws2[f"D{r_idx}"].border = CELL_BORDER
        ws2[f"D{r_idx}"].font = FONT_REGULAR

        ws2[f"E{r_idx}"].alignment = ALIGN_LEFT
        ws2[f"E{r_idx}"].border = CELL_BORDER
        ws2[f"E{r_idx}"].font = FONT_SUBTITLE

    # =============================================================
    # PESTAÑA 3: ANÁLISIS DE ESCENARIOS (PRUDENTE, REALISTA, OPTIMISTA)
    # =============================================================
    ws3 = wb.create_sheet(title="Escenarios")
    ws3.views.sheetView[0].showGridLines = True

    ws3["B2"] = "EVALUACIÓN DE RETORNO ECONÓMICO POR ESCENARIOS DE EFICIENCIA"
    ws3["B2"].font = FONT_TITLE
    ws3["B3"] = "Fórmulas dinámicas vinculadas a la hoja 'Parámetros Director' | Horas analistas, contención y paradas de planta"
    ws3["B3"].font = FONT_SUBTITLE

    ws3["B5"] = "CONCEPTO / INDICADOR"
    ws3["C5"] = "ESCENARIO PRUDENTE"
    ws3["D5"] = "ESCENARIO REALISTA"
    ws3["E5"] = "ESCENARIO OPTIMISTA"

    for col in ["B", "C", "D", "E"]:
        c = ws3[f"{col}5"]
        c.fill = NAVY_HEADER
        c.font = FONT_HEADER
        c.alignment = ALIGN_CENTER
        c.border = CELL_BORDER

    esc_rows = [
        (6, "% Reducción tiempo revisión alertas", 0.70, 0.85, 0.95, PERCENT_FORMAT),
        (7, "% Bloqueos automatizados por SOAR", 0.80, 0.95, 1.00, PERCENT_FORMAT),
        (8, "Horas de parada de servicio evitadas al año", 0, 1, 2, NUMBER_FORMAT),
        (9, "--- VOLÚMENES OPERATIVOS MENSUALES ---", "", "", "", "@"),
        (10, "Horas analista triaje (AS-IS mensual)", "='Parámetros Director'!C6*('Parámetros Director'!C7/60)", "='Parámetros Director'!C6*('Parámetros Director'!C7/60)", "='Parámetros Director'!C6*('Parámetros Director'!C7/60)", NUMBER_FORMAT),
        (11, "Horas analista triaje con NEXUS 2.0 (mensual)", "=C10*(1-C6)", "=D10*(1-D6)", "=E10*(1-E6)", NUMBER_FORMAT),
        (12, "Horas de triaje ahorradas al mes", "=C10-C11", "=D10-D11", "=E10-E11", NUMBER_FORMAT),
        (13, "Horas de contención/bloqueo ahorradas al mes", "='Parámetros Director'!C9*('Parámetros Director'!C10/60)*C7", "='Parámetros Director'!C9*('Parámetros Director'!C10/60)*D7", "='Parámetros Director'!C9*('Parámetros Director'!C10/60)*E7", NUMBER_FORMAT),
        (14, "--- IMPACTO ECONÓMICO ANUAL ---", "", "", "", "@"),
        (15, "Coste anual triaje AS-IS (Sin NEXUS)", "=C10*'Parámetros Director'!C8*12", "=D10*'Parámetros Director'!C8*12", "=E10*'Parámetros Director'!C8*12", CURRENCY_FORMAT),
        (16, "Coste anual triaje con NEXUS 2.0", "=C11*'Parámetros Director'!C8*12", "=D11*'Parámetros Director'!C8*12", "=E11*'Parámetros Director'!C8*12", CURRENCY_FORMAT),
        (17, "Ahorro anual en triaje de alertas", "=C12*'Parámetros Director'!C8*12", "=D12*'Parámetros Director'!C8*12", "=E12*'Parámetros Director'!C8*12", CURRENCY_FORMAT),
        (18, "Ahorro anual en contención SOAR", "=C13*'Parámetros Director'!C8*12", "=D13*'Parámetros Director'!C8*12", "=E13*'Parámetros Director'!C8*12", CURRENCY_FORMAT),
        (19, "Ahorro Operativo Anual en Personal (Triaje + SOAR)", "=C17+C18", "=D17+D18", "=E17+E18", CURRENCY_FORMAT),
        (20, "Coste de parada evitado en plantas Sampol", "=C8*'Parámetros Director'!C11", "=D8*'Parámetros Director'!C11", "=E8*'Parámetros Director'!C11", CURRENCY_FORMAT),
        (21, "BENEFICIO BRUTO AÑO 1 (Ahorro + Paradas)", "=C19+C20", "=D19+D20", "=E19+E20", CURRENCY_FORMAT),
        (22, "RETORNO DE LA INVERSIÓN (ROI AÑO 1)", "=(C21-('Parámetros Director'!C12+'Parámetros Director'!C16))/('Parámetros Director'!C12+'Parámetros Director'!C16)", "=(D21-('Parámetros Director'!C12+'Parámetros Director'!C16))/('Parámetros Director'!C12+'Parámetros Director'!C16)", "=(E21-('Parámetros Director'!C12+'Parámetros Director'!C16))/('Parámetros Director'!C12+'Parámetros Director'!C16)", PERCENT_FORMAT),
        (23, "PERIODO DE AMORTIZACIÓN (PAYBACK EN MESES)", "=('Parámetros Director'!C12)/((C21-'Parámetros Director'!C16)/12)", "=('Parámetros Director'!C12)/((D21-'Parámetros Director'!C16)/12)", "=('Parámetros Director'!C12)/((E21-'Parámetros Director'!C16)/12)", "0.0")
    ]

    for r_idx, label, v_c, v_d, v_e, fmt in esc_rows:
        ws3[f"B{r_idx}"] = label
        if fmt == "@":
            ws3.merge_cells(f"B{r_idx}:E{r_idx}")
            ws3[f"B{r_idx}"].fill = LIGHT_BG
            ws3[f"B{r_idx}"].font = FONT_BOLD
            ws3[f"B{r_idx}"].alignment = ALIGN_CENTER
            continue

        ws3[f"C{r_idx}"] = v_c
        ws3[f"D{r_idx}"] = v_d
        ws3[f"E{r_idx}"] = v_e

        ws3[f"B{r_idx}"].font = FONT_BOLD if r_idx in [19, 21, 22, 23] else FONT_REGULAR
        ws3[f"B{r_idx}"].border = CELL_BORDER

        for col in ["C", "D", "E"]:
            c = ws3[f"{col}{r_idx}"]
            c.border = CELL_BORDER
            c.alignment = ALIGN_RIGHT
            c.font = FONT_BOLD if r_idx in [19, 21, 22, 23] else FONT_REGULAR
            if fmt:
                c.number_format = fmt
            if r_idx in [6, 7, 8]:
                c.fill = INPUT_CELL

        if r_idx in [21, 22, 23]:
            for col in ["C", "D", "E"]:
                ws3[f"{col}{r_idx}"].fill = SUCCESS_BG

    # =============================================================
    # PESTAÑA 4: COMPARATIVA TCO A 3 AÑOS (BUILD VS. BUY)
    # =============================================================
    ws4 = wb.create_sheet(title="TCO 3 Años (Build vs Buy)")
    ws4.views.sheetView[0].showGridLines = True

    ws4["B2"] = "COMPARATIVA DE COSTE TOTAL DE PROPIEDAD (TCO) A 3 AÑOS"
    ws4["B2"].font = FONT_TITLE
    ws4["B3"] = "Evaluación Build vs. Buy: Desarrollo Interno NEXUS 2.0 vs. Plataforma Comercial de Mercado"
    ws4["B3"].font = FONT_SUBTITLE

    ws4["B5"] = "CONCEPTO DE COSTE"
    ws4["C5"] = "AÑO 1"
    ws4["D5"] = "AÑO 2"
    ws4["E5"] = "AÑO 3"
    ws4["F5"] = "TOTAL 3 AÑOS"

    for col in ["B", "C", "D", "E", "F"]:
        c = ws4[f"{col}5"]
        c.fill = NAVY_HEADER
        c.font = FONT_HEADER
        c.alignment = ALIGN_CENTER
        c.border = CELL_BORDER

    tco_rows = [
        (6, "Opción 1: Plataforma Comercial de Mercado (Buy)", "", "", "", "", "@"),
        (7, "  - Licenciamiento recurrente", "='Parámetros Director'!C13", "='Parámetros Director'!C13", "='Parámetros Director'!C13", "=SUM(C7:E7)", CURRENCY_FORMAT),
        (8, "  - Implantación y setup inicial", "='Parámetros Director'!C14", 0, 0, "=SUM(C8:E8)", CURRENCY_FORMAT),
        (9, "TOTAL COSTE PLATAFORMA COMERCIAL (BUY)", "=C7+C8", "=D7+D8", "=E7+E8", "=SUM(F7:F8)", CURRENCY_FORMAT),
        (10, "Opción 2: Desarrollo e Industrialización NEXUS 2.0 (Build)", "", "", "", "", "@"),
        (11, "  - Inversión inicial de desarrollo (400 h x 50 €)", "='Parámetros Director'!C12", 0, 0, "=SUM(C11:E11)", CURRENCY_FORMAT),
        (12, "  - Soporte, evolución y mantenimiento (20 h/mes x 50 €)", "='Parámetros Director'!C16", "='Parámetros Director'!C16", "='Parámetros Director'!C16", "=SUM(C12:E12)", CURRENCY_FORMAT),
        (13, "TOTAL COSTE NEXUS 2.0 (BUILD)", "=C11+C12", "=D11+D12", "=E11+E12", "=SUM(F11:F12)", CURRENCY_FORMAT),
        (14, "--- BALANCE Y DIFERENCIAL ---", "", "", "", "", "@"),
        (15, "AHORRO NETO ACUMULADO (BUY - BUILD)", "=C9-C13", "=D9-D13", "=E9-E13", "=F9-F13", CURRENCY_FORMAT),
        (16, "% DE AHORRO EN COSTE TOTAL", "=C15/C9", "=D15/D9", "=E15/E9", "=F15/F9", PERCENT_FORMAT)
    ]

    for r_idx, label, v_c, v_d, v_e, v_f, fmt in tco_rows:
        ws4[f"B{r_idx}"] = label
        if fmt == "@":
            ws4.merge_cells(f"B{r_idx}:F{r_idx}")
            ws4[f"B{r_idx}"].fill = LIGHT_BG
            ws4[f"B{r_idx}"].font = FONT_BOLD
            ws4[f"B{r_idx}"].alignment = ALIGN_LEFT
            continue

        ws4[f"C{r_idx}"] = v_c
        ws4[f"D{r_idx}"] = v_d
        ws4[f"E{r_idx}"] = v_e
        ws4[f"F{r_idx}"] = v_f

        is_tot = r_idx in [9, 13, 15, 16]
        ws4[f"B{r_idx}"].font = FONT_BOLD if is_tot else FONT_REGULAR
        ws4[f"B{r_idx}"].border = CELL_BORDER

        for col in ["C", "D", "E", "F"]:
            c = ws4[f"{col}{r_idx}"]
            c.border = TOTAL_BORDER if is_tot else CELL_BORDER
            c.alignment = ALIGN_RIGHT
            c.font = FONT_BOLD if is_tot else FONT_REGULAR
            if fmt:
                c.number_format = fmt

        if r_idx in [15, 16]:
            for col in ["C", "D", "E", "F"]:
                ws4[f"{col}{r_idx}"].fill = SUCCESS_BG
                ws4[f"{col}{r_idx}"].font = Font(name="Calibri", size=11, bold=True, color="166534")

    # Eliminar hoja por defecto sobrante
    if default_sheet in wb.worksheets:
        wb.remove(default_sheet)

    # Autoajustar ancho de columnas en todas las hojas
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if '\n' in val_str:
                    val_str = max(val_str.split('\n'), key=len)
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    out_file = r"C:\Users\osesj\Documents\Nexus-Hackathon\MODELO_FINANCIERO_ROI_SAMPOL.xlsx"
    wb.save(out_file)
    print(f"Modelo financiero generado con éxito en: {out_file}")

if __name__ == "__main__":
    build_financial_model()
