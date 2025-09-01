# chatbot/admin.py

from django.contrib import admin
from .models import Conversa, Direcionamento

@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'iniciada_em', 'finalizada_em', 'status')
    list_filter = ('status', 'paciente')
    search_fields = ('paciente__nome_completo', 'paciente__telefone_whatsapp')
    list_per_page = 20

@admin.register(Direcionamento)
class DirecionamentoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'conversa', 'tipo_solicitacao', 'status')
    list_filter = ('status', 'paciente', 'tipo_solicitacao')
    search_fields = ('paciente__nome_completo', 'paciente__telefone_whatsapp')
    list_per_page = 20
