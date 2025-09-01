# agendamento/admin.py
from django.contrib import admin
from .models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('paciente_nome', 'medico', 'data_hora_inicio', 'status')
    list_filter = ('status', 'medico')
    search_fields = ('paciente_nome', 'medico__nome')
    list_per_page = 20