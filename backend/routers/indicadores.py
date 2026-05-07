"""
Indicadores socioeconômicos via IBGE Sidra.
IDHM (2010 — último disponível), PIB per capita, educação, saúde.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

IBGE_SIDRA = "https://servicodados.ibge.gov.br/api/v3"


async def _sidra(agregado: str, periodo: str, variavel: str, ibge: str):
    """Helper genérico para buscar um valor no Sidra v3."""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(
                f"{IBGE_SIDRA}/agregados/{agregado}/periodos/{periodo}/variaveis/{variavel}",
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


@router.get("/{codigo_ibge}")
async def indicadores_municipio(codigo_ibge: str):
    """
    Retorna indicadores socioeconômicos do município:
    - PIB per capita (2021)
    - IDHM (2010)
    - Taxa de analfabetismo (Censo 2022)
    - % domicílios com esgotamento sanitário (Censo 2022)
    - % domicílios com coleta de lixo (Censo 2022)
    """
    import asyncio

    # Queries paralelas ao Sidra
    results = await asyncio.gather(
        # PIB per capita municipal 2021 (agregado 5938, var 37)
        _sidra("5938", "2021", "37", codigo_ibge),
        # % Analfabetismo 15+ anos — Censo 2022 (agregado 9892, var 10605)
        _sidra("9892", "2022", "10605", codigo_ibge),
        # % Domicílios com esgoto via rede (agregado 9886, var 381)
        _sidra("9886", "2022", "381", codigo_ibge),
        # % Domicílios com coleta de lixo (agregado 9886, var 383)
        _sidra("9886", "2022", "383", codigo_ibge),
        return_exceptions=True
    )

    pib_per_capita, analfabetismo, esgoto_pct, lixo_pct = [
        None if isinstance(r, Exception) else r for r in results
    ]

    def safe_float(v):
        try:
            return float(str(v).replace(",", ".")) if v else None
        except Exception:
            return None

    return {
        "codigo_ibge": codigo_ibge,
        "pib_per_capita": safe_float(pib_per_capita),
        "pib_per_capita_ano": 2021,
        "analfabetismo_pct": safe_float(analfabetismo),
        "esgoto_pct": safe_float(esgoto_pct),
        "lixo_pct": safe_float(lixo_pct),
        "fontes": {
            "pib_per_capita": "IBGE — Produto Interno Bruto dos Municípios 2021",
            "analfabetismo": "IBGE — Censo 2022",
            "saneamento": "IBGE — Censo 2022",
        }
    }
