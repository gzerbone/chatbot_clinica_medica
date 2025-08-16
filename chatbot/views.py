import json  # Importe a biblioteca json
import os  # Importe a biblioteca os

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import send_whatsapp_message

# Create your views here.
# chatbot/views.py


# Defina seu Token de Verificação aqui. Deve ser uma string longa e secreta.
# É uma boa prática carregá-lo de uma variável de ambiente.
VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN') # Token de verificação do Webhook (esta no .env)

class WebhookView(APIView):
    """
    Esta view manipula as requisições que a Meta envia para nosso webhook.
    """
    def get(self, request):
        """
        Este é o primeiro passo da configuração do Webhook na Meta.
        A Meta envia uma requisição GET para verificar se nossa URL é válida.
        """
        print("Recebida requisição GET para verificação do Webhook...")

        # Extrai os parâmetros da requisição
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')

        # Verifica se o 'mode' é 'subscribe' e se o token corresponde ao nosso
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("Verificação do Webhook bem-sucedida. Retornando o challenge.")
            return Response(int(challenge), status=status.HTTP_200_OK)
        else:
            # Se a verificação falhar, retorna um erro
            print("Verificação do Webhook falhou.")
            return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        """
        Este método é chamado quando a Meta nos envia dados de uma mensagem real.
        """
        print("\nRecebida requisição POST (nova mensagem)...")

        # O corpo da requisição vem como bytes, então o decodificamos
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        # Imprimimos o corpo da mensagem para depuração.
        # Use json.dumps para formatar a saída e torná-la legível.
        #print(json.dumps(data, indent=2))

        # #####################################################################
        # AQUI COMEÇA A LÓGICA DO SEU CHATBOT
        # #####################################################################
        
        # Processa os dados recebidos do WhatsApp
        try:
            # Verifica se é uma mensagem do WhatsApp Business
            if data['object'] == 'whatsapp_business_account':
                for entry in data['entry']:
                    for change in entry['changes']:
                        value = change['value']
                        
                        # Verifica se contém mensagens (mensagem real do usuário)
                        if 'messages' in value:
                            metadata = value['metadata']
                            phone_number_id = metadata['phone_number_id']
                            display_phone_number = metadata['display_phone_number']
                            
                            print(f"📱 Número de telefone ID: {phone_number_id}")
                            print(f"📱 Número de exibição: {display_phone_number}")
                            
                            for message in value['messages']:
                                from_number = message['from']
                                message_id = message['id']
                                timestamp = message['timestamp']
                                message_type = message['type']
                                
                                print(f"💬 NOVA MENSAGEM de: {from_number}")
                                print(f"💬 ID da mensagem: {message_id}")
                                print(f"💬 Timestamp: {timestamp}")
                                print(f"💬 Tipo: {message_type}")
                                
                                # Processa diferentes tipos de mensagem
                                if message_type == 'text':
                                    message_text = message['text']['body']
                                    print(f"💬 Texto: {message_text}")
                                    
                                    # ######################################################
                                    # ##### AQUI A MÁGICA ACONTECE: ENVIANDO A RESPOSTA ####
                                    # ######################################################
                                    response_text = f"Você disse: {message_text}"
                                    print(f"🤖 Enviando resposta para {from_number}: {response_text}")
                                    send_whatsapp_message(from_number, response_text)
                                
                                elif message_type == 'image':
                                    print("Imagem recebida")
                                elif message_type == 'audio':
                                    print("Áudio recebido")
                                elif message_type == 'document':
                                    print("Documento recebido")
                        
                        # Verifica se contém status de entrega/leitura (não precisa responder)
                        elif 'statuses' in value:
                            metadata = value['metadata']
                            phone_number_id = metadata['phone_number_id']
                            display_phone_number = metadata['display_phone_number']
                            
                            print(f"📋 Status de entrega recebido do número: {display_phone_number}")
                            
                            for status_info in value['statuses']:
                                message_id = status_info['id']
                                status_type = status_info['status']
                                timestamp = status_info['timestamp']
                                recipient_id = status_info['recipient_id']
                                
                                print(f"📋 Status da mensagem {message_id}: {status_type}")
                                print(f"📋 Para: {recipient_id}")
                                print(f"📋 Timestamp: {timestamp}")
                                print("📋 (Status de entrega - não necessita resposta)")

        except KeyError as e:
            # Se a estrutura do JSON for diferente, apenas registre o erro
            print(f"Erro ao processar a mensagem: Chave não encontrada. Erro: {e}")
            print(f"Dados recebidos: {json.dumps(data, indent=2)}")
        except Exception as e:
            # Captura qualquer outra exceção que possa ocorrer
            print(f"Erro inesperado ao processar a mensagem: {e}")
            print(f"Dados recebidos: {json.dumps(data, indent=2)}")
            pass

        # #####################################################################
        # FIM DA LÓGICA DO CHATBOT
        # #####################################################################

        # A Meta espera uma resposta 200 OK para saber que recebemos a mensagem.
        return Response(status=status.HTTP_200_OK)