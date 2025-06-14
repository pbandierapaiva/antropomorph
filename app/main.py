from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import IndividuoCreate, ResultadoProcessamentoIndividual, ResultadoProcessamentoLote
from app.services.anthropometry_service import AnthropometryService
from app.db.session import get_db, engine, Base # Importe Base e engine
from app.core.config import settings

# TODO: Descomente e importe os modelos SQLAlchemy quando estiverem definidos
# from app.models import TabelaReferenciaWHO0_60Meses, TabelaClassificacao

# Crie as tabelas no banco de dados (se não existirem)
# Isso é para desenvolvimento. Em produção, use Alembic para migrações.
# Base.metadata.create_all(bind=engine) # Descomente quando os modelos SQLAlchemy estiverem prontos

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Montar arquivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates Jinja2
templates = Jinja2Templates(directory="app/templates")

# Endpoint principal para servir a página HTML
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Avaliação Antropométrica"})

# Endpoint para processamento de dados individuais
@app.post("/api/processar/individual", response_model=ResultadoProcessamentoIndividual)
async def processar_dados_individuais(
    individuo_data: IndividuoCreate,
    db: Session = Depends(get_db) # Injetar a sessão do DB
):
    try:
        service = AnthropometryService(db=db) # Passe a sessão para o serviço
        resultado = service.process_individual_data(individuo_data)
        return resultado
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Logar o erro em um sistema de logging real
        print(f"Erro inesperado no processamento individual: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")

# Endpoint para processamento de dados em lote (upload de arquivo)
@app.post("/api/processar/lote", response_model=List[ResultadoProcessamentoIndividual]) # Ou um modelo ResultadoProcessamentoLote
async def processar_dados_lote(
    file: UploadFile = File(...),
    db: Session = Depends(get_db) # Injetar a sessão do DB
):
    if not file.filename or not (file.filename.endswith(".csv") or file.filename.endswith(".tsv")):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido ou nome de arquivo não fornecido. Use CSV ou TSV.")

    try:
        contents = await file.read()
        service = AnthropometryService(db=db) # Passe a sessão para o serviço
        # A função process_batch_data deve retornar uma lista de ResultadoProcessamentoIndividual
        # ou um objeto ResultadoProcessamentoLote que contenha essa lista e estatísticas.
        resultados = service.process_batch_data(contents, file.filename)
        # return resultados # Se retornar List[ResultadoProcessamentoIndividual]

        # Se você quiser retornar um objeto ResultadoProcessamentoLote:
        # num_erros = ... # Calcule o número de erros se sua função os retornar
        # return ResultadoProcessamentoLote(
        #     nome_arquivo=file.filename,
        #     total_processados=len(resultados),
        #     total_com_erros=0, # Atualizar com a contagem de erros real
        #     resultados_individuais=resultados
        # )
        return resultados # Ajuste conforme o que process_batch_data retorna

    except ValueError as ve: # Erros de validação de dados ou formato de arquivo
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Logar o erro
        print(f"Erro inesperado no processamento em lote: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor ao processar o lote: {e}")

# Para executar: uvicorn app.main:app --reload (na raiz do projeto)