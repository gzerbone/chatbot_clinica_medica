from django.urls import path

from . import views

app_name = 'agendamento'

urlpatterns = [
    # URLs para agendamentos
    path('', views.lista_agendamentos, name='lista_agendamentos'),
    path('novo/', views.novo_agendamento, name='novo_agendamento'),
    path('<int:pk>/', views.detalhe_agendamento, name='detalhe_agendamento'),
    path('<int:pk>/editar/', views.editar_agendamento, name='editar_agendamento'),
    path('<int:pk>/cancelar/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('<int:pk>/confirmar/', views.confirmar_agendamento, name='confirmar_agendamento'),
    
    # URLs para consulta de disponibilidade
    path('disponibilidade/', views.consulta_disponibilidade, name='consulta_disponibilidade'),
    path('disponibilidade/medico/<int:medico_id>/', views.disponibilidade_medico, name='disponibilidade_medico'),
    
    # URLs para histórico
    path('historico/', views.historico_agendamentos, name='historico_agendamentos'),
    path('historico/paciente/<int:paciente_id>/', views.historico_paciente, name='historico_paciente'),
]
