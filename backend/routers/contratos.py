"""
Despesas municipais por função via SICONFI (Tesouro Nacional) — RREO Anexo 02.
Substitui contratos do PNCP (que não tem filtro funcional por município).
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

SICONFI_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"

COLUNA_REALIZADA = "Até o Bimestre (d)"


def _to_float(v):
    try:
        return float(str(v).replace(",", ".")) if v not in (None, "", "-") else None
    except Exception:
        return None


async def _buscar_anexo02(client: httpx.AsyncClient, ano: int, ibge: str):
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
    if r.status_code != 200:
        return None
    items = r.json().get("items", [])
    return items if items else None


@router.get("/{codigo_ibge}")
async def contratos_municipio(codigo_ibge: str, pagina: int = 1):
    """
    Retorna execução de despesas municipais por função via SICONFI (RREO Anexo 02).
    """
    async with httpx.AsyncClient(timeout=25) as client:
        try:
            items = None
            ano_encontrado = 2024
            for ano in (2024, 2023, 2022, 2021):
                items = await _buscar_anexo02(client, ano, codigo_ibge)
                if items:
                    ano_encontrado = ano
                    break

            if not items:
                return {
                    "codigo_ibge": codigo_ibge,
                    "disponivel": False,
                    "fonte": "SICONFI — Tesouro Nacional (RREO Anexo 02)",
                }

            meta = items[0]
            municipio = meta.get("instituicao", "")

            realizadas = [i for i in items if i.get("coluna") == COLUNA_REALIZADA]

            # Filtrar apenas funções principais (cod_conta começa com 2 dígitos = função)
            funcoes = []
            despesa_total = None
            for item in realizadas:
                cod = item.get("cod_conta", "")
                conta = str(item.get("conta", "")).strip()
                valor = _to_float(item.get("valor"))
                if valor is None or valor <= 0:
                    continue
                # DespesaTotal é a linha de total
                if cod in ("DespesaExcetoIntraOrcamentaria", "DespesaTotal"):
                    despesa_total = valor
                    continue
                # Funções têm cod_conta numérico de 2 dígitos (ex: "04", "08", "10")
                if cod.isdigit() and len(cod) == 2:
                    funcoes.append({
                        "numero": cod,
                        "objeto": conta,
                        "orgao": municipio,
                        "ano": str(ano_encontrado),
                        "data_publicacao": f"{ano_encontrado}-12-31",
                        "valorInicialCompra": valor,
                        "url": None,
                        "fornecedor": {"nome": "Execução Orçamentária"},
                        "objetoContrato": conta,
                    })

            funcoes.sort(key=lambda x: -(x["valorInicialCompra"] or 0))

            return {
                "codigo_ibge": codigo_ibge,
                "disponivel": True,
                "total": len(funcoes),
                "ano": ano_encontrado,
                "despesa_total": despesa_total,
                "dados": funcoes[:8],
                "tipo": "despesas_por_funcao",
                "fonte": "SICONFI — Tesouro Nacional (RREO Anexo 02 — Despesas por Função)",
            }
        except Exception as e:
            return {"codigo_ibge": codigo_ibge, "disponivel": False, "erro": str(e)}
