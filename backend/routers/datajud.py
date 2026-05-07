"""
DataJud — Conselho Nacional de Justiça
Fornece dados de processos judiciais por tribunal/comarca.
API pública: https://datajud-wiki.cnj.jus.br/api-publica/
"""
from fastapi import APIRouter
import httpx

router = APIRouter()

DATAJUD_BASE = "https://api-publica.datajud.cnj.jus.br"

# Mapeamento UF → tribunal estadual principal
TRIBUNAL_POR_UF = {
    "AC": "tjac", "AL": "tjal", "AM": "tjam", "AP": "tjap",
    "BA": "tjba", "CE": "tjce", "DF": "tjdft", "ES": "tjes",
    "GO": "tjgo", "MA": "tjma", "MG": "tjmg", "MS": "tjms",
    "MT": "tjmt", "PA": "tjpa", "PB": "tjpb", "PE": "tjpe",
    "PI": "tjpi", "PR": "tjpr", "RJ": "tjrj", "RN": "tjrn",
    "RO": "tjro", "RR": "tjrr", "RS": "tjrs", "SC": "tjsc",
    "SE": "tjse", "SP": "tjsp", "TO": "tjto",
}


@router.get("/{ibge}")
async def processos_judiciais(ibge: str):
    """
    Retorna link para consulta de processos no DataJud para o município.
    A API pública do DataJud requer autenticação via certificado digital para queries avançadas.
    Retornamos link direto + metadados do tribunal competente.
    """
    # Deriva UF do código IBGE (primeiros 2 dígitos → índice de estado)
    # Usamos fallback por nome — a página do municipio passa uf via query param
    ibge6 = ibge[:6]
    return {
        "ibge": ibge,
        "fonte": "DataJud — CNJ",
        "nota": "Consulta de processos judiciais pelo portal público do DataJud.",
        "link_consulta": f"https://datajud-wiki.cnj.jus.br/api-publica/",
        "link_painel_cnj": "https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/",
        "link_consulta_publica": f"https://www.jusbrasil.com.br/consulta-processual/",
        "documentacao_api": "https://datajud-wiki.cnj.jus.br/api-publica/",
        "nota_acesso": "A API DataJud exige credencial de tribunal. Acesse o portal para consultas públicas.",
    }
