from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime

# --- Modelos Pydantic para Request/Response da API ---

class IndividuoBase(BaseModel):
    nome: Optional[str] = Field(None, description="Nome completo (opcional para processamento, necessário para salvar)")
    data_nascimento: date = Field(..., description="Data de nascimento (YYYY-MM-DD)")
    data_avaliacao: date = Field(..., description="Data da avaliação (YYYY-MM-DD)")
    sexo: str = Field(..., description="Sexo ('M' para masculino, 'F' para feminino)") # Ou use um Enum
    peso_kg: float = Field(..., gt=0, description="Peso em quilogramas (ex: 15.5)")
    altura_cm: float = Field(..., gt=0, description="Altura/Comprimento em centímetros (ex: 95.3)")

    @validator('sexo')
    def sexo_must_be_M_or_F(cls, v):
        if v.upper() not in ['M', 'F']:
            raise ValueError('Sexo deve ser "M" ou "F"')
        return v.upper()

    @validator('data_avaliacao')
    def data_avaliacao_not_before_nascimento(cls, v, values):
        if 'data_nascimento' in values and v < values['data_nascimento']:
            raise ValueError('Data de avaliação não pode ser anterior à data de nascimento')
        return v

class IndividuoCreate(IndividuoBase):
    pass

class IndicadorCalculado(BaseModel):
    tipo: str # Ex: "P/I", "A/I", "IMC/I"
    valor_medido: Optional[float] = None # Peso, Altura ou IMC
    escore_z: Optional[float] = None
    classificacao: Optional[str] = None
    destaque: bool = False # True se houver alguma alteração nutricional

class ResultadoProcessamentoIndividual(BaseModel):
    dados_entrada: IndividuoBase
    idade_calculada_str: str # Ex: "2 anos, 3 meses e 15 dias"
    idade_anos: int
    idade_meses: int
    idade_dias: int
    imc_calculado: Optional[float] = None
    indicadores: List[IndicadorCalculado] = []

class ResultadoProcessamentoLote(BaseModel):
    nome_arquivo: Optional[str] = None
    total_processados: int
    total_com_erros: int
    resultados_individuais: List[ResultadoProcessamentoIndividual] # Ou apenas um resumo estatístico
    # Adicionar estatísticas consolidadas aqui
    # Ex: distribuicao_imc: Dict[str, int] = {} # {"Baixo Peso": 10, "Eutrófico": 50, ...}

# --- Modelos SQLAlchemy para o Banco de Dados (Tabelas de Referência SISVAN) ---
# Estes são apenas exemplos conceituais. Você precisará definir as colunas
# exatamente como nas tabelas do SISVAN que você vai importar.
# A importação dos dados CSV para essas tabelas será um passo crucial.

from sqlalchemy import Integer, String, Float, Date, Enum as SQLAlchemyEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
import enum

class SexoEnumDB(enum.Enum):
    MASCULINO = "M"
    FEMININO = "F"

class TabelaReferenciaSISVAN(Base): # Novo nome, mais genérico
    __tablename__ = "sisvan_referencia_valores_z" # Nome da tabela no DB

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    indicador: Mapped[str] = mapped_column(String(20), index=True, nullable=False) # Ex: "peso_idade", "altura_idade", "imc_idade"
    sexo: Mapped[SexoEnumDB] = mapped_column(SQLAlchemyEnum(SexoEnumDB), index=True, nullable=False)
    idade_meses: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # Renomeando sdX para valor_z_... para clareza e evitar problemas com nomes de colunas
    valor_z_neg_3: Mapped[Optional[float]] = mapped_column("z_neg_3", Float, nullable=True)
    valor_z_neg_2: Mapped[Optional[float]] = mapped_column("z_neg_2", Float, nullable=True)
    valor_z_neg_1: Mapped[Optional[float]] = mapped_column("z_neg_1", Float, nullable=True)
    valor_z_0: Mapped[Optional[float]] = mapped_column("z_0", Float, nullable=True) # Mediana
    valor_z_pos_1: Mapped[Optional[float]] = mapped_column("z_pos_1", Float, nullable=True)
    valor_z_pos_2: Mapped[Optional[float]] = mapped_column("z_pos_2", Float, nullable=True)
    valor_z_pos_3: Mapped[Optional[float]] = mapped_column("z_pos_3", Float, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('indicador', 'sexo', 'idade_meses', name='uq_indicador_sexo_idade_val_z'),
    )

class TabelaClassificacao(Base):
    __tablename__ = "sisvan_classification_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    indicador: Mapped[str] = mapped_column(String(20), index=True) # Aumentei o tamanho para "peso_idade", etc.
    idade_min_meses: Mapped[int] = mapped_column(Integer)
    idade_max_meses: Mapped[int] = mapped_column(Integer)
    sexo_aplicavel: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    z_score_min: Mapped[float] = mapped_column(Float)
    z_score_max: Mapped[float] = mapped_column(Float)
    classificacao_pt: Mapped[str] = mapped_column(String(100))
    # Adicionar um campo para "destaque" ou criticidade pode ser útil
    # Se quiser adicionar, seria algo como:
    # criticidade_nivel: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Ex: 0=Normal, 1=Atenção, 2=Grave

# TODO: Adicionar mais modelos SQLAlchemy para as outras tabelas de referência SISVAN
# e para dados de pacientes (se o usuário optar por salvar).