from django.contrib import admin

from .models import (ConfiguracaoSistema, LogAcesso, NotificacaoAdmin,
                     RelatorioPersonalizado)


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'acao', 'objeto_tipo', 'objeto_id', 'sucesso', 'data_hora', 'ip_address')
    list_filter = ('sucesso', 'acao', 'objeto_tipo', 'data_hora')
    search_fields = ('usuario__username', 'acao', 'mensagem', 'ip_address')
    date_hierarchy = 'data_hora'
    readonly_fields = ('usuario', 'ip_address', 'user_agent', 'acao', 'objeto_tipo', 
                      'objeto_id', 'sucesso', 'mensagem', 'data_hora')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'categoria', 'tipo', 'editavel', 'atualizado_em')
    list_filter = ('categoria', 'tipo', 'editavel')
    search_fields = ('chave', 'descricao', 'valor')
    readonly_fields = ('criado_em', 'atualizado_em', 'atualizado_por')
    list_editable = ('editavel',)
    
    fieldsets = (
        ('Configuração', {
            'fields': ('chave', 'valor', 'tipo', 'categoria')
        }),
        ('Informações', {
            'fields': ('descricao', 'editavel')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'atualizado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj and not obj.editavel and not request.user.is_superuser:
            readonly.extend(['chave', 'valor', 'tipo', 'categoria'])
        return readonly


@admin.register(NotificacaoAdmin)
class NotificacaoAdminAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_colored', 'prioridade_colored', 'lida', 'ativa', 'criado_em')
    list_filter = ('tipo', 'prioridade', 'lida', 'ativa', 'criado_em')
    search_fields = ('titulo', 'mensagem')
    filter_horizontal = ('destinatarios',)
    date_hierarchy = 'criado_em'
    readonly_fields = ('criado_em', 'criado_por')
    
    fieldsets = (
        ('Notificação', {
            'fields': ('titulo', 'mensagem', 'tipo', 'prioridade')
        }),
        ('Configurações', {
            'fields': ('destinatarios', 'lida', 'ativa', 'url_acao')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_colored(self, obj):
        from django.utils.html import format_html
        colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'success': '#28a745',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.tipo, '#000'),
            obj.get_tipo_display()
        )
    tipo_colored.short_description = 'Tipo'
    
    def prioridade_colored(self, obj):
        from django.utils.html import format_html
        colors = {
            'baixa': '#6c757d',
            'media': '#17a2b8',
            'alta': '#ffc107',
            'urgente': '#dc3545',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.prioridade, '#000'),
            obj.get_prioridade_display()
        )
    prioridade_colored.short_description = 'Prioridade'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(RelatorioPersonalizado)
class RelatorioPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'modelo', 'agrupamento', 'ordenacao', 'publico', 'ativo', 'criado_por')
    list_filter = ('ativo', 'publico', 'modelo')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por')
    list_editable = ('ativo', 'publico')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ativo', 'publico')
        }),
        ('Configuração do Relatório', {
            'fields': ('modelo', 'query_sql', 'filtros', 'campos_exibir', 'agrupamento', 'ordenacao')
        }),
        ('Metadados', {
            'fields': ('criado_por', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(models.Q(publico=True) | models.Q(criado_por=request.user))