"""
Informações eleitorais e de governança municipal.
- Dados do prefeito via IBGE MUNIC (Pesquisa de Informações Básicas Municipais)
- Link direto para TSE com resultado de 2024
- Dados de câmara via Câmara dos Vereadores (camara.gov.br não tem API municipal)
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

IBGE_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
IBGE_PESQUISAS = "https://servicodados.ibge.gov.br/api/v1/pesquisas/indicadores"
QUERIDO_DIARIO = "https://queridodiario.ok.org.br/api/gazettes"

# IBGE MUNIC indicators relacionados à governança política
# 47 = Plano Diretor, 77 = Conselho Municipal de Saúde, 78 = Conselho de Educação
INDICADORES_GOVERNANCA = [47, 77, 78]


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


async def _fetch_indicador(client: httpx.AsyncClient, indicador_id: int, ibge6: str) -> dict:
    """Busca um indicador IBGE MUNIC para o município."""
    try:
        r = await client.get(
            f"{IBGE_PESQUISAS}/{indicador_id}/resultados/{ibge6}",
            headers={"Accept": "application/json"},
        )
        if r.status_code != 200:
            return {}
        data = r.json()
        res = data[0]["res"][0]["res"]
        if not res:
            return {}
        ultimo_ano = sorted(res.keys())[-1]
        return {"indicador": indicador_id, "ano": ultimo_ano, "valor": res[ultimo_ano]}
    except Exception:
        return {}


def _tse_link(municipio_nome: str, uf: str) -> str:
    """Gera link para o TSE com resultado de 2024."""
    return (
        f"https://resultados.tse.jus.br/oficial/app/index.html"
        f"#/eleicao;e=e619/uf={uf.upper()}"
    )


@router.get("/{ibge}")
async def eleicoes_municipio(ibge: str):
    try:
        _validar_ibge(ibge)
        ibge6 = ibge[:6]

        async with httpx.AsyncClient(timeout=20) as client:
            municipio_response = await client.get(
                f"{IBGE_LOCALIDADES}/{ibge}",
                headers={"Accept": "application/json"},
            )
            if municipio_response.status_code != 200:
                return {
                    "disponivel": False,
                    "erro": f"Município não encontrado ({municipio_response.status_code})",
                    "fonte": "IBGE",
                }

            municipio = municipio_response.json()
            nome = municipio.get("nome", "")
            uf = (
                municipio
                .get("microrregiao", {})
                .get("mesorregiao", {})
                .get("UF", {})
                .get("sigla", "")
            )

            # Indicadores de governança municipal (IBGE MUNIC)
            import asyncio
            indicadores_raw = await asyncio.gather(
                _fetch_indicador(client, 47, ibge6),   # Plano Diretor
                _fetch_indicador(client, 77, ibge6),   # Conselho Saúde
                _fetch_indicador(client, 78, ibge6),   # Conselho Educação
            )

            # Querido Diário — Diário Oficial
            diario_disponivel = False
            try:
                dr = await client.get(
                    QUERIDO_DIARIO,
                    params={"territory_id": ibge, "is_extra_edition": "false", "size": 1},
                    headers={"Accept": "application/json"},
                )
                if dr.status_code == 200 and "application/json" in dr.headers.get("content-type", ""):
                    payload = dr.json()
                    diario_disponivel = bool(payload.get("count"))
            except Exception:
                pass

        # Parse indicadores
        governanca = {}
        labels = {
            47: "plano_diretor",
            77: "conselho_saude",
            78: "conselho_educacao",
        }
        for ind in indicadores_raw:
            if ind and ind.get("indicador"):
                chave = labels.get(ind["indicador"], str(ind["indicador"]))
                governanca[chave] = {
                    "valor": ind["valor"],
                    "ano": ind["ano"],
                }

        tse_url = _tse_link(nome, uf)

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "municipio": nome,
            "uf": uf,
            "eleicao_ano": 2024,
            "tse_resultado_url": tse_url,
            "governanca_municipal": governanca,
            "diario_oficial_disponivel": diario_disponivel,
            "fontes": {
                "eleicoes": "TSE — Tribunal Superior Eleitoral",
                "governanca": "IBGE — Pesquisa de Informações Básicas Municipais (MUNIC)",
                "diario": "Querido Diário / Open Knowledge Brasil",
            },
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "TSE / IBGE"}
