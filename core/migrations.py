# Configuração para migrações
# Este arquivo ajuda a resolver dependências entre os apps

MIGRATION_DEPENDENCIES = {
    'usuarios': [],
    'clinica': [],
    'medicos': ['usuarios', 'clinica'],
    'agendamento': ['usuarios', 'clinica', 'medicos'],
    'chatbot': ['usuarios'],
    'admin_custom': ['usuarios'],
}
