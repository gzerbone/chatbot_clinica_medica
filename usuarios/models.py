from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo customizado de usuário que estende o AbstractUser do Django.
    Pode ser usado para adicionar campos específicos para diferentes tipos de usuários.
    """
    TIPO_USUARIO_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('secretaria', 'Secretária'),
        ('admin', 'Administrador'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='paciente'
    )
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_tipo_usuario_display()})"


class Paciente(models.Model):
    """
    Modelo para armazenar informações específicas de pacientes.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_paciente'
    )
    endereco = models.TextField(blank=True, null=True)
    convenio = models.CharField(max_length=100, blank=True, null=True)
    historico_medico = models.TextField(blank=True, null=True)
    alergias = models.TextField(blank=True, null=True)
    medicamentos_uso_continuo = models.TextField(blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
    
    def __str__(self):
        return f"Paciente: {self.usuario.get_full_name() or self.usuario.username}"