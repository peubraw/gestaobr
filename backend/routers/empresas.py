"""
Empresas — BrasilAPI CNPJ + Receita Federal
Busca empresas sediadas no município via BrasilAPI.
"""
from fastapi import APIRouter, Query
import httpx

router = APIRouter()

BRASILAPI_BASE = "https://brasilapi.com.br/api"
RECEITAWS_BASE = "https://receitaws.com.br/v1"


@router.get("/{ibge}/cnpj/{cnpj}")
async def buscar_empresa(ibge: str, cnpj: str):
    """Busca dados de empresa pelo CNPJ via BrasilAPI."""
    cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(f"{BRASILAPI_BASE}/cnpj/v1/{cnpj_clean}")
            if r.status_code == 200:
                data = r.json()
                return {
                    "ibge": ibge,
                    "fonte": "BrasilAPI / Receita Federal",
                    "empresa": {
                        "cnpj": data.get("cnpj"),
                        "razao_social": data.get("razao_social"),
                        "nome_fantasia": data.get("nome_fantasia"),
                        "situacao_cadastral": data.get("descricao_situacao_cadastral"),
                        "data_situacao": data.get("data_situacao_cadastral"),
                        "data_abertura": data.get("data_inicio_atividade"),
                        "porte": data.get("descricao_porte"),
                        "natureza_juridica": data.get("natureza_juridica"),
                        "atividade_principal": data.get("cnae_fiscal_descricao"),
                        "municipio": data.get("municipio"),
                        "uf": data.get("uf"),
                        "cep": data.get("cep"),
                        "capital_social": data.get("capital_social"),
                        "socios": data.get("qsa", []),
                    },
                }
        except Exception:
            pass

    return {
        "ibge": ibge,
        "erro": "Não foi possível consultar o CNPJ.",
        "link_receita": f"https://servicos.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Entrada.asp",
    }


@router.get("/{ibge}/resumo")
async def resumo_empresas(ibge: str):
    """
    Retorna links e referências para consulta de empresas no município.
    BrasilAPI não suporta busca por município — apenas por CNPJ individual.
    """
    return {
        "ibge": ibge,
        "fonte": "Receita Federal / BrasilAPI",
        "nota": "Para buscar empresas do município, use o portal da Receita Federal ou o CNPJ específico.",
        "links": {
            "receita_federal": "https://servicos.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Entrada.asp",
            "brasilapi_docs": "https://brasilapi.com.br/docs#tag/CNPJ",
            "cnes_estabelecimentos": f"https://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp",
            "junta_comercial": "https://regin.drei.gov.br/",
        },
        "uso_api": "GET /empresas/{ibge}/cnpj/{cnpj} para consultar empresa específica",
    }
