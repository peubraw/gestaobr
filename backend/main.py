from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routers.chat as chat  # pyright: ignore[reportImplicitRelativeImport]
import routers.contratos as contratos  # pyright: ignore[reportImplicitRelativeImport]
import routers.diario_oficial as diario_oficial  # pyright: ignore[reportImplicitRelativeImport]
import routers.educacao as educacao  # pyright: ignore[reportImplicitRelativeImport]
import routers.eleicoes as eleicoes  # pyright: ignore[reportImplicitRelativeImport]
import routers.emendas as emendas  # pyright: ignore[reportImplicitRelativeImport]
import routers.indicadores as indicadores  # pyright: ignore[reportImplicitRelativeImport]
import routers.licitacoes as licitacoes  # pyright: ignore[reportImplicitRelativeImport]
import routers.meio_ambiente as meio_ambiente  # pyright: ignore[reportImplicitRelativeImport]
import routers.municipios as municipios  # pyright: ignore[reportImplicitRelativeImport]
import routers.orcamento as orcamento  # pyright: ignore[reportImplicitRelativeImport]
import routers.saude as saude  # pyright: ignore[reportImplicitRelativeImport]
import routers.seguranca as seguranca  # pyright: ignore[reportImplicitRelativeImport]
import routers.vereadores as vereadores  # pyright: ignore[reportImplicitRelativeImport]

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
app.include_router(saude.router, prefix="/saude", tags=["saude"])
app.include_router(educacao.router, prefix="/educacao", tags=["educacao"])
app.include_router(licitacoes.router, prefix="/licitacoes", tags=["licitacoes"])
app.include_router(eleicoes.router, prefix="/eleicoes", tags=["eleicoes"])
app.include_router(diario_oficial.router, prefix="/diario", tags=["diario"])
app.include_router(emendas.router, prefix="/emendas", tags=["emendas"])
app.include_router(seguranca.router, prefix="/seguranca", tags=["seguranca"])
app.include_router(meio_ambiente.router, prefix="/meio_ambiente", tags=["meio_ambiente"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/health")
def health():
    return {"status": "ok"}
