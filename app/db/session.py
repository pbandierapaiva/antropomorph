# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Importa o objeto 'settings' que contém a URL do banco
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not configured")

engine = create_engine(DATABASE_URL, 
    #poolclass=NullPool,
    # Recicla conexões antes do timeout do MariaDB (ex: 1 hora)
    pool_recycle=3600, 
    # Testa a conexão ANTES de cada uso. Se estiver morta, reconecta.
    pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base que será importada pelos seus modelos em 'models.py'
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()