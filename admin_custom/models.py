from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class LogAcesso(models.Model):
    """
    Modelo para registrar acessos ao sistema administrativo.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logs_acesso'
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    acao = models.CharField(max_length=100)
    objeto_tipo = models.CharField(max_length=100, blank=True, null=True)
    objeto_id = models.IntegerField(blank=True, null=True)
    sucesso = models.BooleanField(default=True)
    mensagem = models.TextField(blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        indexes = [
            models.Index(fields=['-data_hora']),
            models.Index(fields=['usuario', '-data_hora']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class ConfiguracaoSistema(models.Model):
    """
    Modelo para armazenar configurações globais do sistema.
    """
    chave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('string', 'Texto'),
            ('integer', 'Número Inteiro'),
            ('float', 'Número Decimal'),
            ('boolean', 'Verdadeiro/Falso'),
            ('json', 'JSON'),
        ],
        default='string'
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Descrição da configuração"
    )
    editavel = models.BooleanField(
        default=True,
        help_text="Se esta configuração pode ser editada via admin"
    )
    categoria = models.CharField(
        max_length=50,
        default='geral',
        help_text="Categoria da configuração"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    atualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='configuracoes_atualizadas'
    )
    
    class Meta:
        ordering = ['categoria', 'chave']
        verbose_name = 'Configuração do Sistema'
        verbose_name_plural = 'Configurações do Sistema'
    
    def __str__(self):
        return f"{self.categoria} - {self.chave}"
    
    def get_valor(self):
        """Retorna o valor convertido para o tipo correto"""
        if self.tipo == 'integer':
            return int(self.valor)
        elif self.tipo == 'float':
            return float(self.valor)
        elif self.tipo == 'boolean':
            return self.valor.lower() in ('true', '1', 'sim', 'yes')
        elif self.tipo == 'json':
            import json
            return json.loads(self.valor)
        return self.valor


class NotificacaoAdmin(models.Model):
    """
    Modelo para notificações internas do sistema administrativo.
    """
    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
        ('success', 'Sucesso'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='info'
    )
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='media'
    )
    destinatarios = models.ManyToManyField(
        User,
        related_name='notificacoes_admin',
        blank=True,
        help_text="Deixe em branco para enviar a todos os administradores"
    )
    lida = models.BooleanField(default=False)
    ativa = models.BooleanField(default=True)
    url_acao = models.URLField(
        blank=True,
        null=True,
        help_text="URL para ação relacionada"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='notificacoes_criadas'
    )
    
    class Meta:
        ordering = ['-criado_em', '-prioridade']
        verbose_name = 'Notificação Admin'
        verbose_name_plural = 'Notificações Admin'
    
    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo}"


class RelatorioPersonalizado(models.Model):
    """
    Modelo para armazenar configurações de relatórios personalizados.
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    query_sql = models.TextField(
        blank=True,
        null=True,
        help_text="Query SQL personalizada (use com cuidado)"
    )
    modelo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nome do modelo Django"
    )
    filtros = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtros em formato JSON"
    )
    campos_exibir = models.JSONField(
        default=list,
        blank=True,
        help_text="Campos a exibir no relatório"
    )
    agrupamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Campo para agrupamento"
    )
    ordenacao = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Campo para ordenação"
    )
    ativo = models.BooleanField(default=True)
    publico = models.BooleanField(
        default=False,
        help_text="Se o relatório é visível para todos os usuários"
    )
    
    criado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='relatorios_criados'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Relatório Personalizado'
        verbose_name_plural = 'Relatórios Personalizados'
    
    def __str__(self):
        return self.nome