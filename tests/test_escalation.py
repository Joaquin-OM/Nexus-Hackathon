"""
Test Suite: Escalado Jerárquico por Incidente No Reconocido (NEXUS Smart Notifications)
"""

from datetime import datetime, timedelta, timezone
import pytest
from notifications.escalation_engine import check_and_escalate_notification

def test_p1_unacknowledged_escalation_level_1():
    now = datetime.now(timezone.utc)
    notif = {
        "id": 101,
        "incident_id": "INC-TEST-MORENO",
        "priority": "P1",
        "status": "active",
        "created_at": now - timedelta(minutes=16),
        "escalation_level": 0
    }
    res = check_and_escalate_notification(notif, now=now)
    assert res is not None
    assert res["escalation_level"] == 1
    assert res["new_recipient_id"] == "guardia_soc@sampol.com"

def test_p1_unacknowledged_escalation_level_2():
    now = datetime.now(timezone.utc)
    notif = {
        "id": 102,
        "incident_id": "INC-TEST-MORENO",
        "priority": "P1",
        "status": "escalated",
        "created_at": now - timedelta(minutes=35),
        "escalation_level": 1
    }
    res = check_and_escalate_notification(notif, now=now)
    assert res is not None
    assert res["escalation_level"] == 2
    assert res["new_recipient_id"] == "supervisor_soc@sampol.com"

def test_p1_unacknowledged_escalation_level_3_director():
    now = datetime.now(timezone.utc)
    notif = {
        "id": 103,
        "incident_id": "INC-TEST-MORENO",
        "priority": "P1",
        "status": "escalated",
        "created_at": now - timedelta(minutes=65),
        "escalation_level": 2
    }
    res = check_and_escalate_notification(notif, now=now)
    assert res is not None
    assert res["escalation_level"] == 3
    assert res["new_recipient_id"] == "dirti@sampol.com"

def test_acknowledged_notification_does_not_escalate():
    now = datetime.now(timezone.utc)
    notif = {
        "id": 104,
        "incident_id": "INC-TEST-MORENO",
        "priority": "P1",
        "status": "acknowledged", # Ya fue reconocida por el analista
        "created_at": now - timedelta(minutes=50),
        "escalation_level": 0
    }
    res = check_and_escalate_notification(notif, now=now)
    assert res is None

def test_p3_does_not_escalate():
    now = datetime.now(timezone.utc)
    notif = {
        "id": 105,
        "incident_id": "INC-TEST-DIGEST",
        "priority": "P3",
        "status": "active",
        "created_at": now - timedelta(minutes=120),
        "escalation_level": 0
    }
    res = check_and_escalate_notification(notif, now=now)
    assert res is None
