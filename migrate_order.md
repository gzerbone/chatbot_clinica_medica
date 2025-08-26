# Ordem das Migrações

Devido às dependências entre os apps, execute as migrações na seguinte ordem:

## 1. Primeiro: Apps Base
```bash
python manage.py makemigrations usuarios
python manage.py makemigrations clinica
```

## 2. Segundo: Apps que dependem dos base
```bash
python manage.py makemigrations medicos
python manage.py makemigrations admin_custom
```

## 3. Terceiro: Apps que dependem de múltiplos outros
```bash
python manage.py makemigrations agendamento
```

## 4. Quarto: App chatbot (pode ser feito em paralelo)
```bash
python manage.py makemigrations chatbot
```

## 5. Aplicar todas as migrações
```bash
python manage.py migrate
```

## ⚠️ Importante

- **NÃO** execute `makemigrations` sem especificar o app
- Execute as migrações na ordem correta para evitar erros de dependência
- Se houver problemas, pode ser necessário deletar o banco e recriar

## 🔄 Recriar Banco (se necessário)

Se houver problemas com as migrações:

1. Delete o arquivo `db.sqlite3`
2. Delete todas as pastas `migrations/` (exceto `__init__.py`)
3. Execute as migrações na ordem acima
4. Crie um novo superusuário: `python manage.py createsuperuser`
