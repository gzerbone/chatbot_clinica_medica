from django.contrib import admin

# Register your models here.
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone_whatsapp', 'primeiro_contato', 'ultimo_contato')
    search_fields = ('nome_completo', 'telefone_whatsapp')
    list_filter = ('primeiro_contato', 'ultimo_contato')
    list_per_page = 20
