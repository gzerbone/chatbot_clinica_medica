from django.shortcuts import render

# Create your views here.
# chatbot/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os # Importe a biblioteca os
import json # Importe a biblioteca json

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
        print(json.dumps(data, indent=2))

        # #####################################################################
        # AQUI COMEÇA A LÓGICA DO SEU CHATBOT
        # #####################################################################
        
        # Exemplo de como extrair a mensagem do usuário (pode variar um pouco)
        try:
            # Verifica se é uma mensagem do WhatsApp
            if data['object'] == 'whatsapp_business_account':
                for entry in data['entry']:
                    for change in entry['changes']:
                        if 'messages' in change['value']:
                            message_data = change['value']['messages'][0]
                            from_number = message_data['from']
                            message_text = message_data['text']['body']

                            print(f"Mensagem de: {from_number}")
                            print(f"Texto: {message_text}")
                            
                            # AQUI VOCÊ CHAMARIA A FUNÇÃO PARA ENVIAR UMA RESPOSTA
                            # Ex: send_whatsapp_message(from_number, "Olá! Recebi sua mensagem.")

        except KeyError as e:
            # Se a estrutura do JSON for diferente, apenas registre o erro
            print(f"Erro ao processar a mensagem: Estrutura de dados inesperada. Erro: {e}")
            pass

        # #####################################################################
        # FIM DA LÓGICA DO CHATBOT
        # #####################################################################

        # A Meta espera uma resposta 200 OK para saber que recebemos a mensagem.
        return Response(status=status.HTTP_200_OK)