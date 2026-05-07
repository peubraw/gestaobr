"""
Contratos da União via PNCP (Portal Nacional de Contratações Públicas).
Substitui Portal da Transparência que bloqueia requests de servidores (403).
"""
import httpx
from fastapi import APIRouter, Query

router = APIRouter()

PNCP_SEARCH = "https://pncp.gov.br/api/search/"
PNCP_BASE = "https://pncp.gov.br"


def _parse_contrato(item: dict) -> dict:
    return {
        "numero": item.get("title") or item.get("id"),
        "objeto": item.get("description") or "—",
        "orgao": item.get("orgao_nome") or "—",
        "ano": item.get("ano"),
        "data_publicacao": (item.get("createdAt") or "")[:10],
        "valorInicialCompra": item.get("valor"),
        "url": f"{PNCP_BASE}{item['item_url']}" if item.get("item_url") else None,
        "fornecedor": {"nome": item.get("fornecedor_nome") or "—"},
        "objetoContrato": item.get("description"),
    }


@router.get("/{codigo_ibge}")
async def contratos_municipio(codigo_ibge: str, pagina: int = 1):
    """
    Retorna contratos da União firmados no município via PNCP.
    """
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.get(
                PNCP_SEARCH,
                params={
                    "status": "publicado",
                    "tipos_documento": "contrato",
                    "municipio_ibge": codigo_ibge,
                    "pagina": pagina,
                    "tam_pagina": 8,
                },
                headers={"Accept": "application/json"},
            )

            if r.status_code != 200:
                return {"codigo_ibge": codigo_ibge, "disponivel": False, "status_code": r.status_code}

            payload = r.json()
            itens = payload.get("items", []) if isinstance(payload, dict) else []
            total = payload.get("total", len(itens)) if isinstance(payload, dict) else len(itens)

            return {
                "codigo_ibge": codigo_ibge,
                "disponivel": True,
                "total": total,
                "dados": [_parse_contrato(i) for i in itens],
                "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
            }
        except Exception as e:
            return {"codigo_ibge": codigo_ibge, "disponivel": False, "erro": str(e)}
