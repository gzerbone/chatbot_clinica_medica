# chatbot/models.py
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ConversaWhatsApp(models.Model):
    """
    Modelo para armazenar conversas do WhatsApp com o chatbot.
    """
    numero_whatsapp = models.CharField(max_length=20)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='conversas_whatsapp'
    )
    contexto = models.JSONField(
        default=dict,
        help_text="Contexto da conversa em formato JSON"
    )
    ultima_interacao = models.DateTimeField(auto_now=True)
    ativa = models.BooleanField(default=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-ultima_interacao']
        verbose_name = 'Conversa WhatsApp'
        verbose_name_plural = 'Conversas WhatsApp'
    
    def __str__(self):
        return f"Conversa com {self.numero_whatsapp}"


class MensagemWhatsApp(models.Model):
    """
    Modelo para armazenar mensagens individuais do WhatsApp.
    """
    TIPO_MENSAGEM_CHOICES = [
        ('usuario', 'Usuário'),
        ('bot', 'Bot'),
        ('sistema', 'Sistema'),
    ]
    
    conversa = models.ForeignKey(
        ConversaWhatsApp,
        on_delete=models.CASCADE,
        related_name='mensagens'
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_MENSAGEM_CHOICES
    )
    conteudo = models.TextField()
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados da mensagem (IDs, timestamps, etc)"
    )
    processada = models.BooleanField(default=False)
    erro = models.TextField(blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['criado_em']
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.conteudo[:50]}..."


class IntencaoUsuario(models.Model):
    """
    Modelo para armazenar intenções identificadas nas mensagens dos usuários.
    """
    INTENCAO_CHOICES = [
        ('agendar_consulta', 'Agendar Consulta'),
        ('remarcar_consulta', 'Remarcar Consulta'),
        ('cancelar_consulta', 'Cancelar Consulta'),
        ('informacao_medico', 'Informação sobre Médico'),
        ('informacao_exame', 'Informação sobre Exame'),
        ('informacao_clinica', 'Informação sobre Clínica'),
        ('horario_funcionamento', 'Horário de Funcionamento'),
        ('localizacao', 'Localização'),
        ('valores', 'Valores e Preços'),
        ('convenios', 'Convênios'),
        ('outro', 'Outro'),
    ]
    
    mensagem = models.ForeignKey(
        MensagemWhatsApp,
        on_delete=models.CASCADE,
        related_name='intencoes'
    )
    intencao = models.CharField(
        max_length=30,
        choices=INTENCAO_CHOICES
    )
    confianca = models.FloatField(
        default=0.0,
        help_text="Nível de confiança na identificação da intenção (0-1)"
    )
    entidades = models.JSONField(
        default=dict,
        blank=True,
        help_text="Entidades extraídas (datas, nomes, etc)"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confianca']
        verbose_name = 'Intenção do Usuário'
        verbose_name_plural = 'Intenções dos Usuários'
    
    def __str__(self):
        return f"{self.get_intencao_display()} (Confiança: {self.confianca:.2f})"


class RespostaAutomatica(models.Model):
    """
    Modelo para armazenar respostas automáticas padrão do chatbot.
    """
    gatilho = models.CharField(
        max_length=100,
        unique=True,
        help_text="Palavra-chave ou padrão que ativa esta resposta"
    )
    resposta = models.TextField(
        help_text="Texto da resposta automática"
    )
    tipo = models.CharField(
        max_length=30,
        default='informacao',
        help_text="Tipo/categoria da resposta"
    )
    prioridade = models.IntegerField(
        default=0,
        help_text="Prioridade da resposta (maior número = maior prioridade)"
    )
    ativa = models.BooleanField(default=True)
    uso_contador = models.IntegerField(
        default=0,
        help_text="Contador de quantas vezes foi usada"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prioridade', 'gatilho']
        verbose_name = 'Resposta Automática'
        verbose_name_plural = 'Respostas Automáticas'
    
    def __str__(self):
        return f"{self.gatilho} - {self.tipo}"


class LogChatbot(models.Model):
    """
    Modelo para registrar logs de atividades do chatbot.
    """
    NIVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    nivel = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        default='info'
    )
    modulo = models.CharField(
        max_length=100,
        help_text="Módulo/componente que gerou o log"
    )
    mensagem = models.TextField()
    detalhes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detalhes adicionais em JSON"
    )
    conversa = models.ForeignKey(
        ConversaWhatsApp,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='logs'
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Log do Chatbot'
        verbose_name_plural = 'Logs do Chatbot'
        indexes = [
            models.Index(fields=['-criado_em', 'nivel']),
        ]
    
    def __str__(self):
        return f"[{self.get_nivel_display()}] {self.modulo}: {self.mensagem[:50]}..."