"""
Serviço responsável pelo gerenciamento de conversas e estados
"""
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db import transaction

from .ai_service import AIService
from .whatsapp_service import WhatsAppService
from ..models import Conversa, MensagemConversa, Direcionamento
from usuarios.models import Paciente


class ConversationService:
    """Serviço para gerenciar o estado e fluxo das conversas"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.whatsapp_service = WhatsAppService()
    
    def process_user_message(self, telefone_whatsapp: str, message_text: str) -> str:
        """
        Processa mensagem do usuário e retorna resposta
        
        Args:
            telefone_whatsapp: Número do WhatsApp do usuário
            message_text: Texto da mensagem recebida
            
        Returns:
            Resposta processada para enviar ao usuário
        """
        with transaction.atomic():
            # 1. Busca/cria paciente
            paciente, created = Paciente.objects.get_or_create(
                telefone_whatsapp=telefone_whatsapp
            )
            
            # 2. Verifica se tem direcionamento pendente
            if paciente.has_pending_direcionamento():
                return "Sua solicitação já foi encaminhada para nossa secretária. Aguarde o contato!"
            
            # 3. Busca/cria conversa ativa
            conversa = self._get_or_create_active_conversation(paciente)
            
            # 4. Salva mensagem do usuário
            self._save_message(conversa, 'user', message_text)
            
            # 5. Gera histórico para IA
            chat_history = self._build_chat_history(conversa)
            
            # 6. Gera resposta da IA
            ai_response = self.ai_service.generate_response(chat_history)
            
            # 7. Salva resposta da IA
            self._save_message(conversa, 'bot', ai_response)
            
            # 8. Processa comandos especiais
            final_response = self._process_ai_commands(ai_response, conversa)
            
            return final_response
    
    def _get_or_create_active_conversation(self, paciente: Paciente) -> Conversa:
        """Busca conversa ativa ou cria nova"""
        active_conversation = paciente.get_active_conversation()
        
        if active_conversation:
            return active_conversation
        
        # Cria nova conversa
        return Conversa.objects.create(
            paciente=paciente,
            status='ativa'
        )
    
    def _save_message(self, conversa: Conversa, remetente: str, conteudo: str):
        """Salva mensagem no histórico"""
        MensagemConversa.objects.create(
            conversa=conversa,
            remetente=remetente,
            conteudo=conteudo
        )
    
    def _build_chat_history(self, conversa: Conversa) -> List[Dict]:
        """Constrói histórico para a IA"""
        mensagens = conversa.mensagens.all()
        history = []
        
        for msg in mensagens:
            role = 'user' if msg.remetente == 'user' else 'model'
            history.append({
                'role': role,
                'parts': [msg.conteudo]
            })
        
        return history
    
    def _process_ai_commands(self, ai_response: str, conversa: Conversa) -> str:
        """
        Processa comandos especiais da IA
        """
        if '[CONSULTAR_AGENDA:' in ai_response:
            print("COMANDO DETECTADO: [CONSULTAR_AGENDA]")
            # Futuramente: integrar com Google Calendar
            return "Ok, estou verificando a agenda... (simulação). Encontrei horários às 10:00, 11:00 e 15:00. Qual prefere?"
        
        elif '[CRIAR_AGENDAMENTO:' in ai_response:
            print("COMANDO DETECTADO: [CRIAR_AGENDAMENTO]")
            # Cria direcionamento para secretária
            self._create_direcionamento(conversa, 'agendamento')
            return "Perfeito! Sua solicitação foi encaminhada para nossa secretária. Você receberá um contato em breve!"
        
        elif '[DIRECIONAR_SECRETARIA]' in ai_response:
            # Quando bot não consegue responder
            self._create_direcionamento(conversa, 'duvida_complexa')
            return "Vou encaminhar sua dúvida para nossa secretária. Em breve você receberá um contato!"
        
        else:
            # Resposta normal da IA
            return ai_response
    
    def _create_direcionamento(self, conversa: Conversa, tipo_solicitacao: str, medico=None):
        """Cria direcionamento para secretária"""
        # Finaliza conversa
        conversa.status = 'redirecionada'
        conversa.finalizada_em = timezone.now()
        conversa.resumo = self._generate_conversation_summary(conversa)
        conversa.save()
        
        # Cria direcionamento
        Direcionamento.objects.create(
            paciente=conversa.paciente,
            conversa=conversa,
            tipo_solicitacao=tipo_solicitacao,
            medico_interesse=medico,
            resumo_conversa=conversa.resumo,
            status='pendente'
        )
    
    def _generate_conversation_summary(self, conversa: Conversa) -> str:
        """Gera resumo da conversa para secretária"""
        mensagens_usuario = conversa.mensagens.filter(remetente='user')
        summary_lines = []
        
        for msg in mensagens_usuario:
            summary_lines.append(f"- {msg.conteudo}")
        
        return "\n".join(summary_lines)
    
    def reset_conversation(self, telefone_whatsapp: str):
        """Reseta conversa do usuário"""
        try:
            paciente = Paciente.objects.get(telefone_whatsapp=telefone_whatsapp)
            active_conversation = paciente.get_active_conversation()
            
            if active_conversation:
                active_conversation.status = 'finalizada'
                active_conversation.finalizada_em = timezone.now()
                active_conversation.save()
                
        except Paciente.DoesNotExist:
            pass
    
    def get_conversation_summary(self, telefone_whatsapp: str) -> Dict:
        """Retorna resumo da conversa atual"""
        try:
            paciente = Paciente.objects.get(telefone_whatsapp=telefone_whatsapp)
            active_conversation = paciente.get_active_conversation()
            
            if active_conversation:
                return {
                    'status': active_conversation.status,
                    'message_count': active_conversation.mensagens.count(),
                    'started_at': active_conversation.iniciada_em,
                    'has_pending_direcionamento': paciente.has_pending_direcionamento()
                }
            
            return {'status': 'no_active_conversation'}
            
        except Paciente.DoesNotExist:
            return {'status': 'user_not_found'}