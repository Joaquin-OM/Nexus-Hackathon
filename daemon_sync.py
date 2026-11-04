"""
NEXUS 2.0 — Daemon de Ingesta Continua, Auto-Bloqueo SOAR y Actualización del Front
Vigila el buzón de Microsoft Graph permanentemente cada 45 segundos.
- Ingesta y deduplica correos en raw_emails y alerts.
- Ejecuta autoblock_engine ante compromisos confirmados (Directriz 1).
- Agrupa en Notificaciones Inteligentes (P1/P2/P3/P4).
- Exporta data_export.json y regenera index.html automáticamente para el front.
- Mantiene el sistema en piloto automático 24/7 sin intervención manual.
"""

import time
import logging
from datetime import datetime
from config import get_conn
from ingest_and_classify import main as run_ingest
from sync_alerts_to_notifications import sync_existing_alerts
from export_data import export_data
from generate_portal import main as run_generate_portal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [DAEMON-NEXUS] %(levelname)s: %(message)s"
)
logger = logging.getLogger("daemon_sync")

def run_daemon_loop(poll_interval: int = 45):
    logger.info("=============================================================")
    logger.info("INICIANDO DAEMON DE SINCRONIZACIÓN Y CONTENCIÓN CONTINUA NEXUS")
    logger.info(f"Intervalo de consulta: {poll_interval} segundos")
    logger.info("=============================================================")

    iteration = 1
    while True:
        try:
            logger.info(f"[CICLO #{iteration}] Comprobando buzón Microsoft Graph...")
            run_ingest()
            sync_existing_alerts()
            logger.info(f"[CICLO #{iteration}] Ingesta y SOAR completados. Actualizando front...")
            export_data()
            run_generate_portal()
            logger.info(f"[CICLO #{iteration}] Base de datos y Front (index.html / data_export.json) actualizados con éxito.")
        except Exception as e:
            logger.error(f"[CICLO #{iteration}] Error durante el ciclo de sincronización: {e}", exc_info=True)

        iteration += 1
        time.sleep(poll_interval)

if __name__ == "__main__":
    run_daemon_loop(poll_interval=45)
