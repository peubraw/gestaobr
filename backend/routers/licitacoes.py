"""
Licitações municipais via PNCP.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

PNCP_URL = "https://pncp.gov.br/api/pncp/v1/contratacoes/publicacao"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _to_list(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for chave in ("data", "items", "content", "resultado", "resultados"):
            valor = payload.get(chave)
            if isinstance(valor, list):
                return valor
    return []


@router.get("/{ibge}")
async def licitacoes_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                PNCP_URL,
                params={"codigoMunicipio": ibge, "pagina": 1, "tamanhoPagina": 10},
                headers={"Accept": "application/json"},
            )

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar PNCP ({response.status_code})",
                "fonte": "PNCP",
            }

        payload = response.json()
        itens = _to_list(payload)
        licitacoes = []
        for item in itens[:10]:
            licitacoes.append(
                {
                    "numero": item.get("numeroControlePNCP") or item.get("numeroCompra") or item.get("sequencialCompra"),
                    "objeto": item.get("objetoCompra") or item.get("objeto") or item.get("descricao"),
                    "valor_total": item.get("valorTotalEstimado") or item.get("valorTotalHomologado") or item.get("valorTotal"),
                    "situacao": item.get("situacaoCompraNome") or item.get("situacaoCompra") or item.get("status"),
                    "data_publicacao": item.get("dataPublicacaoPncp") or item.get("dataPublicacao") or item.get("dataInclusao"),
                }
            )

        total = payload.get("totalRegistros") if isinstance(payload, dict) else None
        if total is None:
            total = payload.get("total") if isinstance(payload, dict) else None
        if total is None:
            total = len(itens)

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total": total,
            "licitacoes": licitacoes,
            "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "PNCP"}
