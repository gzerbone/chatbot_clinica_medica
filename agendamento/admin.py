from django.contrib import admin
from django.utils.html import format_html

from .models import Agendamento, BloqueioAgenda, HistoricoAgendamento


class HistoricoInline(admin.TabularInline):
    model = HistoricoAgendamento
    extra = 0
    readonly_fields = ('acao', 'descricao', 'usuario', 'data_hora', 'data_hora_anterior', 'medico_anterior')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente_nome', 'medico', 'data_hora_inicio', 'tipo_consulta', 
                   'status_colored', 'confirmado_por_paciente', 'agendado_via')
    list_filter = ('status', 'tipo_consulta', 'medico', 'especialidade', 'agendado_via', 
                  'confirmado_por_paciente', 'data_hora_inicio')
    search_fields = ('paciente_nome', 'paciente_telefone', 'paciente_email', 'paciente_cpf', 
                    'medico__nome', 'motivo_consulta')
    date_hierarchy = 'data_hora_inicio'
    readonly_fields = ('criado_em', 'atualizado_em', 'google_event_id', 'duracao_minutos_display')
    inlines = [HistoricoInline]
    
    fieldsets = (
        ('Informações do Paciente', {
            'fields': ('paciente', 'paciente_nome', 'paciente_telefone', 'paciente_email', 'paciente_cpf')
        }),
        ('Informações da Consulta', {
            'fields': ('medico', 'especialidade', 'tipo_consulta', 'data_hora_inicio', 
                      'data_hora_fim', 'duracao_minutos_display', 'status')
        }),
        ('Detalhes', {
            'fields': ('motivo_consulta', 'observacoes', 'convenio_utilizado', 'valor_consulta')
        }),
        ('Confirmação e Lembretes', {
            'fields': ('confirmado_por_paciente', 'data_confirmacao', 'lembrete_enviado', 'data_lembrete')
        }),
        ('Informações do Sistema', {
            'fields': ('agendado_via', 'agendado_por', 'google_event_id', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'pendente': '#FFA500',
            'confirmado': '#008000',
            'cancelado': '#FF0000',
            'realizado': '#0000FF',
            'nao_compareceu': '#808080',
            'remarcado': '#800080',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def duracao_minutos_display(self, obj):
        return f"{obj.duracao_minutos} minutos"
    duracao_minutos_display.short_description = 'Duração'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se for um novo agendamento
            obj.agendado_por = request.user
        super().save_model(request, obj, form, change)
        
        # Criar registro no histórico
        acao = 'criado' if not change else 'confirmado'
        HistoricoAgendamento.objects.create(
            agendamento=obj,
            acao=acao,
            usuario=request.user,
            descricao=f"Agendamento {acao} via admin"
        )


@admin.register(HistoricoAgendamento)
class HistoricoAgendamentoAdmin(admin.ModelAdmin):
    list_display = ('agendamento', 'acao', 'usuario', 'data_hora')
    list_filter = ('acao', 'data_hora')
    search_fields = ('agendamento__paciente_nome', 'descricao')
    date_hierarchy = 'data_hora'
    readonly_fields = ('agendamento', 'acao', 'descricao', 'usuario', 'data_hora', 
                      'data_hora_anterior', 'medico_anterior')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BloqueioAgenda)
class BloqueioAgendaAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'medico_ou_todos', 'tipo', 'data_hora_inicio', 'data_hora_fim', 'criado_por')
    list_filter = ('tipo', 'aplica_todos_medicos', 'data_hora_inicio')
    search_fields = ('motivo', 'medico__nome')
    date_hierarchy = 'data_hora_inicio'
    
    fieldsets = (
        ('Informações do Bloqueio', {
            'fields': ('tipo', 'motivo', 'medico', 'aplica_todos_medicos')
        }),
        ('Período', {
            'fields': ('data_hora_inicio', 'data_hora_fim')
        }),
        ('Metadados', {
            'fields': ('criado_por', 'criado_em'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('criado_em',)
    
    def medico_ou_todos(self, obj):
        if obj.aplica_todos_medicos or not obj.medico:
            return "Todos os médicos"
        return f"Dr(a). {obj.medico.nome}"
    medico_ou_todos.short_description = 'Aplicável a'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)