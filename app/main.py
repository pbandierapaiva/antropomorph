from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

# Importações do projeto
from app.models import IndividuoCreate, ResultadoProcessamentoIndividual, ErroLinha
from app.services.anthropometry_service import AnthropometryService
from app.db.session import get_db
from app.core.config import settings

from fastapi.staticfiles import StaticFiles
from app.models import ResultadoProcessamentoIndividual, ErroLinha

# Define ResultadoProcessamentoLote model
class ResultadoProcessamentoLote(BaseModel):
    nome_arquivo: str
    total_registros_no_arquivo: int
    total_processados_com_sucesso: int
    total_com_erros: int
    resultados_individuais: List[ResultadoProcessamentoIndividual]
    erros_por_linha: List[ErroLinha]

# Importação para o novo gerador de PDF (Puro Python)
from fpdf import FPDF
from fpdf.enums import Align

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    """Serve a página principal da aplicação."""
    return templates.TemplateResponse(request, "index.html", {"title": "Avaliação Antropométrica"})

@app.post("/api/processar/individual", response_model=ResultadoProcessamentoIndividual)
async def processar_dados_individuais(
    individuo_data: IndividuoCreate,
    db: Session = Depends(get_db)
):
    """Processa os dados de um único indivíduo e retorna a avaliação nutricional."""
    try:
        service = AnthropometryService(db=db)
        return service.process_individual_data(individuo_data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Erro inesperado no processamento individual: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")

@app.post("/api/processar/lote", response_model=ResultadoProcessamentoLote)
async def processar_dados_lote(
    batchFile: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Processa um arquivo em lote (CSV/TSV) e retorna os resultados."""
    if not batchFile.filename or not (batchFile.filename.endswith(".csv") or batchFile.filename.endswith(".tsv")):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Use CSV ou TSV.")
    try:
        contents = await batchFile.read()
        service = AnthropometryService(db=db)
        processed_data = service.process_batch_data(contents, batchFile.filename)
        return ResultadoProcessamentoLote(
            nome_arquivo=batchFile.filename,
            total_registros_no_arquivo=processed_data["total_rows_attempted"],
            total_processados_com_sucesso=len(processed_data["resultados_individuais"]),
            total_com_erros=len(processed_data["erros_por_linha"]),
            resultados_individuais=processed_data["resultados_individuais"],
            erros_por_linha=processed_data["erros_por_linha"]
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Erro inesperado no processamento em lote: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor ao processar o lote: {e}")


class ReportData(BaseModel):
    """Modelo de dados para receber as informações para o relatório PDF."""
    identifier: str
    sub_identifier: Optional[str] = None
    batch_results: ResultadoProcessamentoLote

class PDF(FPDF):
    """Classe customizada para criar o PDF com cabeçalho e rodapé."""
    def __init__(self, identifier: str = '', sub_identifier: str = ''):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.identifier = identifier
        self.sub_identifier = sub_identifier
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, self.identifier, 0, 1, 'L')
        if self.sub_identifier:
            self.set_font('Helvetica', '', 12)
            self.cell(0, 8, self.sub_identifier, 0, 1, 'L')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.cell(0, 10, f'Gerado em: {now}', 0, 0, 'R')

def get_fpdf_color(classification_text: Optional[str]):
    """Retorna uma tupla de cor RGB para o fpdf2 com base no texto da classificação."""
    if not classification_text:
        return None
    lower_class = classification_text.lower().replace(' ', '_')
    if any(s in lower_class for s in ['magreza_acentuada', 'muito_baixo_peso', 'obesidade_grave', 'erro']): return (254, 226, 226)
    if any(s in lower_class for s in ['magreza', 'baixo_peso', 'baixa_estatura', 'obesidade']): return (254, 242, 242)
    if any(s in lower_class for s in ['eutrofia', 'peso_adequado', 'estatura_adequada']): return (236, 253, 245)
    if any(s in lower_class for s in ['risco_de_sobrepeso', 'sobrepeso']): return (254, 252, 232)
    return None

def encode_for_latin1(text: str) -> str:
    """Codifica o texto para o formato latin-1, substituindo caracteres incompatíveis."""
    return text.encode('latin-1', 'replace').decode('latin-1')

@app.post("/api/export/pdf")
async def export_pdf_fpdf(report_data: ReportData):
    """Gera um relatório PDF usando FPDF2."""
    try:
        pdf = PDF(identifier=report_data.identifier, sub_identifier=report_data.sub_identifier or '')
        pdf.alias_nb_pages()
        pdf.add_page()
        
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(22, 78, 99)
        pdf.set_text_color(255, 255, 255)
        col_widths = (40, 15, 20, 25, 15, 18, 15, 30, 30, 30)
        header = ['Nome', 'Sexo', 'Nasc.', 'Idade', 'Peso(kg)', 'Altura(cm)', 'IMC', 'P/I', 'A/I', 'IMC/I']
        for i, header_text in enumerate(header):
            pdf.cell(col_widths[i], 8, header_text, border=1, align='C', fill=True)
        pdf.ln()

        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(0, 0, 0)
        
        def get_classification_from_indicators(indicators, prefix):
            return next((i.classificacao for i in indicators if i.tipo.startswith(prefix)), "N/A")

        for res in report_data.batch_results.resultados_individuais or []:
            imc_i_class = get_classification_from_indicators(res.indicadores, "IMC-para-Idade")
            color = get_fpdf_color(imc_i_class)
            fill = bool(color)
            if color:
                pdf.set_fill_color(*color)

            pdf.cell(col_widths[0], 6, encode_for_latin1(res.nome or 'N/A'), border=1, align='L', fill=fill)
            pdf.cell(col_widths[1], 6, 'M' if res.sexo == 'M' else 'F', border=1, align='C', fill=fill)
            pdf.cell(col_widths[2], 6, res.data_nascimento.strftime('%d/%m/%Y'), border=1, align='C', fill=fill)
            pdf.cell(col_widths[3], 6, f"{res.idade:.1f}a" if hasattr(res, 'idade_anos') else "N/A", border=1, align='L', fill=fill)
            pdf.cell(col_widths[4], 6, f"{res.peso_kg:.1f}", border=1, align='C', fill=fill)
            pdf.cell(col_widths[5], 6, f"{res.altura_cm:.1f}", border=1, align='C', fill=fill)
            pdf.cell(col_widths[6], 6, f"{res.imc:.2f}" if res.imc else "N/A", border=1, align='C', fill=fill)
            pdf.cell(col_widths[7], 6, encode_for_latin1(get_classification_from_indicators(res.indicadores, "Peso-para-Idade")), border=1, align='L', fill=fill)
            pdf.cell(col_widths[8], 6, encode_for_latin1(get_classification_from_indicators(res.indicadores, "Altura-para-Idade")), border=1, align='L', fill=fill)
            pdf.cell(col_widths[9], 6, encode_for_latin1(imc_i_class), border=1, align='L', fill=fill)
            pdf.ln()

        if report_data.batch_results.erros_por_linha:
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_fill_color(254, 226, 226)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(sum(col_widths), 8, 'Registros com Erro no Processamento', border=1, align='C', fill=True)
            pdf.ln()
            pdf.set_font('Helvetica', '', 7)
            for err in report_data.batch_results.erros_por_linha:
                nome = err.dados_originais.get('nome', 'N/A')
                erro_msg = f"Linha {err.linha}: {nome} - Erro: {err.erro}"
                pdf.multi_cell(sum(col_widths), 6, encode_for_latin1(erro_msg), border=1, align=Align.L, fill=True)

        pdf_bytes = pdf.output()
        
        file_name = f"Relatorio_{report_data.identifier.replace(' ', '_')}.pdf"
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=\"{file_name}\""})

    except Exception as e:
        print(f"Erro ao gerar PDF com fpdf2: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro ao gerar o relatório em PDF.")