from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os


app = FastAPI()

app.mount("/static", StaticFiles(directory="web"), name="static")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Pontos de referência (idade_dias, IMC) ↔ (pixel_x, pixel_y)
REFERENCE_POINTS = {
    (0, 10): (167, 1056),      # Recém-nascido (0 dias)
    (731, 22): (1972, 74)    # 2 anos em dias (2 * 365.5)
}

def calcular_idade_em_dias(data_nascimento: str) -> int:
    """Converte data de nascimento para idade em dias."""
    hoje = datetime.now()
    nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d")
    return (hoje - nascimento).days

def map_to_pixel(idade_dias: int, imc: float) -> tuple[int, int]:
    (idade0, imc0), (idade1, imc1) = REFERENCE_POINTS.keys()
    x0, y0 = REFERENCE_POINTS[(idade0, imc0)]
    x1, y1 = REFERENCE_POINTS[(idade1, imc1)]
    pixel_x = x0 + (idade_dias - idade0) * (x1 - x0) / (idade1 - idade0)
    pixel_y = y0 + (imc - imc0) * (y1 - y0) / (imc1 - imc0)
    return int(pixel_x), int(pixel_y)



# Rota principal: Retorna o HTML
@app.get("/", response_class=HTMLResponse)
async def ler_plota_html():
    with open(os.path.join("web", "plota.html"), "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.get("/plotar-ponto/")
async def plotar_ponto(data_nascimento: str, imc: float):
    idade_dias = calcular_idade_em_dias(data_nascimento)
    if not (0 <= idade_dias <= 732):  # 2 anos em dias
        raise HTTPException(status_code=400, detail="Idade deve estar entre 0 e 2 anos.")
    if not (10 <= imc <= 23):
        raise HTTPException(status_code=400, detail="IMC deve estar entre 10 e 23 kg/m².")
    
    background_image = mpimg.imread("imagens/imc02.png")
    pixel_x, pixel_y = map_to_pixel(idade_dias, imc)
    
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.imshow(background_image)
    ax.plot(pixel_x, pixel_y, 'ro', markersize=10, label=f'({idade_dias} dias, IMC={imc})')
    ax.legend()
    plt.axis('off')
    
    temp_file = "temp_plot.png"
    plt.savefig(temp_file, bbox_inches='tight', dpi=300)
    plt.close()
    
    return FileResponse(temp_file, media_type="image/png")
