from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Integer, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class Emprestimo(Base):
    __tablename__ = "emprestimos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(100), nullable=False)
    tipo_emprestimo = Column(String(20), nullable=False)
    valor_principal = Column(Numeric(15, 2), nullable=False)
    saldo_devedor = Column(Numeric(15, 2), nullable=False)
    taxa_juros = Column(Numeric(5, 2), nullable=False)  # Taxa anual
    total_parcelas = Column(Integer, nullable=False)
    parcelas_pagas = Column(Integer, default=0)
    valor_parcela = Column(Numeric(15, 2), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    proximo_vencimento = Column(Date)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo_emprestimo IN ('pessoal', 'habitacional', 'veiculo', 'estudantil', 'empresarial')", name="check_tipo_emprestimo"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="emprestimos")
    transacoes = relationship("Transacao", back_populates="emprestimo")
    parcelas = relationship("ParcelaEmprestimo", back_populates="emprestimo", cascade="all, delete-orphan")
    
    @property
    def parcelas_restantes(self):
        return self.total_parcelas - self.parcelas_pagas
    
    @property
    def percentual_pago(self):
        if self.total_parcelas > 0:
            return (self.parcelas_pagas / self.total_parcelas) * 100
        return 0.0
    
    @property
    def valor_total_juros(self):
        if self.valor_parcela and self.total_parcelas and self.valor_principal:
            valor_total = float(self.valor_parcela) * self.total_parcelas
            return valor_total - float(self.valor_principal)
        return 0.0
    
    def __repr__(self):
        return f"<Emprestimo(id={self.id}, nome='{self.nome}', saldo_devedor={self.saldo_devedor})>"