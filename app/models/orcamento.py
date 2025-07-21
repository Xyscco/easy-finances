from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class Orcamento(Base):
    __tablename__ = "orcamentos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id", ondelete="CASCADE"))
    nome = Column(String(100), nullable=False)
    valor_limite = Column(Numeric(15, 2), nullable=False)
    valor_gasto = Column(Numeric(15, 2), default=Decimal('0.00'))
    tipo_periodo = Column(String(20), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo_periodo IN ('mensal', 'anual')", name="check_tipo_periodo"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="orcamentos")
    categoria = relationship("Categoria", back_populates="orcamentos")
    
    @property
    def valor_disponivel(self):
        if self.valor_limite and self.valor_gasto:
            return float(self.valor_limite - self.valor_gasto)
        return float(self.valor_limite) if self.valor_limite else 0.0
    
    @property
    def percentual_gasto(self):
        if self.valor_limite and self.valor_gasto:
            return (float(self.valor_gasto) / float(self.valor_limite)) * 100
        return 0.0
    
    @property
    def esta_estourado(self):
        return self.valor_gasto and self.valor_limite and self.valor_gasto > self.valor_limite
    
    @property
    def proximo_limite(self):
        # Retorna True se está próximo do limite (80% ou mais)
        return self.percentual_gasto >= 80.0
    
    @property
    def status_orcamento(self):
        if self.esta_estourado:
            return "estourado"
        elif self.proximo_limite:
            return "atencao"
        elif self.percentual_gasto >= 50.0:
            return "moderado"
        else:
            return "normal"
    
    def __repr__(self):
        return f"<Orcamento(id={self.id}, nome='{self.nome}', limite={self.valor_limite}, gasto={self.valor_gasto})>"