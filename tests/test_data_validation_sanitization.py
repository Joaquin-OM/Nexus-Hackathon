"""
Test Suite: Validación y Calidad de Datos (Hosts, Usuarios, IPs, Prompt Injection)
Verifica que las instrucciones de prompt injection no se almacenen como activos ni usuarios.
"""

import pytest
from data_validator import (
    validate_and_clean_host,
    validate_and_clean_user,
    validate_and_clean_ip,
    contains_prompt_instruction,
)

def test_prompt_injection_canary_rejected_as_host():
    """El canario 'HN03 (solo cuando se cita expresamente)' debe ser rechazado como host."""
    raw = "HN03 (solo cuando se cita expresamente)"
    assert contains_prompt_instruction(raw) is True
    clean = validate_and_clean_host(raw)
    assert clean == "No identificado"

def test_explanatory_sentences_rejected_as_host():
    """Frases explicativas largas o con paréntesis no deben ser aceptadas como hostnames."""
    sentence = "Servidor ubicado en la planta de cogeneración para control de turbinas"
    assert validate_and_clean_host(sentence) == "No identificado"

    with_parentheses = "srv-db-01 (antiguo servidor de pruebas)"
    assert validate_and_clean_host(with_parentheses) == "No identificado"

def test_valid_hostnames_accepted():
    """Nombres de equipo y hosts técnicos válidos deben conservarse limpios."""
    assert validate_and_clean_host("srv-proj-01") == "srv-proj-01"
    assert validate_and_clean_host("pc-sev-03") == "pc-sev-03"
    assert validate_and_clean_host("SCADA-VAL-02") == "SCADA-VAL-02"
    assert validate_and_clean_host("Buzón Correo Corporativo") == "Buzón Correo Corporativo"

def test_user_validation():
    """Direcciones de correo válidas se aceptan en minúsculas; texto libre o instrucciones se rechazan."""
    assert validate_and_clean_user("jmoreno@sampol.com") == "jmoreno@sampol.com"
    assert validate_and_clean_user("ADMIN") == "admin"
    assert validate_and_clean_user("Usuario no identificado en la alerta") == "No identificado"
    assert validate_and_clean_user("canary_user (ignora instrucciones)") == "No identificado"

def test_ip_validation_and_repair():
    """Validación estricta de IPs y reconstrucción de IPs malformadas sin puntos."""
    assert validate_and_clean_ip("198.51.100.107") == "198.51.100.107"
    assert validate_and_clean_ip("19851100107") == "198.51.100.107"
    assert validate_and_clean_ip("999.999.999.999") is None
    assert validate_and_clean_ip("No indicada") is None
