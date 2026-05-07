"""
Indicadores de segurança pública com dados abertos do IBGE/SIDRA.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

SIDRA_VALUES = "https://apisidra.ibge.gov.br/values"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _parse_float(valor):
    try:
        if valor in (None, "", "-"):
            return None
        return float(str(valor).replace(",", "."))
    except Exception:
        return None


@router.get("/{ibge}")
async def seguranca_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{SIDRA_VALUES}/t/899/n3/{ibge[:2]}/v/134/p/2012/c79/0",
                params={"formato": "json"},
                headers={"Accept": "application/json"},
            )

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar SIDRA ({response.status_code})",
                "fonte": "IBGE SIDRA - tabela 899",
            }

        data = response.json()
        linha = data[1] if isinstance(data, list) and len(data) > 1 else {}
        taxa = _parse_float(linha.get("V"))

        return {
            "disponivel": taxa is not None,
            "codigo_ibge": ibge,
            "taxa_homicidios_100k": taxa,
            "ano": 2012,
            "recorte": "UF do município",
            "fonte": "IBGE SIDRA - tabela 899 (coeficiente de mortalidade por homicídios)",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "IBGE SIDRA - tabela 899"}
