# NEXUS SOC 2.0 — Intelligent Security Operations
### Hackathon SAMPOL 2026 (24 Horas) · Equipo 1

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Portal-0784B7?style=for-the-badge&logo=github)](https://joaquin-om.github.io/Nexus-Hackathon/)
[![Azure PostgreSQL](https://img.shields.io/badge/Azure-PostgreSQL%2018.6-336791?style=for-the-badge&logo=postgresql)](https://portal.azure.com/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20REST-009688?style=for-the-badge&logo=fastapi)](http://127.0.0.1:8000/docs)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit%20SOC-42A83B?style=for-the-badge&logo=streamlit)](http://localhost:8501)
[![Tests Passing](https://img.shields.io/badge/Tests-35%2F35%20Passing-16A34A?style=for-the-badge)](tests/)

> **Portal Web Corporativo en Vivo:**  
> **[https://joaquin-om.github.io/Nexus-Hackathon/](https://joaquin-om.github.io/Nexus-Hackathon/)**  
> *(Identidad empresarial SAMPOL, 0 emojis, iconografía técnica Lucide, diseño responsive verificado en 320px–1920px, gestión operativa de incidentes, vista dual Tabla/Kanban, visor forense, simulador anti-fatiga y calculadora financiera de ROI).*

---

## 1. Resumen Ejecutivo de la Solución
**NEXUS SOC 2.0** es la plataforma corporativa de gestión de alertas, investigación pericial y contención autónoma desarrollada por el **Equipo 1** para las operaciones de **SAMPOL**:

1. **Ingesta Continua y Evidencia Inmutable:** Sincronización continua con Microsoft Graph API sobre el buzón corporativo (`equipo_1_hackaton@sampol.com`), generando hashes criptográficos `SHA-256` inmutables por cada mensaje con custodia forense RFC 822.
2. **Triaje y Taxonomía Nacional INCIBE (10 Clases):** Motor de clasificación que encuadra cada evento en la taxonomía nacional de ciberseguridad con justificaciones técnicas y separación estricta entre severidad de origen, criticidad de activo y prioridad de incidente.
3. **NEXUS Smart Notifications & Motor Anti-Fatiga:** Transforma el volumen de alertas brutas en **incidentes consolidados** (reducción del 65% de ruido operativo) mediante agrupación por vector, ventanas de *cooldown* y matriz de riesgo explicable P1–P4 con SLA de 15 minutos para incidentes críticos.
4. **Contención Autónoma y Salvaguardas SOAR (Directriz 1):** Orquestación conectada a la API de Azure (`/equipo-1/bloquear`), con control de idempotencia estricto y **Lista Blanca protegida** que blinda a la dirección (`director.ti@sampol.com`) y redes industriales OT/SCADA frente a desconexiones erróneas.
5. **Seguridad y Control de Acceso por Roles (RBAC):** Autenticación validada en servidor con tokens HMAC-SHA256, autorización RBAC (`Analista SOC`, `Supervisor SOC`, `Responsable de TI`, `Administrador`), restricción estricta de CORS y canales SSE privados por usuario.
6. **Cumplimiento Normativo NIS2 (INCIBE-CERT):** Generación automática de la pre-notificación formal en menos de 24 horas conforme al Artículo 23 de la Directiva Europea NIS2.
7. **Caso de Negocio y Modelo Financiero (ROI):** Ahorro operativo y retorno de inversión cuantificado mediante sliders paramétricos en el módulo independiente de Finanzas.

---

## 2. Métricas y Veracidad de Datos (Auditoría del Sistema)

Para garantizar la máxima transparencia técnica, el sistema distingue rigurosamente entre **datos reales persistidos en base de datos** y **proyecciones/estimaciones de negocio**:

### A. Datos Operativos Reales (Base de Datos Azure PostgreSQL `alertas-soc-1`)
| Métrica Operativa | Valor Real | Fuente / Método de Cálculo |
| :--- | :---: | :--- |
| **Correos Ingeridos en Buzón** | **142** | Conteo exacto en tabla `raw_emails` con hash SHA-256 |
| **Alertas SOC Únicas** | **93** | Vista `v_soc_unique_alerts` (filtrando ruido administrativo y duplicados) |
| **Incidentes Consolidados** | **50** | Tabla `notifications` tras agrupación canónica y deduplicación |
| **Incidentes Críticos P1** | **8** | Incidentes con score de riesgo ≥ 80 o precursor confirmado |
| **Acciones SOAR Registradas** | **62** | Registros en tabla `soar_actions` (bloqueos, liberaciones y verificaciones) |
| **Cuentas Contenidas Autónomas** | **13** | Ejecutadas bajo Directriz 1 tras confirmar compromiso efectivo |
| **Salvaguardas Whitelist Activas** | **100%** | Activos OT y cuentas clave blindadas en `protected_assets_whitelist` |

### B. Especificaciones de Diseño y Capacidad de Escala
- **Capacidad de Ingesta Sostenida:** Diseñado y validado para procesar hasta **200.000 alertas diarias** (equivalente a una media sostenida de **2,31 alertas por segundo**, con capacidad de absorción de ráfagas en memoria evaluada en `test_noise_reduction_scale.py`).
- **Supresión de Ruido:** Reducción de fatiga del analista en más del **65% en volumen de avisos directos**, derivando eventos P3 a cola de trabajo y P4 a registro silencioso.

### C. Proyecciones Financieras (Módulo de Finanzas)
*Nota: Las cifras económicas corresponden a proyecciones basadas en las hipótesis y parámetros operativos facilitados por el Director de TI (3.000 alertas/mes, 12 min tiempo medio manual, 27 €/h coste empresa).*
- **Ahorro Bruto Estimado:** ~184.500 € / año en horas liberadas de analistas de primer nivel.
- **Retorno de Inversión (ROI):** > 2.000% sobre coste de infraestructura cloud y desarrollo.
- **Payback Estimado:** 1,3 meses (~40 días).

---

## 3. Arquitectura de Seguridad y Control de Acceso (RBAC)

NEXUS SOC 2.0 implementa una arquitectura defensiva en profundidad:

```
[ Cliente Web / Dashboard ]
           │
           ▼
[ Capa de Seguridad (security.py) ]
  ├── CORS Restringido (Dominios explícitos, no wildcard)
  ├── Validación de Tokens HMAC-SHA256 (Bearer)
  ├── Modo Demostración Seguro (NEXUS_DEMO_MODE=true) con directorio @sampol.com
  └── Matriz RBAC (Analista SOC, Supervisor SOC, Responsable TI, Administrador)
           │
           ▼
[ Endpoints FastAPI (backend_api.py + notifications/router.py) ]
  ├── GET /api/smart-notifications (Aislamiento por usuario y rol)
  ├── POST /alerts/{id} [PATCH] (Requiere Supervisor SOC o Admin)
  ├── POST /soar/approve (Requiere Supervisor SOC o Responsable TI)
  └── GET /api/smart-notifications/stream (SSE privado por suscripción en memoria)
```

---

## 4. Puesta en Marcha Rápida

### Prerrequisitos
- Python 3.10+ o [`uv`](https://github.com/astral-sh/uv) (recomendado)
- Acceso a base de datos PostgreSQL

### 1. Clonar el repositorio
```bash
git clone https://github.com/Joaquin-OM/Nexus-Hackathon.git
cd Nexus-Hackathon
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y ajusta las credenciales:
```bash
cp .env.example .env
```
Variables clave:
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`: Conexión Azure PostgreSQL.
- `SOAR_API_URL`, `SOAR_API_KEY`: Endpoint de la API Bloqueador del hackathon.
- `NEXUS_DEMO_MODE`: `true` para modo demostración / evaluación local.
- `NEXUS_AUTH_SECRET`: Clave secreta para firma de tokens HMAC.

### 3. Ejecutar la Suite Completa de Tests (35 Tests)
```bash
uv run --with pytest --with fastapi --with pydantic --with pg8000 --with httpx pytest -o pythonpath=. tests/
```

### 4. Iniciar el Backend API (FastAPI)
```bash
uv run --with pg8000 --with fastapi --with uvicorn uvicorn backend_api:app --host 127.0.0.1 --port 8000
```
Documentación OpenAPI Swagger: `http://127.0.0.1:8000/docs`

### 5. Iniciar el Cuadro de Mando de Investigación (Streamlit)
```bash
uv run --with pg8000 --with fastapi --with uvicorn --with streamlit --with pandas streamlit run dashboard.py --server.port 8501
```

### 6. Iniciar el Daemon de Sincronización Continua
```bash
uv run --with pg8000 python daemon_sync.py
```

---

## 5. Estructura de Suites de Pruebas Automatizadas

| Suite de Pruebas | Archivo | Casos | Aspectos Validados |
| :--- | :--- | :---: | :--- |
| **Seguridad y RBAC** | `test_security_auth_rbac.py` | 5 | Orígenes CORS, prevención de spoofing `X-User-Id`, roles Analista vs Supervisor, verificación criptográfica de tokens. |
| **Calidad y Sanitización de Datos** | `test_data_validation_sanitization.py` | 5 | Neutralización de canarios de Prompt Injection (`HN03`), sintaxis de hosts, validación de emails y reconstrucción de IPs sin puntos. |
| **Riesgo y Deduplicación** | `test_generalized_risk_dedup.py` | 4 | Desglose modular de factores de riesgo, privilegios por rol desacoplados de nombres, campañas configurables. |
| **Salvaguardas SOAR** | `test_soar_safeguards_mock.py` | 3 | Protección inviolable de lista blanca OT/IT, idempotencia de órdenes y verificación de errores HTTP 500 de API externa. |
| **Priorización de Incidentes** | `test_prioritization.py` | 5 | Clasificación P1 (compromiso de identidad/C2), P2, P3 y P4. |
| **Deduplicación y Cooldown** | `test_deduplication_cooldown.py` | 6 | Amortiguación de ráfagas, escaladas inmediatas sin cooldown, claves estables. |
| **Escalado Anti-Fatiga** | `test_escalation.py` | 5 | Escalado jerárquico L1 -> L2 -> Director TI ante incidentes P1 desatendidos. |
| **Capacidad de Escala** | `test_noise_reduction_scale.py` | 2 | Simulación de ráfagas de 5.000 alertas y throughput de diseño. |

---

## 6. Documentación y Entregables Oficiales

- **[GUION_PITCH_5_MINUTOS.md](GUION_PITCH_5_MINUTOS.md):** Guion estructurado para la defensa ante el tribunal del hackathon.
- **[PITCH_DECK_HACKATHON_SAMPOL.pptx](PITCH_DECK_HACKATHON_SAMPOL.pptx):** Presentación ejecutiva oficial en PowerPoint.
- **[MODELO_FINANCIERO_ROI_SAMPOL.xlsx](MODELO_FINANCIERO_ROI_SAMPOL.xlsx):** Modelo financiero completo en Excel con fórmulas vivas.
- **[INFORME_EJECUTIVO_PLAN_INDUSTRIALIZACION_NEXUS_2_0.docx](INFORME_EJECUTIVO_PLAN_INDUSTRIALIZACION_NEXUS_2_0.docx):** Memoria ejecutiva e industrialización.
- **[INFORME_FORENSE_KILL_CHAIN.docx](INFORME_FORENSE_KILL_CHAIN.docx):** Reconstrucción pericial de la Kill Chain y cronología del incidente.
- **[PRENOTIFICACION_INCIDENTE_NIS2_INCIBE_CERT.docx](PRENOTIFICACION_INCIDENTE_NIS2_INCIBE_CERT.docx):** Pre-notificación oficial bajo la Directiva Europea NIS2.
- **[PLAN_MAESTRO_NEXUS_2_0_ACTUALIZADO.md](PLAN_MAESTRO_NEXUS_2_0_ACTUALIZADO.md):** Documento técnico maestro de arquitectura.
- **[index.html](index.html):** Portal web estático responsive publicado en GitHub Pages con identidad visual corporativa SAMPOL.
