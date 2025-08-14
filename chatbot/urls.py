# chatbot/urls.py (arquivo novo)
from django.urls import path
from .views import WebhookView

urlpatterns = [
    # A URL completa será /chatbot/webhook/
    path('webhook/', WebhookView.as_view(), name='webhook'),
]