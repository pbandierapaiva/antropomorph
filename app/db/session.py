from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Verifica se DATABASE_URL está configurada
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL não está configurada. Verifique app/core/config.py ou seu arquivo .env.")

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para obter uma sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Você precisará criar as tabelas no banco de dados.
# Uma forma é usar Alembic para migrações, ou criar um script simples.
# Por enquanto, vamos apenas definir a base.
# Exemplo de como criar tabelas (coloque isso em um script de inicialização do DB ou use Alembic):
# from app.models import SeuModeloDeTabela  # Importe seus modelos SQLAlchemy
# Base.metadata.create_all(bind=engine)