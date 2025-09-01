from django.db import models

# usuarios/models.py
class Paciente(models.Model):
    nome_completo = models.CharField(max_length=255, blank=True, null=True)
    telefone_whatsapp = models.CharField(max_length=20, unique=True)
    primeiro_contato = models.DateTimeField(auto_now_add=True)
    ultimo_contato = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        nome = self.nome_completo or "Não informado"
        return f"{nome} ({self.telefone_whatsapp})"