### ❌ FUNÇÕES QUE DEVEM SER DELETADAS/MODIFICADAS:
1. Sistema de Cache → Substituir por Banco de Dados
```python
# ❌ DELETAR - baseado em cache
def get_conversation_data(self, user_number: str) -> Dict
def update_conversation_data(self, user_number: str, data: Dict, timeout: int = 120)
def add_message_to_history(self, user_number: str, message: str, role: str = 'user')
def reset_conversation(self, user_number: str)
def get_conversation_summary(self, user_number: str) -> Dict

# ✅ SUBSTITUIR por - baseado em models
def get_or_create_conversation(self, telefone_whatsapp: str)
def save_message(self, conversa, remetente, conteudo)
def create_direcionamento(self, conversa, tipo_solicitacao, medico=None)

```
2. Lógica de Estados → Substituir por Status do Banco

```python

# ❌ MODIFICAR - não usa mais 'state' em cache
def process_user_message(self, user_number: str, message_text: str) -> str
def _process_ai_commands(self, ai_response: str, current_state: str) -> Tuple[str, str]
```


### ✅ FUNÇÕES QUE PODEM SER MANTIDAS:
__init__() - OK, mantém os services
A estrutura geral de process_user_message() - mas com modificações internas


## 📋 RESUMO DAS MUDANÇAS:
### 🗑️ DELETAR completamente:
- `get_conversation_data()`  
- `update_conversation_data()`
- `add_message_to_history()`
- Todo sistema de cache  

### 🔄 MODIFICAR significativamente:
- `process_user_message()` - agora usa banco de dados
- `_process_ai_commands()` - agora cria direcionamentos


### ➕ ADICIONAR:
- `_get_or_create_active_conversation()`
- `_save_message()`
- `_build_chat_history()`
- `_create_direcionamento()`
- `_generate_conversation_summary()`  

### ✅ MANTER (com pequenos ajustes):
- `__init__()`  
- `reset_conversation()` - mas mudando lógica  
- `get_conversation_summary()` - mas mudando lógica    

**Resultado:** Sistema muito mais robusto, persistente e profissional! 🚀