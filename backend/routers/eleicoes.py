"""
Informações eleitorais municipais com apoio de APIs públicas abertas.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

IBGE_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
QUERIDO_DIARIO = "https://queridodiario.ok.org.br/api/gazettes"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def eleicoes_municipio(ibge: str):
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
                    "fonte": "TSE / IBGE",
                }

            diario_response = await client.get(
                QUERIDO_DIARIO,
                params={"territory_id": ibge, "is_extra_edition": "false", "size": 1},
                headers={"Accept": "application/json"},
            )

        municipio = municipio_response.json()
        diario_payload = diario_response.json() if diario_response.status_code == 200 else {}
        total_diarios = diario_payload.get("count") or diario_payload.get("total") or 0

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "municipio": municipio.get("nome"),
            "uf": municipio.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("sigla"),
            "eleicao_ano": 2024,
            "fonte": "TSE",
            "aviso": "Dados detalhados disponíveis no portal oficial do TSE.",
            "diario_oficial_disponivel": bool(total_diarios),
            "fonte_auxiliar": "IBGE / Querido Diário",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "TSE / IBGE"}
