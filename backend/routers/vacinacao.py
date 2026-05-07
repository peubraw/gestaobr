"""
Cobertura vacinal via SI-PNI (DATASUS) e fallback para portal.
API: https://imunizacao-es.saude.gov.br/_search (Elasticsearch público)
Fallback: link direto para tabnet.datasus.gov.br
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

# Vacinas prioritárias para monitoramento municipal
VACINAS_REFERENCIA = [
    "Poliomielite",
    "Tríplice viral (sarampo, caxumba, rubéola)",
    "Pentavalente (DTP/Hib/HepB)",
    "BCG",
    "Febre Amarela",
    "COVID-19",
]


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def vacinacao_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        # Tenta buscar cobertura via SI-PNI ElasticSearch público
        coberturas = []
        meta_ano = None

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://imunizacao-es.saude.gov.br/desc-imunizacao/_search",
                    json={
                        "size": 10,
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"co_municipio_ibge": ibge}},
                                    {"term": {"nu_ano": 2024}},
                                ]
                            }
                        },
                        "_source": ["no_vacina", "nu_cobertura", "nu_ano", "no_municipio"],
                    },
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    hits = data.get("hits", {}).get("hits", [])
                    for h in hits:
                        src = h.get("_source", {})
                        if src.get("nu_cobertura") is not None:
                            coberturas.append({
                                "vacina": src.get("no_vacina"),
                                "cobertura_pct": src.get("nu_cobertura"),
                                "ano": src.get("nu_ano"),
                            })
                    if coberturas:
                        meta_ano = coberturas[0]["ano"]
        except Exception:
            pass

        # Link direto Tabnet para consulta manual
        link_tabnet = (
            f"http://tabnet.datasus.gov.br/cgi/dhdat.exe?bd_pni/dpnibr.def"
        )
        link_sisab = f"https://sisab.saude.gov.br/paginas/acessoRestrito/relatorio/federal/indicadores/indicadorPainel.xhtml"

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "coberturas": coberturas[:10],
            "total_vacinas": len(coberturas),
            "ano_referencia": meta_ano or 2024,
            "vacinas_monitoradas": VACINAS_REFERENCIA,
            "link_sipni": f"https://sipni.datasus.gov.br/si-pni-web/faces/relatorio/municipio/cobertura.jsf",
            "link_tabnet": link_tabnet,
            "fonte": "SI-PNI / DATASUS",
            "aviso": "Dados de cobertura vacinal por município. Meta nacional: ≥95% para maioria das vacinas." if not coberturas else None,
        }

    except Exception as e:
        return {
            "disponivel": False,
            "erro": str(e),
            "link_sipni": "https://sipni.datasus.gov.br/si-pni-web/faces/relatorio/municipio/cobertura.jsf",
            "fonte": "SI-PNI / DATASUS",
        }
