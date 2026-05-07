from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import municipios, indicadores, orcamento, vereadores, contratos

app = FastAPI(
    title="GestãoBR API",
    description="API de gestão pública municipal",
    version="1.0.0",
    root_path="/gestaobr/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(municipios.router, prefix="/municipios", tags=["municipios"])
app.include_router(indicadores.router, prefix="/indicadores", tags=["indicadores"])
app.include_router(orcamento.router, prefix="/orcamento", tags=["orcamento"])
app.include_router(vereadores.router, prefix="/vereadores", tags=["vereadores"])
app.include_router(contratos.router, prefix="/contratos", tags=["contratos"])

@app.get("/health")
def health():
    return {"status": "ok"}
