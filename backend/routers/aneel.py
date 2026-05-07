"""
ANEEL — Agência Nacional de Energia Elétrica
Fornece dados de distribuidoras, tarifas e qualidade do serviço de energia elétrica.
API ANEEL: https://dadosabertos.aneel.gov.br/
"""
from fastapi import APIRouter
import httpx

router = APIRouter()

ANEEL_DADOS = "https://dadosabertos.aneel.gov.br/api/3/action"

# Mapeamento UF → distribuidoras principais
DISTRIBUIDORAS_UF = {
    "AC": ["Energisa Acre"],
    "AL": ["Equatorial Alagoas"],
    "AM": ["Amazonas Energia"],
    "AP": ["CEA Equatorial"],
    "BA": ["Neoenergia Coelba"],
    "CE": ["Enel Ceará"],
    "DF": ["Neoenergia Brasília"],
    "ES": ["EDP Espírito Santo"],
    "GO": ["Enel Goiás"],
    "MA": ["Equatorial Maranhão"],
    "MG": ["CEMIG"],
    "MS": ["Energisa Mato Grosso do Sul"],
    "MT": ["Energisa Mato Grosso"],
    "PA": ["Equatorial Pará"],
    "PB": ["Energisa Paraíba"],
    "PE": ["Neoenergia Pernambuco"],
    "PI": ["Equatorial Piauí"],
    "PR": ["Copel"],
    "RJ": ["Light", "Enel Rio"],
    "RN": ["Neoenergia Cosern"],
    "RO": ["Energisa Rondônia"],
    "RR": ["Roraima Energia"],
    "RS": ["RGE", "CEEE-D"],
    "SC": ["Celesc"],
    "SE": ["Energisa Sergipe"],
    "SP": ["Enel SP", "CPFL Paulista", "EDP São Paulo"],
    "TO": ["Energisa Tocantins"],
}


@router.get("/{ibge}")
async def energia_eletrica(ibge: str):
    """
    Retorna dados e links sobre energia elétrica no município via ANEEL.
    """
    ibge6 = ibge[:6]

    # Tenta buscar tarifas via API CKAN da ANEEL
    tarifas = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{ANEEL_DADOS}/datastore_search",
                params={
                    "resource_id": "b1bd71e7-d0ad-4214-9053-cbd58e9564a7",  # tarifas homologadas
                    "limit": 5,
                },
            )
            if r.status_code == 200:
                records = r.json().get("result", {}).get("records", [])
                for rec in records[:5]:
                    tarifas.append({
                        "distribuidora": rec.get("SigAgente"),
                        "modalidade": rec.get("DscModalidadeTarifaria"),
                        "subgrupo": rec.get("DscSubGrupo"),
                        "vigencia": rec.get("DatInicioVigencia"),
                    })
    except Exception:
        pass

    return {
        "ibge": ibge,
        "fonte": "ANEEL — Agência Nacional de Energia Elétrica",
        "links": {
            "portal_dadosabertos": "https://dadosabertos.aneel.gov.br/",
            "tarifas": "https://www.aneel.gov.br/tarifas",
            "qualidade_energia": "https://www.aneel.gov.br/indicadores-de-qualidade",
            "reclamacoes": "https://www.aneel.gov.br/ouvidoria",
            "geoambiente": "https://geoambiente.aneel.gov.br/",
            "consulta_distribuidoras": "https://www.aneel.gov.br/agentes-de-distribuicao",
        },
        "tarifas_recentes": tarifas,
        "indicadores_qualidade": [
            {"indicador": "DEC", "descricao": "Duração Equivalente de Interrupção por Unidade Consumidora"},
            {"indicador": "FEC", "descricao": "Frequência Equivalente de Interrupção por Unidade Consumidora"},
        ],
        "nota": "Para tarifas e DEC/FEC específicos do município, consulte o portal ANEEL com o nome da distribuidora.",
    }
