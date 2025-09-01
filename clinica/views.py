from django.shortcuts import get_object_or_404, render

from .models import ClinicaInfo, Especialidade, Exame


def informacoes_clinica(request):
    """Informações gerais da clínica"""
    try:
        clinica = ClinicaInfo.objects.first()
    except ClinicaInfo.DoesNotExist:
        clinica = None
    return render(request, 'clinica/informacoes_clinica.html', {'clinica': clinica})

def sobre_clinica(request):
    """Página sobre a clínica"""
    try:
        clinica = ClinicaInfo.objects.first()
    except ClinicaInfo.DoesNotExist:
        clinica = None
    return render(request, 'clinica/sobre_clinica.html', {'clinica': clinica})

def contato_clinica(request):
    """Informações de contato da clínica"""
    try:
        clinica = ClinicaInfo.objects.first()
    except ClinicaInfo.DoesNotExist:
        clinica = None
    return render(request, 'clinica/contato_clinica.html', {'clinica': clinica})

def localizacao_clinica(request):
    """Localização e endereço da clínica"""
    try:
        clinica = ClinicaInfo.objects.first()
    except ClinicaInfo.DoesNotExist:
        clinica = None
    return render(request, 'clinica/localizacao_clinica.html', {'clinica': clinica})

def lista_especialidades(request):
    """Lista de especialidades médicas"""
    especialidades = Especialidade.objects.filter(ativa=True)
    return render(request, 'clinica/lista_especialidades.html', {'especialidades': especialidades})

def detalhe_especialidade(request, pk):
    """Detalhes de uma especialidade específica"""
    especialidade = get_object_or_404(Especialidade, pk=pk)
    return render(request, 'clinica/detalhe_especialidade.html', {'especialidade': especialidade})

def lista_exames(request):
    """Lista de exames oferecidos"""
    exames = Exame.objects.all()
    return render(request, 'clinica/lista_exames.html', {'exames': exames})

def detalhe_exame(request, pk):
    """Detalhes de um exame específico"""
    exame = get_object_or_404(Exame, pk=pk)
    return render(request, 'clinica/detalhe_exame.html', {'exame': exame})

#Não há models chamado Convenio

#def lista_convenios(request):
#    """Lista de convênios aceitos"""
#   convenios = Convenio.objects.filter(ativo=True)
#    return render(request, 'clinica/lista_convenios.html', {'convenios': convenios})

def detalhe_convenio(request, pk):
    """Detalhes de um convênio específico"""
    convenio = get_object_or_404(Convenio, pk=pk)
    return render(request, 'clinica/detalhe_convenio.html', {'convenio': convenio})
