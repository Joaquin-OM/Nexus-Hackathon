# 🧠 ESTADO DE MEMORIA Y HANDOFF — NEXUS 2.0 (EQUIPO 1)
**Fecha de corte:** 03/11/2026 — 18:37 CET (Post-Tutoría 17:00, Directriz 1 y 2 del Director de TI desplegadas y probadas)  
**Repositorio local:** `C:\Users\osesj\Documents\Nexus-Hackathon`

---

## 1. INFRAESTRUCTURA, SERVICIOS EN EJECUCIÓN Y CREDENCIALES

### 1.1 Servicios Locales Activos (Daemons)
- **FastAPI Backend (`task-284`):** `http://127.0.0.1:8000` (Swagger UI: `http://127.0.0.1:8000/docs`)
  - Comando: `uv run --python "C:\Python315\python.EXE" --with pg8000 --with fastapi --with uvicorn uvicorn backend_api:app --host 127.0.0.1 --port 8000`
- **Streamlit Dashboard 6 Pestañas (`task-285`):** `http://localhost:8501`
  - Comando: `uv run --python "C:\Python315\python.EXE" --with pg8000 --with fastapi --with uvicorn --with streamlit --with pandas streamlit run dashboard.py --server.port 8501 --server.headless true`

### 1.2 Base de Datos Azure PostgreSQL 18.6 (`alertas-soc-1`)
- **Host:** `alertas-soc-1.postgres.database.azure.com`, DB: `postgres`, User: `team1`.
- **Estado de Tablas (Corte 18:37 CET):**
  - `raw_emails`: **121 correos** (con hash `sha256` y referencia `.eml`).
  - `alerts`:
    - **78 alertas SOC únicas** (`is_soc_alert = TRUE AND is_duplicate = FALSE`, vista `v_soc_unique_alerts`).
    - **21 duplicados y solicitudes operativas vinculadas** (`is_duplicate = TRUE`, incluyendo `SOL-B-001..012` y `SOL-L-001, 004, 007`).
    - **9 correos No-SOC filtrados** (`is_soc_alert = FALSE`).
  - `director_directives`:
    - Directriz 0: *Encargo y herramientas*, *Enunciado!*, *Retorno* (ROI oficial), *Seguimiento*.
    - **Directriz 1 (18:02 CET):** *`Automatizar`* -> Estado: `completada` (Playbook Autónomo desplegado).
    - **Directriz 2 (18:15 CET):** *`Acceso a los buzón del equipo`* -> Estado: `completada` (Graph sincronizado).
  - `soar_actions`:
    - **22 acciones de bloqueo autónomo** bajo `trigger_mode = 'automatico_directriz_1'` sobre todas las cuentas con compromiso confirmado.
    - Acciones de órdenes `orden_soc` (`SOL-B-001..012` y `SOL-L-001, 004, 007`).
    - Acciones supervisadas y sincronizadas.
  - `protected_assets_whitelist`: Lista blanca de activos IT/OT protegidos (cuentas VIP, concentradores, buzones clave).

---

## 2. HITOS COMPLETADOS EN ESTE TURNO (18:15 – 18:37 CET)

1. **Ingesta de las 5 últimas alertas del buzón (Total 121 correos):**
   - Ingerida `AL-20261030-0013` (`mgonzalez@sampol.com`, `ACCOUNT-LAB`, intrusión activa).
   - Ingerida `AL-20261030-0041` (`cmoreno@sampol.com`, `READ-LAB`, exfiltración en curso).
   - Ingerida `AL-20261030-0182` (`amartinez@sampol.com`, `SABOTAGE-LAB`, sabotaje físico).
   - Ingerida `AL-20261030-0044` (`bmoreno@sampol.com`, `SPRAY-LAB`, 154 fallos sin sesión).
   - Ingerido aviso del Director/Monitor a las 18:15 CET (`Acceso a los buzón del equipo`).

2. **Creación del Motor de Bloqueo Autónomo (`autoblock_engine.py`):**
   - Evalúa en tiempo real las alertas de compromiso (`ACCOUNT-LAB`, `ADMIN-LAB`, `APP-LAB`, `APT-LAB`, `C2-LAB`, `MALWARE-LAB`, `READ-LAB`, `MODIFY-LAB`, `MINING-LAB` y órdenes `SOL-B-*`).
   - Bloqueó automáticamente a las 13 cuentas comprometidas:
     `jmoreno@sampol.com`, `amoreno@sampol.com`, `cmoreno@sampol.com`, `mgonzalez@sampol.com`, `rperez@sampol.com`, `sperez@sampol.com`, `agomez@sampol.com`, `cgomez@sampol.com`, `vgomez@sampol.com`, `pgomez@sampol.com`, `qgomez@sampol.com`, `sgomez@sampol.com`, `hfernandez@sampol.com`.
   - Idempotencia estricta: Saltó alertas posteriores de la misma cadena para evitar duplicados.
   - Respetó fielmente las liberaciones `SOL-L-001, 004, 007` (`jgonzalez`, `bgonzalez`, `fgonzalez`).
   - Protegió a usuarios en intentos fallidos simples sin sesión (`bmoreno@sampol.com`).

3. **Integración Permanente en Ingesta (`ingest_and_classify.py`):**
   - Ahora, cada vez que entra un correo nuevo en el buzón, `ingest_and_classify.py` ejecuta automáticamente `run_autoblock_sweep()` al final de la ingesta.

4. **Actualización de la BBDD y Cuadro de Mando (`dashboard.py`):**
   - Actualizada fila `id = 7` en `director_directives` con `directive_number = 1`, respuesta del equipo y detalle técnico.
   - Pestaña 3 (SOAR): Añadido botón "🚨 Ejecutar Barrido de Bloqueo Autónomo (Directriz 1)" y tabla completa con el registro de `soar_actions`.
   - Pestaña 5 (Caso de Negocio y Directrices): Añadida sección con el Cuadro de Directrices Oficiales del Director de TI.

5. **Actualización de Documentación (`PLAN_MAESTRO_NEXUS_2_0_ACTUALIZADO.md`):**
   - Añadida la **Sección 9** detallando el cumplimiento de la Directriz 1 y 2, la justificación de contención y los resultados forenses.
   - Sincronizado con `PLAN_MAESTRO_NEXUS_EQUIPO1.md`.
