from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    primeiro_nome = Column(String(100), nullable=False)
    ultimo_nome = Column(String(100), nullable=False)
    telefone = Column(String(20))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    categorias = relationship("Categoria", back_populates="usuario", cascade="all, delete-orphan")
    contas_bancarias = relationship("ContaBancaria", back_populates="usuario", cascade="all, delete-orphan")
    cartoes_credito = relationship("CartaoCredito", back_populates="usuario", cascade="all, delete-orphan")
    emprestimos = relationship("Emprestimo", back_populates="usuario", cascade="all, delete-orphan")
    transacoes = relationship("Transacao", back_populates="usuario", cascade="all, delete-orphan")
    orcamentos = relationship("Orcamento", back_populates="usuario", cascade="all, delete-orphan")
    metas_financeiras = relationship("MetaFinanceira", back_populates="usuario", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="usuario", cascade="all, delete-orphan")
    configuracao = relationship("ConfiguracaoUsuario", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    
    @property
    def nome_completo(self):
        return f"{self.primeiro_nome} {self.ultimo_nome}"
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', nome='{self.nome_completo}')>"