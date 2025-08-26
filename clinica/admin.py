from django.contrib import admin

from .models import ClinicaInfo, Convenio, Especialidade, Exame


@admin.register(ClinicaInfo)
class ClinicaInfoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone_contato', 'email', 'atualizado_em')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'objetivo_geral', 'secretaria_nome')
        }),
        ('Contato', {
            'fields': ('telefone_contato', 'telefone_whatsapp', 'email')
        }),
        ('Localização', {
            'fields': ('endereco', 'referencia_localizacao')
        }),
        ('Horários e Políticas', {
            'fields': ('horario_funcionamento', 'politica_agendamento', 'politica_cancelamento')
        }),
        ('Integração', {
            'fields': ('google_calendar_id',)
        }),
        ('Redes Sociais', {
            'fields': ('instagram', 'facebook', 'website'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Permite adicionar apenas se não existir nenhuma instância
        return not ClinicaInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Não permite deletar
        return False


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa', 'criado_em')
    list_filter = ('ativa',)
    search_fields = ('nome', 'descricao')
    list_editable = ('ativa')
    ordering = ('nome')


@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'duracao_media', 'ativo', 'criado_em')
    list_filter = ('ativo', 'especialidades')
    search_fields = ('nome', 'o_que_e', 'como_funciona')
    list_editable = ('preco', 'ativo')
    filter_horizontal = ('especialidades',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'preco', 'duracao_media', 'ativo')
        }),
        ('Descrições', {
            'fields': ('o_que_e', 'como_funciona', 'preparacao', 'vantagem')
        }),
        ('Relacionamentos', {
            'fields': ('especialidades',)
        }),
    )


@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')
    list_editable = ('ativo',)