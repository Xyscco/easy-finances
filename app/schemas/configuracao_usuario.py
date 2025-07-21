from pydantic import BaseModel, ConfigDict, validator
from typing import Optional
import uuid

class ConfiguracaoUsuarioBase(BaseModel):
    moeda: str = 'BRL'
    formato_data: str = 'DD/MM/YYYY'
    tema: str = 'auto'
    notificacoes_email: bool = True
    notificacoes_push: bool = True
    dia_fechamento_mes: int = 1

class ConfiguracaoUsuarioCreate(ConfiguracaoUsuarioBase):
    pass

class ConfiguracaoUsuarioUpdate(BaseModel):
    moeda: Optional[str] = None
    formato_data: Optional[str] = None
    tema: Optional[str] = None
    notificacoes_email: Optional[bool] = None
    notificacoes_push: Optional[bool] = None
    dia_fechamento_mes: Optional[int] = None
    
    @validator('tema')
    def validar_tema(cls, v):
        if v and v not in ['claro', 'escuro', 'auto']:
            raise ValueError('Tema deve ser: claro, escuro ou auto')
        return v
    
    @validator('dia_fechamento_mes')
    def validar_dia_fechamento(cls, v):
        if v and (v < 1 or v > 31):
            raise ValueError('Dia de fechamento deve estar entre 1 e 31')
        return v

class ConfiguracaoUsuarioResponse(ConfiguracaoUsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    usuario_id: uuid.UUID