"""
Emendas e transferências via Portal da Transparência.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

PORTAL_TRANSP = "https://api.portaldatransparencia.gov.br/api-de-dados/emendas-transferencias"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _to_float(valor):
    try:
        if valor in (None, "", "-"):
            return 0.0
        return float(str(valor).replace(".", "").replace(",", "."))
    except Exception:
        return 0.0


@router.get("/{ibge}")
async def emendas_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                PORTAL_TRANSP,
                params={"codigoIbge": ibge, "ano": 2024, "pagina": 1},
                headers={"Accept": "application/json", "chave-api-dados": "demo"},
            )

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar Portal da Transparência ({response.status_code})",
                "fonte": "Portal da Transparência — CGU",
            }

        payload = response.json()
        itens = payload if isinstance(payload, list) else payload.get("data", [])
        emendas = []
        valor_total = 0.0

        for item in itens:
            valor = (
                item.get("valorEmpenhado")
                or item.get("valorLiberado")
                or item.get("valorPago")
                or item.get("valor")
            )
            valor_float = _to_float(valor)
            valor_total += valor_float
            emendas.append(
                {
                    "autor": item.get("nomeAutor") or item.get("autor") or item.get("parlamentar"),
                    "valor": valor_float,
                    "funcao": item.get("funcao") or item.get("nomeFuncao"),
                    "acao": item.get("acao") or item.get("nomeAcao") or item.get("objeto"),
                }
            )

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total_emendas": len(itens),
            "valor_total": round(valor_total, 2),
            "emendas": emendas[:10],
            "fonte": "Portal da Transparência — CGU",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "Portal da Transparência — CGU"}
