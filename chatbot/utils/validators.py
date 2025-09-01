"""
Funções utilitárias para validação de dados
"""
import re
from typing import Optional


def validate_whatsapp_number(phone_number: str) -> bool:
    """
    Valida se um número de telefone está no formato correto para WhatsApp
    
    Args:
        phone_number: Número de telefone para validar
        
    Returns:
        True se válido, False caso contrário
    """
    # Remove caracteres não numéricos
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Verifica se tem 10-13 dígitos (com código do país)
    if len(clean_number) < 10 or len(clean_number) > 13:
        return False
    
    # Verifica se começa com código de país (ex: 55 para Brasil)
    if not clean_number.startswith('55'):
        return False
    
    return True


def format_whatsapp_number(phone_number: str) -> Optional[str]:
    """
    Formata número de telefone para o padrão WhatsApp
    
    Args:
        phone_number: Número de telefone para formatar
        
    Returns:
        Número formatado ou None se inválido
    """
    if not validate_whatsapp_number(phone_number):
        return None
    
    # Remove caracteres não numéricos
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Garante que tenha código do país
    if not clean_number.startswith('55'):
        clean_number = '55' + clean_number
    
    return clean_number


def validate_message_length(message: str, max_length: int = 4096) -> bool:
    """
    Valida se uma mensagem está dentro do limite de caracteres
    
    Args:
        message: Mensagem para validar
        max_length: Limite máximo de caracteres
        
    Returns:
        True se válida, False caso contrário
    """
    return len(message) <= max_length


def sanitize_message(message: str) -> str:
    """
    Remove caracteres potencialmente perigosos da mensagem
    
    Args:
        message: Mensagem para sanitizar
        
    Returns:
        Mensagem sanitizada
    """
    # Remove caracteres de controle
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', message)
    
    # Remove HTML tags básicas
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    # Limita tamanho
    if len(sanitized) > 4096:
        sanitized = sanitized[:4093] + "..."
    
    return sanitized
