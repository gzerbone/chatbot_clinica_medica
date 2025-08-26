from django.contrib import admin

from .models import (ConversaWhatsApp, IntencaoUsuario, LogChatbot,
                     MensagemWhatsApp, RespostaAutomatica)


class MensagemInline(admin.TabularInline):
    model = MensagemWhatsApp
    extra = 0
    readonly_fields = ('criado_em',)
    fields = ('tipo', 'conteudo', 'processada', 'erro', 'criado_em')


class IntencaoInline(admin.TabularInline):
    model = IntencaoUsuario
    extra = 0
    readonly_fields = ('criado_em',)
    fields = ('intencao', 'confianca', 'entidades', 'criado_em')


@admin.register(ConversaWhatsApp)
class ConversaWhatsAppAdmin(admin.ModelAdmin):
    list_display = ('numero_whatsapp', 'usuario', 'ativa', 'ultima_interacao', 'criado_em')
    list_filter = ('ativa', 'ultima_interacao', 'criado_em')
    search_fields = ('numero_whatsapp', 'usuario__username', 'usuario__email')
    readonly_fields = ('criado_em', 'ultima_interacao')
    inlines = [MensagemInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_whatsapp', 'usuario', 'ativa')
        }),
        ('Contexto', {
            'fields': ('contexto',)
        }),
        ('Timestamps', {
            'fields': ('ultima_interacao', 'criado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MensagemWhatsApp)
class MensagemWhatsAppAdmin(admin.ModelAdmin):
    list_display = ('conversa', 'tipo', 'conteudo_resumido', 'processada', 'criado_em')
    list_filter = ('tipo', 'processada', 'criado_em')
    search_fields = ('conteudo', 'conversa__numero_whatsapp')
    readonly_fields = ('criado_em',)
    inlines = [IntencaoInline]
    
    def conteudo_resumido(self, obj):
        return f"{obj.conteudo[:100]}..." if len(obj.conteudo) > 100 else obj.conteudo
    conteudo_resumido.short_description = 'Conteúdo'


@admin.register(IntencaoUsuario)
class IntencaoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('mensagem', 'intencao', 'confianca_percentual', 'criado_em')
    list_filter = ('intencao', 'confianca', 'criado_em')
    search_fields = ('mensagem__conteudo',)
    readonly_fields = ('criado_em',)
    
    def confianca_percentual(self, obj):
        return f"{obj.confianca * 100:.1f}%"
    confianca_percentual.short_description = 'Confiança'


@admin.register(RespostaAutomatica)
class RespostaAutomaticaAdmin(admin.ModelAdmin):
    list_display = ('gatilho', 'tipo', 'prioridade', 'ativa', 'uso_contador', 'atualizado_em')
    list_filter = ('tipo', 'ativa', 'prioridade')
    search_fields = ('gatilho', 'resposta')
    list_editable = ('prioridade', 'ativa')
    readonly_fields = ('uso_contador', 'criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Configuração', {
            'fields': ('gatilho', 'tipo', 'prioridade', 'ativa')
        }),
        ('Resposta', {
            'fields': ('resposta',)
        }),
        ('Estatísticas', {
            'fields': ('uso_contador', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LogChatbot)
class LogChatbotAdmin(admin.ModelAdmin):
    list_display = ('nivel_colored', 'modulo', 'mensagem_resumida', 'conversa', 'criado_em')
    list_filter = ('nivel', 'modulo', 'criado_em')
    search_fields = ('mensagem', 'modulo')
    readonly_fields = ('criado_em',)
    date_hierarchy = 'criado_em'
    
    def nivel_colored(self, obj):
        from django.utils.html import format_html
        colors = {
            'debug': '#6c757d',
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'critical': '#721c24',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.nivel, '#000'),
            obj.get_nivel_display()
        )
    nivel_colored.short_description = 'Nível'
    
    def mensagem_resumida(self, obj):
        return f"{obj.mensagem[:100]}..." if len(obj.mensagem) > 100 else obj.mensagem
    mensagem_resumida.short_description = 'Mensagem'
    
    def has_add_permission(self, request):
        return False