"""
Serviço responsável pelo gerenciamento de conversas e estados
"""
from typing import Dict, List, Optional, Tuple

from django.core.cache import cache

from .ai_service import AIService
from .whatsapp_service import WhatsAppService


class ConversationService:
    """Serviço para gerenciar o estado e fluxo das conversas"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.whatsapp_service = WhatsAppService()
    
    def get_conversation_data(self, user_number: str) -> Dict:
        """Recupera dados da conversa do cache"""
        session_key = f"whatsapp_session_{user_number}"
        return cache.get(session_key, {
            'state': 'START',
            'history': [],
            'context': {}
        })
    
    def update_conversation_data(self, user_number: str, data: Dict, timeout: int = 120):
        """Atualiza dados da conversa no cache"""
        session_key = f"whatsapp_session_{user_number}"
        cache.set(session_key, data, timeout=timeout)
    
    def add_message_to_history(self, user_number: str, message: str, role: str = 'user'):
        """Adiciona mensagem ao histórico da conversa"""
        conversation_data = self.get_conversation_data(user_number)
        conversation_data['history'].append({
            'role': role, 
            'parts': [message]
        })
        self.update_conversation_data(user_number, conversation_data)
    
    def process_user_message(self, user_number: str, message_text: str) -> str:
        """
        Processa mensagem do usuário e retorna resposta
        
        Args:
            user_number: Número do WhatsApp do usuário
            message_text: Texto da mensagem recebida
            
        Returns:
            Resposta processada para enviar ao usuário
        """
        # Adiciona mensagem do usuário ao histórico
        self.add_message_to_history(user_number, message_text, 'user')
        
        # Recupera dados da conversa
        conversation_data = self.get_conversation_data(user_number)
        chat_history = conversation_data['history']
        current_state = conversation_data['state']
        
        # Gera resposta da IA
        ai_response = self.ai_service.generate_response(chat_history)
        
        # Adiciona resposta da IA ao histórico
        self.add_message_to_history(user_number, ai_response, 'model')
        
        # Processa comandos especiais
        final_response, new_state = self._process_ai_commands(ai_response, current_state)
        
        # Atualiza estado da conversa
        conversation_data['state'] = new_state
        self.update_conversation_data(user_number, conversation_data)
        
        return final_response
    
    def _process_ai_commands(self, ai_response: str, current_state: str) -> Tuple[str, str]:
        """
        Processa comandos especiais da IA e retorna resposta final e novo estado
        
        Returns:
            Tuple com (resposta_final, novo_estado)
        """
        if '[CONSULTAR_AGENDA:' in ai_response:
            # Simula consulta à agenda (futuramente integra com Google Calendar)
            print("COMANDO DETECTADO: [CONSULTAR_AGENDA]")
            return (
                "Ok, estou verificando a agenda... (simulação). Encontrei horários às 10:00, 11:00 e 15:00. Qual prefere?",
                'AWAITING_TIME_CHOICE'
            )
        
        elif '[CRIAR_AGENDAMENTO:' in ai_response:
            # Simula criação de agendamento (futuramente integra com Google Calendar)
            print("COMANDO DETECTADO: [CRIAR_AGENDAMENTO]")
            return (
                "Perfeito! Agendamento confirmado! (simulação).",
                'START'
            )
        
        else:
            # Resposta normal da IA
            return ai_response, current_state
    
    def reset_conversation(self, user_number: str):
        """Reseta a conversa para o estado inicial"""
        self.update_conversation_data(user_number, {
            'state': 'START',
            'history': [],
            'context': {}
        })
    
    def get_conversation_summary(self, user_number: str) -> Dict:
        """Retorna resumo da conversa atual"""
        conversation_data = self.get_conversation_data(user_number)
        return {
            'state': conversation_data['state'],
            'message_count': len(conversation_data['history']),
            'last_message': conversation_data['history'][-1] if conversation_data['history'] else None
        }
