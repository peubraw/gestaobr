"""
Diário oficial municipal via Querido Diário.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

QUERIDO_DIARIO = "https://queridodiario.ok.org.br/api/gazettes"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def diario_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                QUERIDO_DIARIO,
                params={"territory_id": ibge, "is_extra_edition": "false", "size": 5},
                headers={"Accept": "application/json"},
            )

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar Querido Diário ({response.status_code})",
                "fonte": "Querido Diário / OKBR",
            }

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return {
                "disponivel": False,
                "erro": "API do Querido Diário retornou HTML em vez de JSON (serviço temporariamente indisponível)",
                "link_portal": f"https://queridodiario.ok.org.br/diarios?territory_id={ibge}",
                "fonte": "Querido Diário / Open Knowledge Brasil",
            }

        payload = response.json()
        gazettes = payload.get("results") or payload.get("gazettes") or []

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total_edicoes": payload.get("count") or len(gazettes),
            "edicoes_recentes": [
                {
                    "date": item.get("publication_date") or item.get("date"),
                    "url": item.get("url"),
                    "edition_number": item.get("edition_number") or item.get("edition") or item.get("extrato"),
                }
                for item in gazettes[:5]
            ],
            "fonte": "Querido Diário / Open Knowledge Brasil",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "Querido Diário / OKBR"}
