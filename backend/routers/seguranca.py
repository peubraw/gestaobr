"""
Indicadores de segurança pública — óbitos por causas externas via IBGE SIDRA (tabela 2683).
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

SIDRA_VALUES = "https://apisidra.ibge.gov.br/values"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _parse_float(valor: object) -> float | None:
    try:
        if valor in (None, "", "-", "..."):
            return None
        return float(str(valor).replace(",", "."))
    except Exception:
        return None


@router.get("/{ibge}")
async def seguranca_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        # Tabela 2683: Número de óbitos ocorridos no ano — nível municipal
        url = f"{SIDRA_VALUES}/t/2683/n6/{ibge}/v/all/p/last?formato=json"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers={"Accept": "application/json"})

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar SIDRA ({response.status_code})",
                "fonte": "IBGE SIDRA — tabela 2683 (óbitos municipais)",
            }

        data = response.json()
        # First row is header, rows after contain data
        rows = data[1:] if isinstance(data, list) and len(data) > 1 else []

        obitos_total: float | None = None
        ano: str | None = None
        variaveis: list[dict] = []

        for row in rows:
            v = _parse_float(row.get("V"))
            nome_var = str(row.get("D2N", ""))
            ano_row = str(row.get("D3N", ""))
            if ano is None and ano_row:
                ano = ano_row
            variaveis.append({"variavel": nome_var, "valor": v, "ano": ano_row})
            # Prefer "Número de óbitos" total
            if obitos_total is None and v is not None:
                obitos_total = v

        return {
            "disponivel": obitos_total is not None,
            "codigo_ibge": ibge,
            "obitos_totais": obitos_total,
            "ano": ano,
            "variaveis": variaveis[:5],
            "nota": "Óbitos por todas as causas registradas no município",
            "fonte": "IBGE SIDRA — tabela 2683 (óbitos municipais)",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "IBGE SIDRA — tabela 2683"}
