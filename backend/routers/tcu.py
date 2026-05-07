"""
TCU — processos, acórdãos e irregularidades envolvendo o município.
API pública: https://contas.tcu.gov.br/ords/f (sem chave)
Busca via Portal da Transparência TCU: https://portal.tcu.gov.br/
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

TCU_ACORDAOS = "https://contas.tcu.gov.br/ords/f?p=CONTAS:CONSULTA_ACORDAO_SIMPLIFICADO_JSON"
TCU_INIDONES = "https://certidoes-apf.apps.tcu.gov.br/"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def tcu_municipio(ibge: str, nome_municipio: str = ""):
    try:
        _validar_ibge(ibge)

        acordaos = []
        irregularidades = []

        # Tenta buscar acórdãos do TCU mencionando o município via API pública
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # API REST do TCU (ORDS Oracle)
                resp = await client.get(
                    "https://contas.tcu.gov.br/ords/tcuweb/acordao/pesquisar",
                    params={
                        "q": nome_municipio or ibge,
                        "offset": 0,
                        "limit": 5,
                    },
                    headers={"Accept": "application/json"},
                )
                if resp.status_code == 200 and "json" in resp.headers.get("content-type", ""):
                    data = resp.json()
                    items = data.get("items", data.get("acordaos", []))
                    for item in items[:5]:
                        acordaos.append({
                            "numero": item.get("numAcordao") or item.get("numero"),
                            "ano": item.get("anoAcordao") or item.get("ano"),
                            "tipo": item.get("tipoProcesso") or item.get("tipo"),
                            "relator": item.get("relator"),
                            "ementa": (item.get("ementa") or "")[:200],
                            "url": item.get("url") or f"https://contas.tcu.gov.br/juris/SvlHighLight?key={item.get('chave','')}&texto=",
                        })
        except Exception:
            pass

        # Links diretos para consulta
        link_tcu_juris = f"https://contas.tcu.gov.br/juris/Web/Juris/ConsultarTexto/ConsultarTexto.faces"
        link_certidao = f"https://certidoes-apf.apps.tcu.gov.br/"
        link_portal = f"https://portal.tcu.gov.br/municipios/"

        return {
            "disponivel": True,
            "ibge": ibge,
            "acordaos_recentes": acordaos,
            "total_acordaos": len(acordaos),
            # chaves alinhadas com o frontend
            "link_certidao": link_certidao,
            "link_acordaos": link_tcu_juris,
            "link_portal": link_portal,
            "nota": "Consulte a certidão de regularidade e acórdãos do TCU relativos ao município.",
            "fonte": "TCU / Tribunal de Contas da União",
        }

    except Exception as e:
        return {
            "disponivel": False,
            "ibge": ibge,
            "erro": str(e),
            "link_certidao": "https://certidoes-apf.apps.tcu.gov.br/",
            "link_acordaos": "https://contas.tcu.gov.br/juris/Web/Juris/ConsultarTexto/ConsultarTexto.faces",
            "link_portal": "https://portal.tcu.gov.br/municipios/",
            "nota": "Consulte a certidão de regularidade e acórdãos do TCU relativos ao município.",
            "fonte": "TCU / Tribunal de Contas da União",
        }
