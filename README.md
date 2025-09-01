# 🎮 BC Games - Sistema de Autenticação

Sistema completo de gerenciamento de keys de autenticação com interface web administrativa e API REST.

## 🚀 Funcionalidades

### 🌐 Interface Web Administrativa
- ✅ Dashboard com estatísticas em tempo real
- ✅ Criação de keys de 8 dígitos únicos
- ✅ Configuração de dias de expiração
- ✅ Busca por key específica
- ✅ Logs completos de todas as keys
- ✅ Pausar/retomar todas as keys
- ✅ Reset de HWID individual
- ✅ Exclusão de keys específicas ou em lote
- ✅ Interface responsiva e moderna

### 🔌 API REST
- ✅ Endpoint de login para clientes
- ✅ Validação de HWID (Hardware ID)
- ✅ Keys de uso único
- ✅ Contagem de dias apenas após primeiro login
- ✅ Sistema de pausar/retomar keys
- ✅ Estatísticas completas
- ✅ CORS habilitado

### 🔐 Sistema de Segurança
- ✅ Keys únicas de 8 dígitos
- ✅ Validação de HWID do computador
- ✅ Expiração automática baseada em dias
- ✅ Logs de auditoria completos
- ✅ Controle de acesso por key

## 📁 Estrutura do Projeto

```
bc-games-auth/
├── src/
│   ├── models/
│   │   ├── user.py          # Modelo de usuário (template)
│   │   └── auth_key.py      # Modelo das keys de autenticação
│   ├── routes/
│   │   ├── user.py          # Rotas de usuário (template)
│   │   └── auth.py          # Rotas de autenticação
│   ├── static/
│   │   └── index.html       # Interface web administrativa
│   ├── database/
│   │   └── app.db           # Banco SQLite
│   └── main.py              # Aplicação principal Flask
├── venv/                    # Ambiente virtual Python
├── requirements.txt         # Dependências Python
├── README.md               # Este arquivo
└── TUTORIAL_DEPLOY.md      # Tutorial de deploy
```

## 🛠️ Instalação Local

### Pré-requisitos
- Python 3.8+
- pip

### Passos
1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/bc-games-auth.git
cd bc-games-auth
```

2. Ative o ambiente virtual:
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python src/main.py
```

5. Acesse: `http://localhost:5000`

## 🌐 Deploy em Produção

Consulte o arquivo [TUTORIAL_DEPLOY.md](TUTORIAL_DEPLOY.md) para instruções completas de deploy no PythonAnywhere.

## 📚 Documentação da API

### Endpoints Principais

#### 🔐 Login de Cliente
```http
POST /api/login
Content-Type: application/json

{
  "key": "12345678",
  "hwid": "HARDWARE_ID_HERE"
}
```

**Resposta de Sucesso:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "expires_at": "2025-10-01T15:30:00"
}
```

#### 🔑 Criar Keys
```http
POST /api/keys
Content-Type: application/json

{
  "quantity": 10,
  "expiration_days": 30
}
```

#### 📋 Listar Keys
```http
GET /api/keys
```

#### 🔍 Buscar Key Específica
```http
GET /api/keys/{key_value}
```

#### 🗑️ Apagar Key
```http
DELETE /api/keys/{key_value}
```

#### ⏸️ Pausar Todas as Keys
```http
POST /api/keys/pause-all
```

#### ▶️ Retomar Todas as Keys
```http
POST /api/keys/resume-all
```

#### 🔄 Reset HWID
```http
POST /api/keys/{key_value}/reset-hwid
```

#### 📊 Estatísticas
```http
GET /api/stats
```

#### 📝 Logs
```http
GET /api/logs
```

## 🎯 Como Usar

### 1. Criar Keys
1. Acesse a interface web
2. No painel "Criar Novas Keys"
3. Defina quantidade e dias de expiração
4. Clique em "Criar Keys"

### 2. Gerenciar Keys
- **Buscar:** Digite a key no campo de busca
- **Pausar:** Use "Pausar Todas" para desativar temporariamente
- **Reset HWID:** Permite que a key seja usada em outro computador
- **Apagar:** Remove keys específicas ou todas

### 3. Monitorar
- Dashboard mostra estatísticas em tempo real
- Lista completa com status de cada key
- Logs detalhados de todas as operações

## 🔧 Configuração

### Alterar Secret Key
No arquivo `src/main.py`:
```python
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
```

### Configurar CORS
Para permitir acesso de outros domínios, o CORS já está habilitado.

### Banco de Dados
O sistema usa SQLite por padrão. Para PostgreSQL ou MySQL, altere a configuração em `main.py`.

## 🐛 Solução de Problemas

### Erro de Banco de Dados
```bash
# Recriar banco
rm src/database/app.db
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

### Erro de Dependências
```bash
pip install --upgrade -r requirements.txt
```

### Erro de CORS
Verifique se `flask-cors` está instalado e configurado em `main.py`.

## 📈 Estatísticas

O sistema fornece:
- Total de keys criadas
- Keys utilizadas vs não utilizadas
- Keys ativas vs pausadas
- Keys expiradas
- Logs completos com timestamps

## 🔒 Segurança

### Recomendações para Produção
1. Altere a SECRET_KEY
2. Use HTTPS
3. Configure firewall
4. Faça backups regulares
5. Monitore logs de acesso
6. Use banco de dados dedicado

### Limitações Atuais
- Criptografia básica (Base64)
- SQLite para desenvolvimento
- Sem rate limiting
- Sem autenticação de admin

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 📞 Suporte

- 📧 Email: suporte@bcgames.com
- 🌐 Website: https://bcgames.com
- 📚 Documentação: Consulte este README e o tutorial de deploy

---

**Desenvolvido com ❤️ para BC Games**

