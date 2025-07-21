from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional
import uuid
from datetime import datetime, timedelta

from app.models.usuario import Usuario
from app.models.configuracao_usuario import ConfiguracaoUsuario
from app.models.categoria import Categoria
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.schemas.auth import Token

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def criar_usuario_completo(self, usuario_data: UsuarioCreate) -> UsuarioResponse:
        """
        Cria um usuário completo com configurações padrão e categorias iniciais
        """
        try:
            # Verificar se email já existe
            if self.db.query(Usuario).filter(Usuario.email == usuario_data.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado no sistema"
                )
            
            # Criar o usuário
            senha_hash = get_password_hash(usuario_data.senha)
            
            novo_usuario = Usuario(
                email=usuario_data.email,
                senha_hash=senha_hash,
                primeiro_nome=usuario_data.primeiro_nome,
                ultimo_nome=usuario_data.ultimo_nome,
                telefone=usuario_data.telefone
            )
            
            self.db.add(novo_usuario)
            self.db.flush()  # Para obter o ID sem fazer commit
            
            # Criar configurações padrão
            self._criar_configuracoes_padrao(novo_usuario.id)
            
            # Criar categorias padrão
            self._criar_categorias_padrao(novo_usuario.id)
            
            # Commit final
            self.db.commit()
            self.db.refresh(novo_usuario)
            
            return UsuarioResponse.from_orm(novo_usuario)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao criar usuário. Email pode já estar em uso."
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}"
            )
    
    def _criar_configuracoes_padrao(self, usuario_id: uuid.UUID):
        """Cria configurações padrão para o usuário"""
        configuracao = ConfiguracaoUsuario(
            usuario_id=usuario_id,
            moeda='BRL',
            formato_data='DD/MM/YYYY',
            tema='auto',
            notificacoes_email=True,
            notificacoes_push=True,
            dia_fechamento_mes=1
        )
        self.db.add(configuracao)
    
    def _criar_categorias_padrao(self, usuario_id: uuid.UUID):
        """Cria categorias padrão para o usuário"""
        categorias_padrao = [
            # Categorias de Despesa
            {
                'nome': 'Alimentação',
                'descricao': 'Gastos com comida e bebida',
                'tipo': 'despesa',
                'cor': '#FF6B6B',
                'icone': 'restaurant'
            },
            {
                'nome': 'Transporte',
                'descricao': 'Gastos com locomoção',
                'tipo': 'despesa',
                'cor': '#4ECDC4',
                'icone': 'directions_car'
            },
            {
                'nome': 'Moradia',
                'descricao': 'Aluguel, financiamento, condomínio',
                'tipo': 'despesa',
                'cor': '#45B7D1',
                'icone': 'home'
            },
            {
                'nome': 'Saúde',
                'descricao': 'Médicos, medicamentos, plano de saúde',
                'tipo': 'despesa',
                'cor': '#96CEB4',
                'icone': 'local_hospital'
            },
            # Categorias de Receita
            {
                'nome': 'Salário',
                'descricao': 'Salário e bonificações',
                'tipo': 'receita',
                'cor': '#55A3FF',
                'icone': 'work'
            },
            {
                'nome': 'Freelance',
                'descricao': 'Trabalhos extras',
                'tipo': 'receita',
                'cor': '#26DE81',
                'icone': 'business_center'
            }
        ]
        
        for cat_data in categorias_padrao:
            categoria = Categoria(
                usuario_id=usuario_id,
                **cat_data
            )
            self.db.add(categoria)
    
    def autenticar_usuario(self, email: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário"""
        usuario = self.db.query(Usuario).filter(
            Usuario.email == email,
            Usuario.ativo == True
        ).first()
        
        if not usuario:
            return None
        
        if not verify_password(senha, usuario.senha_hash):
            return None
        
        return usuario
    
    def fazer_login(self, email: str, senha: str) -> Token:
        """Realiza o login e retorna o token"""
        usuario = self.autenticar_usuario(email, senha)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(usuario.id)}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutos em segundos
            usuario=UsuarioResponse.from_orm(usuario)
        )
    
    def obter_usuario_por_id(self, usuario_id: uuid.UUID) -> Optional[Usuario]:
        """Obtém um usuário pelo ID"""
        return self.db.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.ativo == True
        ).first()