from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routers.ana as ana  # pyright: ignore[reportImplicitRelativeImport]
import routers.aneel as aneel  # pyright: ignore[reportImplicitRelativeImport]
import routers.anp as anp  # pyright: ignore[reportImplicitRelativeImport]
import routers.chat as chat  # pyright: ignore[reportImplicitRelativeImport]
import routers.contratos as contratos  # pyright: ignore[reportImplicitRelativeImport]
import routers.diario_oficial as diario_oficial  # pyright: ignore[reportImplicitRelativeImport]
import routers.educacao as educacao  # pyright: ignore[reportImplicitRelativeImport]
import routers.eleicoes as eleicoes  # pyright: ignore[reportImplicitRelativeImport]
import routers.emendas as emendas  # pyright: ignore[reportImplicitRelativeImport]
import routers.datajud as datajud  # pyright: ignore[reportImplicitRelativeImport]
import routers.empresas as empresas  # pyright: ignore[reportImplicitRelativeImport]
import routers.farmacia_popular as farmacia_popular  # pyright: ignore[reportImplicitRelativeImport]
import routers.fnde as fnde  # pyright: ignore[reportImplicitRelativeImport]
import routers.indicadores as indicadores  # pyright: ignore[reportImplicitRelativeImport]
import routers.licitacoes as licitacoes  # pyright: ignore[reportImplicitRelativeImport]
import routers.meio_ambiente as meio_ambiente  # pyright: ignore[reportImplicitRelativeImport]
import routers.municipios as municipios  # pyright: ignore[reportImplicitRelativeImport]
import routers.noticias as noticias  # pyright: ignore[reportImplicitRelativeImport]
import routers.orcamento as orcamento  # pyright: ignore[reportImplicitRelativeImport]
import routers.saude as saude  # pyright: ignore[reportImplicitRelativeImport]
import routers.seguranca as seguranca  # pyright: ignore[reportImplicitRelativeImport]
import routers.tcu as tcu  # pyright: ignore[reportImplicitRelativeImport]
import routers.vacinacao as vacinacao  # pyright: ignore[reportImplicitRelativeImport]
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
app.include_router(vacinacao.router, prefix="/vacinacao", tags=["vacinacao"])
app.include_router(fnde.router, prefix="/fnde", tags=["fnde"])
app.include_router(tcu.router, prefix="/tcu", tags=["tcu"])
app.include_router(farmacia_popular.router, prefix="/farmacia_popular", tags=["farmacia_popular"])
app.include_router(noticias.router, prefix="/noticias", tags=["noticias"])
app.include_router(anp.router, prefix="/anp", tags=["anp"])
app.include_router(datajud.router, prefix="/datajud", tags=["datajud"])
app.include_router(empresas.router, prefix="/empresas", tags=["empresas"])
app.include_router(ana.router, prefix="/ana", tags=["ana"])
app.include_router(aneel.router, prefix="/aneel", tags=["aneel"])

@app.get("/health")
def health():
    return {"status": "ok"}
