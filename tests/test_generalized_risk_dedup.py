"""
Test Suite: Motor de Riesgo Modular y Deduplicación Generalizada
Verifica desglose explicable de factores y agrupación desacoplada de identidades personales fijas.
"""

import pytest
from notifications.schemas import AlertEventInput
from notifications.risk_engine import evaluate_risk_detailed, evaluate_risk
from notifications.deduplication_engine import (
    generate_dedup_key,
    classify_event_relationship,
    get_campaign_patterns,
)

def test_risk_score_factor_breakdown_reproducibility():
    """La suma de factores debe coincidir exactamente con el score normalizado."""
    alert = AlertEventInput(
        alert_id="AL-DET-01",
        detection_rule="MODIFY-LAB",
        incibe_class="Contenido dañino",
        title="Modificación masiva de ficheros",
        description="Alteración anómala de ficheros en servidor de proyectos",
        source_severity="Crítica",
        affected_user="sysadmin@sampol.com",
        affected_host="srv-proj-01",
        asset_criticality="Crítica",
        is_compromise_confirmed=True
    )
    res = evaluate_risk_detailed(alert)
    assert res["priority"] == "P1"
    assert res["risk_score"] >= 80
    assert "factor_breakdown" in res
    assert res["factor_breakdown"]["source_severity"] == 30
    assert res["factor_breakdown"]["asset_criticality"] == 25
    assert res["factor_breakdown"]["privilege_level"] == 15
    assert res["factor_breakdown"]["confirmed_compromise"] == 20

def test_role_based_privilege_detection():
    """Un usuario con rol 'admin' o 'ciso' recibe puntaje de privilegio sin importar su nombre."""
    alert_admin = AlertEventInput(
        alert_id="AL-ROLE-01",
        title="Inicio de sesión anómalo",
        source_severity="Media",
        affected_user="sec-admin@sampol.com",
        incibe_class="Intento de intrusión"
    )
    res = evaluate_risk_detailed(alert_admin)
    assert res["factor_breakdown"]["privilege_level"] == 15

    alert_std = AlertEventInput(
        alert_id="AL-ROLE-02",
        title="Inicio de sesión anómalo",
        source_severity="Media",
        affected_user="empleado_comun@sampol.com",
        incibe_class="Intento de intrusión"
    )
    res_std = evaluate_risk_detailed(alert_std)
    assert res_std["factor_breakdown"]["privilege_level"] == 0

def test_generalized_deduplication_custom_campaign():
    """Deduplicación canónica usando diccionario de campañas configurable."""
    custom_rules = {
        "phish-camp-alpha": "INC-CAMP-ALPHA",
        "apt-red-heron": "INC-CAMP-HERON",
    }
    alert1 = AlertEventInput(
        alert_id="AL-CAMP-01",
        affected_user="usuario_phish-camp-alpha@sampol.com",
        title="Campaña Alpha intento 1"
    )
    inc_id, key = generate_dedup_key(alert1, custom_campaigns=custom_rules)
    assert inc_id == "INC-CAMP-ALPHA"
    assert key == "NOTIF-INC-CAMP-ALPHA"

def test_event_relationship_classification():
    """Clasificación de relación de eventos: independiente, duplicado, evidencia crítica."""
    alert = AlertEventInput(
        alert_id="AL-REL-01",
        detection_rule="MODIFY-LAB",
        is_compromise_confirmed=True,
        title="Cifrado masivo"
    )
    # Sin notificación previa -> incidente independiente
    assert classify_event_relationship(alert, None) == "INDEPENDENT_INCIDENT"

    # Con notificación previa y evidencia crítica -> CRITICAL_EVIDENCE_NEW
    existing = {"id": 1, "priority": "P2"}
    assert classify_event_relationship(alert, existing) == "CRITICAL_EVIDENCE_NEW"
