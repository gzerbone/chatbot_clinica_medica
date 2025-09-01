# chatbot/models.py

from django.db import models

class Conversa(models.Model):
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('finalizada', 'Finalizada'),
        ('redirecionada', 'Redirecionada para Secretária'),
    ]
    
    paciente = models.ForeignKey('usuarios.Paciente', on_delete=models.CASCADE)
    iniciada_em = models.DateTimeField(auto_now_add=True)
    finalizada_em = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')
    resumo = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Conversa com {self.paciente.telefone_whatsapp} - {self.status}"
    
class Direcionamento(models.Model):
    TIPO_CHOICES = [
        ('agendamento', 'Solicitação de Agendamento'),
        ('duvida_complexa', 'Dúvida Complexa'),
        ('solicitacao_humana', 'Pediu Atendimento Humano'),
        ('informacao_especifica', 'Informação Específica'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('resolvido', 'Resolvido'),
    ]
    
    paciente = models.ForeignKey('usuarios.Paciente', on_delete=models.CASCADE)
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE)
    tipo_solicitacao = models.CharField(max_length=30, choices=TIPO_CHOICES)
    medico_interesse = models.ForeignKey('clinica.Medico', on_delete=models.SET_NULL, blank=True, null=True)
    resumo_conversa = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    atendida_em = models.DateTimeField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Direcionamento: {self.paciente.telefone_whatsapp} - {self.tipo_solicitacao}"