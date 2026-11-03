"""Prototype FastAPI router. Uses an in-memory store; replace with PostgreSQL for deployment."""
from datetime import datetime, timedelta, timezone
from threading import Lock
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix='/api/smart-notifications', tags=['smart-notifications'])
_lock = Lock()
_notifications = {}

class AlertInput(BaseModel):
    alert_id: str
    incident_id: str
    title: str
    description: str = ''
    risk_score: int = Field(ge=0, le=100)
    asset_criticality: str = 'medium'
    significant_change: bool = False


def classify(alert: AlertInput) -> str:
    if alert.risk_score >= 90 or (alert.risk_score >= 75 and alert.asset_criticality == 'critical'):
        return 'P1'
    if alert.risk_score >= 70:
        return 'P2'
    if alert.risk_score >= 40:
        return 'P3'
    return 'P4'

@router.post('/evaluate')
def evaluate(alert: AlertInput):
    """Demo ingestion endpoint. PROTECT with service authentication before exposure."""
    priority = classify(alert)
    key = alert.incident_id
    now = datetime.now(timezone.utc)
    with _lock:
        old = _notifications.get(key)
        if old and alert.alert_id in old['alert_ids']:
            return {'action': 'already_processed', 'notification_id': key}
        if old:
            old['alert_ids'].add(alert.alert_id)
            old['count'] += 1
            old['description'] = alert.description
            previous_priority = old['priority']
            if int(priority[1]) < int(previous_priority[1]):
                old['priority'] = priority
            should_notify = alert.significant_change or (int(priority[1]) < int(previous_priority[1]))
            if not should_notify and priority in ('P1','P2') and (now-old['last_notified_at']) >= timedelta(minutes=15):
                should_notify = True
            if should_notify:
                old['acknowledged'] = False
                old['last_notified_at'] = now
            return {'action': 'notify' if should_notify else 'update_existing', 'notification_id': key}
        _notifications[key] = {'id':key,'incident_id':key,'title':alert.title,'description':alert.description,'priority':priority,'count':1,'alert_ids':{alert.alert_id},'acknowledged':False,'last_notified_at':now}
        return {'action':'notify' if priority in ('P1','P2') else 'queue','notification_id':key}

@router.get('')
def list_notifications():
    with _lock:
        return [{'id':n['id'],'incident_id':n['incident_id'],'title':n['title'],'description':n['description'],'priority':n['priority'],'count':n['count'],'acknowledged':n['acknowledged']} for n in _notifications.values()]

@router.post('/{notification_id}/acknowledge')
def acknowledge(notification_id: str):
    """DEMO ONLY: add authentication and recipient authorization before production."""
    with _lock:
        n = _notifications.get(notification_id)
        if not n:
            raise HTTPException(404, 'Notification not found')
        n['acknowledged'] = True
        return {'ok':True,'id':notification_id}
