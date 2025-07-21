from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from ...core.database import get_db
from ...core.security import verify_token
from ...services.auth_service import AuthService
from ...schemas.auth import LoginRequest, Token
from ...schemas.usuario import UsuarioCreate, UsuarioResponse
from ...models.usuario import Usuario

router = APIRouter()
security = HTTPBearer()

@router.post("/registrar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registra um novo usuário no sistema com configurações e categorias padrão
    """
    auth_service = AuthService(db)
    return auth_service.criar_usuario_completo(usuario_data)

@router.post("/login", response_model=Token)
def fazer_login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Realiza o login do usuário
    """
    auth_service = AuthService(db)
    return auth_service.fazer_login(login_data.email, login_data.senha)

# Dependency para obter usuário atual
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency para obter o usuário atual baseado no token JWT
    """
    token = credentials.credentials
    usuario_id = verify_token(token)
    
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService(db)
    usuario = auth_service.obter_usuario_por_id(usuario_id)
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return usuario

@router.get("/me", response_model=UsuarioResponse)
def obter_usuario_atual(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém informações do usuário autenticado
    """
    return current_user

@router.post("/logout")
def fazer_logout():
    """
    Logout do usuário (no frontend, remover o token)
    """
    return {"message": "Logout realizado com sucesso"}

