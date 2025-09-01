from decimal import Decimal

from django.db import models


# Modelo para armazenar informações globais da clínica (só haverá 1 registro)
class ClinicaInfo(models.Model):
    nome = models.CharField(max_length=100, default="Clínica PneumoSono")
    objetivo_geral = models.TextField()
    secretaria_nome = models.CharField(max_length=100, default="Raro")
    telefone_contato = models.CharField(max_length=20)
    numero_whatsapp = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.TextField()
    referencia_localizacao = models.CharField(max_length=200)
    politica_agendamento = models.TextField(help_text="Texto sobre a política de horários pré-agendados e possíveis demoras.")

    # NOVO CAMPO AQUI: O ID da agenda principal da clínica
    google_calendar_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="O ID do Google Calendar PRINCIPAL da clínica."
    )

    def __str__(self):
        return self.nome

# Modelo para as especialidades médicas
class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True, help_text="Descrição da especialidade")
    ativa = models.BooleanField(default=True, help_text="Se a especialidade está ativa para seleção")
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'
    
    def __str__(self):
        return self.nome


class Medico(models.Model):
    nome = models.CharField(max_length=100)
    especialidades = models.ManyToManyField(
        Especialidade, 
        related_name='medicos',
        help_text="Selecione uma ou mais especialidades do médico"
    )
    bio = models.TextField()
    convenios = models.CharField(max_length=200, help_text="Ex: Atende apenas CASSI")
    preco_particular = models.DecimalField(max_digits=8, decimal_places=2)
    formas_pagamento = models.CharField(max_length=200)
    retorno_info = models.CharField(max_length=100, default="Consulta de retorno em até 30 dias incluído no valor.")

    def __str__(self):
        return self.nome
    
    def get_especialidades_display(self):
        """Retorna as especialidades como string formatada"""
        return ", ".join([esp.nome for esp in self.especialidades.filter(ativa=True)])

class Exame(models.Model):
    nome = models.CharField(max_length=100)
    o_que_e = models.TextField()
    como_funciona = models.TextField()
    preparacao = models.TextField(blank=True, null=True)
    vantagem = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nome

# NOVO MODELO: Para definir os blocos de horário de trabalho de cada médico.
class HorarioTrabalho(models.Model):
    DIA_DA_SEMANA_CHOICES = [
        (1, "Segunda-feira"),
        (2, "Terça-feira"),
        (3, "Quarta-feira"),
        (4, "Quinta-feira"),
        (5, "Sexta-feira"),
        (6, "Sábado"),
        (7, "Domingo"),
    ]

    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="horarios_trabalho")
    dia_da_semana = models.IntegerField(choices=DIA_DA_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        unique_together = ('medico', 'dia_da_semana', 'hora_inicio') # Garante que não haja horários duplicados

    def __str__(self):
        return f"{self.medico.nome} - {self.get_dia_da_semana_display()}: {self.hora_inicio} às {self.hora_fim}"
