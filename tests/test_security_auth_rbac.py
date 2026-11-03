"""
Test Suite: Seguridad, Autenticación y Control de Acceso por Roles (RBAC)
Valida el aislamiento de identidades, prevención de spoofing y protección de endpoints críticos.
"""

import pytest
from fastapi.testclient import TestClient
from backend_api import app
from security import (
    create_access_token,
    UserRole,
    Permission,
    ROLE_PERMISSIONS,
    AuthenticatedUser,
)

client = TestClient(app)

def test_cors_configuration():
    """Comprueba que CORS rechaza orígenes maliciosos y permite los autorizados."""
    # Origen autorizado
    resp_ok = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:8501",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp_ok.status_code == 200
    assert resp_ok.headers.get("access-control-allow-origin") == "http://localhost:8501"

    # Origen no autorizado no debe recibir cabecera allow-origin
    resp_bad = client.options(
        "/health",
        headers={
            "Origin": "http://evil-attacker.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp_bad.headers.get("access-control-allow-origin") is None

def test_spoofed_identity_rejected():
    """Un usuario que intenta enviar un correo ajeno fuera del directorio de Sampol debe ser rechazado."""
    resp = client.get(
        "/api/smart-notifications",
        headers={"X-User-Id": "hacker@evil.com"}
    )
    assert resp.status_code == 403
    assert "Identidad no autorizada" in resp.json()["detail"]

def test_analista_role_permissions():
    """Un Analista SOC puede leer notificaciones pero no aprobar contenciones SOAR."""
    # 1. Leer notificaciones autorizadas
    resp_read = client.get(
        "/api/smart-notifications",
        headers={"X-User-Id": "guardia_soc@sampol.com"}
    )
    assert resp_read.status_code == 200

    # 2. Intentar parchear categoría de alerta sin permiso -> HTTP 403
    resp_patch = client.patch(
        "/alerts/1",
        json={"incibe_class": "Intrusión"},
        headers={"X-User-Id": "guardia_soc@sampol.com"}
    )
    assert resp_patch.status_code == 403
    assert "Acceso denegado" in resp_patch.json()["detail"]

def test_supervisor_role_permissions():
    """Un Supervisor SOC sí tiene permiso para modificar clasificación de alertas."""
    # Con identidad de supervisor
    resp = client.patch(
        "/alerts/999999",  # ID inexistente para probar validación de permisos previa
        json={"incibe_class": "Intrusión"},
        headers={"X-User-Id": "supervisor_soc@sampol.com"}
    )
    # Debe pasar la validación de seguridad (permiso concedido) y fallar en 404 de BBDD
    assert resp.status_code in (404, 200)

def test_token_cryptographic_verification():
    """Valida la generación y verificación de tokens HMAC-SHA256."""
    token = create_access_token("dirti@sampol.com", expires_in_seconds=3600)
    assert len(token.split(".")) == 2

    # Invocar endpoint con Bearer token
    resp = client.get(
        "/api/smart-notifications/unread-count",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200

    # Token adulterado debe ser rechazado
    bad_token = token[:-4] + "dead"
    resp_bad = client.get(
        "/api/smart-notifications/unread-count",
        headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert resp_bad.status_code == 401
