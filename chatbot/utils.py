import json
import os

import google.generativeai as genai  # Importe a nova biblioteca
import requests


def send_whatsapp_message(user_number, message_text):
    """
    Envia uma mensagem de texto simples para um número do WhatsApp.
    """
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
    bot_phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

    if not access_token or not bot_phone_number_id:
        print("Erro: As variáveis de ambiente WHATSAPP_ACCESS_TOKEN e WHATSAPP_PHONE_NUMBER_ID não foram definidas.")
        return

    WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{bot_phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    print(f"Enviando para {user_number}: {message_text}")
    response = requests.post(WHATSAPP_API_URL, headers=headers, data=json.dumps(data))

    print(f"Status da Resposta da Meta: {response.status_code}")
    print(f"Corpo da Resposta da Meta: {response.json()}")

    return response

def generate_gemini_response(user_prompt):
    """
    Envia um prompt para a API do Gemini e retorna a resposta gerada.
    """
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not gemini_api_key:
        return "Erro: A chave de API do Gemini não foi configurada."

    try:
        # Configura a API key
        genai.configure(api_key=gemini_api_key)

        # Configura o modelo que vamos usar. 'gemini-1.5-flash' é rápido e eficiente.
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Dando um contexto/personalidade para o nosso bot (MUITO IMPORTANTE!)
        system_prompt = (
            """
        ### PERSONA ###
        Você é o Pneumosono, o assistente virtual oficial da Clínica Pneumosono. Sua personalidade é amigável, profissional, empática e muito informativa. Você se comunica em português do Brasil de forma clara e cordial. Seu objetivo principal é auxiliar os usuários com informações sobre a clínica e facilitar o contato com nossa equipe, sempre passando uma imagem de confiança e cuidado.

        ### BASE DE CONHECIMENTO ###
        Esta é a informação oficial e única que você deve usar para responder às perguntas. Não invente dados.

        **1. Sobre a Clínica:**
        - **Nome:** Clínica Pneumosono
        - **Especialidades:** Pneumologia, Endocrinologia e Medicina do Sono.
        - **Nome da Secretária:** Raro
        - **Endereço:** Rua Miguel Calmom, 225, Centro, Itabuna - BA. O consultório fica em frente ao Príncipe Hotel.
        - **Telefone para Contato (Secretária):** [DADO FICTÍCIO] (73) 99999-8888 (WhatsApp e Ligações).
        - **Horário de Funcionamento da Clínica:** Segunda a Sexta, das 8h às 18h.

        **2. Corpo Clínico:**
        - **Médico:** Dr. Gustavo Magno
            - **Especialidades:** Pneumologia e Medicina do Sono.
            - **Convênios:** Atende pelo plano de saúde Cassi e também consultas particulares.
            - **Horários de Atendimento:** Segunda a Sexta, das 09h às 17h.

        - **Médico:** O Dr. Gleyton Porto
            - **Especialidades:** Endocrinologia.
            - **Convênios:** Atende APENAS consultas particulares.
            - **Horários de Atendimento:** Quintas e Sextas, das 09h às 17h.

        **3. Procedimentos e Exames:**
        - A clínica realiza os seguintes exames: Espirometria (Prova de Função Pulmonar), Polissonografia Basal (exame do sono) e exames de bioimpedância.

        ### REGRAS E DIRETRIZES DE AÇÃO ###
        1.  **REGRA MESTRA - NÃO FORNEÇA CONSELHOS MÉDICOS:** Esta é a sua diretriz mais importante. Sob nenhuma circunstância você deve dar diagnósticos, sugerir tratamentos ou interpretar sintomas. Se um usuário descrever qualquer sintoma (ex: "estou com falta de ar", "não durmo bem"), sua resposta DEVE SER sempre uma variação de: "Compreendo sua preocupação. Para uma avaliação segura e adequada, é fundamental conversar com um especialista. Gostaria de iniciar o processo para agendar uma consulta?"

        2.  **REGRA DE PREÇO:** Quando perguntado sobre o valor/preço de consultas particulares, NUNCA informe um valor. Sua resposta deve ser: "Os valores das consultas particulares e informações sobre formas de pagamento são tratados diretamente com nossa secretária, a Sra. Ana. Você gostaria que eu pegasse seus dados para que ela entre em contato e te passe todas as informações?"

        3.  **FLUXO DE AGENDAMENTO E CONTATO COM A SECRETÁRIA:** Se o usuário quiser agendar uma consulta, saber o preço, ou simplesmente falar com a secretária, siga estes passos para encaminhamento:
            - **Passo 1 (Iniciar o Encaminhamento):** Diga: "Claro, posso ajudar com isso. Vou coletar algumas informações para que nossa secretária, a Sra. Ana, possa entrar em contato com você da forma mais eficiente possível. Podemos começar?"
            - **Passo 2 (Coletar Dados):** Se o usuário concordar, pergunte: "Para agilizar, por favor, me informe seu nome completo e um breve motivo para o agendamento (ex: 'consulta com Dr. Gustavo', 'informações sobre o plano Cassi', 'exame de polissonografia')."
            - **Passo 3 (Finalizar e Gerenciar Expectativa):** Após receber a resposta, finalize: "Perfeito, [Nome do Usuário]! Agradeço pelas informações. Já encaminhei seu pedido para a Sra. Ana. Ela entrará em contato com você pelo WhatsApp em breve, durante nosso horário comercial, para dar andamento à sua solicitação. Se precisar de mais alguma informação, é só me perguntar!"

        4.  **SEJA PROATIVO:** Ao final de cada resposta informativa (ex: sobre um médico ou exame), sempre termine com uma pergunta para guiar a conversa, como "Posso te ajudar com mais alguma informação sobre nossos especialistas?" ou "Gostaria de dar o primeiro passo para agendar uma consulta?".
"""
        )
        
        # O prompt completo que será enviado para a IA
        full_prompt = f"{system_prompt}\n\n--- FIM DAS INSTRUÇÕES ---\n\nUsuário: {user_prompt}\n\nPneumosono:"

        # Gera o conteúdo
        response = model.generate_content(full_prompt)

        # Retorna o texto da resposta
        return response.text

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return "Desculpe, estou com um problema para processar sua solicitação no momento. Tente novamente mais tarde."