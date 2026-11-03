-- ============================================================================
-- ESQUEMA DE BASE DE DATOS POSTGRESQL — EQUIPO 1 (NEXUS 2.0)
-- Hackathon FP Sampol · Reto SOC 24 Horas ("El caso del director de TI")
-- ============================================================================

-- 1. Catálogo oficial de la Guía Nacional de INCIBE
CREATE TABLE IF NOT EXISTS incibe_taxonomy (
    id SERIAL PRIMARY KEY,
    class_code VARCHAR(32) NOT NULL,
    class_name VARCHAR(128) NOT NULL,
    subtype_name VARCHAR(128) NOT NULL,
    default_danger_level VARCHAR(32) NOT NULL,
    description TEXT,
    UNIQUE(class_name, subtype_name)
);

-- 2. Almacén inmutable de correos originales (Evidencia Forense con SHA-256)
CREATE TABLE IF NOT EXISTS raw_emails (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(512) UNIQUE NOT NULL,
    conversation_id VARCHAR(255),
    sender_name VARCHAR(255),
    sender_email VARCHAR(255),
    recipients JSONB DEFAULT '[]'::jsonb,
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    headers_json JSONB DEFAULT '{}'::jsonb,
    attachments_json JSONB DEFAULT '[]'::jsonb,
    raw_payload JSONB DEFAULT '{}'::jsonb,
    raw_content_ref VARCHAR(512),
    sha256 VARCHAR(64),
    received_at_raw VARCHAR(128),
    original_timezone VARCHAR(64) DEFAULT 'UTC',
    received_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2b. Adjuntos de correo (con hash SHA-256 individual)
CREATE TABLE IF NOT EXISTS attachments (
    id SERIAL PRIMARY KEY,
    email_id INTEGER NOT NULL REFERENCES raw_emails(id) ON DELETE CASCADE,
    filename VARCHAR(512) NOT NULL,
    mime_type VARCHAR(128),
    size_bytes INTEGER DEFAULT 0,
    storage_ref VARCHAR(512),
    sha256 VARCHAR(64),
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Campañas / Incidentes correlacionados (Para Investigación Forense / Ransomware)
CREATE TABLE IF NOT EXISTS attack_campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(64) DEFAULT 'en_investigacion',
    entry_vector TEXT,
    patient_zero_user VARCHAR(255),
    patient_zero_host VARCHAR(255),
    attacker_ips JSONB DEFAULT '[]'::jsonb,
    affected_accounts JSONB DEFAULT '[]'::jsonb,
    affected_hosts JSONB DEFAULT '[]'::jsonb,
    forensic_summary TEXT,
    nis2_report_draft TEXT,
    first_seen_utc TIMESTAMPTZ,
    last_seen_utc TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Tabla principal de Alertas del SOC (Estructuradas, Categorizadas y Deduplicadas)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_code VARCHAR(64) UNIQUE NOT NULL,
    internal_alert_id VARCHAR(64),
    raw_email_id INTEGER REFERENCES raw_emails(id) ON DELETE SET NULL,
    
    -- Fechas normalizadas y zona horaria original
    event_timestamp_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_timezone_raw VARCHAR(64) DEFAULT 'UTC',
    
    -- Fuente, Regla y Gravedad
    source_tool VARCHAR(255) DEFAULT 'Desconocida',
    detection_rule VARCHAR(128),
    source_severity VARCHAR(64) DEFAULT 'N/A',
    normalized_severity VARCHAR(32) DEFAULT 'MEDIA', -- CRITICA, ALTA, MEDIA, BAJA, INFO
    
    -- Categorización Guía Nacional INCIBE
    incibe_class VARCHAR(128) NOT NULL DEFAULT 'Otros',
    incibe_type VARCHAR(128) DEFAULT 'Sin clasificar',
    incibe_danger_level VARCHAR(32) DEFAULT 'Medio', -- Muy Alto, Alto, Medio, Bajo
    incibe_impact_level VARCHAR(32) DEFAULT 'Medio', -- Crítico (OT/Planta), Alto, Medio, Bajo
    classification_justification TEXT,
    secondary_incibe_class VARCHAR(128),
    classified_by VARCHAR(128) DEFAULT 'Motor Híbrido (IA + Reglas)',
    confidence_score NUMERIC(5,2) DEFAULT 92.00,
    
    -- Entidades extraídas (Indicadores / Activos / Sede)
    affected_host VARCHAR(255),
    source_ip VARCHAR(64),
    destination_ip VARCHAR(64),
    affected_user VARCHAR(255),
    sede VARCHAR(64) DEFAULT 'No indicada',
    asset_criticality VARCHAR(64) DEFAULT 'Media',
    affected_asset_type VARCHAR(64) DEFAULT 'IT',
    ioc_list JSONB DEFAULT '[]'::jsonb,
    mitre_stage VARCHAR(128),
    
    -- Contenido limpio
    title TEXT NOT NULL,
    description TEXT,
    
    -- Estado, Deduplicación y Banderas Especiales
    status VARCHAR(32) NOT NULL DEFAULT 'nueva', -- nueva, en_revision, cerrada, falsa_alarma
    is_soc_alert BOOLEAN NOT NULL DEFAULT TRUE,
    is_noise_or_false_positive BOOLEAN NOT NULL DEFAULT FALSE,
    is_director_directive BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Gestión de duplicados (relacionados con la alerta original sin contar doble)
    is_duplicate BOOLEAN NOT NULL DEFAULT FALSE,
    parent_alert_id INTEGER REFERENCES alerts(id) ON DELETE SET NULL,
    duplicate_count INTEGER NOT NULL DEFAULT 1,
    fingerprint VARCHAR(255),
    
    -- Seguridad de IA (Anti-Prompt Injection)
    prompt_injection_detected BOOLEAN NOT NULL DEFAULT FALSE,
    prompt_injection_evidence TEXT,
    
    -- Correlación Forense
    attack_campaign_id INTEGER REFERENCES attack_campaigns(id) ON DELETE SET NULL,
    
    -- Métricas de Negocio / ROI
    processing_time_ms INTEGER DEFAULT 250,
    estimated_manual_minutes NUMERIC(6,2) DEFAULT 10.00,
    reviewed_by_human BOOLEAN NOT NULL DEFAULT FALSE,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Historial de Auditoría de Cambios (Trazabilidad completa)
CREATE TABLE IF NOT EXISTS alert_audit_log (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    changed_by VARCHAR(128) NOT NULL,
    action_type VARCHAR(64) NOT NULL, -- CREACION, CAMBIO_CATEGORIA, CAMBIO_ESTADO, MARCADO_DUPLICADO, ACCION_SOAR
    field_changed VARCHAR(64),
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Registro de Acciones SOAR (con aprobación humana e idempotencia)
CREATE TABLE IF NOT EXISTS soar_actions (
    id SERIAL PRIMARY KEY,
    external_block_id INTEGER,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE SET NULL,
    action VARCHAR(32) NOT NULL, -- bloquear, liberar
    target_type VARCHAR(32) NOT NULL, -- ip, usuario
    target_value VARCHAR(255) NOT NULL,
    trigger_mode VARCHAR(32) NOT NULL DEFAULT 'manual', -- automatico, manual, sincronizado, orden_soc
    status VARCHAR(32) NOT NULL DEFAULT 'ejecutado', -- pendiente_aprobacion, aprobado, ejecutado, liberado, rechazado_whitelist, error
    requested_by VARCHAR(128) DEFAULT 'Responsable SOC / Analista',
    approved_by VARCHAR(128),
    idempotency_key VARCHAR(255) UNIQUE,
    api_status_code INTEGER,
    api_response JSONB DEFAULT '{}'::jsonb,
    reason TEXT,
    executed_by VARCHAR(128) DEFAULT 'Sistema SOAR NEXUS',
    time_saved_minutes NUMERIC(6,2) DEFAULT 15.00,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Lista Blanca (Whitelist) de Activos Críticos OT/IT y VIPs (Anti Auto-Sabotaje)
CREATE TABLE IF NOT EXISTS protected_assets_whitelist (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(32) NOT NULL, -- ip, usuario, hostname
    asset_value VARCHAR(255) UNIQUE NOT NULL,
    asset_category VARCHAR(64) DEFAULT 'OT_PLANTA', -- OT_PLANTA, VIP_DIRECCION, INFRA_CRITICA
    description TEXT NOT NULL,
    requires_manual_approval BOOLEAN NOT NULL DEFAULT TRUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Registro de Directrices del Director de TI (18:00, 20:00, 00:00, 08:00)
CREATE TABLE IF NOT EXISTS director_directives (
    id SERIAL PRIMARY KEY,
    directive_number INTEGER,
    received_at_utc TIMESTAMPTZ DEFAULT NOW(),
    raw_email_id INTEGER REFERENCES raw_emails(id) ON DELETE SET NULL,
    subject TEXT NOT NULL,
    request_summary TEXT NOT NULL,
    team_response TEXT,
    implemented_features TEXT,
    status VARCHAR(32) DEFAULT 'pendiente',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Parámetros de Negocio y Costes (Para cálculo dinámico de ROI en el Cuadro de Mando)
CREATE TABLE IF NOT EXISTS business_parameters (
    param_key VARCHAR(64) PRIMARY KEY,
    param_value NUMERIC(12,2) NOT NULL,
    unit VARCHAR(32) NOT NULL,
    description TEXT NOT NULL,
    source VARCHAR(128) DEFAULT 'Estimación inicial (ajustable con datos del Director)',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_alerts_event_ts ON alerts(event_timestamp_utc DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_incibe_class ON alerts(incibe_class);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_is_duplicate ON alerts(is_duplicate);
CREATE INDEX IF NOT EXISTS idx_alerts_affected_user ON alerts(affected_user);
CREATE INDEX IF NOT EXISTS idx_alerts_affected_host ON alerts(affected_host);
CREATE INDEX IF NOT EXISTS idx_alerts_source_ip ON alerts(source_ip);
CREATE INDEX IF NOT EXISTS idx_alerts_fingerprint ON alerts(fingerprint);
CREATE INDEX IF NOT EXISTS idx_alerts_sede ON alerts(sede);

-- Vistas
CREATE OR REPLACE VIEW v_soc_unique_alerts AS
SELECT *
FROM alerts
WHERE is_soc_alert = TRUE
  AND is_duplicate = FALSE;

CREATE OR REPLACE VIEW v_forensic_timeline AS
SELECT
    a.id AS alert_id,
    a.alert_code,
    a.internal_alert_id,
    a.event_timestamp_utc,
    a.event_timezone_raw,
    a.normalized_severity,
    a.incibe_class,
    a.incibe_type,
    a.mitre_stage,
    a.source_tool,
    a.detection_rule,
    a.sede,
    a.asset_criticality,
    a.affected_user,
    a.affected_host,
    a.source_ip,
    a.destination_ip,
    a.title,
    a.description,
    a.is_duplicate,
    a.duplicate_count,
    a.prompt_injection_detected,
    r.sender_email,
    r.subject AS email_subject,
    r.sha256 AS email_sha256,
    r.attachments_json
FROM alerts a
LEFT JOIN raw_emails r ON a.raw_email_id = r.id
WHERE a.is_soc_alert = TRUE
ORDER BY a.event_timestamp_utc ASC;
