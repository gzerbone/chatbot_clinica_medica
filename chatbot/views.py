import json  # Importe a biblioteca json
import os  # Importe a biblioteca os

from django.core.cache import cache  # Importe o cache do Django
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
                        
                        if 'messages' in value:
                            message_data = value['messages'][0]
                            from_number = message_data['from']
                            
                            # Apenas processa mensagens de texto por enquanto
                            if message_data['type'] == 'text':
                                message_text = message_data['text']['body']
                                
                                # --- INÍCIO DA LÓGICA DE MEMÓRIA ---
                                
                                # 1. Cria uma chave de sessão única para este usuário
                                session_key = f"whatsapp_session_{from_number}"
                                
                                # 2. Tenta recuperar a "ficha de atendimento" (dados da conversa) do cache
                                conversation_data = cache.get(session_key, {}) # Retorna {} se não encontrar
                                
                                # 3. Recupera o histórico e o estado atual da conversa
                                chat_history = conversation_data.get('history', [])
                                conversation_state = conversation_data.get('state', 'START')
                                
                                print(f"Usuário: {from_number} | Estado Atual: {conversation_state}")

                                # 4. Adiciona a nova mensagem do usuário ao histórico
                                chat_history.append({'role': 'user', 'parts': [message_text]})

                                # 5. Chama a IA, agora passando o histórico da conversa
                                gemini_response_text = generate_gemini_response(chat_history)
                                
                                # 6. Adiciona a resposta da IA ao histórico
                                chat_history.append({'role': 'model', 'parts': [gemini_response_text]})
                                
                                # 7. Processa a resposta da IA para ver se é um comando
                                if '[CONSULTAR_AGENDA:' in gemini_response_text:
                                    # O bot decidiu que é hora de consultar a agenda.
                                    # Por enquanto, vamos apenas simular e mudar o estado.
                                    
                                    # Futuramente, aqui você extrairia os dados e chamaria o google_calendar_service.py
                                    print("COMANDO DETECTADO: [CONSULTAR_AGENDA]")
                                    
                                    # Mudamos o estado para o próximo passo
                                    new_state = 'AWAITING_TIME_CHOICE'
                                    
                                    # Mensagem de simulação para o usuário
                                    final_response_text = "Ok, estou verificando a agenda... (simulação). Encontrei horários às 10:00, 11:00 e 15:00. Qual prefere?"
                                
                                elif '[CRIAR_AGENDAMENTO:' in gemini_response_text:
                                    # Lógica similar para o comando de criação
                                    print("COMANDO DETECTADO: [CRIAR_AGENDAMENTO]")
                                    new_state = 'START' # Reseta a conversa
                                    final_response_text = "Perfeito! Agendamento confirmado! (simulação)."
                                    
                                else:
                                    # É uma resposta normal, o estado continua o mesmo ou reseta se necessário
                                    new_state = conversation_state # Mantém o estado
                                    final_response_text = gemini_response_text
                                
                                # 8. Atualiza a "ficha de atendimento" com os novos dados
                                updated_conversation_data = {
                                    'state': new_state,
                                    'history': chat_history
                                }
                                
                                # 9. Salva a ficha atualizada no cache por 15 minutos
                                cache.set(session_key, updated_conversation_data, timeout=60)
                                
                                # 10. Envia a resposta final para o usuário
                                send_whatsapp_message(from_number, final_response_text)

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