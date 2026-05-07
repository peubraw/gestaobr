"""
Orçamento municipal via SICONFI (Tesouro Nacional).
Retorna receitas e despesas da LOA executada.
"""
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()

# API do Sistema de Informações Contábeis e Fiscais (SICONFI/STN)
SICONFI = "https://apidatalake.tesouro.fazenda.gov.br/ords/siconfi/tt"


@router.get("/{codigo_ibge}")
async def orcamento_municipio(codigo_ibge: str, ano: int = 2023):
    """
    Retorna dados de execução orçamentária municipal via SICONFI.
    Inclui receitas realizadas e despesas empenhadas.
    """
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            # Declarações de Contas Anuais — DCA (municípios)
            r = await client.get(
                f"{SICONFI}/rreo",
                params={
                    "an_exercicio": ano,
                    "in_periodicidade": "A",
                    "nr_periodo": 6,
                    "co_tipo_demonstrativo": "RREO",
                    "co_esfera": "M",
                    "co_municipio": codigo_ibge,
                }
            )
            if r.status_code != 200:
                return {"codigo_ibge": codigo_ibge, "ano": ano, "disponivel": False, "dados": None}

            data = r.json()
            items = data.get("items", [])
            if not items:
                return {"codigo_ibge": codigo_ibge, "ano": ano, "disponivel": False, "dados": None}

            # Filtra receita corrente líquida e despesa total
            receitas = [i for i in items if "RECEITA" in str(i.get("no_conta", "")).upper()]
            despesas = [i for i in items if "DESPESA" in str(i.get("no_conta", "")).upper()]

            return {
                "codigo_ibge": codigo_ibge,
                "ano": ano,
                "disponivel": True,
                "resumo": items[:20],  # top 20 linhas do demonstrativo
                "fonte": "SICONFI — Secretaria do Tesouro Nacional",
            }
        except Exception as e:
            return {"codigo_ibge": codigo_ibge, "ano": ano, "disponivel": False, "erro": str(e)}


@router.get("/fpm/{codigo_ibge}")
async def fpm_municipio(codigo_ibge: str):
    """
    Retorna dados de FPM (Fundo de Participação dos Municípios) via STN.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(
                f"{SICONFI}/municipios_fpm",
                params={"co_municipio": codigo_ibge}
            )
            if r.status_code != 200:
                return {"disponivel": False}
            return r.json()
        except Exception:
            return {"disponivel": False}
