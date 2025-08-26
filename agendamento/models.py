from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from clinica.models import Especialidade
from medicos.models import Medico
from usuarios.models import Paciente

User = get_user_model()


class Agendamento(models.Model):
    """
    Modelo para armazenar as consultas agendadas.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('realizado', 'Realizado'),
        ('nao_compareceu', 'Não Compareceu'),
        ('remarcado', 'Remarcado'),
    ]
    
    TIPO_CONSULTA_CHOICES = [
        ('consulta', 'Consulta'),
        ('retorno', 'Retorno'),
        ('exame', 'Exame'),
    ]
    
    # Informações do paciente
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name='agendamentos',
        blank=True,
        null=True,
        help_text="Paciente registrado no sistema"
    )
    paciente_nome = models.CharField(
        max_length=255,
        help_text="Nome do paciente (usado quando não há cadastro)"
    )
    paciente_telefone = models.CharField(
        max_length=20,
        help_text="Telefone/WhatsApp do paciente"
    )
    paciente_email = models.EmailField(blank=True, null=True)
    paciente_cpf = models.CharField(max_length=14, blank=True, null=True)
    
    # Informações da consulta
    medico = models.ForeignKey(
        Medico, 
        on_delete=models.PROTECT,
        related_name='agendamentos'
    )
    especialidade = models.ForeignKey(
        Especialidade,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Especialidade da consulta"
    )
    tipo_consulta = models.CharField(
        max_length=20,
        choices=TIPO_CONSULTA_CHOICES,
        default='primeira_vez'
    )
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pendente'
    )
    
    # Informações adicionais
    motivo_consulta = models.TextField(
        blank=True,
        null=True,
        help_text="Motivo ou sintomas relatados pelo paciente"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações sobre o agendamento"
    )
    convenio_utilizado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Convênio utilizado para esta consulta"
    )
    valor_consulta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Valor da consulta"
    )
    
    # Integração com Google Calendar
    google_event_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True,
        help_text="ID do evento no Google Calendar"
    )
    
    # Controle de confirmação
    confirmado_por_paciente = models.BooleanField(
        default=False,
        help_text="Se o paciente confirmou o agendamento"
    )
    data_confirmacao = models.DateTimeField(blank=True, null=True)
    lembrete_enviado = models.BooleanField(
        default=False,
        help_text="Se o lembrete foi enviado ao paciente"
    )
    data_lembrete = models.DateTimeField(blank=True, null=True)
    
    # Metadados
    agendado_via = models.CharField(
        max_length=50,
        default='chatbot',
        help_text="Canal pelo qual foi feito o agendamento (chatbot, telefone, presencial)"
    )
    agendado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='agendamentos_criados',
        help_text="Usuário que criou o agendamento"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_hora_inicio']
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        indexes = [
            models.Index(fields=['data_hora_inicio', 'medico']),
            models.Index(fields=['status']),
            models.Index(fields=['paciente_telefone']),
        ]
    
    def __str__(self):
        return f"Consulta de {self.paciente_nome} com Dr(a). {self.medico.nome} em {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        """Validações do modelo"""
        if self.data_hora_fim <= self.data_hora_inicio:
            raise ValidationError('A data/hora de fim deve ser posterior à data/hora de início.')
        
        # Verifica se o horário está dentro do expediente do médico
        # (implementar lógica adicional conforme necessário)
    
    def save(self, *args, **kwargs):
        # Se não houver valor definido, usa o preço padrão do médico
        if not self.valor_consulta and self.medico:
            if self.tipo_consulta == 'retorno' and self.medico.preco_retorno:
                self.valor_consulta = self.medico.preco_retorno
            else:
                self.valor_consulta = self.medico.preco_consulta
        
        # Se houver paciente cadastrado, preenche automaticamente alguns campos
        if self.paciente:
            if not self.paciente_nome:
                self.paciente_nome = self.paciente.usuario.get_full_name() or self.paciente.usuario.username
            if not self.paciente_telefone:
                self.paciente_telefone = self.paciente.usuario.telefone
            if not self.paciente_email:
                self.paciente_email = self.paciente.usuario.email
            if not self.paciente_cpf:
                self.paciente_cpf = self.paciente.usuario.cpf
        
        super().save(*args, **kwargs)
    
    @property
    def duracao_minutos(self):
        """Retorna a duração da consulta em minutos"""
        delta = self.data_hora_fim - self.data_hora_inicio
        return int(delta.total_seconds() / 60)
    
    @property
    def is_futuro(self):
        """Verifica se o agendamento é futuro"""
        return self.data_hora_inicio > timezone.now()
    
    @property
    def is_hoje(self):
        """Verifica se o agendamento é hoje"""
        hoje = timezone.now().date()
        return self.data_hora_inicio.date() == hoje


class HistoricoAgendamento(models.Model):
    """
    Modelo para armazenar o histórico de mudanças nos agendamentos.
    """
    ACAO_CHOICES = [
        ('criado', 'Criado'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('remarcado', 'Remarcado'),
        ('realizado', 'Realizado'),
        ('nao_compareceu', 'Não Compareceu'),
        ('lembrete_enviado', 'Lembrete Enviado'),
    ]
    
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='historico'
    )
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Usuário que realizou a ação"
    )
    data_hora = models.DateTimeField(auto_now_add=True)
    
    # Campos para remarcação
    data_hora_anterior = models.DateTimeField(blank=True, null=True)
    medico_anterior = models.ForeignKey(
        Medico,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historico_remarcacoes'
    )
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Histórico de Agendamento'
        verbose_name_plural = 'Históricos de Agendamentos'
    
    def __str__(self):
        return f"{self.agendamento} - {self.get_acao_display()} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class BloqueioAgenda(models.Model):
    """
    Modelo para bloquear períodos na agenda (feriados, manutenção, etc).
    """
    TIPO_BLOQUEIO_CHOICES = [
        ('feriado', 'Feriado'),
        ('manutencao', 'Manutenção'),
        ('reuniao', 'Reunião'),
        ('outro', 'Outro'),
    ]
    
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name='bloqueios',
        blank=True,
        null=True,
        help_text="Médico específico (deixe em branco para bloquear todos)"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_BLOQUEIO_CHOICES,
        default='outro'
    )
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    motivo = models.CharField(max_length=200)
    aplica_todos_medicos = models.BooleanField(
        default=False,
        help_text="Se o bloqueio se aplica a todos os médicos"
    )
    
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_hora_inicio']
        verbose_name = 'Bloqueio de Agenda'
        verbose_name_plural = 'Bloqueios de Agenda'
    
    def __str__(self):
        medico_str = f"Dr(a). {self.medico.nome}" if self.medico else "Todos os médicos"
        return f"Bloqueio - {medico_str}: {self.data_hora_inicio.strftime('%d/%m/%Y %H:%M')} - {self.motivo}"
    
    def clean(self):
        """Validações do modelo"""
        if self.data_hora_fim <= self.data_hora_inicio:
            raise ValidationError('A data/hora de fim deve ser posterior à data/hora de início.')
        
        if not self.medico and not self.aplica_todos_medicos:
            raise ValidationError('Selecione um médico ou marque "Aplica a todos os médicos".')