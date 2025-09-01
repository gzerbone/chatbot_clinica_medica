from django.db import models


class Paciente(models.Model):
    nome_completo = models.CharField(max_length=255, blank=True, null=True)
    telefone_whatsapp = models.CharField(max_length=20, unique=True)
    primeiro_contato = models.DateTimeField(auto_now_add=True)
    ultimo_contato = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    
    def has_active_conversation(self):
        """Verifica se tem conversa ativa"""
        # Usando string reference para evitar import circular
        from django.apps import apps
        Conversa = apps.get_model('chatbot', 'Conversa')
        return Conversa.objects.filter(paciente=self, status='ativa').exists()
    
    def has_pending_direcionamento(self):
        """Verifica se tem direcionamento pendente"""
        # Usando string reference para evitar import circular
        from django.apps import apps
        Direcionamento = apps.get_model('chatbot', 'Direcionamento')
        return Direcionamento.objects.filter(
            paciente=self,
            status__in=['pendente', 'em_andamento']
        ).exists()
    
    def get_active_conversation(self):
        """Retorna conversa ativa ou None"""
        # Usando string reference para evitar import circular
        from django.apps import apps
        Conversa = apps.get_model('chatbot', 'Conversa')
        return Conversa.objects.filter(paciente=self, status='ativa').first()
    
    def __str__(self):
        nome = self.nome_completo or "Não informado"
        return f"{nome} ({self.telefone_whatsapp})"