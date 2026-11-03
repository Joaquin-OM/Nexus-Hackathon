"""
NEXUS Smart Notifications — Motor de Evaluación de Riesgo y Priorización Explicable
Calcula una puntuación de riesgo entre 0 y 100 basada en hechos comprobables y evidencias,
con desglose matemático estructurado y reglas desacopladas de nombres personales.
"""

import os
from typing import Tuple, List, Dict, Any, Set
from notifications.schemas import AlertEventInput, PriorityLevel

# Catálogo oficial de reglas críticas de amenaza y precursores de ransomware/intrusión
CRITICAL_RULES = {
    "MODIFY-LAB": ("Modificación masiva de ficheros (precursor de ransomware / wiper)", 25),
    "C2-LAB": ("Canal activo de Comando y Control (C2) hacia infraestructura externa hostil", 25),
    "APT-LAB": ("Persistencia de amenaza persistente y movimiento lateral avanzado", 25),
    "ADMIN-LAB": ("Escalada no autorizada a privilegios de Administrador local", 22),
    "ACCOUNT-LAB": ("Acceso con credenciales robadas / compromiso efectivo de identidad", 22),
    "MALWARE-LAB": ("Ejecución confirmada de binario o malware en endpoint", 22),
    "READ-LAB": ("Exfiltración o lectura anómala de ficheros confidenciales", 18),
    "MINING-LAB": ("Uso no autorizado de recursos de computación corporativa", 15),
}

# Roles y perfiles con privilegios elevados en infraestructura SAMPOL
PRIVILEGED_ROLE_KEYWORDS = {
    "admin", "root", "dirti", "director", "ciso", "sec-admin",
    "soc-lead", "sysadmin", "responsable", "jefe", "ingenieria", "proyectos"
}

# Lista configurable de cuentas VIP de proyecto (cargable desde variables de entorno o configuración)
def get_configured_vip_accounts() -> Set[str]:
    raw = os.environ.get(
        "NEXUS_VIP_ACCOUNTS",
        "dirti@sampol.com,director@sampol.com,cmoreno@sampol.com,amoreno@sampol.com,bmoreno@sampol.com,jmoreno@sampol.com"
    )
    return {acc.strip().lower() for acc in raw.split(",") if acc.strip()}

def clean_text(s: str) -> str:
    if not s:
        return ""
    return s.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

