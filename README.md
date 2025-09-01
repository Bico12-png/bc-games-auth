# BC Games Auth - Sistema de Autenticação

Sistema completo de autenticação com API Flask para gerenciamento de chaves e aplicação C# para login de clientes.

## 🚀 Funcionalidades

### API Flask
- ✅ Criação de chaves únicas de 8 dígitos
- ✅ Sistema de expiração baseado em dias
- ✅ Detecção e registro de HWID (Hardware ID)
- ✅ Chaves de uso único (vinculadas ao primeiro login)
- ✅ Pausar/despausar chaves individuais ou em lote
- ✅ Resetar HWID de chaves específicas
- ✅ Busca por chave específica
- ✅ Logs completos de todas as ações
- ✅ Estatísticas em tempo real
- ✅ Interface web de administração moderna

### Cliente C#
- ✅ Login com chave de 8 dígitos
- ✅ Geração automática de HWID
- ✅ Salvamento automático da chave
- ✅ Interface moderna e responsiva
- ✅ Tratamento de erros robusto
- ✅ Compatível com .NET 7.0

## 📋 Estrutura do Projeto

```
bc-games-auth/
├── src/
│   ├── models/
│   │   ├── user.py          # Modelo de usuário (template)
│   │   └── key.py           # Modelo de chaves e logs
│   ├── routes/
│   │   ├── user.py          # Rotas de usuário (template)
│   │   └── auth.py          # Rotas de autenticação
│   ├── static/
│   │   ├── index.html       # Interface de administração
│   │   ├── styles.css       # Estilos CSS
│   │   └── script.js        # JavaScript da interface
│   ├── database/
│   │   └── app.db           # Banco SQLite (criado automaticamente)
│   └── main.py              # Aplicação principal Flask
├── venv/                    # Ambiente virtual Python
├── requirements.txt         # Dependências Python
├── README.md               # Este arquivo
└── DEPLOY_TUTORIAL.md      # Tutorial de deploy
```

## 🛠️ Instalação Local

### Pré-requisitos
- Python 3.11+
- Git

### Passos
1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/bc-games-auth.git
cd bc-games-auth
```

2. **Criar ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Executar aplicação**
```bash
python src/main.py
```

5. **Acessar interface**
- Abra: http://localhost:5001
- API: http://localhost:5001/api

## 🌐 Deploy no PythonAnywhere

Consulte o arquivo [DEPLOY_TUTORIAL.md](DEPLOY_TUTORIAL.md) para instruções completas de deploy.

## 📚 API Endpoints

### Autenticação
- `POST /api/login` - Login do cliente

### Gerenciamento de Chaves
- `POST /api/keys` - Criar novas chaves
- `GET /api/keys` - Listar todas as chaves
- `GET /api/keys/{key}` - Buscar chave específica
- `DELETE /api/keys/{key}` - Deletar chave específica
- `DELETE /api/keys` - Deletar todas as chaves

### Ações de Chaves
- `POST /api/keys/{key}/pause` - Pausar chave
- `POST /api/keys/{key}/unpause` - Despausar chave
- `POST /api/keys/{key}/reset-hwid` - Resetar HWID
- `POST /api/keys/pause-all` - Pausar todas as chaves
- `POST /api/keys/unpause-all` - Despausar todas as chaves

### Logs e Estatísticas
- `GET /api/logs` - Obter logs do sistema
- `GET /api/stats` - Obter estatísticas

## 🔧 Configuração

### Variáveis de Ambiente
```python
# src/main.py
app.config['SECRET_KEY'] = 'sua-chave-secreta'
```

### URL da API (Cliente C#)
```csharp
// Form1.cs
private const string API_BASE_URL = "https://seu-usuario.pythonanywhere.com/api";
```

## 📊 Banco de Dados

O sistema usa SQLite com as seguintes tabelas:

### Keys
- `id` - ID único
- `key_value` - Chave de 8 dígitos
- `hwid` - Hardware ID do cliente
- `expiration_days` - Dias para expiração
- `created_at` - Data de criação
- `first_login_at` - Data do primeiro login
- `expires_at` - Data de expiração
- `is_used` - Se a chave foi usada
- `is_paused` - Se a chave está pausada
- `last_login_at` - Último login
- `login_count` - Número de logins

### KeyLogs
- `id` - ID único
- `key_id` - Referência à chave
- `action` - Ação realizada
- `details` - Detalhes da ação
- `timestamp` - Data/hora
- `ip_address` - IP do cliente

## 🎨 Interface Web

A interface de administração inclui:

### Dashboard
- Estatísticas em tempo real
- Criação de novas chaves
- Busca por chave específica
- Ações em lote

### Gerenciar Chaves
- Lista paginada de todas as chaves
- Filtros e busca
- Ações individuais por chave
- Detalhes completos de cada chave

### Logs
- Histórico completo de ações
- Paginação e filtros
- Informações de IP e timestamp

## 🔒 Segurança

### Chaves
- Geração aleatória de 8 dígitos
- Verificação de unicidade
- Vinculação por HWID
- Uso único por chave

### HWID
- Baseado em hardware real
- Fallback para identificadores do sistema
- Hash para privacidade

### API
- CORS configurado
- Validação de entrada
- Tratamento de erros
- Logs de auditoria

## 🧪 Testes

### Testar API
```bash
# Criar chave
curl -X POST http://localhost:5001/api/keys \
  -H "Content-Type: application/json" \
  -d '{"quantity": 1, "expiration_days": 30}'

# Login
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"key": "12345678", "hwid": "ABC123"}'
```

### Testar Interface
1. Acesse http://localhost:5001
2. Crie algumas chaves
3. Teste busca e ações
4. Verifique logs

## 📱 Cliente C#

### Compilação
```bash
# Via .NET CLI
dotnet build --configuration Release

# Via Visual Studio
Build → Build Solution
```

### Configuração
- Altere `API_BASE_URL` para sua URL de produção
- Configure timeout se necessário
- Personalize interface conforme necessário

## 🐛 Troubleshooting

### Erro de Conexão
- Verifique se a API está rodando
- Confirme a URL da API
- Teste conectividade de rede

### Erro de HWID
- Execute como administrador
- Verifique WMI no Windows
- Teste fallback de identificação

### Erro de Banco
- Verifique permissões do diretório
- Confirme se SQLite está disponível
- Recrie o banco se necessário

## 📄 Licença

Este projeto é propriedade da BC Games. Todos os direitos reservados.

## 🤝 Contribuição

Para contribuir:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para suporte técnico:
- Consulte a documentação
- Verifique os logs de erro
- Teste localmente primeiro
- Abra uma issue no GitHub

---

**Desenvolvido com ❤️ para BC Games**

