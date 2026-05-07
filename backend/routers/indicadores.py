"""
Indicadores socioeconômicos via IBGE.
- PIB per capita: SIDRA v3 agregado 5938 (total PIB Mil R$) ÷ população estimada (tabela 6579)
- Taxa de analfabetismo: apisidra tabela 9941 (Censo 2022) ou tabela 9841 fallback
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


async def _sidra_v3_serie(agregado: str, periodo: str, variavel: str, ibge: str) -> str | None:
    """Helper para SIDRA v3 — retorna valor da série ou None."""
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
            return val if val not in (None, "-", "...") else None
        except Exception:
            return None


async def _apisidra_tabela(tabela: str, ibge: str, variavel_codigo: str) -> str | None:
    """Busca um valor específico via apisidra.ibge.gov.br."""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(
                f"{IBGE_APISIDRA}/t/{tabela}/n6/{ibge}/v/{variavel_codigo}/p/last"
            )
            if r.status_code != 200:
                return None
            data = r.json()
            for item in data[1:]:
                v = item.get("V")
                if v and v not in ("-", "..."):
                    return v
            return None
        except Exception:
            return None


async def _pesquisa_indicador(indicador_id: int, ibge: str) -> str | None:
    """
    Busca via API de pesquisas do IBGE Cidades (indicadores pré-calculados).
    Retorna o valor mais recente disponível.
    """
    localidade = ibge[:6]
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(f"{IBGE_PESQUISAS}/{indicador_id}/resultados/{localidade}")
            if r.status_code != 200:
                return None
            data = r.json()
            res = data[0]["res"][0]["res"]
            if not res:
                return None
            ultimo_ano = sorted(res.keys())[-1]
            return res[ultimo_ano]
        except Exception:
            return None


async def _analfabetismo(ibge6: str) -> float | None:
    """
    Taxa de analfabetismo 15+ anos.
    Tenta tabela 9941 (taxa de analfabetismo direta, Censo 2022), depois tabela 9841
    (taxa de alfabetização — inverte: 100 - alfab).
    """
    # Tabela 9941: taxa de analfabetismo, variável 2690
    v = await _apisidra_tabela("9941", ibge6, "2690")
    if v is not None:
        val = _safe_float(v)
        if val is not None:
            return round(val, 2)

    # Fallback: tabela 9841 = taxa de alfabetização, variável 2513
    v2 = await _apisidra_tabela("9841", ibge6, "2513")
    if v2 is not None:
        alfab = _safe_float(v2)
        if alfab is not None:
            return round(100.0 - alfab, 2)

    return None


async def _populacao(ibge7: str) -> float | None:
    """
    Busca população do município. Tenta:
    1. SIDRA tabela 9514 var 93 (Censo 2022 — melhor cobertura)
    2. SIDRA tabela 6579 var 9324 (estimativa anual)
    """
    import asyncio
    # Tabela 9514: Censo 2022, var 93 = população residente total
    pop_raw = await _sidra_v3_serie("9514", "2022", "93", ibge7)
    pop = _safe_float(pop_raw)
    if pop and pop > 0:
        return pop

    # Fallback: estimativa anual 6579
    for ano in ("2022", "2021", "2020"):
        pop_raw2 = await _sidra_v3_serie("6579", ano, "9324", ibge7)
        pop2 = _safe_float(pop_raw2)
        if pop2 and pop2 > 0:
            return pop2

    return None


async def _pib_per_capita(ibge7: str) -> tuple[float | None, int | None]:
    """
    Calcula PIB per capita = PIB_total (R$ Mil) × 1000 ÷ população.
    - PIB total: SIDRA tabela 5938, variável 37 (Mil Reais)
    - População: tabela 9514 (Censo 2022) ou 6579 (estimativa)
    Busca o último ano disponível entre 2019-2022.
    """
    import asyncio

    pop = await _populacao(ibge7)
    if not pop or pop <= 0:
        return None, None

    for ano in ("2022", "2021", "2020", "2019"):
        pib_raw = await _sidra_v3_serie("5938", ano, "37", ibge7)
        pib = _safe_float(pib_raw)
        if pib and pib > 0:
            per_capita = round((pib * 1000) / pop, 2)
            return per_capita, int(ano)

    return None, None


@router.get("/{codigo_ibge}")
async def indicadores_municipio(codigo_ibge: str):
    """
    Retorna indicadores socioeconômicos do município:
    - PIB per capita (SIDRA 5938 total ÷ população estimada)
    - Taxa de analfabetismo (Censo 2022 via apisidra)
    - % domicílios com esgotamento sanitário (IBGE Cidades indicador 60030)
    - % domicílios com coleta de lixo (IBGE Cidades indicador 60031)
    """
    import asyncio

    ibge6 = codigo_ibge[:6]

    pib_result, analfab_result, esgoto_raw, lixo_raw = await asyncio.gather(
        _pib_per_capita(codigo_ibge),
        _analfabetismo(ibge6),
        _pesquisa_indicador(60030, codigo_ibge),
        _pesquisa_indicador(60031, codigo_ibge),
        return_exceptions=True
    )

    pib_per_capita, pib_ano = pib_result if not isinstance(pib_result, Exception) else (None, None)
    analfabetismo_pct = None if isinstance(analfab_result, Exception) else analfab_result
    esgoto_pct = _safe_float(None if isinstance(esgoto_raw, Exception) else esgoto_raw)
    lixo_pct = _safe_float(None if isinstance(lixo_raw, Exception) else lixo_raw)

    return {
        "codigo_ibge": codigo_ibge,
        "pib_per_capita": pib_per_capita,
        "pib_per_capita_ano": pib_ano,
        "analfabetismo_pct": analfabetismo_pct,
        "esgoto_pct": esgoto_pct,
        "lixo_pct": lixo_pct,
        "fontes": {
            "pib_per_capita": f"IBGE — PIB Municipal {pib_ano or 2021} ÷ Pop. Estimada",
            "analfabetismo": "IBGE — Censo Demográfico 2022",
            "esgoto": "IBGE — Censo Demográfico 2022",
            "lixo": "IBGE — Censo Demográfico 2010",
        }
    }
