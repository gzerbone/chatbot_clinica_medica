from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clinica.models import Medico

from .models import Agendamento


def lista_agendamentos(request):
    """Lista de agendamentos"""
    agendamentos = Agendamento.objects.all().order_by('-data_hora_inicio')
    return render(request, 'agendamento/lista_agendamentos.html', {'agendamentos': agendamentos})

def novo_agendamento(request):
    """Criar novo agendamento"""
    if request.method == 'POST':
        # Lógica de criação aqui
        messages.success(request, 'Agendamento criado com sucesso!')
        return redirect('agendamento:lista_agendamentos')
    
    medicos = Medico.objects.filter(ativo=True)
    return render(request, 'agendamento/novo_agendamento.html', {'medicos': medicos})

def detalhe_agendamento(request, pk):
    """Detalhes de um agendamento específico"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    return render(request, 'agendamento/detalhe_agendamento.html', {'agendamento': agendamento})

def editar_agendamento(request, pk):
    """Editar um agendamento"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        # Lógica de edição aqui
        messages.success(request, 'Agendamento atualizado com sucesso!')
        return redirect('agendamento:detalhe_agendamento', pk=pk)
    
    medicos = Medico.objects.filter(ativo=True)
    return render(request, 'agendamento/editar_agendamento.html', {
        'agendamento': agendamento,
        'medicos': medicos
    })

def cancelar_agendamento(request, pk):
    """Cancelar um agendamento"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        # Lógica de cancelamento aqui
        messages.success(request, 'Agendamento cancelado com sucesso!')
        return redirect('agendamento:lista_agendamentos')
    
    return render(request, 'agendamento/cancelar_agendamento.html', {'agendamento': agendamento})

def confirmar_agendamento(request, pk):
    """Confirmar um agendamento"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        # Lógica de confirmação aqui
        messages.success(request, 'Agendamento confirmado com sucesso!')
        return redirect('agendamento:detalhe_agendamento', pk=pk)
    
    return render(request, 'agendamento/confirmar_agendamento.html', {'agendamento': agendamento})

def consulta_disponibilidade(request):
    """Consultar disponibilidade geral"""
    medicos = Medico.objects.filter(ativo=True)
    return render(request, 'agendamento/consulta_disponibilidade.html', {'medicos': medicos})

def disponibilidade_medico(request, medico_id):
    """Disponibilidade de um médico específico"""
    medico = get_object_or_404(Medico, pk=medico_id)
    return render(request, 'agendamento/disponibilidade_medico.html', {'medico': medico})

def historico_agendamentos(request):
    """Histórico geral de agendamentos"""
    agendamentos = Agendamento.objects.all().order_by('-data_hora_inicio')
    return render(request, 'agendamento/historico_agendamentos.html', {'agendamentos': agendamentos})

def historico_paciente(request, paciente_id):
    """Histórico de agendamentos de um paciente específico"""
    # Aqui você pode implementar a lógica para buscar agendamentos por paciente
    agendamentos = Agendamento.objects.all().order_by('-data_hora_inicio')
    return render(request, 'agendamento/historico_paciente.html', {'agendamentos': agendamentos})
