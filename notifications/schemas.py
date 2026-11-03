"""
NEXUS Smart Notifications — Modelos Pydantic (Contratos de Datos)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

PriorityLevel = Literal["P1", "P2", "P3", "P4"]
NotificationStatus = Literal["active", "acknowledged", "escalated", "dismissed", "resolved"]
DeliveryStatus = Literal["pending", "delivered", "read", "failed"]

class AlertEventInput(BaseModel):
    alert_id: str = Field(..., description="ID externo o código de alerta (ej: AL-20261030-0045 o SOC-...)")
    incident_id: Optional[str] = Field(None, description="ID del incidente o campaña relacionada (ej: INC-CAMP-MORENO)")
    source_tool: str = Field("SOC-Sensor", description="Herramienta origen (EDR, NGFW, EntraID, etc.)")
    detection_rule: Optional[str] = Field("", description="Regla detectora (ej: ACCOUNT-LAB, SPRAY-LAB)")
    incibe_class: Optional[str] = Field("Otros", description="Clasificación según taxonomía INCIBE")
    title: str = Field(..., description="Título de la alerta")
    description: str = Field("", description="Detalle descriptivo de la alerta")
    source_severity: str = Field("Media", description="Severidad original (Crítica, Alta, Media, Baja, Info)")
    affected_user: Optional[str] = Field(None, description="Cuenta de usuario comprometida / afectada")
    affected_host: Optional[str] = Field(None, description="Host o equipo afectado")
    source_ip: Optional[str] = Field(None, description="Dirección IP de origen")
    destination_ip: Optional[str] = Field(None, description="Dirección IP de destino")
    asset_criticality: str = Field("Media", description="Criticidad del activo: Crítica, Alta, Media, Baja")
    sede: Optional[str] = Field("Palma de Mallorca", description="Sede Sampol afectada")
    is_compromise_confirmed: bool = Field(False, description="Evidencia confirmada de compromiso efectivo")
    significant_change: bool = Field(False, description="Bandera que fuerza notificación inmediata por cambio crítico")

class RiskEvaluationResult(BaseModel):
    incident_id: str
    risk_score: int = Field(..., ge=0, le=100)
    priority: PriorityLevel
    reasons: List[str]
    requires_human_action: bool
    should_notify: bool
    action: Literal["notify", "update_existing", "already_processed", "suppressed_cooldown", "queued_digest"]

class NotificationRecipientOut(BaseModel):
    user_id: str
    role: str
    delivery_status: DeliveryStatus
    delivered_at: datetime
    read_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

class NotificationOut(BaseModel):
    id: int
    incident_id: str
    notification_type: str
    priority: PriorityLevel
    risk_score: int
    title: str
    message: str
    affected_asset: Optional[str] = None
    affected_user: Optional[str] = None
    event_count: int
    first_event_at: datetime
    last_event_at: datetime
    dedup_key: str
    reasons: List[str]
    requires_human_action: bool
    status: NotificationStatus
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    last_notified_at: datetime
    created_at: datetime
    updated_at: datetime
    recipients: Optional[List[NotificationRecipientOut]] = []

class NotificationAcknowledgeRequest(BaseModel):
    actor_id: str = Field("analista_guardia@sampol.com", description="Identificador del usuario que reconoce el aviso")
    comment: Optional[str] = Field(None, description="Observaciones opcionales del reconocimiento")

class NotificationPreferencesIn(BaseModel):
    enabled_priorities: List[PriorityLevel] = ["P1", "P2", "P3"]
    in_app_enabled: bool = True
    push_enabled: bool = False
    digest_frequency: Literal["realtime", "hourly", "shift", "daily", "none"] = "shift"
    quiet_hours: Dict[str, Any] = {"enabled": False, "start": "22:00", "end": "07:00"}
    timezone: str = "Europe/Madrid"

class NotificationPreferencesOut(NotificationPreferencesIn):
    user_id: str
    updated_at: datetime

class UnreadCountOut(BaseModel):
    total_unread: int
    total_unacknowledged: int
    p1_critical_count: int
    p2_high_count: int
    has_critical_unacknowledged: bool

class NoiseReductionMetricsOut(BaseModel):
    total_raw_emails: int
    total_alerts: int
    deduplicated_alerts: int
    total_notifications_issued: int
    p1_critical_count: int
    p2_high_count: int
    p3_medium_count: int
    p4_low_count: int
    acknowledged_count: int
    escalations_count: int
    noise_reduction_percentage: float
    formula_explanation: str
