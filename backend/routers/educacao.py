"""
Dados de educação municipal via IBGE Localidades e SIDRA.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

IBGE_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
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
async def educacao_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            municipio_response = await client.get(
                f"{IBGE_LOCALIDADES}/{ibge}",
                headers={"Accept": "application/json"},
            )
            if municipio_response.status_code != 200:
                return {
                    "disponivel": False,
                    "erro": f"Município não encontrado no IBGE ({municipio_response.status_code})",
                    "fonte": "IBGE Localidades / SIDRA",
                }

            escolarizacao_response = await client.get(
                f"{SIDRA_VALUES}/t/10056/n6/{ibge}/v/3795/p/2022/c58/31615/c2/6794/c86/95251",
                params={"formato": "json"},
                headers={"Accept": "application/json"},
            )

        if escolarizacao_response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar SIDRA ({escolarizacao_response.status_code})",
                "fonte": "IBGE SIDRA - tabela 10056",
            }

        data = escolarizacao_response.json()
        linha = data[1] if isinstance(data, list) and len(data) > 1 else {}
        taxa = _parse_float(linha.get("V"))

        return {
            "disponivel": taxa is not None,
            "codigo_ibge": ibge,
            "taxa_escolarizacao": taxa,
            "ano": 2022,
            "fonte": "IBGE SIDRA - tabela 10056 (taxa de frequência escolar bruta, 6 a 14 anos)",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "IBGE Localidades / SIDRA"}
