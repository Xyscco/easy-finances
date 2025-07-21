from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base

class Alerta(Base):
    __tablename__ = "alertas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    tipo_alerta = Column(String(30), nullable=False)
    titulo = Column(String(200), nullable=False)
    mensagem = Column(Text, nullable=False)
    data_alerta = Column(DateTime(timezone=True), nullable=False)
    lido = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo_alerta IN ('vencimento_fatura', 'vencimento_emprestimo', 'limite_orcamento', 'meta_atingida', 'saldo_baixo')", name="check_tipo_alerta"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="alertas")
    
    @property
    def eh_urgente(self):
        return self.tipo_alerta in ['vencimento_fatura', 'vencimento_emprestimo', 'saldo_baixo']
    
    @property
    def eh_positivo(self):
        return self.tipo_alerta == 'meta_atingida'
    
    @property
    def icone_alerta(self):
        icones = {
            'vencimento_fatura': 'credit_card',
            'vencimento_emprestimo': 'account_balance',
            'limite_orcamento': 'warning',
            'meta_atingida': 'check_circle',
            'saldo_baixo': 'account_balance_wallet'
        }
        return icones.get(self.tipo_alerta, 'notification_important')
    
    @property
    def cor_alerta(self):
        cores = {
            'vencimento_fatura': 'orange',
            'vencimento_emprestimo': 'red',
            'limite_orcamento': 'yellow',
            'meta_atingida': 'green',
            'saldo_baixo': 'red'
        }
        return cores.get(self.tipo_alerta, 'blue')
    
    def __repr__(self):
        return f"<Alerta(id={self.id}, tipo='{self.tipo_alerta}', titulo='{self.titulo}', lido={self.lido})>"