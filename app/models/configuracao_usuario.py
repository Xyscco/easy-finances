from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base

class ConfiguracaoUsuario(Base):
    __tablename__ = "configuracoes_usuario"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    moeda = Column(String(3), default='BRL')
    formato_data = Column(String(10), default='DD/MM/YYYY')
    tema = Column(String(10), default='auto')
    notificacoes_email = Column(Boolean, default=True)
    notificacoes_push = Column(Boolean, default=True)
    dia_fechamento_mes = Column(Integer, default=1)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tema IN ('claro', 'escuro', 'auto')", name="check_tema"),
        CheckConstraint("dia_fechamento_mes BETWEEN 1 AND 31", name="check_dia_fechamento_mes"),
        UniqueConstraint("usuario_id", name="uq_usuario_configuracao"),
        {"schema": None}
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="configuracao")
    
    @property
    def simbolo_moeda(self):
        simbolos = {
            'BRL': 'R\$',
            'USD': '$',
            'EUR': '€',
            'GBP': '£'
        }
        return simbolos.get(self.moeda, 'R\$')
    
    @property
    def nome_moeda(self):
        nomes = {
            'BRL': 'Real Brasileiro',
            'USD': 'Dólar Americano',
            'EUR': 'Euro',
            'GBP': 'Libra Esterlina'
        }
        return nomes.get(self.moeda, 'Real Brasileiro')
    
    def formatar_valor(self, valor):
        """Formata um valor monetário de acordo com a configuração do usuário"""
        if valor is None:
            return f"{self.simbolo_moeda} 0,00"
        
        valor_float = float(valor)
        if self.moeda == 'BRL':
            return f"{self.simbolo_moeda} {valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            return f"{self.simbolo_moeda} {valor_float:,.2f}"
    
    def __repr__(self):
        return f"<ConfiguracaoUsuario(id={self.id}, usuario_id={self.usuario_id}, moeda='{self.moeda}')>"