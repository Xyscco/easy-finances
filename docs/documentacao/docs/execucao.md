# 🎯 Como Executar

## 1. Preparar o ambiente

``` bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

```

## 2. Configurar o banco de dados

```bash
Criar banco: financial_db
Usuário: postgres
Senha: senha123
```

## 3. Executar o projeto

```bash
# Método 1: Usando o script
python run.py

# Método 2: Diretamente
python -m app.main

# Método 3: Uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Testar a API

```bash
# Acessar documentação
http://localhost:8000/api/v1/docs

# Testar health check
curl http://localhost:8000/health

# Registrar usuário
curl -X POST "http://localhost:8000/api/v1/auth/registrar" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "primeiro_nome": "Teste",
    "ultimo_nome": "Usuario",
    "senha": "MinhaSenh@123",
    "confirmar_senha": "MinhaSenh@123"
  }'
```

