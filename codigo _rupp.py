from django.shortcuts import render

# Create your views here.
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

logger = logging.getLogger(_name_)

import json # É uma boa prática importar
from msgreceiver.models import Lead, Message
# Supondo que VERIFY_TOKEN esteja definido em algum lugar, como no seu settings.py
VERIFY_TOKEN = "gabi" 

ACCESS_TOKEN = "EAAHqPN7ohfcBO4fJp1Fyy4AHjQTSj3tkKMYTFfBuF8dlWNSgt343IfDh8X6hnC19cZBw9pPJgDYQ3q44wL7hE9MQCNMdjU8dYHixQZC7k2dvGPNX8RCEtINPnc84CAGNQknebOvzbRQXVZCZBgQPmaLZBjp1QZAdIAD2u1s0CCjqC3DQQFCQOhswR40NogJXuXZAAZDZD"
PHONE_NUMBER_ID = "463940203471489"



import requests


def send_whatsapp_message(recipient, message):
    ACCESS_TOKEN = "EAAHqPN7ohfcBO4fJp1Fyy4AHjQTSj3tkKMYTFfBuF8dlWNSgt343IfDh8X6hnC19cZBw9pPJgDYQ3q44wL7hE9MQCNMdjU8dYHixQZC7k2dvGPNX8RCEtINPnc84CAGNQknebOvzbRQXVZCZBgQPmaLZBjp1QZAdIAD2u1s0CCjqC3DQQFCQOhswR40NogJXuXZAAZDZD"
    PHONE_NUMBER_ID = "463940203471489"
    WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": message
        }
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    return response.json()


from openai import OpenAI

def generate_response(message_user,memoria_gerada):
    client = OpenAI(api_key = "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")
    prompt_geral = """Você atuará como secretário(a) de uma clínica médica. Formate as respostas com Emojis e simbolos para facilitar o entendimento
    Sempre faca um questionamento por vez ao usuário, para que ele possa responder de forma clara e objetiva.
    Sua função é responder às perguntas dos usuários de forma cordial e objetiva, seguindo estritamente estas regras:
    \n\n1.  *Planos de Saúde*: Aceitamos exclusivamente Unimed e Bradesco. Se o usuário perguntar sobre qualquer outro plano, informe que não o aceitamos.
    \n\n2.  *Consulta Particular*: O valor da consulta particular é de R$ 500,00.
    \n\n3.  *Horário de Funcionamento*: Nosso horário de atendimento é das 07:30 às 22:00.
     """
    print(memoria_gerada)
    messages_memory  = [{"role": "system", "content":prompt_geral }] + memoria_gerada + [
            {"role": "user", "content": f'{message_user}'},
        ]
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages_memory
        )

    return response.choices[0].message.content


def generate_memory(lead):
    from msgreceiver.models import Lead
    memoria = []
    menssagem_usuario =Message.objects.filter(lead=lead)

    if menssagem_usuario.exists():
        for menssagem in menssagem_usuario:
            if menssagem.remetente == 'user':
                memoria.append({"role": "user", "content": menssagem.body})
            elif menssagem.remetente == 'assistant':
                memoria.append({"role": "assistant", "content": menssagem.body})
    return memoria 
                

class WebhookView(APIView):
    def get(self, request):
        # Verificação inicial do webhook
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFICADO")
            return HttpResponse(challenge, status=200)
        return HttpResponse("Erro de verificação", status=403)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            # Acessa os dados da mensagem
            value = data['entry'][0]['changes'][0]['value']
            
            # Verifica se é uma mensagem de texto
            if value.get('messages') and value['messages'][0].get('type') == 'text':
                message_data = value['messages'][0]
                contact_data = value['contacts'][0]
                
                # Extrai os campos solicitados
                profile_name = contact_data['profile']['name']
                whatsapp_id = contact_data['wa_id']
                text_body = message_data['text']['body']
                message_type = message_data['type'] # Será sempre 'text' devido à verificação
                
                # Imprime os dados no console
                print("--- Nova Mensagem Recebida ---")
                print(f"Nome do Contato: {profile_name}")
                print(f"ID do WhatsApp: {whatsapp_id}")
                print(f"Corpo do Texto: {text_body}")
                print(f"Tipo: {message_type}")
                print("---------------------------------")
                
                # de um get or create no banco de dados na tabela Lead 
                from msgreceiver.models import Lead, Message
                lead, created = Lead.objects.get_or_create(
                    name=profile_name,
                    wa_id=whatsapp_id
                )

                # Cria uma nova mensagem associada ao lead
                Message.objects.create(
                    lead=lead,
                    remetente='user',
                    body=text_body, 
                    message_type=message_type
                )


                memoria_gerada=generate_memory(lead)

            

                response_text = generate_response(text_body,memoria_gerada)


                send_whatsapp_message(whatsapp_id, response_text)


                Message.objects.create(
                    lead=lead,
                    remetente='assistant',
                    body=response_text, 
                    message_type=message_type
                )
                
        except (KeyError, IndexError):
            # Ignora webhooks que não são mensagens de texto (ex: status de entrega)
            pass

        # Retorna HTTP 201 Created para confirmar o recebimento ao WhatsApp
        return Response(status=status.HTTP_201_CREATED)