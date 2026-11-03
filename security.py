"""
NEXUS SOC 2.0 — Módulo de Autenticación, Autorización y Control de Acceso (RBAC)
Proporciona validación de identidad estricta en el servidor, roles y permisos.
"""

import os
import hmac
import hashlib
import json
import time
from enum import Enum
from typing import Optional, List, Dict, Any, Set
from fastapi import Request, HTTPException, status, Depends, Header
from pydantic import BaseModel

# ============================================================================
# ROLES Y MATRIZ DE PERMISOS
# ============================================================================

class UserRole(str, Enum):
    ANALISTA_SOC = "Analista SOC"
    SUPERVISOR_SOC = "Supervisor SOC"
    RESPONSABLE_TI = "Responsable de TI"
    ADMINISTRADOR = "Administrador"

class Permission(str, Enum):
    READ_ALERTS = "alerts:read"
    PATCH_ALERTS = "alerts:patch"
    READ_NOTIFICATIONS = "notifications:read"
    ACK_NOTIFICATIONS = "notifications:ack"
    READ_INCIDENTS = "incidents:read"
    REASSIGN_INCIDENTS = "incidents:reassign"
    REQUEST_SOAR = "soar:request"
    APPROVE_SOAR = "soar:approve"
    RELEASE_SOAR = "soar:release"
    READ_FINANCES = "finances:read"
    SYSTEM_CONFIG = "system:config"

ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ANALISTA_SOC: {
        Permission.READ_ALERTS,
        Permission.READ_NOTIFICATIONS,
        Permission.ACK_NOTIFICATIONS,
        Permission.READ_INCIDENTS,
        Permission.REQUEST_SOAR,
    },
    UserRole.SUPERVISOR_SOC: {
        Permission.READ_ALERTS,
        Permission.PATCH_ALERTS,
        Permission.READ_NOTIFICATIONS,
        Permission.ACK_NOTIFICATIONS,
        Permission.READ_INCIDENTS,
        Permission.REASSIGN_INCIDENTS,
        Permission.REQUEST_SOAR,
        Permission.APPROVE_SOAR,
        Permission.RELEASE_SOAR,
    },
    UserRole.RESPONSABLE_TI: {
        Permission.READ_ALERTS,
        Permission.READ_NOTIFICATIONS,
        Permission.ACK_NOTIFICATIONS,
        Permission.READ_INCIDENTS,
        Permission.APPROVE_SOAR,
        Permission.READ_FINANCES,
    },
    UserRole.ADMINISTRADOR: set(Permission),  # Todos los permisos
}

# ============================================================================
# MODELOS DE USUARIO AUTENTICADO
# ============================================================================

class AuthenticatedUser(BaseModel):
    user_id: str
    email: str
    name: str
    role: UserRole
    permissions: List[str]
    is_demo: bool = False

    def has_permission(self, perm: Permission) -> bool:
        return perm.value in self.permissions or self.role == UserRole.ADMINISTRADOR

# Directorio de identidades corporativas SAMPOL autorizadas
KNOWN_IDENTITIES: Dict[str, Dict[str, Any]] = {
    "guardia_soc@sampol.com": {
        "user_id": "usr-soc-01",
        "name": "Guardia de Turno SOC",
        "role": UserRole.ANALISTA_SOC,
    },
    "analista1@sampol.com": {
        "user_id": "usr-soc-02",
        "name": "Analista L1 Triaje",
        "role": UserRole.ANALISTA_SOC,
    },
    "supervisor_soc@sampol.com": {
        "user_id": "usr-sup-01",
        "name": "Supervisor de Ciberseguridad",
        "role": UserRole.SUPERVISOR_SOC,
    },
    "dirti@sampol.com": {
        "user_id": "usr-dir-01",
        "name": "Director de TI SAMPOL",
        "role": UserRole.RESPONSABLE_TI,
    },
    "admin_soc@sampol.com": {
        "user_id": "usr-adm-01",
        "name": "Administrador Plataforma NEXUS",
        "role": UserRole.ADMINISTRADOR,
    },
}

# Clave secreta interna para firma de tokens (en producción debe venir de env)
SECRET_KEY = os.environ.get("NEXUS_AUTH_SECRET", "sampol_soc_nexus_2026_super_secure_key_1815")
DEMO_MODE = os.environ.get("NEXUS_DEMO_MODE", "true").lower() in ("true", "1", "yes")

