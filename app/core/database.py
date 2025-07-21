from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

# Criar engine com configurações otimizadas
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Função para criar todas as tabelas no banco de dados
    """
    try:
        # Importar todos os models para garantir que sejam registrados
        from app.models.usuario import Usuario
        from app.models.categoria import Categoria
        from app.models.conta_bancaria import ContaBancaria
        from app.models.cartao_credito import CartaoCredito
        from app.models.emprestimo import Emprestimo
        from app.models.transacao import Transacao
        from app.models.fatura_cartao import FaturaCartao
        from app.models.parcela_emprestimo import ParcelaEmprestimo
        from app.models.orcamento import Orcamento
        from app.models.meta_financeira import MetaFinanceira
        from app.models.alerta import Alerta
        from app.models.configuracao_usuario import ConfiguracaoUsuario
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Todas as tabelas foram criadas com sucesso!")
        
    except SQLAlchemyError as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise e

def test_connection():
    """
    Testa a conexão com o banco de dados
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False