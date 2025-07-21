from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from ..core.database import Base

class Transacao(Base):
    __tablename__ = "transacoes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id", ondelete="SET NULL"))
    conta_bancaria_id = Column(UUID(as_uuid=True), ForeignKey("contas_bancarias.id", ondelete="SET NULL"))
    cartao_credito_id = Column(UUID(as_uuid=True), ForeignKey("cartoes_credito.id", ondelete="SET NULL"))
    emprestimo_id = Column(UUID(as_uuid=True), ForeignKey("emprestimos.id", ondelete="SET NULL"))
    
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(15, 2), nullable=False)
    tipo_transacao = Column(String(20), nullable=False)
    data_transacao = Column(Date, nullable=False)
    data_vencimento = Column(Date)
    
    eh_recorrente = Column(Boolean, default=False)
    frequencia_recorrencia = Column(String(20))
    data_fim_recorrencia = Column(Date)
    
    status = Column(String(20), default="concluida")
    observacoes = Column(Text)
    etiquetas = Column(ARRAY(String))
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo_transacao IN ('receita', 'despesa', 'transferencia', 'pagamento_emprestimo', 'pagamento_cartao')", name="check_tipo_transacao"),
        CheckConstraint("frequencia_recorrencia IN ('diaria', 'semanal', 'mensal', 'anual') OR frequencia_recorrencia IS NULL", name="check_frequencia_recorrencia"),
        CheckConstraint("status IN ('pendente', 'concluida', 'cancelada')", name="check_status_transacao"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="transacoes")
    categoria = relationship("Categoria", back_populates="transacoes")
    conta_bancaria = relationship("ContaBancaria", back_populates="transacoes")
    cartao_credito = relationship("CartaoCredito", back_populates="transacoes")
    emprestimo = relationship("Emprestimo", back_populates="transacoes")
    
    @property
    def valor_formatado(self):
        return float(self.valor) if self.valor else 0.0
    
    @property
    def eh_receita(self):
        return self.tipo_transacao == 'receita'
    
    @property
    def eh_despesa(self):
        return self.tipo_transacao == 'despesa'
    
    @property
    def origem_transacao(self):
        if self.conta_bancaria_id:
            return "conta_bancaria"
        elif self.cartao_credito_id:
            return "cartao_credito"
        elif self.emprestimo_id:
            return "emprestimo"
        return "indefinido"
    
    def __repr__(self):
        return f"<Transacao(id={self.id}, descricao='{self.descricao}', valor={self.valor}, tipo='{self.tipo_transacao}')>"