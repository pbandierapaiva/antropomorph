# app/models.py

from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base

# --- Modelos Pydantic (para validação na API) ---

class SexoEnum(str, Enum):
    M = "M"
    F = "F"

class IndividuoBase(BaseModel):
    nome: Optional[str] = None
    data_nascimento: date
    data_avaliacao: date
    sexo: SexoEnum
    peso_kg: Decimal = Field(..., gt=0, description="Peso em quilogramas")
    altura_cm: Decimal = Field(..., gt=0, description="Altura em centímetros")

class IndividuoCreate(BaseModel):
    nome: str
    data_nascimento: date
    data_avaliacao: date  # <-- CAMPO ADICIONADO AQUI
    sexo: SexoEnum
    peso_kg: Decimal = Field(..., gt=0, description="Peso em quilogramas")
    altura_cm: Decimal = Field(..., gt=0, description="Altura em centímetros")

class Indicador(BaseModel):
    tipo: str
    valor_observado: Decimal
    escore_z: float
    classificacao: str

class ResultadoProcessamentoIndividual(BaseModel):
    nome: str
    sexo: str
    data_nascimento: date
    data_avaliacao: date  # <-- CAMPO ADICIONADO AQUI
    idade: str
    peso_kg: Decimal
    altura_cm: Decimal
    imc: Optional[float]
    indicadores: List[Indicador]

class ErroLinha(BaseModel):
    linha: int
    erro: str
    dados_originais: Dict[str, Any]

class ReportData(BaseModel):
    success_results: List[ResultadoProcessamentoIndividual]
    error_results: List[ErroLinha]


# --- Modelos SQLAlchemy (Tabelas do Banco de Dados) ---
# (Nenhuma alteração necessária aqui)

class TabelaReferenciaSISVAN(Base):
    __tablename__ = 'sisvan_referencia_valores_z'
    
    id = Column(Integer, primary_key=True, index=True)
    indicador = Column(String(50), nullable=False, index=True)
    sexo = Column(String(10), nullable=False, index=True)
    idade_meses = Column(Integer, nullable=False, index=True)
    
    valor_z_neg_3 = Column(Float, nullable=True)
    valor_z_neg_2 = Column(Float, nullable=True)
    valor_z_neg_1 = Column(Float, nullable=True)
    valor_z_0 = Column(Float, nullable=True)
    valor_z_pos_1 = Column(Float, nullable=True)
    valor_z_pos_2 = Column(Float, nullable=True)
    valor_z_pos_3 = Column(Float, nullable=True)

    m = Column(Float, nullable=True)
    l = Column(Float, nullable=True)
    s = Column(Float, nullable=True)

class TabelaClassificacao(Base):
    __tablename__ = 'regras_classificacao_sisvan'

    id = Column(Integer, primary_key=True, index=True)
    indicador = Column(String(50), nullable=False, index=True)
    idade_min_meses = Column(Integer, nullable=False)
    idade_max_meses = Column(Integer, nullable=False)
    sexo_aplicavel = Column(String(10), nullable=True)
    z_score_min = Column(Float, nullable=False)
    z_score_max = Column(Float, nullable=False)
    classificacao = Column(String(255), nullable=False)