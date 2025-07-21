from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.configuracao_usuario import ConfiguracaoUsuario
from ...schemas.configuracao_usuario import ConfiguracaoUsuarioResponse, ConfiguracaoUsuarioUpdate
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=ConfiguracaoUsuarioResponse)
def obter_configuracoes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém as configurações do usuário
    """
    configuracao = db.query(ConfiguracaoUsuario).filter(
        ConfiguracaoUsuario.usuario_id == current_user.id
    ).first()
    
    if not configuracao:
        raise HTTPException(status_code=404, detail="Configurações não encontradas")
    
    return configuracao

@router.put("/", response_model=ConfiguracaoUsuarioResponse)
def atualizar_configuracoes(
    configuracao_update: ConfiguracaoUsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Atualiza as configurações do usuário
    """
    configuracao = db.query(ConfiguracaoUsuario).filter(
        ConfiguracaoUsuario.usuario_id == current_user.id
    ).first()
    
    if not configuracao:
        raise HTTPException(status_code=404, detail="Configurações não encontradas")
    
    update_data = configuracao_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(configuracao, field, value)
    
    db.commit()
    db.refresh(configuracao)
    return configuracao