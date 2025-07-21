from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class FaturaCartao(Base):
    __tablename__ = "faturas_cartao"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cartao_credito_id = Column(UUID(as_uuid=True), ForeignKey("cartoes_credito.id", ondelete="CASCADE"), nullable=False)
    mes_referencia = Column(Date, nullable=False)
    valor_total = Column(Numeric(15, 2), nullable=False)
    pagamento_minimo = Column(Numeric(15, 2), nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_fechamento = Column(Date, nullable=False)
    status = Column(String(20), default="aberta")
    valor_pago = Column(Numeric(15, 2), default=Decimal('0.00'))
    data_pagamento = Column(Date)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('aberta', 'fechada', 'paga', 'vencida')", name="check_status_fatura"),
        {"schema": None}
    )
    
    # Relacionamentos
    cartao_credito = relationship("CartaoCredito", back_populates="faturas")
    
    @property
    def valor_restante(self):
        if self.valor_total and self.valor_pago:
            return float(self.valor_total - self.valor_pago)
        return float(self.valor_total) if self.valor_total else 0.0
    
    @property
    def percentual_pago(self):
        if self.valor_total and self.valor_pago:
            return (float(self.valor_pago) / float(self.valor_total)) * 100
        return 0.0
    
    @property
    def esta_vencida(self):
        from datetime import date
        return self.data_vencimento < date.today() and self.status != 'paga'
    
    @property
    def esta_paga(self):
        return self.status == 'paga' or (self.valor_pago and self.valor_pago >= self.valor_total)
    
    def __repr__(self):
        return f"<FaturaCartao(id={self.id}, mes_referencia={self.mes_referencia}, valor_total={self.valor_total})>"