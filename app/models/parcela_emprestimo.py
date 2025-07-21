from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, ForeignKey, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class ParcelaEmprestimo(Base):
    __tablename__ = "parcelas_emprestimo"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    emprestimo_id = Column(UUID(as_uuid=True), ForeignKey("emprestimos.id", ondelete="CASCADE"), nullable=False)
    numero_parcela = Column(Integer, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    valor = Column(Numeric(15, 2), nullable=False)
    valor_principal = Column(Numeric(15, 2), nullable=False)
    valor_juros = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), default="pendente")
    data_pagamento = Column(Date)
    valor_pago = Column(Numeric(15, 2), default=Decimal('0.00'))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('pendente', 'paga', 'vencida')", name="check_status_parcela"),
        UniqueConstraint("emprestimo_id", "numero_parcela", name="uq_emprestimo_parcela"),
        {"schema": None}
    )
    
    # Relacionamentos
    emprestimo = relationship("Emprestimo", back_populates="parcelas")
    
    @property
    def valor_restante(self):
        if self.valor and self.valor_pago:
            return float(self.valor - self.valor_pago)
        return float(self.valor) if self.valor else 0.0
    
    @property
    def esta_vencida(self):
        from datetime import date
        return self.data_vencimento < date.today() and self.status != 'paga'
    
    @property
    def esta_paga(self):
        return self.status == 'paga' or (self.valor_pago and self.valor_pago >= self.valor)
    
    @property
    def dias_vencimento(self):
        from datetime import date
        if self.data_vencimento:
            delta = self.data_vencimento - date.today()
            return delta.days
        return None
    
    def __repr__(self):
        return f"<ParcelaEmprestimo(id={self.id}, numero={self.numero_parcela}, valor={self.valor}, status='{self.status}')>"