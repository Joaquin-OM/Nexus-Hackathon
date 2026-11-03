"""
Test Suite: Deduplicación, Cooldown y Anti-Saturación (NEXUS Smart Notifications)
"""

from datetime import datetime, timedelta, timezone
import pytest
from notifications.schemas import AlertEventInput
from notifications.deduplication_engine import generate_dedup_key, evaluate_anti_saturation

def test_deterministic_dedup_key():
    alert1 = AlertEventInput(
        alert_id="AL-001",
        affected_user="bmoreno@sampol.com",
        title="Intento de acceso 1"
    )
    alert2 = AlertEventInput(
        alert_id="AL-002",
        affected_user="bmoreno@sampol.com",
        title="Intento de acceso 2"
    )
    inc1, key1 = generate_dedup_key(alert1)
    inc2, key2 = generate_dedup_key(alert2)

    assert inc1 == inc2 == "INC-CAMP-MORENO"
    assert key1 == key2 == "NOTIF-INC-CAMP-MORENO"

def test_initial_p1_notification():
    """Un incidente P1 nuevo debe notificarse de inmediato."""
    should_notify, action = evaluate_anti_saturation(
        current_priority="P1",
        existing_notification=None
    )
    assert should_notify is True
    assert action == "notify"

def test_initial_p3_queued_digest():
    """Un evento P3 nuevo entra a la cola de digest sin interrumpir."""
    should_notify, action = evaluate_anti_saturation(
        current_priority="P3",
        existing_notification=None
    )
    assert should_notify is False
    assert action == "queued_digest"

def test_burst_suppression_within_cooldown():
    """Llegada de alertas masivas P2 en ráfaga (ej: 50 en 2 minutos) no genera 50 notificaciones."""
    now = datetime.now(timezone.utc)
    existing = {
        "id": 10,
        "priority": "P2",
        "last_notified_at": now - timedelta(minutes=2),
        "status": "active"
    }
    # Segunda alerta recibida 2 min después (cooldown P2 es 15 min)
    should_notify, action = evaluate_anti_saturation(
        current_priority="P2",
        existing_notification=existing,
        now=now
    )
    assert should_notify is False
    assert action == "burst_suppressed_update"

def test_escalation_bypasses_cooldown():
    """Si un incidente P3 o P2 escala a P1, se debe notificar INMEDIATAMENTE sin importar el cooldown."""
    now = datetime.now(timezone.utc)
    existing = {
        "id": 11,
        "priority": "P3",
        "last_notified_at": now - timedelta(minutes=1),
        "status": "active"
    }
    should_notify, action = evaluate_anti_saturation(
        current_priority="P1",
        existing_notification=existing,
        now=now
    )
    assert should_notify is True
    assert action == "escalated_priority_notify"

def test_significant_change_forces_notification():
    """Bandera significant_change fuerza aviso de inmediato."""
    now = datetime.now(timezone.utc)
    existing = {
        "id": 12,
        "priority": "P2",
        "last_notified_at": now - timedelta(minutes=1),
        "status": "active"
    }
    should_notify, action = evaluate_anti_saturation(
        current_priority="P2",
        existing_notification=existing,
        significant_change=True,
        now=now
    )
    assert should_notify is True
    assert action == "significant_change_notify"
