"""
Orçamento municipal via SICONFI (Tesouro Nacional).
Retorna receitas realizadas da LOA — RREO Anexo 01.
URL correta: apidatalake.tesouro.gov.br (não fazenda.gov.br).
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

SICONFI = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"


def _to_float(v):
    try:
        return float(str(v).replace(",", ".")) if v not in (None, "", "-") else None
    except Exception:
        return None


async def _buscar_rreo(client: httpx.AsyncClient, ano: int, ibge: str):
    r = await client.get(
        f"{SICONFI}/rreo",
        params={
            "an_exercicio": ano,
            "in_periodicidade": "B",
            "nr_periodo": 6,
            "co_tipo_demonstrativo": "RREO",
            "no_anexo": "RREO-Anexo 01",
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
async def orcamento_municipio(codigo_ibge: str, ano: int = 2024):
    """
    Retorna dados de execução orçamentária municipal via SICONFI (RREO Anexo 01).
    Tenta o ano solicitado e faz fallback para anos anteriores até 2021.
    """
    async with httpx.AsyncClient(timeout=25) as client:
        try:
            items = None
            ano_encontrado = ano
            for tentativa in (ano, ano - 1, ano - 2, 2021):
                items = await _buscar_rreo(client, tentativa, codigo_ibge)
                if items:
                    ano_encontrado = tentativa
                    break

            if not items:
                return {"codigo_ibge": codigo_ibge, "ano": ano, "disponivel": False}

            meta = items[0]
            municipio = meta.get("instituicao", "")

            COLUNA = "Até o Bimestre (c)"
            realizadas = [i for i in items if i.get("coluna") == COLUNA]

            CONTAS = {
                "ReceitasExcetoIntraOrcamentarias",
                "ReceitasCorrentes",
                "ReceitasTributarias",
                "ReceitasTransferencias",
                "ReceitasTransferenciasUniao",
                "ReceitasTransferenciasEstados",
                "ReceitasCapital",
            }

            resumo = []
            receita_total = None
            for item in realizadas:
                cod = item.get("cod_conta", "")
                valor = _to_float(item.get("valor"))
                conta = str(item.get("conta", "")).strip()
                if cod == "ReceitasExcetoIntraOrcamentarias":
                    receita_total = valor
                if cod in CONTAS and valor is not None:
                    resumo.append({
                        "no_conta": conta,
                        "cod_conta": cod,
                        "vl_realizado": valor,
                        "vl_orcado_atualizado": _to_float(
                            next((x.get("valor") for x in items
                                  if x.get("cod_conta") == cod and x.get("coluna") == "PREVISÃO ATUALIZADA"), None)
                        ),
                    })

            return {
                "codigo_ibge": codigo_ibge,
                "ano": ano_encontrado,
                "municipio": municipio,
                "disponivel": True,
                "receita_total": receita_total,
                "resumo": resumo[:10],
                "fonte": "SICONFI — Secretaria do Tesouro Nacional (RREO Anexo 01)",
            }
        except Exception as e:
            return {"codigo_ibge": codigo_ibge, "ano": ano, "disponivel": False, "erro": str(e)}


@router.get("/fpm/{codigo_ibge}")
async def fpm_municipio(codigo_ibge: str):
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(f"{SICONFI}/municipios_fpm", params={"co_municipio": codigo_ibge})
            if r.status_code != 200:
                return {"disponivel": False}
            return r.json()
        except Exception:
            return {"disponivel": False}