def evaluate_risk_detailed(alert: AlertEventInput, accumulated_events: int = 1) -> Dict[str, Any]:
    """
    Evalúa el riesgo de forma modular, ortogonal y explicable:
    - Evita contar dos veces la misma evidencia técnica.
    - Genera un desglose detallado de factores que suman al score.
    - Desacopla la lógica de identidades personales mediante roles y criticidad.
    """
    factors = {
        "source_severity": 0,
        "threat_impact": 0,
        "asset_criticality": 0,
        "privilege_level": 0,
        "correlation_volume": 0,
        "confirmed_compromise": 0
    }
    reasons: List[str] = []

    # 1. Severidad de la fuente original (Sensor/Concentrador)
    sev = clean_text(alert.source_severity)
    if "crit" in sev:
        factors["source_severity"] = 30
        reasons.append("Severidad original calificada como Crítica por el sensor")
    elif "alt" in sev or "high" in sev:
        factors["source_severity"] = 20
        reasons.append("Severidad original clasificada como Alta")
    elif "med" in sev:
        factors["source_severity"] = 10
    else:
        factors["source_severity"] = 5

    # 2. Amenaza Técnica (INCIBE + Regla específica) con tope conjunto para evitar doble conteo
    inc = clean_text(alert.incibe_class)
    rule = (alert.detection_rule or "").upper()
    threat_points = 0

    # Categoría INCIBE oficial
    if "intrus" in inc:
        threat_points += 25
        reasons.append(f"Categoría INCIBE de alto impacto: '{alert.incibe_class}'")
    elif "danin" in inc or "malware" in inc or "ransom" in inc:
        threat_points += 28
        reasons.append("Presencia de código dañino o precursor de ransomware")
    elif "compromis" in inc:
        threat_points += 22
        reasons.append("Compromiso confirmado de la integridad o confidencialidad de la información")
    elif "fraud" in inc:
        threat_points += 15
        reasons.append("Evento clasificado como Fraude / Phishing")
    elif "disponibil" in inc:
        threat_points += 20
        reasons.append("Amenaza contra la disponibilidad de servicios esenciales")

    # Regla específica del sensor
    matched_rule_desc = None
    matched_rule_score = 0
    for crit_rule, (rule_desc, r_score) in CRITICAL_RULES.items():
        if crit_rule in rule:
            matched_rule_desc = f"Regla crítica detectada: {crit_rule} — {rule_desc}"
            matched_rule_score = r_score
            break

    if matched_rule_desc:
        reasons.append(matched_rule_desc)
        # Si la categoría INCIBE ya sumó por malware o intrusión, acotar el incremento para no sobrestimar
        threat_points = max(threat_points, matched_rule_score) + (10 if threat_points > 0 else matched_rule_score)

    factors["threat_impact"] = min(threat_points, 35)

    # 3. Criticidad del activo y entorno industrial
    crit = clean_text(alert.asset_criticality)
    if "crit" in crit or "ot" in crit or "planta" in crit:
        factors["asset_criticality"] = 25
        reasons.append("Activo afectado pertenece a Infraestructura Crítica / Planta Industrial OT")
    elif "alt" in crit:
        factors["asset_criticality"] = 15
        reasons.append("Activo corporativo de criticidad Alta (Servidor de Proyectos / DC)")

    # 4. Privilegios de la cuenta de usuario afectada
    user = (alert.affected_user or "").lower()
    vip_accounts = get_configured_vip_accounts()
    is_privileged = any(kw in user for kw in PRIVILEGED_ROLE_KEYWORDS) or (user in vip_accounts)
    if is_privileged and user:
        factors["privilege_level"] = 15
        reasons.append(f"Cuenta de usuario involucrada con privilegios elevados o clave en proyectos: '{alert.affected_user}'")

    # 5. Frecuencia y correlación de alertas acumuladas en el incidente
    if accumulated_events >= 50:
        factors["correlation_volume"] = 20
        reasons.append(f"Volumen masivo correlacionado: {accumulated_events} alertas acumuladas sobre este vector")
    elif accumulated_events >= 10:
        factors["correlation_volume"] = 12
        reasons.append(f"Patrón reiterado: {accumulated_events} alertas correlacionadas en la misma ventana")
    elif accumulated_events >= 3:
        factors["correlation_volume"] = 5

    # 6. Evidencia fehaciente de compromiso efectivo
    if alert.is_compromise_confirmed or alert.significant_change:
        factors["confirmed_compromise"] = 20
        reasons.append("Evidencia fehaciente de compromiso de seguridad confirmado")

    # Suma total y normalización 0 a 100
    raw_total = sum(factors.values())
    risk_score = min(max(raw_total, 5), 100)

    # Clasificación formal P1, P2, P3, P4
    rule_has_crit = any(cr in rule for cr in ["MODIFY", "C2", "APT"])
    if risk_score >= 80 or (risk_score >= 65 and ("crit" in crit or rule_has_crit)):
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

    return {
        "risk_score": risk_score,
        "priority": priority,
        "reasons": reasons,
        "factor_breakdown": factors,
        "requires_human_action": requires_human_action
    }

def evaluate_risk(alert: AlertEventInput, accumulated_events: int = 1) -> Tuple[int, PriorityLevel, List[str], bool]:
    """Interfaz estándar compatible con el contrato de la API."""
    res = evaluate_risk_detailed(alert, accumulated_events=accumulated_events)
    return res["risk_score"], res["priority"], res["reasons"], res["requires_human_action"]
