"""
Serviço responsável pela comunicação com WhatsApp Business API
"""
import json
import os
from typing import Optional

import requests


class WhatsAppService:
    """Serviço para gerenciar comunicação com WhatsApp"""
    
    def __init__(self):
        self.access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
        self.bot_phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
        
        if not self.access_token or not self.bot_phone_number_id:
            raise ValueError("Variáveis de ambiente do WhatsApp não configuradas")
        
        self.api_url = f"https://graph.facebook.com/v19.0/{self.bot_phone_number_id}/messages"
    
    def send_text_message(self, user_number: str, message_text: str) -> Optional[requests.Response]:
        """
        Envia uma mensagem de texto para um número do WhatsApp
        
        Args:
            user_number: Número do usuário (formato: 5511999999999)
            message_text: Texto da mensagem
            
        Returns:
            Response da API ou None em caso de erro
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
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
        
        try:
            print(f"Enviando para {user_number}: {message_text}")
            response = requests.post(
                self.api_url, 
                headers=headers, 
                data=json.dumps(data)
            )
            
            print(f"Status da Resposta da Meta: {response.status_code}")
            print(f"Corpo da Resposta da Meta: {response.json()}")
            
            return response
            
        except Exception as e:
            print(f"Erro ao enviar mensagem WhatsApp: {e}")
            return None
    
    def send_template_message(self, user_number: str, template_name: str, language_code: str = "pt_BR") -> Optional[requests.Response]:
        """
        Envia uma mensagem de template do WhatsApp
        
        Args:
            user_number: Número do usuário
            template_name: Nome do template aprovado
            language_code: Código do idioma (padrão: pt_BR)
            
        Returns:
            Response da API ou None em caso de erro
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": user_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                data=json.dumps(data)
            )
            return response
            
        except Exception as e:
            print(f"Erro ao enviar template WhatsApp: {e}")
            return None
