import json
import os

import google.generativeai as genai  # Importe a nova biblioteca
import requests

from .models import Agendamento, ClinicaInfo, Exame, HorarioTrabalho, Medico


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

def generate_gemini_response(chat_history):
    """
    Envia o histórico da conversa para a API do Gemini e retorna a resposta gerada.
    chat_history: Lista de mensagens no formato [{'role': 'user'/'model', 'parts': ['texto']}]
    """
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not gemini_api_key:
        return "Erro: A chave de API do Gemini não foi configurada."

    try:
        # Configura a API key
        genai.configure(api_key=gemini_api_key)

        # Configura o modelo que vamos usar. 'gemini-1.5-flash' é rápido e eficiente.
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # --- BUSCA DINÂMICA DE DADOS ---
        clinica = ClinicaInfo.objects.first() # Pega o primeiro (e único) registro da clínica
        medicos = Medico.objects.all()
        exames = Exame.objects.all()
        horarios_trabalho = HorarioTrabalho.objects.all()

        # --- MONTAGEM DA BASE DE CONHECIMENTO ESTRUTURADA ---
        knowledge_base = "<knowledge_base>\n"
        
        # Informações da Clínica
        knowledge_base += f"<clinica>\n"
        knowledge_base += f"  <nome>{clinica.nome}</nome>\n"
        knowledge_base += f"  <objetivo>{clinica.objetivo_geral}</objetivo>\n"
        knowledge_base += f"  <secretaria>O agendamento é feito exclusivamente pela secretária {clinica.secretaria_nome}.</secretaria>\n"
        knowledge_base += f"  <contato_telefonico>{clinica.telefone_contato}</contato_telefonico>\n"
        knowledge_base += f"  <endereco>{clinica.endereco}</endereco>\n"
        knowledge_base += f"  <referencia>{clinica.referencia_localizacao}</referencia>\n"
        knowledge_base += f"  <politica_atendimento>{clinica.politica_agendamento}</politica_atendimento>\n"
        knowledge_base += "</clinica>\n"

        # Informações dos Médicos
        knowledge_base += "<corpo_clinico>\n"
        for medico in medicos:
            knowledge_base += f"<medico>\n"
            knowledge_base += f"  <nome>{medico.nome}</nome>\n"
            knowledge_base += f"  <especialidades>{medico.get_especialidades_display()}</especialidades>\n"
            knowledge_base += f"  <bio>{medico.bio}</bio>\n"
            knowledge_base += f"  <convenios>{medico.convenios}</convenios>\n"
            knowledge_base += f"  <preco_particular>R$ {medico.preco_particular:.2f}</preco_particular>\n"
            knowledge_base += f"  <formas_pagamento>{medico.formas_pagamento}</formas_pagamento>\n"
            knowledge_base += f"  <retorno>{medico.retorno_info}</retorno>\n"
            knowledge_base += "</medico>\n"
        knowledge_base += "</corpo_clinico>\n"

        # Informações dos Horários de Trabalho
        knowledge_base += "<horarios_trabalho>\n"
        for horario in horarios_trabalho:
            knowledge_base += f"<horario>\n"
            knowledge_base += f"  <medico>{horario.medico.nome}</medico>\n"
            knowledge_base += f"  <dia>{horario.get_dia_da_semana_display()}</dia>\n"
            knowledge_base += f"  <horario_inicio>{horario.hora_inicio}</horario_inicio>\n"
            knowledge_base += f"  <horario_fim>{horario.hora_fim}</horario_fim>\n"
            knowledge_base += "</horario>\n"
        knowledge_base += "</horarios_trabalho>\n"

        # Informações dos Exames
        knowledge_base += "<exames_realizados>\n"
        for exame in exames:
            knowledge_base += f"<exame>\n"
            knowledge_base += f"  <nome>{exame.nome}</nome>\n"
            knowledge_base += f"  <preco>R$ {exame.preco:.2f}</preco>\n"
            knowledge_base += f"  <o_que_e>{exame.o_que_e}</o_que_e>\n"
            knowledge_base += f"  <como_funciona>{exame.como_funciona}</como_funciona>\n"
            knowledge_base += f"  <preparacao>{exame.preparacao or 'Nenhuma preparação específica necessária.'}</preparacao>\n"
            knowledge_base += f"  <vantagem>{exame.vantagem or ''}</vantagem>\n"
            knowledge_base += "</exame>\n"
        knowledge_base += "</exames_realizados>\n"
        
        knowledge_base += "</knowledge_base>"

        # --- TEMPLATE DO PROMPT (PARTE FIXA) ---
        system_prompt = f"""
            ### PERSONA ###
            Você é o PneumoSono, o assistente virtual oficial da Clínica PneumoSono. Sua personalidade é amigável, profissional e humana. Você se comunica em português do Brasil de forma clara e cordial.

            ### BASE DE CONHECIMENTO ###
            {knowledge_base}

            ### GUIA DE CONTEÚDO E TOM ###
            - **Pneumologia:** Ao falar sobre, use a descrição: "Especialidade dedicada à investigação, diagnóstico e tratamento das doenças do sistema respiratório..."
            - **Endocrinologia e Metabologia:** Ao falar sobre, use a descrição: "A Endocrinologia cuida do funcionamento das glândulas... A Metabologia foca no funcionamento do corpo..."
            - **Medicina do Sono:** Ao falar sobre, use a descrição: "Esta área apresenta intersecção com as demais especialidades. A principal doença é a apneia obstrutiva do sono..."
            - **Orientações sobre Sintomas:** Se o usuário perguntar o que fazer com sintomas, use os textos da seção "Orientações sobre Sintomas por Especialidade" do documento original, sempre reforçando que apenas uma consulta presencial pode dar um diagnóstico.

            ### REGRAS DE AÇÃO ###
            1.  **FONTE DA VERDADE:** Suas respostas devem se basear EXCLUSIVAMENTE nas informações dentro de `<knowledge_base>`. NUNCA invente informações. Se a informação não estiver lá, diga que não possui o detalhe e ofereça encaminhar para a secretária {clinica.secretaria_nome}.
            2.  **NÃO DÊ CONSELHOS MÉDICOS:** Se o usuário descrever sintomas, siga o GUIA DE CONTEÚDO, explique brevemente a relação com a especialidade e IMEDIATAMENTE recomende o agendamento de uma consulta.
            3.  **FLUXO DE AGENDAMENTO DE CONSULTA (NOVO E MAIS IMPORTANTE):**
            Sua principal função é guiar o usuário pelo processo de agendamento. Siga estes passos de forma estrita:

            - **PASSO A (Intenção):** Quando o usuário expressar o desejo de agendar, sua primeira ação é perguntar para qual médico ele deseja a consulta, listando os nomes disponíveis na `<knowledge_base>`.

            - **PASSO B (Coleta do Dia):** Após o usuário escolher o médico, sua segunda ação é perguntar para qual DIA ele gostaria de verificar a disponibilidade. Peça por uma data específica (ex: "para hoje", "amanhã", "dia 25 de agosto").

            - **PASSO C (Sinalização para o Sistema):** Após o usuário fornecer o dia, sua resposta para o sistema deve ser **APENAS** um comando especial formatado. Este comando será lido pelo nosso sistema para consultar a agenda real. O formato é:
            `[CONSULTAR_AGENDA: medico='Nome do Médico', dia='Data Informada pelo Usuário']`
            **Exemplos de como você deve responder nesta etapa:**
            - Se o usuário pediu Dr. Gustavo para amanhã: `[CONSULTAR_AGENDA: medico='Dr. Gustavo Magno', dia='amanhã']`
            - Se o usuário pediu Dr. Gleyton para 25/08/2025: `[CONSULTAR_AGENDA: medico='O Dr. Gleyton Porto', dia='25/08/2025']`
            **NÃO adicione nenhum outro texto, apenas o comando.**

            - **PASSO D (Apresentação e Confirmação):** O sistema irá processar o comando e te fornecerá os horários disponíveis. Sua tarefa será apresentar esses horários de forma amigável ao usuário e perguntar qual ele prefere. Uma vez que o usuário confirme um horário, você pedirá o nome completo dele para finalizar.

            - **PASSO E (Sinalização de Criação):** Após o usuário confirmar o horário e fornecer o nome, sua resposta para o sistema será outro comando especial:
            `[CRIAR_AGENDAMENTO: medico='Nome do Médico', dia='Data Confirmada', horario='Horário Confirmado', nome_paciente='Nome Completo do Paciente']`

            4.  **SEJA PROATIVO:** Sempre termine suas respostas com uma pergunta para guiar a conversa.
            """
            
        # Verifica se há histórico de conversa
        if not chat_history:
            return "Erro: Histórico de conversa vazio."
        
        # Prepara o histórico para o Gemini (exceto a última mensagem do usuário)
        gemini_history = [
            {'role': 'user', 'parts': [system_prompt]},
            {'role': 'model', 'parts': ["Entendido. Estou pronto para ajudar os pacientes da Clínica PneumoSono."]}
        ]
        
        # Adiciona o histórico anterior (se houver mais de 1 mensagem)
        if len(chat_history) > 1:
            gemini_history.extend(chat_history[:-1])
        
        # Inicia um chat com o system_prompt e o histórico
        chat = model.start_chat(history=gemini_history)

        # Envia a última mensagem do usuário para obter a nova resposta
        last_user_message = chat_history[-1]['parts'][0]
        response = chat.send_message(last_user_message)

        return response.text

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return "Desculpe, estou com um problema para processar sua solicitação no momento. Tente novamente mais tarde."
