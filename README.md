# 🛡️ NEXUS 2.0 — Centro de Operaciones SOC & Respuesta a Incidentes (SOAR)
### Hackathon FP Sampol 2026 (24 Horas) — Equipo 1

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Portal-00f2fe?style=for-the-badge&logo=github)](https://joaquin-om.github.io/Nexus-Hackathon/)
[![Azure PostgreSQL](https://img.shields.io/badge/Azure-PostgreSQL%2018.6-336791?style=for-the-badge&logo=postgresql)](https://portal.azure.com/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20REST-009688?style=for-the-badge&logo=fastapi)](http://127.0.0.1:8000/docs)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit%206%20Tabs-ff4b4b?style=for-the-badge&logo=streamlit)](http://localhost:8501)

> 🌐 **Portal Web en Vivo para el Jurado y Compañeros:**  
> 👉 **[https://joaquin-om.github.io/Nexus-Hackathon/](https://joaquin-om.github.io/Nexus-Hackathon/)**  
> *(Accede sin instalar nada desde móvil, tablet o PC: incluye Cuadro de Mando interactivo, Investigación Forense, Contención SOAR, Calculadora ROI y visor de las 78 alertas únicas).*

---

## 🚀 1. Resumen Ejecutivo de la Solución
**NEXUS 2.0** es la solución integral diseñada por el **Equipo 1** para el reto *"El caso del director de TI"*:
1. **Ingesta Continua e Inmutable:** Conexión con Microsoft Graph API para procesar el buzón del SOC (`equipo_1_hackaton@sampol.com`), generando hashes `SHA-256` inmutables por cada correo y persistencia forense.
2. **Triaje y Clasificación Híbrida INCIBE (10 Clases Oficiales):** Motor semántico determinista que clasifica cada alerta en la taxonomía nacional de seguridad (Intento de intrusión, Disponibilidad, Contenido dañino, Fraude, Compromiso de información, Intrusión, Vulnerable, Obtención de información, Contenido abusivo y Otros).
3. **Filtrado Inteligente de Ruido y Duplicados:** Reducción del **24,8% del volumen manual** descartando avisos administrativos y enlazando duplicados y órdenes operativas a su incidente padre.
4. **Respuesta a la Directriz 1 (18:00 CET — Playbook Autónomo `autoblock_engine.py`):** Contención automática inmediata ante robo de credenciales, intrusión o malware/C2, bloqueando a 13 cuentas comprometidas en la API de Sampol con protección de Lista Blanca IT/OT y resolución de falsos positivos (`SOL-L`).
5. **Caso de Negocio y Modelo Financiero (ROI Oficial):** Retorno de inversión del **2.010%**, periodo de recuperación (Payback) en **10 días** y ahorro de **174.000 € en 3 años** frente a alternativas comerciales.

---

## 📊 2. Estado Operativo en Vivo (Azure PostgreSQL `alertas-soc-1`)

| Métrica | Valor | Observaciones Técnicas |
| :--- | :---: | :--- |
| **Correos Totales Ingeridos (`raw_emails`)** | **121** | Con hash forense `SHA-256` y trazabilidad RFC 822 |
| **Alertas SOC Únicas (`v_soc_unique_alerts`)** | **78** | Normalizadas, geolocalizadas por sede y con criticidad de activo |
| **Duplicados y Órdenes Vinculadas** | **21** | Órdenes `SOL-B-001..012` y `SOL-L-001, 004, 007` enlazadas |
| **Correos No-SOC Filtrados** | **9** | Avisos de mantenimiento, agenda corporativa y bienvenida |
| **Contenciones SOAR Ejecutadas (`soar_actions`)** | **57** | 22 bajo `automatico_directriz_1`, 20 de órdenes SOC y 15 supervisadas |
| **Cuentas Comprometidas Contenidas** | **13** | `jmoreno`, `amoreno`, `cmoreno`, `mgonzalez`, `rperez`, `sperez`, `agomez`, `cgomez`, etc. |

---

## 🛠️ 3. Puesta en Marcha Local

### Prerrequisitos
- Python 3.10+ o [`uv`](https://github.com/astral-sh/uv) (recomendado)
- Acceso a Azure PostgreSQL

### 1. Clonar el repositorio
```bash
git clone https://github.com/Joaquin-OM/Nexus-Hackathon.git
cd Nexus-Hackathon
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y rellena tus credenciales:
```bash
cp .env.example .env
```

### 3. Iniciar el Backend API (FastAPI)
```bash
uv run --with pg8000 --with fastapi --with uvicorn uvicorn backend_api:app --host 127.0.0.1 --port 8000
```
Swagger interactivo disponible en: `http://127.0.0.1:8000/docs`

### 4. Iniciar el Cuadro de Mando (Streamlit)
```bash
uv run --with pg8000 --with fastapi --with uvicorn --with streamlit --with pandas streamlit run dashboard.py --server.port 8501
```
Abre en tu navegador: `http://localhost:8501`

### 5. Ejecutar Ingesta y Bloqueo Autónomo
```bash
# Ingesta Graph + Clasificación INCIBE + Barrido Autónomo Directriz 1
uv run --with pg8000 python ingest_and_classify.py
```

---

## 📑 4. Documentación y Entregables
- [PLAN_MAESTRO_NEXUS_2_0_ACTUALIZADO.md](PLAN_MAESTRO_NEXUS_2_0_ACTUALIZADO.md): Informe técnico y funcional completo (9 secciones).
- [schema.sql](schema.sql): Esquema DDL de Azure PostgreSQL (tablas, índices, vistas forenses y vistas operativas).
- [autoblock_engine.py](autoblock_engine.py): Playbook autónomo de contención ante la Directriz 1.
- [index.html](index.html): Portal estático para GitHub Pages.
