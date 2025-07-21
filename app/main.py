import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import engine, create_tables
from app.api.v1 import auth, configuracoes

# Função para inicializar o banco de dados
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando aplicação...")
    print("📊 Criando tabelas do banco de dados...")
    try:
        create_tables()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Encerrando aplicação...")

# Criar instância do FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API de Gerenciamento Financeiro - Módulo de Autenticação",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware para tratamento de erros
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erro interno do servidor",
            "status_code": 500,
            "detail": str(exc) if settings.DEBUG else "Erro interno"
        }
    )

# Incluir routers
app.include_router(
    auth.router, 
    prefix=f"{settings.API_V1_STR}/auth", 
    tags=["🔐 Autenticação"]
)

app.include_router(
    configuracoes.router, 
    prefix=f"{settings.API_V1_STR}/configuracoes", 
    tags=["⚙️ Configurações"]
)

# Rota raiz
@app.get("/", tags=["📋 Informações"])
def read_root():
    """
    Endpoint de informações da API
    """
    return {
        "message": "API de Gerenciamento Financeiro",
        "version": settings.VERSION,
        "status": "🟢 Online",
        "docs": f"{settings.API_V1_STR}/docs",
        "endpoints": {
            "registrar": f"{settings.API_V1_STR}/auth/registrar",
            "login": f"{settings.API_V1_STR}/auth/login",
            "perfil": f"{settings.API_V1_STR}/auth/me",
            "configuracoes": f"{settings.API_V1_STR}/configuracoes"
        }
    }

# Endpoint de health check
@app.get("/health", tags=["📋 Informações"])
def health_check():
    """
    Endpoint para verificar se a API está funcionando
    """
    try:
        # Testar conexão com banco
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "🟢 Healthy",
            "database": "🟢 Connected",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "🔴 Unhealthy",
                "database": "🔴 Disconnected",
                "error": str(e),
                "timestamp": "2024-01-15T10:30:00Z"
            }
        )

# Endpoint para listar todas as rotas disponíveis
@app.get("/routes", tags=["📋 Informações"])
def list_routes():
    """
    Lista todas as rotas disponíveis na API
    """
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    
    return {
        "total_routes": len(routes),
        "routes": routes
    }

# Função principal para executar a aplicação
def start_server():
    """
    Função para iniciar o servidor
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )

if __name__ == "__main__":
    start_server()