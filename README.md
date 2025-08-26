# Chatbot Clínica Médica - Projeto Modularizado

Este projeto Django foi modularizado em 6 apps especializados para melhor organização e manutenibilidade.

## 🏗️ Estrutura do Projeto

### Apps Principais

#### 1. **usuarios** - Gestão de Usuários e Pacientes
- **Modelo de Usuário Customizado**: Estende o AbstractUser do Django
- **Perfil de Paciente**: Informações específicas de pacientes
- **Tipos de Usuário**: Paciente, Médico, Secretária, Administrador

#### 2. **clinica** - Informações da Clínica
- **ClinicaInfo**: Configurações globais da clínica (singleton)
- **Especialidades**: Especialidades médicas oferecidas
- **Exames**: Exames disponíveis com descrições detalhadas
- **Convênios**: Convênios aceitos pela clínica

#### 3. **medicos** - Gestão de Médicos
- **Medico**: Perfil completo dos médicos
- **HorarioTrabalho**: Horários de trabalho de cada médico
- **IndisponibilidadeMedico**: Períodos de indisponibilidade (férias, congressos)

#### 4. **agendamento** - Sistema de Agendamento
- **Agendamento**: Consultas agendadas
- **HistoricoAgendamento**: Histórico de mudanças nos agendamentos
- **BloqueioAgenda**: Bloqueios na agenda (feriados, manutenção)

#### 5. **chatbot** - Sistema de Chatbot
- **ConversaWhatsApp**: Conversas do WhatsApp
- **MensagemWhatsApp**: Mensagens individuais
- **IntencaoUsuario**: Intenções identificadas nas mensagens
- **RespostaAutomatica**: Respostas automáticas padrão
- **LogChatbot**: Logs de atividades do chatbot

#### 6. **admin_custom** - Administração Personalizada
- **LogAcesso**: Logs de acesso ao sistema
- **ConfiguracaoSistema**: Configurações globais do sistema
- **NotificacaoAdmin**: Notificações internas
- **RelatorioPersonalizado**: Relatórios customizados

## 🔧 Configurações

### Modelo de Usuário Customizado
```python
AUTH_USER_MODEL = 'usuarios.Usuario'
```

### Apps Instalados
```python
INSTALLED_APPS = [
    # Django padrão
    'django.contrib.admin',
    'django.contrib.auth',
    # ... outros apps Django
    
    # Apps de terceiros
    'rest_framework',
    
    # Apps do projeto
    'usuarios.apps.UsuariosConfig',
    'clinica.apps.ClinicaConfig',
    'medicos.apps.MedicosConfig',
    'agendamento.apps.AgendamentoConfig',
    'chatbot.apps.ChatbotConfig',
    'admin_custom.apps.AdminCustomConfig',
]
```

## 📁 Estrutura de URLs

```
/usuarios/          # Gestão de usuários
/clinica/           # Informações da clínica
/medicos/           # Gestão de médicos
/agendamento/       # Sistema de agendamento
/chatbot/           # Sistema de chatbot
/admin-custom/      # Administração personalizada
```

## 🚀 Como Usar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 4. Executar o Projeto
```bash
python manage.py runserver
```

## 🔄 Dependências entre Apps

- **usuarios**: Base para todos os outros apps
- **clinica**: Fornece especialidades e convênios
- **medicos**: Depende de usuarios e clinica
- **agendamento**: Depende de usuarios, clinica e medicos
- **chatbot**: Depende de usuarios
- **admin_custom**: Depende de usuarios

## 📝 Notas Importantes

1. **Migrações**: Execute as migrações na ordem correta devido às dependências
2. **Usuário Customizado**: O modelo de usuário foi alterado, pode ser necessário recriar o banco
3. **Admin**: Cada app tem seu próprio arquivo admin.py configurado
4. **URLs**: Cada app tem seu próprio arquivo urls.py

## 🛠️ Desenvolvimento

Para adicionar novos modelos ou funcionalidades:
1. Identifique o app apropriado
2. Adicione o modelo no models.py do app
3. Configure o admin.py se necessário
4. Crie as migrações
5. Atualize as URLs se necessário

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação do Django ou entre em contato com a equipe de desenvolvimento.
