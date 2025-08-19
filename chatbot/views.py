import json  # Importe a biblioteca json
import os  # Importe a biblioteca os

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import generate_gemini_response, send_whatsapp_message

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
                        
                        # Verifica se contém mensagens
                        if 'messages' in value:
                            for message in value['messages']:
                                from_number = message['from']
                                message_type = message['type']
                                
                                if message_type == 'text':
                                    message_text = message['text']['body']
                                    print(f"Texto do usuário: {message_text}")
                                    
                                    # Nova lógica com o "Cérebro" Gemini
                                    print("Consultando a IA do Google para obter uma resposta...")
                                    response_text = generate_gemini_response(message_text)
                                    print(f"Resposta gerada pela IA: {response_text}")
                                    
                                    # Envia a resposta inteligente para o usuário
                                    send_whatsapp_message(from_number, response_text)
                                
                                elif message_type == 'image':
                                    print("Imagem recebida")
                                elif message_type == 'audio':
                                    print("Áudio recebido")
                                elif message_type == 'document':
                                    print("Documento recebido")
                        
                        # Verifica se contém status de entrega/leitura (não precisa responder)
                        elif 'statuses' in value:
                            print("📋 Status de entrega recebido (ignorando)")

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