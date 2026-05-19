"""
Estados router — dados estaduais via IBGE e BrasilAPI
"""
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()

BRASIL_API = "https://brasilapi.com.br/api"
IBGE_V1 = "https://servicodados.ibge.gov.br/api/v1"
IBGE_SIDRA = "https://servicodados.ibge.gov.br/api/v3"

UF_NAMES: dict[str, str] = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
}

CAPITAIS: dict[str, str] = {
    "AC": "Rio Branco", "AL": "Maceió", "AP": "Macapá", "AM": "Manaus",
    "BA": "Salvador", "CE": "Fortaleza", "DF": "Brasília", "ES": "Vitória",
    "GO": "Goiânia", "MA": "São Luís", "MT": "Cuiabá", "MS": "Campo Grande",
    "MG": "Belo Horizonte", "PA": "Belém", "PB": "João Pessoa", "PR": "Curitiba",
    "PE": "Recife", "PI": "Teresina", "RJ": "Rio de Janeiro", "RN": "Natal",
    "RS": "Porto Alegre", "RO": "Porto Velho", "RR": "Boa Vista", "SC": "Florianópolis",
    "SP": "São Paulo", "SE": "Aracaju", "TO": "Palmas",
}

REGIOES: dict[str, str] = {
    "AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte",
    "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MS": "Centro-Oeste", "MT": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

# IBGE numeric IDs para cada UF (usados na API SIDRA)
UF_IBGE_IDS: dict[str, int] = {
    "RO": 11, "AC": 12, "AM": 13, "RR": 14, "PA": 15, "AP": 16, "TO": 17,
    "MA": 21, "PI": 22, "CE": 23, "RN": 24, "PB": 25, "PE": 26, "AL": 27,
    "SE": 28, "BA": 29,
    "MG": 31, "ES": 32, "RJ": 33, "SP": 35,
    "PR": 41, "SC": 42, "RS": 43,
    "MS": 50, "MT": 51, "GO": 52, "DF": 53,
}


@router.get("/{uf}")
async def detalhe_estado(uf: str):
    """Retorna dados de um estado: info básica, municípios e população."""
    uf = uf.upper()
    if uf not in UF_NAMES:
        raise HTTPException(status_code=404, detail="Estado não encontrado")

    municipios_lista: list[dict] = []
    populacao: int | None = None

    async with httpx.AsyncClient(timeout=20) as client:
        # 1. Lista de municípios via BrasilAPI
        try:
            r = await client.get(f"{BRASIL_API}/ibge/municipios/v1/{uf}")
            if r.status_code == 200:
                municipios_lista = r.json()
        except Exception:
            pass

        # 2. População estadual via IBGE SIDRA (tabela 6579, var 9324, 2024)
        estado_id = UF_IBGE_IDS.get(uf)
        if estado_id:
            try:
                r2 = await client.get(
                    f"{IBGE_SIDRA}/agregados/6579/periodos/2024/variaveis/9324",
                    params={"localidades": f"N3[{estado_id}]"},
                )
                if r2.status_code == 200:
                    data = r2.json()
                    series = data[0]["resultados"][0]["series"][0]["serie"]
                    val = list(series.values())[-1]
                    if val and val not in ("-", "..."):
                        populacao = int(val)
            except Exception:
                pass

    municipios_sorted = sorted(municipios_lista, key=lambda m: m.get("nome", ""))

    return {
        "uf": uf,
        "nome": UF_NAMES[uf],
        "capital": CAPITAIS[uf],
        "regiao": REGIOES[uf],
        "n_municipios": len(municipios_sorted),
        "populacao": populacao,
        "municipios": [
            {"nome": m["nome"], "codigo_ibge": m["codigo_ibge"]}
            for m in municipios_sorted
        ],
    }
