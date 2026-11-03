"""
Test Suite: Clasificación de Prioridades y Motor de Riesgo (NEXUS Smart Notifications)
"""

import pytest
from notifications.schemas import AlertEventInput
from notifications.risk_engine import evaluate_risk

def test_p1_critical_account_compromise():
    """Un compromiso confirmado de cuenta privilegiada o ransomware debe ser clasificado como P1."""
    alert = AlertEventInput(
        alert_id="AL-TEST-001",
        detection_rule="MODIFY-LAB",
        incibe_class="Contenido dañino",
        title="Modificación masiva de ficheros",
        description="Alteración anómala de ficheros en servidor de proyectos",
        source_severity="Crítica",
        affected_user="cmoreno@sampol.com",
        affected_host="srv-proj-01",
        asset_criticality="Crítica",
        is_compromise_confirmed=True
    )
    score, priority, reasons, requires_action = evaluate_risk(alert)
    assert score >= 80, f"Score esperado >= 80, obtenido {score}"
    assert priority == "P1", f"Prioridad esperada P1, obtenida {priority}"
    assert requires_action is True
    assert any("Crítica" in r for r in reasons)
    assert any("MODIFY-LAB" in r for r in reasons)

def test_p1_c2_communication():
    """Tráfico C2 hacia infraestructura hostil debe clasificar como P1."""
    alert = AlertEventInput(
        alert_id="AL-TEST-002",
        detection_rule="C2-LAB",
        incibe_class="Intrusión",
        title="Conexión C2 detectada",
        description="Balizamiento hacia sync-gateway.invalid",
        source_severity="Alta",
        affected_user="amoreno@sampol.com",
        affected_host="pc-sev-03",
        asset_criticality="Alta",
        is_compromise_confirmed=True
    )
    score, priority, reasons, requires_action = evaluate_risk(alert)
    assert priority == "P1"
    assert requires_action is True

def test_p2_high_suspicious_activity():
    """Actividad sospechosa en servidor con severidad alta pero sin malware activo -> P2."""
    alert = AlertEventInput(
        alert_id="AL-TEST-003",
        detection_rule="APP-LAB",
        incibe_class="Intento de intrusión",
        title="Petición anómala a portal web",
        description="Inyección SQL interceptada por WAF",
        source_severity="Alta",
        affected_user="usuario_externo",
        affected_host="web-corp-01",
        asset_criticality="Alta",
        is_compromise_confirmed=False
    )
    score, priority, reasons, requires_action = evaluate_risk(alert)
    assert priority in ("P1", "P2"), f"Esperado P1 o P2, obtenido {priority}"
    assert requires_action is True

def test_p3_medium_routine_digest():
    """Aviso informativo o de saturación moderada -> P3."""
    alert = AlertEventInput(
        alert_id="AL-TEST-004",
        detection_rule="LOSS-LAB",
        incibe_class="Compromiso de la información",
        title="Pérdida accidental de ficheros temporales",
        description="Fallo de almacenamiento recuperado",
        source_severity="Media",
        affected_user="rgomez@sampol.com",
        affected_host="pc-pal-10",
        asset_criticality="Baja",
        is_compromise_confirmed=False
    )
    score, priority, reasons, requires_action = evaluate_risk(alert)
    assert priority in ("P3", "P4"), f"Esperado P3 o P4, obtenido {priority}"

def test_p4_low_informational_noise():
    """Escaneo de puertos sin impacto ni sesión -> P4."""
    alert = AlertEventInput(
        alert_id="AL-TEST-005",
        detection_rule="SCAN-LAB",
        incibe_class="Obtención de información",
        title="Sondeo secuencial de puertos",
        description="Tráfico descartado en perímetro",
        source_severity="Baja",
        affected_user=None,
        affected_host="gw-perim-01",
        asset_criticality="Baja",
        is_compromise_confirmed=False
    )
    score, priority, reasons, requires_action = evaluate_risk(alert)
    assert priority == "P4"
    assert requires_action is False
