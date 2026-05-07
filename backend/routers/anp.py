"""
ANP — Agência Nacional do Petróleo, Gás Natural e Biocombustíveis
Fornece preços de combustíveis por município (série histórica pública).
API: https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/series-temporais-de-precos-de-combustiveis
"""
from fastapi import APIRouter
import httpx

router = APIRouter()

ANP_BASE = "https://www.anp.gov.br/anp-cgi/cgb/tabcgi.exe"

COMBUSTIVEIS = [
    {"produto": "Gasolina Comum", "unidade": "R$/litro"},
    {"produto": "Etanol Hidratado", "unidade": "R$/litro"},
    {"produto": "Diesel S10", "unidade": "R$/litro"},
    {"produto": "Diesel Comum", "unidade": "R$/litro"},
    {"produto": "GNV", "unidade": "R$/m³"},
    {"produto": "GLP 13kg", "unidade": "R$/botijão"},
]


@router.get("/{ibge}")
async def precos_combustiveis(ibge: str):
    """
    Retorna preços médios de combustíveis para o município.
    A API pública da ANP não expõe REST JSON por município — usamos link direto
    para o painel de preços e fornecemos referências estáticas dos combustíveis.
    """
    ibge6 = ibge[:6]
    return {
        "ibge": ibge,
        "fonte": "ANP — Agência Nacional do Petróleo",
        "nota": "Consulte os preços atualizados semanalmente no painel oficial da ANP.",
        "link_painel": f"https://preco.anp.gov.br/",
        "link_serie_historica": "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/series-temporais-de-precos-de-combustiveis",
        "link_postos": f"https://preco.anp.gov.br/",
        "combustiveis": COMBUSTIVEIS,
        "referencia": "Dados publicados semanalmente. Para consulta por município acesse o painel ANP.",
    }
