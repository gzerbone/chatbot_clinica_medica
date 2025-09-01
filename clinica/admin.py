from django.contrib import admin


from .models import (ClinicaInfo, Especialidade, Exame,
                     HorarioTrabalho, Medico)


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativa']
    list_filter = ['ativa']
    search_fields = ['nome']
    list_editable = ['ativa']


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'get_especialidades_display', 'preco_particular']
    list_filter = ['especialidades']
    search_fields = ['nome']
    filter_horizontal = ['especialidades']  # Interface melhor para ManyToMany


admin.site.register(ClinicaInfo)
admin.site.register(Exame)
admin.site.register(HorarioTrabalho)