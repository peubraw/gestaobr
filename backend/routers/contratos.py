"""
Despesas municipais por função via SICONFI (Tesouro Nacional) — RREO Anexo 02.
Substitui contratos do PNCP (que não tem filtro funcional por município).
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

SICONFI_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"

COLUNA_REALIZADA = "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)"

# Funções orçamentárias principais (conta sem prefixo FU/subfunção)
FUNCOES_PRINCIPAIS = {
    "Legislativa", "Judiciária", "Essencial à Justiça", "Administração",
    "Defesa Nacional", "Segurança Pública", "Relações Exteriores",
    "Assistência Social", "Previdência Social", "Saúde", "Trabalho",
    "Educação", "Cultura", "Direitos da Cidadania", "Urbanismo",
    "Habitação", "Saneamento", "Gestão Ambiental", "Ciência e Tecnologia",
    "Agricultura", "Organização Agrária", "Indústria", "Comércio e Serviços",
    "Comunicações", "Energia", "Transporte", "Desporto e Lazer",
    "Encargos Especiais",
}


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

            # Filtrar funções principais por campo "conta" (cod_conta é sempre 'RREO2TotalDespesas')
            # Usar dicionário para deduplicar: manter maior valor por conta
            funcoes_map: dict = {}
            despesa_total = None
            for item in realizadas:
                conta = str(item.get("conta", "")).strip()
                valor = _to_float(item.get("valor"))
                if valor is None or valor <= 0:
                    continue
                # Linha de total geral (várias formas possíveis na API)
                if "TOTAL" in conta.upper() or "INTRA" in conta.upper():
                    if despesa_total is None or valor > despesa_total:
                        despesa_total = valor
                    continue
                # Aceitar apenas funções da lista principal
                if conta not in FUNCOES_PRINCIPAIS:
                    continue
                # Deduplicar mantendo o maior valor
                if conta not in funcoes_map or valor > funcoes_map[conta]:
                    funcoes_map[conta] = valor

            funcoes = [
                {
                    "numero": "",
                    "objeto": conta,
                    "orgao": municipio,
                    "ano": str(ano_encontrado),
                    "data_publicacao": f"{ano_encontrado}-12-31",
                    "valorInicialCompra": valor,
                    "url": None,
                    "fornecedor": {"nome": "Execução Orçamentária"},
                    "objetoContrato": conta,
                }
                for conta, valor in funcoes_map.items()
            ]

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
