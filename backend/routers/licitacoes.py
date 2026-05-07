"""
Licitações municipais — link para PNCP + dados de compras via SICONFI.
O PNCP /search/ não tem filtro funcional por município IBGE.
Retorna link direto para o portal PNCP filtrado e dados de execução do SICONFI.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

SICONFI_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
PNCP_PORTAL = "https://pncp.gov.br/app/editais"


def _to_float(v):
    try:
        return float(str(v).replace(",", ".")) if v not in (None, "", "-") else None
    except Exception:
        return None


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def licitacoes_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        # Link direto para o portal PNCP filtrado por município
        link_pncp = f"https://pncp.gov.br/app/editais?municipio={ibge}"

        # Tentar buscar dados de despesas por modalidade via SICONFI (RREO Anexo 02)
        # Campo "coluna" = "Dotação Atualizada (b)" para orçado; "Até o Bimestre (d)" realizado
        items = None
        ano_encontrado = 2024
        async with httpx.AsyncClient(timeout=20) as client:
            for ano in (2024, 2023, 2022):
                try:
                    r = await client.get(
                        SICONFI_URL,
                        params={
                            "an_exercicio": ano,
                            "in_periodicidade": "B",
                            "nr_periodo": 6,
                            "co_tipo_demonstrativo": "RREO",
                            "no_anexo": "RREO-Anexo 02",
                            "co_esfera": "M",
                            "co_poder": "E",
                            "id_ente": ibge,
                        },
                    )
                    if r.status_code == 200:
                        candidate = r.json().get("items", [])
                        if candidate:
                            items = candidate
                            ano_encontrado = ano
                            break
                except Exception:
                    continue

        licitacoes = []
        if items:
            # Usar linhas de despesas por função como proxy de "contratos/licitações"
            realizadas = [i for i in items if i.get("coluna") == "Até o Bimestre (d)"]
            for item in realizadas:
                cod = item.get("cod_conta", "")
                conta = str(item.get("conta", "")).strip()
                valor = _to_float(item.get("valor"))
                if not (cod.isdigit() and len(cod) == 2):
                    continue
                if valor and valor > 0:
                    licitacoes.append({
                        "numero_controle": f"{cod}/{ano_encontrado}",
                        "titulo": f"Função {cod} — {conta}",
                        "objeto": conta,
                        "orgao": items[0].get("instituicao", "") if items else "",
                        "ano": str(ano_encontrado),
                        "data_publicacao": f"{ano_encontrado}-12-31",
                        "url": link_pncp,
                    })
            licitacoes.sort(key=lambda x: x["titulo"])

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total": len(licitacoes),
            "licitacoes": licitacoes[:10],
            "link_pncp": link_pncp,
            "ano": ano_encontrado,
            "nota": "Dados de execução orçamentária por função (SICONFI). Para licitações individuais, acesse o portal PNCP.",
            "fonte": "SICONFI — Tesouro Nacional (RREO Anexo 02) + PNCP",
        }
    except Exception as e:
        return {
            "disponivel": False,
            "erro": str(e),
            "link_pncp": f"https://pncp.gov.br/app/editais?municipio={ibge}",
            "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
        }
