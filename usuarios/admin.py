from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Paciente


class PacienteInline(admin.StackedInline):
    model = Paciente
    can_delete = False
    verbose_name_plural = 'Informações do Paciente'


class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff')
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario', 'telefone', 'cpf', 'data_nascimento')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario', 'telefone', 'cpf', 'data_nascimento')}),
    )
    
    def get_inline_instances(self, request, obj=None):
        if obj and obj.tipo_usuario == 'paciente':
            return [PacienteInline(self.model, self.admin_site)]
        return []


class PacienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'convenio', 'telefone_usuario', 'criado_em')
    list_filter = ('convenio', 'criado_em')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'usuario__email', 'usuario__cpf')
    
    def telefone_usuario(self, obj):
        return obj.usuario.telefone
    telefone_usuario.short_description = 'Telefone'


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Paciente, PacienteAdmin)