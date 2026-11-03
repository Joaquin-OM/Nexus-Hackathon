"""
Test Suite: Salvaguardas y Fiabilidad del Motor SOAR (Autoblock Engine)
Verifica lista blanca OT/IT, idempotencia, verificación de códigos HTTP y trazabilidad forense.
"""

from unittest.mock import MagicMock, patch
import pytest
from autoblock_engine import is_whitelisted, execute_auto_block, execute_auto_release

def test_whitelist_prevents_blocking():
    """Un activo presente en protected_assets_whitelist nunca debe ser bloqueado."""
    mock_conn = MagicMock()
    # Simular que el usuario está en la lista blanca
    mock_conn.run.return_value = [("Planta OT", "Turbina Central Cogeneración")]

    assert is_whitelisted(mock_conn, "scada_admin@sampol.com") is True

    result = execute_auto_block(
        conn=mock_conn,
        alert_id=10,
        internal_id="AL-0010",
        alert_code="SOC-0010",
        user_val="scada_admin@sampol.com",
        rule="ACCOUNT-LAB",
        incibe_class="Intrusión",
        reason_detail="Prueba de contención"
    )
    assert result["status"] == "skipped_whitelist"

def test_idempotency_prevents_duplicate_actions():
    """Si ya existe un registro de bloqueo con la misma idempotency_key, se omite."""
    mock_conn = MagicMock()
    # Primera consulta de whitelist: no está
    # Segunda consulta de soar_actions: ya existe
    mock_conn.run.side_effect = [
        [],  # whitelist vacía
        [(105, "ejecutado", 201)]  # soar_actions existente
    ]

    result = execute_auto_block(
        conn=mock_conn,
        alert_id=20,
        internal_id="AL-0020",
        alert_code="SOC-0020",
        user_val="jmoreno@sampol.com",
        rule="C2-LAB",
        incibe_class="Intrusión",
        reason_detail="Prueba idempotencia"
    )
    assert result["status"] == "idempotent_skip"
    assert result["soar_id"] == 105

@patch("autoblock_engine.call_sampol_soar_api")
def test_failed_api_call_not_marked_as_executed(mock_api):
    """Una llamada a la API que devuelva error HTTP 500 no debe registrarse como ejecutada."""
    mock_api.return_value = (500, {"error": "Internal Server Error"})
    mock_conn = MagicMock()
    mock_conn.run.side_effect = [
        [],  # whitelist
        [],  # idempotency check
        [(201,)],  # INSERT RETURNING id
        None,  # INSERT alert_audit_log
        None   # UPDATE alerts
    ]

    result = execute_auto_block(
        conn=mock_conn,
        alert_id=30,
        internal_id="AL-0030",
        alert_code="SOC-0030",
        user_val="usuario_comprometido@sampol.com",
        rule="MODIFY-LAB",
        incibe_class="Contenido dañino",
        reason_detail="Prueba fallo API"
    )
    # Comprobar el status guardado en el INSERT
    insert_call = mock_conn.run.call_args_list[2]
    kwargs = insert_call[1]
    assert kwargs["st"] == "registrado_error_api"
    assert kwargs["code"] == 500
