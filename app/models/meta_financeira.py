from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class MetaFinanceira(Base):
    __tablename__ = "metas_financeiras"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    valor_objetivo = Column(Numeric(15, 2), nullable=False)
    valor_atual = Column(Numeric(15, 2), default=Decimal('0.00'))
    data_inicio = Column(Date, nullable=False)
    data_objetivo = Column(Date, nullable=False)
    tipo_meta = Column(String(20), nullable=False)
    status = Column(String(20), default="ativa")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo_meta IN ('economia', 'investimento', 'compra', 'viagem', 'emergencia')", name="check_tipo_meta"),
        CheckConstraint("status IN ('ativa', 'concluida', 'pausada', 'cancelada')", name="check_status_meta"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="metas_financeiras")
    
    @property
    def valor_restante(self):
        if self.valor_objetivo and self.valor_atual:
            return float(self.valor_objetivo - self.valor_atual)
        return float(self.valor_objetivo) if self.valor_objetivo else 0.0
    
    @property
    def percentual_atingido(self):
        if self.valor_objetivo and self.valor_atual:
            return (float(self.valor_atual) / float(self.valor_objetivo)) * 100
        return 0.0
    
    @property
    def esta_concluida(self):
        return self.valor_atual and self.valor_objetivo and self.valor_atual >= self.valor_objetivo
    
    @property
    def dias_restantes(self):
        from datetime import date
        if self.data_objetivo:
            delta = self.data_objetivo - date.today()
            return delta.days if delta.days > 0 else 0
        return None
    
    @property
    def valor_mensal_necessario(self):
        if self.dias_restantes and self.dias_restantes > 0:
            meses_restantes = self.dias_restantes / 30.0
            if meses_restantes > 0:
                return self.valor_restante / meses_restantes
        return 0.0
    
    def __repr__(self):
        return f"<MetaFinanceira(id={self.id}, nome='{self.nome}', objetivo={self.valor_objetivo}, atual={self.valor_atual})>"