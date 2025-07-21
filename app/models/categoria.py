from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    cor = Column(String(7))  # Formato hex #FFFFFF
    icone = Column(String(50))
    tipo = Column(String(20), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo IN ('receita', 'despesa')", name="check_categoria_tipo"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="categorias")
    transacoes = relationship("Transacao", back_populates="categoria")
    orcamentos = relationship("Orcamento", back_populates="categoria")
    
    def __repr__(self):
        return f"<Categoria(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"