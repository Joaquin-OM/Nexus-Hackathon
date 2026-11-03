"""
NEXUS Smart Notifications — Motor de Evaluación de Riesgo y Priorización Explicable
Calcula una puntuación de riesgo entre 0 y 100 basada en hechos comprobables y evidencias.
"""

from typing import Tuple, List
from notifications.schemas import AlertEventInput, PriorityLevel

CRITICAL_RULES = {
    "MODIFY-LAB": "Modificación masiva de ficheros (precursor de ransomware / wiper)",
    "C2-LAB": "Canal activo de Comando y Control (C2) hacia infraestructura externa hostil",
    "APT-LAB": "Persistencia de amenaza persistente y movimiento lateral avanzado",
    "ADMIN-LAB": "Escalada no autorizada a privilegios de Administrador local",
    "ACCOUNT-LAB": "Acceso con credenciales robadas / compromiso efectivo de identidad",
    "MALWARE-LAB": "Ejecución confirmada de binario o malware en endpoint"
}

def clean_text(s: str) -> str:
    if not s:
        return ""
    return s.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

def evaluate_risk(alert: AlertEventInput, accumulated_events: int = 1) -> Tuple[int, PriorityLevel, List[str], bool]:
    score = 0
    reasons = []

    # 1. Severidad de la fuente original
    sev = clean_text(alert.source_severity)
    if "crit" in sev:
        score += 30
        reasons.append("Severidad original calificada como Crítica por el sensor")
    elif "alt" in sev or "high" in sev:
        score += 20
        reasons.append("Severidad original clasificada como Alta")
    elif "med" in sev:
        score += 10
    else:
        score += 5

    # 2. Categoría INCIBE oficial
    inc = clean_text(alert.incibe_class)
    if "intrus" in inc:
        score += 25
        reasons.append(f"Categoría INCIBE de alto impacto: '{alert.incibe_class}'")
    elif "danin" in inc or "malware" in inc or "ransom" in inc:
        score += 28
        reasons.append("Presencia de código dañino o precursor de ransomware")
    elif "compromis" in inc:
        score += 22
        reasons.append("Compromiso confirmado de la integridad o confidencialidad de la información")
    elif "fraud" in inc:
        score += 15
        reasons.append("Evento clasificado como Fraude / Phishing")
    elif "disponibil" in inc:
        score += 20
        reasons.append("Amenaza contra la disponibilidad de servicios esenciales")

    # 3. Regla específica de laboratorio / sensor
    rule = (alert.detection_rule or "").upper()
    for crit_rule, rule_desc in CRITICAL_RULES.items():
        if crit_rule in rule:
            score += 25
            reasons.append(f"Regla crítica detectada: {crit_rule} — {rule_desc}")
            break

    # 4. Criticidad del activo y entorno industrial
    crit = clean_text(alert.asset_criticality)
    if "crit" in crit or "ot" in crit or "planta" in crit:
        score += 25
        reasons.append("Activo afectado pertenece a Infraestructura Crítica / Planta Industrial OT")
    elif "alt" in crit:
        score += 15
        reasons.append("Activo corporativo de criticidad Alta (Servidor de Proyectos / DC)")

    # 5. Cuenta de usuario privilegiada o afectada
    user = (alert.affected_user or "").lower()
    if any(vip in user for vip in ["admin", "root", "dirti", "director", "amoreno", "cmoreno", "bmoreno", "jmoreno"]):
        score += 15
        reasons.append(f"Cuenta de usuario involucrada con privilegios elevados o clave en proyectos: '{alert.affected_user}'")

    # 6. Frecuencia y correlación de alertas acumuladas en el incidente
    if accumulated_events >= 50:
        score += 20
        reasons.append(f"Volumen masivo correlacionado: {accumulated_events} alertas acumuladas sobre este vector")
    elif accumulated_events >= 10:
        score += 12
        reasons.append(f"Patrón reiterado: {accumulated_events} alertas correlacionadas en la misma ventana")
    elif accumulated_events >= 3:
        score += 5

    # 7. Evidencia confirmada de compromiso efectivo
    if alert.is_compromise_confirmed or alert.significant_change:
        score += 20
        reasons.append("Evidencia fehaciente de compromiso de seguridad confirmado")

    # Normalizar entre 0 y 100
    risk_score = min(max(score, 5), 100)

    # Clasificación formal P1, P2, P3, P4
    if risk_score >= 80 or (risk_score >= 65 and ("crit" in crit or any(cr in rule for cr in ["MODIFY", "C2", "APT"]))):
        priority = "P1"
        requires_human_action = True
    elif risk_score >= 55:
        priority = "P2"
        requires_human_action = True
    elif risk_score >= 35:
        priority = "P3"
        requires_human_action = False
    else:
        priority = "P4"
        requires_human_action = False

    return risk_score, priority, reasons, requires_human_action
