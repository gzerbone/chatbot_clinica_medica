from django.db import models


# usuarios/models.py
class Paciente(models.Model):
    nome_completo = models.CharField(max_length=255, blank=True, null=True)
    telefone_whatsapp = models.CharField(max_length=20, unique=True)
    primeiro_contato = models.DateTimeField(auto_now_add=True)
    ultimo_contato = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    
    def has_active_conversation(self):
        """Verifica se tem conversa ativa"""
        return self.conversas.filter(status='ativa').exists()
    
    def has_pending_direcionamento(self):
        """Verifica se tem direcionamento pendente"""
        return self.direcionamentos.filter(
            status__in=['pendente', 'em_andamento']
        ).exists()
    
    def get_active_conversation(self):
        """Retorna conversa ativa ou None"""
        return self.conversas.filter(status='ativa').first()
    
    def __str__(self):
        nome = self.nome_completo or "Não informado"
        return f"{nome} ({self.telefone_whatsapp})"