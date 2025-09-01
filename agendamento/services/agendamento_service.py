"""
Serviço responsável pelo gerenciamento de agendamentos
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from django.utils import timezone

from clinica.models import HorarioTrabalho, Medico

from ..models import Agendamento


class AgendamentoService:
    """Serviço para gerenciar agendamentos de consultas"""
    
    def __init__(self):
        # Futuramente: self.google_calendar_service = GoogleCalendarService()
        pass
    
    def get_available_slots(self, medico: Medico, data: datetime) -> List[Dict[str, Any]]:
        """
        Retorna horários disponíveis para um médico em uma data específica
        
        Args:
            medico: Médico para consultar
            data: Data para verificar disponibilidade
            
        Returns:
            Lista de horários disponíveis
        """
        # Busca horários de trabalho do médico para o dia da semana
        dia_semana = data.strftime('%A').lower()
        horarios_trabalho = HorarioTrabalho.objects.filter(
            medico=medico,
            dia_da_semana=dia_semana
        ).first()
        
        if not horarios_trabalho:
            return []
        
        # Gera slots de 30 minutos entre início e fim do horário de trabalho
        slots = []
        hora_atual = horarios_trabalho.hora_inicio
        hora_fim = horarios_trabalho.hora_fim
        
        while hora_atual < hora_fim:
            # Cria datetime completo para o slot
            slot_datetime = datetime.combine(data.date(), hora_atual)
            
            # Verifica se o slot está disponível
            if self._is_slot_available(medico, slot_datetime):
                slots.append({
                    'hora': hora_atual.strftime('%H:%M'),
                    'datetime': slot_datetime,
                    'disponivel': True
                })
            
            # Avança 30 minutos
            hora_atual = (datetime.combine(datetime.min, hora_atual) + 
                         timedelta(minutes=30)).time()
        
        return slots
    
    def _is_slot_available(self, medico: Medico, slot_datetime: datetime) -> bool:
        """
        Verifica se um slot específico está disponível
        
        Args:
            medico: Médico para verificar
            slot_datetime: Data e hora do slot
            
        Returns:
            True se disponível, False caso contrário
        """
        # Verifica se já existe agendamento neste horário
        slot_fim = slot_datetime + timedelta(minutes=30)
        
        existing_booking = Agendamento.objects.filter(
            medico=medico,
            data_hora_inicio__lt=slot_fim,
            data_hora_fim__gt=slot_datetime,
            status__in=['Pendente', 'Confirmado']
        ).exists()
        
        return not existing_booking
    
    def create_agendamento(self, 
                          paciente_nome: str, 
                          paciente_telefone: str,
                          medico: Medico, 
                          data_hora_inicio: datetime,
                          **kwargs) -> Agendamento:
        """
        Cria um novo agendamento
        
        Args:
            paciente_nome: Nome completo do paciente
            paciente_telefone: Telefone/WhatsApp do paciente
            medico: Médico escolhido
            data_hora_inicio: Data e hora de início da consulta
            **kwargs: Outros campos opcionais
            
        Returns:
            Objeto Agendamento criado
        """
        # Calcula hora de fim (30 minutos após início)
        data_hora_fim = data_hora_inicio + timedelta(minutes=30)
        
        # Verifica se o slot ainda está disponível
        if not self._is_slot_available(medico, data_hora_inicio):
            raise ValueError("Horário não está mais disponível")
        
        # Cria o agendamento
        agendamento = Agendamento.objects.create(
            paciente_nome=paciente_nome,
            paciente_telefone=paciente_telefone,
            medico=medico,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            **kwargs
        )
        
        # Futuramente: Integrar com Google Calendar
        # self.google_calendar_service.create_event(agendamento)
        
        return agendamento
    
    def cancel_agendamento(self, agendamento_id: int, motivo: str = None) -> bool:
        """
        Cancela um agendamento existente
        
        Args:
            agendamento_id: ID do agendamento
            motivo: Motivo do cancelamento (opcional)
            
        Returns:
            True se cancelado com sucesso, False caso contrário
        """
        try:
            agendamento = Agendamento.objects.get(id=agendamento_id)
            agendamento.status = 'Cancelado'
            if motivo:
                # Futuramente: adicionar campo motivo_cancelamento ao modelo
                pass
            agendamento.save()
            
            # Futuramente: Atualizar Google Calendar
            # self.google_calendar_service.update_event(agendamento)
            
            return True
            
        except Agendamento.DoesNotExist:
            return False
    
    def get_agendamentos_medico(self, medico: Medico, data: datetime = None) -> List[Agendamento]:
        """
        Retorna agendamentos de um médico para uma data específica
        
        Args:
            medico: Médico para consultar
            data: Data específica (se None, retorna todos)
            
        Returns:
            Lista de agendamentos
        """
        queryset = Agendamento.objects.filter(medico=medico)
        
        if data:
            queryset = queryset.filter(
                data_hora_inicio__date=data.date()
            )
        
        return queryset.order_by('data_hora_inicio')
    
    def get_agendamentos_paciente(self, telefone: str) -> List[Agendamento]:
        """
        Retorna agendamentos de um paciente específico
        
        Args:
            telefone: Telefone/WhatsApp do paciente
            
        Returns:
            Lista de agendamentos
        """
        return Agendamento.objects.filter(
            paciente_telefone=telefone
        ).order_by('-data_hora_inicio')
    
    def confirm_agendamento(self, agendamento_id: int) -> bool:
        """
        Confirma um agendamento pendente
        
        Args:
            agendamento_id: ID do agendamento
            
        Returns:
            True se confirmado com sucesso, False caso contrário
        """
        try:
            agendamento = Agendamento.objects.get(id=agendamento_id)
            if agendamento.status == 'Pendente':
                agendamento.status = 'Confirmado'
                agendamento.save()
                return True
            return False
            
        except Agendamento.DoesNotExist:
            return False
