# NEXUS SOC 2.0 — Intelligent Security Operations
### Hackathon SAMPOL 2026 (24 Horas) · Equipo 1

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Portal-0784B7?style=for-the-badge&logo=github)](https://joaquin-om.github.io/Nexus-Hackathon/)
[![Azure PostgreSQL](https://img.shields.io/badge/Azure-PostgreSQL%2018.6-336791?style=for-the-badge&logo=postgresql)](https://portal.azure.com/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20REST-009688?style=for-the-badge&logo=fastapi)](http://127.0.0.1:8000/docs)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit%20SOC-42A83B?style=for-the-badge&logo=streamlit)](http://localhost:8501)
[![Tests Passing](https://img.shields.io/badge/Tests-18%2F18%20Passing-16A34A?style=for-the-badge)](tests/)

> **Portal Web Corporativo en Vivo:**  
> **[https://joaquin-om.github.io/Nexus-Hackathon/](https://joaquin-om.github.io/Nexus-Hackathon/)**  
> *(Diseño empresarial SAMPOL, 0 emojis, iconografía Lucide, responsive móvil/escritorio, visor forense, simulador anti-fatiga y calculadora financiera de ROI).*

---

## 1. Resumen Ejecutivo de la Solución
**NEXUS SOC 2.0** es la plataforma de gestión de alertas, investigación y contención autónoma desarrollada por el **Equipo 1** para el entorno corporativo de **SAMPOL**, capaz de procesar avalanchas de hasta **200.000 alertas diarias** sin fatiga para el analista:

1. **Ingesta Continua e Inmutable:** Sincronización continua con Microsoft Graph API sobre el buzón corporativo (`equipo_1_hackaton@sampol.com`), generando hashes `SHA-256` inmutables por cada mensaje con custodia forense RFC 822.
2. **Triaje y Clasificación Oficial INCIBE (10 Clases):** Motor de clasificación que mapea cada evento a la taxonomía nacional de ciberseguridad (Intrusión, Fraude, Contenido dañino, Disponibilidad, Compromiso de información, Intento de intrusión, Vulnerable, Obtención de información, Contenido abusivo y Otros).
3. **NEXUS Smart Notifications & Motor Anti-Fatiga:** Transforma 142 alertas brutas en **50 incidentes consolidados** (reducción del 65% de ruido) agrupando por vector de ataque, ventanas de *cooldown* y matriz de riesgo P1–P4 con SLA de 15 minutos para incidentes críticos.
4. **Respuesta a la Directriz 1 (SOAR Auto-Blocker):** Contención inmediata y automática conectada a la API de Azure (`/equipo-1/bloquear`), con **62 acciones ejecutadas**, control de idempotencia y **Lista Blanca estricta** que protege a la dirección (`director.ti@sampol.com`) e infraestructuras industriales OT de desconexiones accidentales.
5. **Cumplimiento Normativo NIS2 (INCIBE-CERT):** Generación automática de la pre-notificación en menos de 24 horas conforme al Artículo 23 de la Directiva Europea NIS2, con impacto de 0 horas de parada de servicio.
6. **Caso de Negocio y Modelo Financiero (ROI):** Ahorro operativo anual de **184.500 €**, retorno de inversión (ROI) del **2.010%** y periodo de recuperación (*Payback*) en **1.3 meses** (40 días) frente a soluciones comerciales.

---

## 2. Estado Operativo en Producción (Azure PostgreSQL `alertas-soc-1`)

| Métrica | Valor | Observaciones Técnicas |
| :--- | :---: | :--- |
| **Correos Totales Ingeridos (`raw_emails`)** | **142** | Hash criptográfico `SHA-256` inmutable verificado |
| **Alertas SOC Únicas (`alerts`)** | **93** | Clasificadas según taxonomía INCIBE y criticidad de activo |
| **Incidentes Consolidados (Smart Notifications)** | **50** | Reducción del 65% del ruido operativo |
| **Avisos P1 Críticos (SLA 15m)** | **8** | Con escalado jerárquico automático a guardia SOC |
| **Contenciones SOAR Ejecutadas (`soar_actions`)** | **62** | Claves de idempotencia y trazabilidad de órdenes `SOL-B` / `SOL-L` |
| **Cuentas y Vectores Contenidos** | **13** | Contención autónoma previa a órdenes manuales humanas |
| **Salvaguardas de Lista Blanca Activas** | **100%** | Exclusión de VIPs y redes OT frente a bloqueos no autorizados |
| **Ahorro Anual Neto Estimado** | **184.500 €** | Calculado en base a costes y tiempos del Director de TI |

---

## 3. Puesta en Marcha Rápida

### Prerrequisitos
- Python 3.10+ o [`uv`](https://github.com/astral-sh/uv) (recomendado)
- Conexión a Azure PostgreSQL

### 1. Clonar el repositorio
```bash
git clone https://github.com/Joaquin-OM/Nexus-Hackathon.git
cd Nexus-Hackathon
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y rellena las credenciales requeridas:
```bash
cp .env.example .env
```

### 3. Ejecutar la Suite de Pruebas Automatizadas
```bash
uv run --with pytest --with fastapi --with pydantic --with pg8000 pytest -o pythonpath=. tests/
# 18 passed in 0.5s
```

### 4. Iniciar el Backend API (FastAPI)
```bash
uv run --with pg8000 --with fastapi --with uvicorn uvicorn backend_api:app --host 127.0.0.1 --port 8000
```
Swagger interactivo disponible en: `http://127.0.0.1:8000/docs`

### 5. Iniciar el Cuadro de Mando de Investigación (Streamlit)
```bash
uv run --with pg8000 --with fastapi --with uvicorn --with streamlit --with pandas streamlit run dashboard.py --server.port 8501
```
Abre en tu navegador: `http://localhost:8501`

### 6. Iniciar el Daemon de Sincronización Continua
```bash
uv run --with pg8000 python daemon_sync.py
```

---

## 4. Documentación y Entregables Oficiales

- **[GUION_PITCH_5_MINUTOS.md](GUION_PITCH_5_MINUTOS.md):** Guion cronometrado de 300 segundos para la defensa ante el tribunal.
- **[PITCH_DECK_HACKATHON_SAMPOL.pptx](PITCH_DECK_HACKATHON_SAMPOL.pptx):** Presentación ejecutiva oficial en diapositivas PowerPoint.
- **[MODELO_FINANCIERO_ROI_SAMPOL.xlsx](MODELO_FINANCIERO_ROI_SAMPOL.xlsx):** Modelo financiero completo en Excel con fórmulas vivas.
- **[INFORME_EJECUTIVO_PLAN_INDUSTRIALIZACION_NEXUS_2_0.docx](INFORME_EJECUTIVO_PLAN_INDUSTRIALIZACION_NEXUS_2_0.docx):** Memoria ejecutiva e industrialización.
- **[INFORME_FORENSE_KILL_CHAIN.docx](INFORME_FORENSE_KILL_CHAIN.docx):** Reconstrucción pericial de la Kill Chain y cronología del incidente.
- **[PRENOTIFICACION_INCIDENTE_NIS2_INCIBE_CERT.docx](PRENOTIFICACION_INCIDENTE_NIS2_INCIBE_CERT.docx):** Pre-notificación oficial bajo el Artículo 23 de la Directiva NIS2.
- **[PLAN_MAESTRO_NEXUS_2_0_ACTUALIZADO.md](PLAN_MAESTRO_NEXUS_2_0_ACTUALIZADO.md):** Documento técnico maestro de arquitectura.
- **[schema.sql](schema.sql) y [notifications_schema.sql](notifications_schema.sql):** Esquemas DDL para PostgreSQL en Azure.
- **[index.html](index.html):** Portal web estático responsive publicado en GitHub Pages con identidad visual corporativa SAMPOL.

---

## 5. Arquitectura del Sistema

```
                        ┌─────────────────────────────────────┐
                        │     Microsoft Graph API (Outlook)   │
                        │    equipo_1_hackaton@sampol.com     │
                        └──────────────────┬──────────────────┘
                                           │ (SHA-256 inmutable)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NEXUS 2.0 CORE INGESTION DAEMON                       │
│    Triaje INCIBE · Extracción Forense IOCs · Cuarentena Prompt Injection    │
└──────────────────┬───────────────────────────────────────┬──────────────────┘
                   │                                       │
                   ▼                                       ▼
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│     Azure PostgreSQL Database        │  │     NEXUS Smart Notifications     │
│   142 Correos · 93 Alertas Únicas    │  │   Motor 200.000 alertas/día       │
│   62 Acciones SOAR · Hash Inmutable  │  │   Deduplicación & Cooldown (P1-P4)│
└──────────────────┬───────────────────┘  └──────────────────┬────────────────┘
                   │                                         │
                   ▼                                         ▼
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│       SOAR Auto-Blocker Engine       │  │        Interfaces de Usuario      │
│   Directriz 1 · API Azure (/bloquear)│  │ 1. Portal Web SAMPOL (Pages)      │
│   Salvaguardas & Whitelist VIP / OT  │  │ 2. Backend REST API (FastAPI)     │
│   Idempotencia & Trazabilidad SOL-B  │  │ 3. Cuadro de Mando (Streamlit)    │
└──────────────────────────────────────┘  └───────────────────────────────────┘
```
