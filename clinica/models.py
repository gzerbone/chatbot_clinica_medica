from django.core.exceptions import ValidationError
from django.db import models


class ClinicaInfo(models.Model):
    """
    Modelo para armazenar informações globais da clínica (singleton - só haverá 1 registro).
    """
    nome = models.CharField(max_length=100, default="Clínica PneumoSono")
    objetivo_geral = models.TextField(
        help_text="Descrição do objetivo geral da clínica"
    )
    secretaria_nome = models.CharField(max_length=100, default="Raro")
    telefone_contato = models.CharField(max_length=20)
    telefone_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    endereco = models.TextField()
    referencia_localizacao = models.CharField(
        max_length=200,
        help_text="Ponto de referência para localização"
    )
    horario_funcionamento = models.TextField(
        blank=True, 
        null=True,
        help_text="Horários de funcionamento da clínica"
    )
    politica_agendamento = models.TextField(
        help_text="Texto sobre a política de horários pré-agendados e possíveis demoras."
    )
    politica_cancelamento = models.TextField(
        blank=True,
        null=True,
        help_text="Política de cancelamento de consultas"
    )
    
    # Integração com Google Calendar
    google_calendar_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="O ID do Google Calendar PRINCIPAL da clínica."
    )
    
    # Redes sociais
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Informações da Clínica'
        verbose_name_plural = 'Informações da Clínica'
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        """Garante que só exista uma instância de ClinicaInfo"""
        if not self.pk and ClinicaInfo.objects.exists():
            # Se estiver tentando criar uma nova instância e já existe uma
            raise ValidationError('Já existe uma configuração de clínica. Edite a existente.')
        super().save(*args, **kwargs)


class Especialidade(models.Model):
    """
    Modelo para as especialidades médicas oferecidas pela clínica.
    """
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(
        blank=True, 
        null=True, 
        help_text="Descrição da especialidade"
    )
    ativa = models.BooleanField(
        default=True, 
        help_text="Se a especialidade está ativa para seleção"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'
    
    def __str__(self):
        return self.nome


class Exame(models.Model):
    """
    Modelo para os exames oferecidos pela clínica.
    """
    nome = models.CharField(max_length=100)
    o_que_e = models.TextField(
        help_text="Explicação sobre o que é o exame"
    )
    como_funciona = models.TextField(
        help_text="Como o exame é realizado"
    )
    preparacao = models.TextField(
        blank=True, 
        null=True,
        help_text="Preparação necessária para o exame"
    )
    vantagem = models.TextField(
        blank=True, 
        null=True,
        help_text="Vantagens e benefícios do exame"
    )
    
    preco = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Preço do exame"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Se o exame está disponível"
    )
    especialidades = models.ManyToManyField(
        Especialidade,
        related_name='exames',
        blank=True,
        help_text="Especialidades relacionadas a este exame"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Exame'
        verbose_name_plural = 'Exames'
    
    def __str__(self):
        return self.nome


class Convenio(models.Model):
    """
    Modelo para os convênios aceitos pela clínica.
    """
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(
        default=True,
        help_text="Se o convênio está ativo"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações sobre o convênio"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Convênio'
        verbose_name_plural = 'Convênios'
    
    def __str__(self):
        return self.nome