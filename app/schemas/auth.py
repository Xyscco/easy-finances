from pydantic import BaseModel
from typing import Optional
from .usuario import UsuarioResponse

class LoginRequest(BaseModel):
    email: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    usuario: UsuarioResponse

class TokenData(BaseModel):
    usuario_id: Optional[str] = None