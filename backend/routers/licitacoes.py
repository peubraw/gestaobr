"""
Licitações municipais via PNCP (search endpoint).
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

PNCP_SEARCH_URL = "https://pncp.gov.br/api/search/"
PNCP_BASE = "https://pncp.gov.br"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _parse_item(item: dict) -> dict:
    return {
        "numero_controle": item.get("numero_controle_pncp") or item.get("id"),
        "titulo": item.get("title") or item.get("titulo"),
        "objeto": item.get("description") or item.get("objeto"),
        "orgao": item.get("orgao_nome") or item.get("orgao"),
        "ano": item.get("ano"),
        "data_publicacao": item.get("createdAt") or item.get("data_publicacao"),
        "url": f"{PNCP_BASE}{item['item_url']}" if item.get("item_url") else None,
    }


@router.get("/{ibge}")
async def licitacoes_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                PNCP_SEARCH_URL,
                params={
                    "status": "publicado",
                    "tipos_documento": "edital",
                    "municipio_ibge": ibge,
                    "pagina": 1,
                    "tam_pagina": 10,
                },
                headers={"Accept": "application/json"},
            )

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar PNCP ({response.status_code})",
                "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
            }

        payload = response.json()
        itens = payload.get("items", []) if isinstance(payload, dict) else []
        total = payload.get("total", len(itens)) if isinstance(payload, dict) else len(itens)

        licitacoes = [_parse_item(item) for item in itens[:10]]

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total": total,
            "licitacoes": licitacoes,
            "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "Portal Nacional de Contratações Públicas (PNCP)"}
