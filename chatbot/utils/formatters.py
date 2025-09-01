"""
Funções utilitárias para formatação de dados
"""
from datetime import date, datetime
from typing import Any, Dict, List


def format_currency(value: float) -> str:
    """
    Formata valor monetário para o padrão brasileiro
    
    Args:
        value: Valor numérico
        
    Returns:
        String formatada (ex: R$ 150,00)
    """
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formata datetime para string legível
    
    Args:
        dt: Objeto datetime
        format_str: String de formatação
        
    Returns:
        String formatada
    """
    if not dt:
        return "Data não informada"
    
    try:
        return dt.strftime(format_str)
    except:
        return str(dt)


def format_date(d: date, format_str: str = "%d/%m/%Y") -> str:
    """
    Formata date para string legível
    
    Args:
        d: Objeto date
        format_str: String de formatação
        
    Returns:
        String formatada
    """
    if not d:
        return "Data não informada"
    
    try:
        return d.strftime(format_str)
    except:
        return str(d)


def format_phone_number(phone: str) -> str:
    """
    Formata número de telefone para exibição
    
    Args:
        phone: Número de telefone
        
    Returns:
        Número formatado (ex: (11) 99999-9999)
    """
    if not phone:
        return "Telefone não informado"
    
    # Remove caracteres não numéricos
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    if len(clean_phone) == 11:  # Com DDD
        return f"({clean_phone[:2]}) {clean_phone[2:7]}-{clean_phone[7:]}"
    elif len(clean_phone) == 10:  # Com DDD (formato antigo)
        return f"({clean_phone[:2]}) {clean_phone[2:6]}-{clean_phone[6:]}"
    else:
        return phone


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto se exceder o tamanho máximo
    
    Args:
        text: Texto para truncar
        max_length: Tamanho máximo
        suffix: Sufixo para indicar truncamento
        
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_list(items: List[Any], separator: str = ", ", max_items: int = 5) -> str:
    """
    Formata lista de itens para exibição
    
    Args:
        items: Lista de itens
        separator: Separador entre itens
        max_items: Número máximo de itens a mostrar
        
    Returns:
        String formatada
    """
    if not items:
        return "Nenhum item"
    
    if len(items) <= max_items:
        return separator.join(str(item) for item in items)
    
    shown_items = items[:max_items]
    remaining = len(items) - max_items
    
    return separator.join(str(item) for item in shown_items) + f" e mais {remaining}"


def format_medical_specialty(specialty: str) -> str:
    """
    Formata especialidade médica para exibição
    
    Args:
        specialty: Código da especialidade
        
    Returns:
        Nome formatado da especialidade
    """
    specialties_map = {
        'pneumologia': 'Pneumologia',
        'endocrinologia': 'Endocrinologia e Metabologia',
        'medicina_sono': 'Medicina do Sono',
    }
    
    return specialties_map.get(specialty.lower(), specialty.title())
