"""
ANA — Agência Nacional de Águas e Saneamento Básico
Fornece dados de recursos hídricos, outorgas e qualidade da água.
Portal de dados: https://dadosabertos.ana.gov.br/
"""
from fastapi import APIRouter
import httpx

router = APIRouter()

ANA_DADOSABERTOS = "https://dadosabertos.ana.gov.br/api/3/action"


@router.get("/{ibge}")
async def recursos_hidricos(ibge: str):
    """
    Retorna dados e links sobre recursos hídricos do município via ANA.
    A API REST da ANA (CKAN) não filtra por município IBGE diretamente —
    retornamos links relevantes e dados de referência.
    """
    ibge6 = ibge[:6]

    # Tenta buscar datasets relevantes via CKAN
    datasets = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{ANA_DADOSABERTOS}/package_search",
                params={"q": "município recursos hídricos", "rows": 5},
            )
            if r.status_code == 200:
                result = r.json().get("result", {})
                for ds in result.get("results", []):
                    datasets.append({
                        "titulo": ds.get("title"),
                        "descricao": ds.get("notes", "")[:150],
                        "link": f"https://dadosabertos.ana.gov.br/datasets/{ds.get('name')}",
                    })
    except Exception:
        pass

    return {
        "ibge": ibge,
        "fonte": "ANA — Agência Nacional de Águas",
        "nota": "Dados de recursos hídricos, outorgas e qualidade da água.",
        "links": {
            "portal_dadosabertos": "https://dadosabertos.ana.gov.br/",
            "snirh": "https://snirh.ana.gov.br/",
            "outorgas": "https://www.ana.gov.br/gestao-da-agua/outorga-e-fiscalizacao",
            "qualidade_agua": "https://portalpnqa.ana.gov.br/",
            "sala_situacao": "https://www.ana.gov.br/sala-de-situacao/",
            "sisconapesca": "https://www.ana.gov.br/",
        },
        "datasets_relacionados": datasets,
        "indicadores_referencia": [
            {"indicador": "Índice de Atendimento de Água", "fonte": "SNIS"},
            {"indicador": "Índice de Atendimento de Esgoto", "fonte": "SNIS"},
            {"indicador": "Qualidade da Água Distribuída", "fonte": "SISAGUA/MS"},
        ],
    }
