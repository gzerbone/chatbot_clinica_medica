from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Paciente, Usuario


# Views para gestão de usuários
def lista_usuarios(request):
    """Lista todos os usuários (apenas para administradores)"""
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

def cadastro_usuario(request):
    """Cadastro de novo usuário"""
    if request.method == 'POST':
        # Lógica de cadastro aqui
        messages.success(request, 'Usuário cadastrado com sucesso!')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/cadastro_usuario.html')

def login_usuario(request):
    """Login de usuário"""
    if request.method == 'POST':
        # Lógica de login aqui
        messages.success(request, 'Login realizado com sucesso!')
        return redirect('usuarios:perfil_usuario')
    return render(request, 'usuarios/login_usuario.html')

def logout_usuario(request):
    """Logout de usuário"""
    # Lógica de logout aqui
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('usuarios:login_usuario')

@login_required
def perfil_usuario(request):
    """Perfil do usuário logado"""
    return render(request, 'usuarios/perfil_usuario.html')

@login_required
def editar_perfil(request):
    """Editar perfil do usuário logado"""
    if request.method == 'POST':
        # Lógica de edição aqui
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('usuarios:perfil_usuario')
    return render(request, 'usuarios/editar_perfil.html')

# Views para gestão de pacientes
def lista_pacientes(request):
    """Lista todos os pacientes"""
    pacientes = Paciente.objects.all()
    return render(request, 'usuarios/lista_pacientes.html', {'pacientes': pacientes})

def cadastro_paciente(request):
    """Cadastro de novo paciente"""
    if request.method == 'POST':
        # Lógica de cadastro aqui
        messages.success(request, 'Paciente cadastrado com sucesso!')
        return redirect('usuarios:lista_pacientes')
    return render(request, 'usuarios/cadastro_paciente.html')

def detalhe_paciente(request, pk):
    """Detalhes de um paciente específico"""
    paciente = get_object_or_404(Paciente, pk=pk)
    return render(request, 'usuarios/detalhe_paciente.html', {'paciente': paciente})

def editar_paciente(request, pk):
    """Editar dados de um paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        # Lógica de edição aqui
        messages.success(request, 'Paciente atualizado com sucesso!')
        return redirect('usuarios:detalhe_paciente', pk=pk)
    return render(request, 'usuarios/editar_paciente.html', {'paciente': paciente})
