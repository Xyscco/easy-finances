from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class CartaoCredito(Base):
    __tablename__ = "cartoes_credito"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(100), nullable=False)
    nome_banco = Column(String(100))
    ultimos_digitos = Column(String(4))
    limite_credito = Column(Numeric(15, 2), nullable=False)
    saldo_atual = Column(Numeric(15, 2), default=Decimal('0.00'))
    dia_fechamento = Column(Integer, nullable=False)
    dia_vencimento = Column(Integer, nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("dia_fechamento BETWEEN 1 AND 31", name="check_dia_fechamento"),
        CheckConstraint("dia_vencimento BETWEEN 1 AND 31", name="check_dia_vencimento"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="cartoes_credito")
    transacoes = relationship("Transacao", back_populates="cartao_credito")
    faturas = relationship("FaturaCartao", back_populates="cartao_credito", cascade="all, delete-orphan")
    
    @property
    def limite_disponivel(self):
        if self.limite_credito and self.saldo_atual:
            return float(self.limite_credito - self.saldo_atual)
        return float(self.limite_credito) if self.limite_credito else 0.0
    
    @property
    def percentual_utilizado(self):
        if self.limite_credito and self.saldo_atual:
            return (float(self.saldo_atual) / float(self.limite_credito)) * 100
        return 0.0
    
    @property
    def nome_mascarado(self):
        if self.ultimos_digitos:
            return f"{self.nome} ****{self.ultimos_digitos}"
        return self.nome
    
    def __repr__(self):
        return f"<CartaoCredito(id={self.id}, nome='{self.nome}', limite={self.limite_credito})>"