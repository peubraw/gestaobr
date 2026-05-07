"""
Indicadores socioeconômicos via IBGE.
- PIB per capita: SIDRA v3 agregado 5938
- Taxa de alfabetização/analfabetismo: apisidra tabela 9841 (Censo 2022)
- Esgotamento sanitário: IBGE pesquisas indicador 60030 (Censo 2022)
- Coleta de lixo: IBGE pesquisas indicador 60031 (Censo 2010 — melhor disponível)
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

IBGE_SIDRA_V3 = "https://servicodados.ibge.gov.br/api/v3"
IBGE_APISIDRA = "https://apisidra.ibge.gov.br/values"
IBGE_PESQUISAS = "https://servicodados.ibge.gov.br/api/v1/pesquisas/indicadores"


def _safe_float(v):
    try:
        return float(str(v).replace(",", ".")) if v and v != "-" else None
    except Exception:
        return None


async def _sidra_v3(agregado: str, periodo: str, variavel: str, ibge: str):
    """Helper para SIDRA v3 (pode retornar 500 para alguns agregados)."""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(
                f"{IBGE_SIDRA_V3}/agregados/{agregado}/periodos/{periodo}/variaveis/{variavel}",
                params={"localidades": f"N6[{ibge}]"}
            )
            if r.status_code != 200:
                return None
            data = r.json()
            series = data[0]["resultados"][0]["series"][0]["serie"]
            val = list(series.values())[-1]
            return val if val != "-" else None
        except Exception:
            return None


async def _apisidra_tabela(tabela: str, ibge: str, variavel_codigo: str) -> str | None:
    """
    Busca um valor específico via apisidra.ibge.gov.br (API alternativa mais estável).
    Filtra pelo código da variável (D2C).
    """
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(
                f"{IBGE_APISIDRA}/t/{tabela}/n6/{ibge}/v/{variavel_codigo}/p/last"
            )
            if r.status_code != 200:
                return None
            data = r.json()
            # data[0] é cabeçalho, data[1+] são resultados
            for item in data[1:]:
                v = item.get("V")
                if v and v != "-":
                    return v
            return None
        except Exception:
            return None


async def _pesquisa_indicador(indicador_id: int, ibge: str) -> str | None:
    """
    Busca via API de pesquisas do IBGE Cidades (indicadores pré-calculados).
    Retorna o valor mais recente disponível.
    """
    # Converte ibge 7 dígitos para 6 (sem dígito verificador)
    localidade = ibge[:6]
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(f"{IBGE_PESQUISAS}/{indicador_id}/resultados/{localidade}")
            if r.status_code != 200:
                return None
            data = r.json()
            res = data[0]["res"][0]["res"]
            # Pega o valor mais recente (última chave ordenada)
            if not res:
                return None
            ultimo_ano = sorted(res.keys())[-1]
            return res[ultimo_ano]
        except Exception:
            return None


@router.get("/{codigo_ibge}")
async def indicadores_municipio(codigo_ibge: str):
    """
    Retorna indicadores socioeconômicos do município:
    - PIB per capita (SIDRA 2021)
    - Taxa de analfabetismo (Censo 2022 via apisidra tabela 9841)
    - % domicílios com esgotamento sanitário (IBGE Cidades indicador 60030, Censo 2022)
    - % domicílios com coleta de lixo (IBGE Cidades indicador 60031)
    """
    import asyncio

    results = await asyncio.gather(
        # PIB per capita municipal 2021 (SIDRA v3)
        _sidra_v3("5938", "2021", "37", codigo_ibge),
        # Taxa de alfabetização 15+ anos — Censo 2022 (apisidra tabela 9841, variável 2513)
        # Analfabetismo = 100 - alfabetização
        _apisidra_tabela("9841", codigo_ibge[:6], "2513"),
        # Esgotamento sanitário % — IBGE Cidades indicador 60030 (Censo 2022)
        _pesquisa_indicador(60030, codigo_ibge),
        # Urbanização de vias (proxy coleta lixo) — indicador 60031 (Censo 2010)
        _pesquisa_indicador(60031, codigo_ibge),
        return_exceptions=True
    )

    pib_per_capita, taxa_alfab, esgoto_pct, lixo_pct = [
        None if isinstance(r, Exception) else r for r in results
    ]

    # Analfabetismo = 100 - alfabetização
    analfabetismo_pct = None
    if taxa_alfab is not None:
        alfab = _safe_float(taxa_alfab)
        if alfab is not None:
            analfabetismo_pct = round(100.0 - alfab, 2)

    return {
        "codigo_ibge": codigo_ibge,
        "pib_per_capita": _safe_float(pib_per_capita),
        "pib_per_capita_ano": 2021,
        "analfabetismo_pct": analfabetismo_pct,
        "esgoto_pct": _safe_float(esgoto_pct),
        "lixo_pct": _safe_float(lixo_pct),
        "fontes": {
            "pib_per_capita": "IBGE — Produto Interno Bruto dos Municípios 2021",
            "analfabetismo": "IBGE — Censo Demográfico 2022",
            "esgoto": "IBGE — Censo Demográfico 2022",
            "lixo": "IBGE — Censo Demográfico 2010",
        }
    }
