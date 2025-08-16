# chatbot/utils.py

import requests
import os
import json

def send_whatsapp_message(to_number, message_text):
    """
    Envia uma mensagem de texto simples para um número do WhatsApp.
    """
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

    if not access_token or not phone_number_id:
        print("Erro: As variáveis de ambiente WHATSAPP_ACCESS_TOKEN e WHATSAPP_PHONE_NUMBER_ID não foram definidas.")
        return

    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    print(f"Enviando para {to_number}: {message_text}")
    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(f"Status da Resposta da Meta: {response.status_code}")
    print(f"Corpo da Resposta da Meta: {response.json()}")

    return response