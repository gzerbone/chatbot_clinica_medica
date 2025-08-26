from django.contrib import admin

from .models import HorarioTrabalho, IndisponibilidadeMedico, Medico


class HorarioTrabalhoInline(admin.TabularInline):
    model = HorarioTrabalho
    extra = 1
    fields = ('dia_da_semana', 'hora_inicio', 'hora_fim', 'ativo')


class IndisponibilidadeInline(admin.TabularInline):
    model = IndisponibilidadeMedico
    extra = 0
    fields = ('tipo', 'data_inicio', 'data_fim', 'motivo')


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'crm', 'get_especialidades_display', 'atende_particular', 'preco_consulta', 'ativo')
    list_filter = ('ativo', 'atende_particular', 'especialidades', 'convenios')
    search_fields = ('nome', 'crm', 'bio')
    filter_horizontal = ('especialidades', 'convenios')
    list_editable = ('ativo', 'preco_consulta')
    inlines = [HorarioTrabalhoInline, IndisponibilidadeInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'nome', 'crm', 'ativo', 'foto')
        }),
        ('Informações Profissionais', {
            'fields': ('especialidades', 'bio', 'formacao')
        }),
        ('Atendimento', {
            'fields': ('convenios', 'atende_particular', 'preco_consulta', 'preco_retorno', 
                      'formas_pagamento', 'retorno_info', 'tempo_consulta')
        }),
        ('Contato', {
            'fields': ('email_profissional', 'telefone_profissional'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HorarioTrabalho)
class HorarioTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('medico', 'dia_da_semana', 'hora_inicio', 'hora_fim', 'ativo')
    list_filter = ('medico', 'dia_da_semana', 'ativo')
    list_editable = ('ativo',)
    ordering = ('medico', 'dia_da_semana', 'hora_inicio')


@admin.register(IndisponibilidadeMedico)
class IndisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('medico', 'tipo', 'data_inicio', 'data_fim', 'motivo')
    list_filter = ('medico', 'tipo', 'data_inicio')
    search_fields = ('medico__nome', 'motivo')
    date_hierarchy = 'data_inicio'