# BC Games - Sistema de Autenticação

Sistema completo de autenticação com API Flask e cliente C# para gerenciamento de keys de acesso.

## 🚀 Características Principais

### Sistema Web (Flask)
- **API REST Completa**: Endpoints para autenticação e administração
- **Interface Administrativa**: Dashboard moderno para gerenciar keys
- **Banco de Dados SQLite**: Armazenamento local eficiente
- **Sistema de Logs**: Rastreamento completo de acessos
- **Design Responsivo**: Interface bonita e funcional

### Cliente C# (.NET 7.0)
- **Autenticação Segura**: Login com keys de 8 dígitos
- **HWID Protection**: Identificação única por máquina
- **Auto-Save**: Salva key após primeiro login
- **Interface Moderna**: Design limpo e profissional

## 📋 Funcionalidades do Sistema

### 🔑 Gerenciamento de Keys
- ✅ Criar keys únicas de 8 dígitos
- ✅ Definir dias de expiração personalizados
- ✅ Controle de quantidade (1-100 keys por vez)
- ✅ Keys de uso único (vinculadas ao HWID)
- ✅ Contagem de expiração após primeiro login

### ⚙️ Administração
- ✅ Buscar key específica
- ✅ Apagar key específica
- ✅ Apagar todas as keys
- ✅ Pausar/despausar todas as keys
- ✅ Resetar HWID de key específica
- ✅ Visualizar estatísticas em tempo real

### 📊 Logs e Monitoramento
- ✅ Log de todas as tentativas de login
- ✅ Rastreamento de IP e User-Agent
- ✅ Histórico de uso por key
- ✅ Estatísticas detalhadas do sistema
- ✅ Taxa de sucesso de autenticações

### 🔒 Segurança
- ✅ Validação rigorosa de entrada
- ✅ HWID único por máquina
- ✅ Keys nunca repetidas
- ✅ Controle de expiração automático
- ✅ Logs de segurança completos

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 3.1.2**: Framework web Python
- **SQLAlchemy 2.0.43**: ORM para banco de dados
- **Flask-CORS**: Suporte a requisições cross-origin
- **SQLite**: Banco de dados local

### Frontend
- **HTML5/CSS3**: Interface moderna
- **JavaScript ES6+**: Funcionalidades interativas
- **Design Responsivo**: Compatível com mobile

### Cliente C#
- **.NET 7.0**: Framework moderno
- **Windows Forms**: Interface nativa
- **Newtonsoft.Json**: Serialização JSON
- **System.Management**: Obtenção de HWID

## 📁 Estrutura do Projeto

```
bc_games_auth_site/
├── src/
│   ├── models/
│   │   └── key.py              # Modelos de dados
│   ├── routes/
│   │   ├── auth.py             # Rotas de autenticação
│   │   └── admin.py            # Rotas administrativas
│   ├── static/
│   │   ├── index.html          # Interface web
│   │   └── favicon.ico         # Ícone do site
│   ├── database/
│   │   └── app.db              # Banco SQLite (criado automaticamente)
│   └── main.py                 # Aplicação principal
├── requirements.txt            # Dependências Python
└── README.md                   # Esta documentação
```

## 🌐 API Endpoints

### Autenticação (Cliente)
- `POST /api/login` - Login do cliente
- `POST /api/validate` - Validar key sem login

### Administração
- `POST /api/admin/keys` - Criar novas keys
- `GET /api/admin/keys` - Listar keys (com paginação)
- `GET /api/admin/keys/{key_id}` - Buscar key específica
- `DELETE /api/admin/keys/{key_id}` - Apagar key específica
- `DELETE /api/admin/keys/delete-all` - Apagar todas as keys
- `POST /api/admin/keys/{key_id}/reset-hwid` - Resetar HWID
- `POST /api/admin/keys/pause-all` - Pausar/despausar todas
- `GET /api/admin/logs` - Obter logs de acesso
- `GET /api/admin/stats` - Estatísticas do sistema

## 🚀 Como Usar Localmente

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o Servidor
```bash
python src/main.py
```

### 3. Acessar o Sistema
- **Interface Web**: http://localhost:5000
- **API**: http://localhost:5000/api

## 📱 Interface Web

### Dashboard
- Estatísticas em tempo real
- Cards informativos coloridos
- Gráficos de uso e performance

### Criar Keys
- Formulário intuitivo
- Validação em tempo real
- Exibição das keys criadas

### Gerenciar Keys
- Tabela paginada
- Filtros por status
- Busca por key específica
- Ações individuais (Reset HWID, Apagar)
- Ações em massa (Pausar/Despausar/Apagar todas)

### Logs
- Histórico completo de acessos
- Filtros por key e status
- Informações detalhadas (IP, User-Agent, etc.)

## 🔧 Configuração do Cliente C#

1. Altere a URL da API no arquivo `Form1.cs`:
```csharp
private const string API_URL = "https://seuusuario.pythonanywhere.com/api";
```

2. Compile o projeto:
```bash
dotnet build
dotnet run
```

## 📊 Exemplo de Uso

### 1. Criar Keys
```javascript
// POST /api/admin/keys
{
    "quantity": 5,
    "expiration_days": 30
}
```

### 2. Login do Cliente
```javascript
// POST /api/login
{
    "key_id": "12345678",
    "hwid": "1234567890"
}
```

### 3. Resposta de Sucesso
```javascript
{
    "success": true,
    "message": "Login realizado com sucesso",
    "key_info": {
        "key_id": "12345678",
        "expires_at": "2024-10-01T19:56:36",
        "expiration_days": 30,
        "first_login": "2024-09-01T19:56:36"
    }
}
```

## 🛡️ Segurança e Boas Práticas

### Validações Implementadas
- Keys sempre com 8 dígitos numéricos
- HWID único por máquina
- Controle de expiração automático
- Logs de todas as tentativas

### Recomendações
- Use HTTPS em produção
- Configure firewall adequadamente
- Monitore logs regularmente
- Faça backup do banco de dados

## 🐛 Solução de Problemas

### Erro de Conexão
- Verifique se o servidor está rodando
- Confirme a URL da API no cliente C#
- Teste a conectividade de rede

### Key Não Encontrada
- Verifique se a key foi criada corretamente
- Confirme que tem exatamente 8 dígitos
- Verifique se não foi apagada

### HWID Não Corresponde
- Use a função "Reset HWID" no painel admin
- Verifique se o cliente está na máquina correta

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique esta documentação
2. Consulte os logs do sistema
3. Teste localmente primeiro
4. Verifique a configuração da API

---

**Desenvolvido com ❤️ para BC Games**

