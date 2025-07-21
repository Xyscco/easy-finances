from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class ContaBancaria(Base):
    __tablename__ = "contas_bancarias"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(100), nullable=False)
    nome_banco = Column(String(100))
    tipo_conta = Column(String(20), nullable=False)
    saldo = Column(Numeric(15, 2), default=Decimal('0.00'))
    saldo_inicial = Column(Numeric(15, 2), default=Decimal('0.00'))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo_conta IN ('corrente', 'poupanca', 'investimento', 'dinheiro')", name="check_tipo_conta"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="contas_bancarias")
    transacoes = relationship("Transacao", back_populates="conta_bancaria")
    
    @property
    def saldo_disponivel(self):
        return float(self.saldo) if self.saldo else 0.0
    
    @property
    def variacao_saldo(self):
        if self.saldo_inicial and self.saldo:
            return float(self.saldo - self.saldo_inicial)
        return 0.0
    
    def __repr__(self):
        return f"<ContaBancaria(id={self.id}, nome='{self.nome}', saldo={self.saldo})>"