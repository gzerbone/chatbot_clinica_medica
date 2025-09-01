import json
import os

from django.core.cache import cache
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.conversation_service import ConversationService
from .services.whatsapp_service import WhatsAppService
from .utils.validators import sanitize_message, validate_whatsapp_number

# Token de verificação do Webhook
VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')


class WebhookView(APIView):
    """
    View para manipular webhooks do WhatsApp Business API
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_service = ConversationService()
        self.whatsapp_service = WhatsAppService()
    
    def get(self, request):
        """
        Verificação inicial do webhook pela Meta
        """
        print("Recebida requisição GET para verificação do Webhook...")
        
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("Verificação do Webhook bem-sucedida. Retornando o challenge.")
            return Response(int(challenge), status=status.HTTP_200_OK)
        else:
            print("Verificação do Webhook falhou.")
            return Response(status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request):
        """
        Processa mensagens recebidas do WhatsApp
        """
        print("\nRecebida requisição POST (nova mensagem)...")
        
        try:
            # Decodifica o corpo da requisição
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            
            # Processa apenas mensagens do WhatsApp Business
            if data['object'] == 'whatsapp_business_account':
                for entry in data['entry']:
                    for change in entry['changes']:
                        value = change['value']
                        
                        if 'messages' in value:
                            message_data = value['messages'][0]
                            from_number = message_data['from']
                            
                            # Valida número do WhatsApp
                            if not validate_whatsapp_number(from_number):
                                print(f"Número inválido: {from_number}")
                                continue
                            
                            # Processa apenas mensagens de texto
                            if message_data['type'] == 'text':
                                message_text = message_data['text']['body']
                                
                                # Sanitiza a mensagem
                                sanitized_message = sanitize_message(message_text)
                                
                                # Processa a mensagem usando o serviço de conversa
                                response_text = self.conversation_service.process_user_message(
                                    from_number, 
                                    sanitized_message
                                )
                                
                                # Envia resposta via WhatsApp
                                self.whatsapp_service.send_text_message(from_number, response_text)
                                
        except KeyError as e:
            print(f"Erro ao processar a mensagem: Chave não encontrada. Erro: {e}")
            print(f"Dados recebidos: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"Erro inesperado ao processar a mensagem: {e}")
            print(f"Dados recebidos: {json.dumps(data, indent=2)}")
        
        # Retorna 200 OK para a Meta
        return Response(status=status.HTTP_200_OK)


class ConversationStatusView(APIView):
    """
    View para consultar status das conversas (útil para debugging)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_service = ConversationService()
    
    def get(self, request, user_number=None):
        """
        Retorna status da conversa de um usuário específico
        """
        if user_number:
            summary = self.conversation_service.get_conversation_summary(user_number)
            return Response(summary)
        
        # Lista todas as conversas ativas (para debugging)
        # Em produção, você pode querer limitar isso
        active_sessions = []
        # Implementar lógica para listar sessões ativas se necessário
        
        return Response({
            'active_sessions': active_sessions,
            'total_sessions': len(active_sessions)
        })
    
    def delete(self, request, user_number):
        """
        Reseta a conversa de um usuário específico
        """
        self.conversation_service.reset_conversation(user_number)
        return Response({'message': 'Conversa resetada com sucesso'})