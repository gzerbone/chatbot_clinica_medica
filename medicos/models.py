from django.contrib.auth import get_user_model
from django.db import models

from clinica.models import Convenio, Especialidade

User = get_user_model()


class Medico(models.Model):
    """
    Modelo para armazenar informações dos médicos.
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_medico',
        blank=True,
        null=True,
        help_text="Usuário associado ao médico (opcional)"
    )
    nome = models.CharField(max_length=100)
    crm = models.CharField(
        max_length=20,
        unique=True,
        help_text="Número do CRM do médico"
    )
    especialidades = models.ManyToManyField(
        Especialidade, 
        related_name='medicos',
        help_text="Selecione uma ou mais especialidades do médico"
    )
    bio = models.TextField(
        help_text="Biografia/Descrição do médico"
    )
    formacao = models.TextField(
        blank=True,
        null=True,
        help_text="Formação acadêmica do médico"
    )
    convenios = models.ManyToManyField(
        Convenio,
        related_name='medicos',
        blank=True,
        help_text="Convênios aceitos pelo médico"
    )
    atende_particular = models.BooleanField(
        default=True,
        help_text="Se o médico atende particular"
    )
    preco_consulta = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Preço da consulta particular"
    )
    preco_retorno = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Preço do retorno (se diferente da consulta)"
    )
    formas_pagamento = models.CharField(
        max_length=200,
        help_text="Formas de pagamento aceitas (ex: Dinheiro, Cartão, PIX)"
    )
    retorno_info = models.CharField(
        max_length=200, 
        default="Consulta de retorno em até 30 dias incluído no valor.",
        help_text="Informações sobre retorno"
    )
    tempo_consulta = models.IntegerField(
        default=30,
        help_text="Tempo médio de consulta em minutos"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Se o médico está ativo na clínica"
    )
    
    # Informações de contato
    email_profissional = models.EmailField(blank=True, null=True)
    telefone_profissional = models.CharField(max_length=20, blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
    
    def __str__(self):
        return f"Dr(a). {self.nome}"
    
    def get_especialidades_display(self):
        """Retorna as especialidades como string formatada"""
        return ", ".join([esp.nome for esp in self.especialidades.filter(ativa=True)])
    
    def get_convenios_display(self):
        """Retorna os convênios como string formatada"""
        return ", ".join([conv.nome for conv in self.convenios.filter(ativo=True)])


class HorarioTrabalho(models.Model):
    """
    Modelo para definir os blocos de horário de trabalho de cada médico.
    """
    DIA_DA_SEMANA_CHOICES = [
        (1, "Segunda-feira"),
        (2, "Terça-feira"),
        (3, "Quarta-feira"),
        (4, "Quinta-feira"),
        (5, "Sexta-feira"),
        (6, "Sábado"),
        (7, "Domingo"),
    ]
    
    medico = models.ForeignKey(
        Medico, 
        on_delete=models.CASCADE, 
        related_name="horarios_trabalho"
    )
    dia_da_semana = models.IntegerField(choices=DIA_DA_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    ativo = models.BooleanField(
        default=True,
        help_text="Se este horário está ativo"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('medico', 'dia_da_semana', 'hora_inicio')
        ordering = ['dia_da_semana', 'hora_inicio']
        verbose_name = 'Horário de Trabalho'
        verbose_name_plural = 'Horários de Trabalho'
    
    def __str__(self):
        return f"{self.medico.nome} - {self.get_dia_da_semana_display()}: {self.hora_inicio} às {self.hora_fim}"
    
    def clean(self):
        """Validação para garantir que hora_fim seja maior que hora_inicio"""
        from django.core.exceptions import ValidationError
        if self.hora_fim <= self.hora_inicio:
            raise ValidationError('A hora de fim deve ser posterior à hora de início.')


class IndisponibilidadeMedico(models.Model):
    """
    Modelo para registrar períodos de indisponibilidade dos médicos (férias, congressos, etc).
    """
    TIPO_CHOICES = [
        ('ferias', 'Férias'),
        ('congresso', 'Congresso'),
        ('licenca', 'Licença'),
        ('outro', 'Outro'),
    ]
    
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name='indisponibilidades'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='outro'
    )
    data_inicio = models.DateField()
    data_fim = models.DateField()
    motivo = models.CharField(max_length=200, blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_inicio']
        verbose_name = 'Indisponibilidade do Médico'
        verbose_name_plural = 'Indisponibilidades dos Médicos'
    
    def __str__(self):
        return f"{self.medico.nome} - {self.get_tipo_display()}: {self.data_inicio} a {self.data_fim}"
    
    def clean(self):
        """Validação para garantir que data_fim seja maior ou igual a data_inicio"""
        from django.core.exceptions import ValidationError
        if self.data_fim < self.data_inicio:
            raise ValidationError('A data de fim deve ser posterior ou igual à data de início.')