# ============================================================================
# GENERACIÓN Y VALIDACIÓN DE TOKENS DE SESIÓN
# ============================================================================

def create_access_token(email: str, expires_in_seconds: int = 86400) -> str:
    """Crea un token firmado HMAC-SHA256 para una identidad autorizada."""
    if email not in KNOWN_IDENTITIES:
        raise ValueError(f"Identidad no registrada en el directorio corporativo: {email}")
    
    info = KNOWN_IDENTITIES[email]
    payload = {
        "sub": email,
        "uid": info["user_id"],
        "name": info["name"],
        "role": info["role"].value,
        "exp": int(time.time()) + expires_in_seconds
    }
    payload_b64 = json.dumps(payload, sort_keys=True).encode("utf-8")
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64, hashlib.sha256).hexdigest()
    token = f"{payload_b64.hex()}.{sig}"
    return token

def verify_access_token(token_str: str) -> Optional[AuthenticatedUser]:
    """Verifica la firma criptográfica y la validez temporal del token."""
    try:
        parts = token_str.split(".")
        if len(parts) != 2:
            return None
        payload_bytes = bytes.fromhex(parts[0])
        sig = parts[1]
        
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        
        payload = json.loads(payload_bytes.decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None  # Token expirado
        
        role = UserRole(payload["role"])
        perms = [p.value for p in ROLE_PERMISSIONS.get(role, set())]
        
        return AuthenticatedUser(
            user_id=payload["uid"],
            email=payload["sub"],
            name=payload["name"],
            role=role,
            permissions=perms,
            is_demo=False
        )
    except Exception:
        return None

# ============================================================================
# DEPENDENCIAS FASTAPI
# ============================================================================

def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_nexus_key: Optional[str] = Header(None, alias="X-NEXUS-KEY"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> AuthenticatedUser:
    """
    Resuelve la identidad del usuario con validación estricta en el servidor:
    1. Si se proporciona Bearer Token, valida firma HMAC y vigencia.
    2. Si se proporciona API Key de servicio (ej. backend o daemon), asigna rol administrativo.
    3. Si está en DEMO_MODE y el cliente envía una identidad conocida, se valida contra el directorio oficial.
    4. En caso de fallo o spoofing de identidad no autorizada, rechaza con HTTP 401.
    """
    # 1. Bearer Token en cabecera Authorization
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):].strip()
        user = verify_access_token(token)
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado"
        )
    
    # 2. Clave interna de servicio
    system_key = os.environ.get("NEXUS_SYSTEM_API_KEY", "nexus-soc-system-token-internal")
    if x_nexus_key and hmac.compare_digest(x_nexus_key, system_key):
        return AuthenticatedUser(
            user_id="sys-daemon-01",
            email="daemon@sampol.com",
            name="NEXUS Ingestion Daemon",
            role=UserRole.ADMINISTRADOR,
            permissions=[p.value for p in Permission],
            is_demo=False
        )
    
    # 3. Modo Demostración Controlado (Hackathon / Entorno de Pruebas)
    if DEMO_MODE:
        target_email = (x_user_id or "guardia_soc@sampol.com").strip().lower()
        if target_email in KNOWN_IDENTITIES:
            info = KNOWN_IDENTITIES[target_email]
            role = info["role"]
            return AuthenticatedUser(
                user_id=info["user_id"],
                email=target_email,
                name=info["name"],
                role=role,
                permissions=[p.value for p in ROLE_PERMISSIONS.get(role, set())],
                is_demo=True
            )
        else:
            # En modo demo NO se aceptan identidades arbitrarias fuera de SAMPOL
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Identidad no autorizada en el entorno corporativo: '{target_email}'. Debe pertenecer al dominio @sampol.com registrado."
            )
    
    # Si no hay credenciales y no es demo mode
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación requeridas. Envíe cabecera Authorization: Bearer <token>"
    )

def require_permission(perm: Permission):
    """Decorador de dependencia para exigir un permiso específico."""
    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not user.has_permission(perm):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: el rol '{user.role.value}' no tiene el permiso '{perm.value}'"
            )
        return user
    return dependency

def require_role(*roles: UserRole):
    """Decorador de dependencia para exigir uno de los roles autorizados."""
    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role not in roles and user.role != UserRole.ADMINISTRADOR:
            allowed = [r.value for r in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: requiere rol en {allowed}, rol actual '{user.role.value}'"
            )
        return user
    return dependency
