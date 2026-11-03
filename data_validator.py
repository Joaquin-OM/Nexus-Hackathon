"""
NEXUS SOC 2.0 — Validador y Normalizador de Datos de Ciberseguridad
Garantiza la calidad de extracción de activos, hosts, usuarios, IPs y evita que
instrucciones de prompt injection o texto libre contaminen el inventario del SOC.
"""

import re
import ipaddress
from typing import Optional, Tuple

PROMPT_INJECTION_INDICATORS = [
    r"\(solo cuando",
    r"cuando se cita",
    r"instrucci[oó]n",
    r"prompt",
    r"canary",
    r"canario",
    r"recurso:\s*hn03",
    r"expresamente",
    r"ignora las instrucciones",
]

def contains_prompt_instruction(text: str) -> bool:
    """Detecta si un fragmento de texto contiene instrucciones o canarios de prompt injection."""
    if not text:
        return False
    t_lower = text.lower()
    for pattern in PROMPT_INJECTION_INDICATORS:
        if re.search(pattern, t_lower, re.I):
            return True
    return False

def validate_and_clean_host(raw_host: Optional[str]) -> str:
    """
    Valida y normaliza el nombre de un equipo o activo tecnológico.
    Rechaza frases completas, paréntesis explicativos e inyecciones de prompt.
    """
    if not raw_host:
        return "No identificado"
    
    val = raw_host.strip()
    
    # 1. Descartar valores ausentes conocidos
    if val.lower() in ("no indicado", "no indicada", "no identificado", "no identificada", "no aplica", "n/a", "none", "null", ""):
        return "No identificado"
    
    # 2. Descartar si contiene canarios o instrucciones
    if contains_prompt_instruction(val):
        return "No identificado"
    
    # 3. Descartar frases o textos explicativos largos
    if len(val) > 45:
        return "No identificado"
    
    # Descartar si contiene paréntesis con explicaciones
    if "(" in val or ")" in val:
        return "No identificado"
        
    # Descartar si tiene más de 3 espacios (indica frase explicativa y no nombre de host)
    if val.count(" ") > 3:
        return "No identificado"
    
    # 4. Validar caracteres admisibles para hostnames / activos corporativos
    # Ejemplos válidos: srv-proj-01, pc-sev-03, SCADA-GEN-01, web-corp-01, 10.0.4.15
    # También descripciones canónicas como 'Buzón Correo Corporativo'
    clean_val = re.sub(r"\s+", " ", val).strip()
    return clean_val

def validate_and_clean_user(raw_user: Optional[str]) -> str:
    """
    Valida y normaliza la identidad de un usuario corporativo.
    Debe ser una dirección de correo RFC-compatible o una cuenta de dominio sin texto explicativo.
    """
    if not raw_user:
        return "No identificado"
    
    val = raw_user.strip()
    if val.lower() in ("no indicado", "no indicada", "no identificado", "no identificada", "no aplica", "n/a", "none", "null", ""):
        return "No identificado"
    
    if contains_prompt_instruction(val):
        return "No identificado"
        
    if len(val) > 60 or " " in val:
        return "No identificado"
        
    # Si contiene @, validar formato de correo
    if "@" in val:
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(email_pattern, val):
            return val.lower()
        return "No identificado"
        
    # Si es nombre de cuenta simple (ej. jmoreno, admin, root)
    if re.match(r"^[a-zA-Z0-9_.-]+$", val):
        return val.lower()
        
    return "No identificado"

def validate_and_clean_ip(raw_ip: Optional[str]) -> Optional[str]:
    """
    Valida una dirección IP usando la librería estándar ipaddress.
    Soporta corrección previa de IPs sin puntos comunes en exportaciones malformadas.
    """
    if not raw_ip:
        return None
    val = raw_ip.strip()
    if val.lower() in ("no indicada", "no identificado", "no aplica", "n/a", ""):
        return None
        
    if contains_prompt_instruction(val):
        return None

    # Intentar validación directa IPv4/IPv6
    try:
        ip_obj = ipaddress.ip_address(val)
        return str(ip_obj)
    except ValueError:
        pass
        
    # Intentar reconstruir IPs de 11 o 12 dígitos sin puntos (ej. 19851100107 -> 198.51.100.107)
    digits_only = re.sub(r"[^\d]", "", val)
    if len(digits_only) in (11, 12):
        # Probar partición estándar
        cand1 = f"{digits_only[:3]}.{digits_only[3:5]}.{digits_only[5:8]}.{digits_only[8:]}"
        cand2 = f"{digits_only[:3]}.{digits_only[3:6]}.{digits_only[6:8]}.{digits_only[8:]}"
        for cand in [cand1, cand2]:
            try:
                ip_obj = ipaddress.ip_address(cand)
                return str(ip_obj)
            except ValueError:
                continue
                
    return None
