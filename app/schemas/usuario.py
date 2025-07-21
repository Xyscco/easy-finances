from pydantic import BaseModel, EmailStr, ConfigDict, validator
from typing import Optional
from datetime import datetime
import uuid

class UsuarioBase(BaseModel):
    email: EmailStr
    primeiro_nome: str
    ultimo_nome: str
    telefone: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    senha: str
    confirmar_senha: str
    
    @validator('confirmar_senha')
    def senhas_devem_coincidir(cls, v, values, **kwargs):
        if 'senha' in values and v != values['senha']:
            raise ValueError('As senhas não coincidem')
        return v
    
    @validator('senha')
    def validar_senha(cls, v):
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('A senha deve conter pelo menos um número')
        if not any(char.isupper() for char in v):
            raise ValueError('A senha deve conter pelo menos uma letra maiúscula')
        return v

class UsuarioUpdate(BaseModel):
    primeiro_nome: Optional[str] = None
    ultimo_nome: Optional[str] = None
    telefone: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    
    @property
    def nome_completo(self):
        return f"{self.primeiro_nome} {self.ultimo_nome}"

class UsuarioComConfiguracoes(UsuarioResponse):
    configuracao: Optional['ConfiguracaoUsuarioResponse'] = None

# Evitar import circular
from .configuracao_usuario import ConfiguracaoUsuarioResponse
UsuarioComConfiguracoes.model_rebuild()