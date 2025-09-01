# chatbot/urls.py
from django.urls import path

from . import views

app_name = 'chatbot'

urlpatterns = [
    # Webhook principal do WhatsApp
    path('webhook/', views.WebhookView.as_view(), name='webhook'),
    
    # Endpoint para consultar status das conversas
    path('conversations/', views.ConversationStatusView.as_view(), name='conversations'),
    path('conversations/<str:user_number>/', views.ConversationStatusView.as_view(), name='conversation_detail'),
]