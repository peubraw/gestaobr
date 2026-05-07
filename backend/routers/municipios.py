"""
Municípios router — busca e detalhes via BrasilAPI + IBGE
"""
import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()

BRASIL_API = "https://brasilapi.com.br/api"
IBGE_SIDRA = "https://servicodados.ibge.gov.br/api/v3"
IBGE_V1 = "https://servicodados.ibge.gov.br/api/v1"

# Cache simples em memória para lista de municípios (evita chamar IBGE a cada request)
_municipios_cache: dict = {}

UF_SIGLAS = [
    "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA",
    "MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN",
    "RO","RR","RS","SC","SE","SP","TO"
]


async def _get_municipios_uf(uf: str) -> list:
    """Busca municípios de um estado no BrasilAPI, com cache."""
    if uf in _municipios_cache:
        return _municipios_cache[uf]
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BRASIL_API}/ibge/municipios/v1/{uf}")
        if r.status_code != 200:
            return []
        data = r.json()
        _municipios_cache[uf] = data
        return data


@router.get("/busca")
async def buscar_municipios(q: str = Query(..., min_length=2), uf: Optional[str] = None):
    """Busca municípios por nome (e opcionalmente UF)."""
    ufs = [uf.upper()] if uf else UF_SIGLAS
    resultados = []
    async with httpx.AsyncClient(timeout=20) as client:
        for sigla in ufs:
            if sigla in _municipios_cache:
                municipios = _municipios_cache[sigla]
            else:
                r = await client.get(f"{BRASIL_API}/ibge/municipios/v1/{sigla}")
                municipios = r.json() if r.status_code == 200 else []
                _municipios_cache[sigla] = municipios

            for m in municipios:
                if q.lower() in m["nome"].lower():
                    resultados.append({
                        "nome": m["nome"],
                        "codigo_ibge": m["codigo_ibge"],
                        "uf": sigla,
                    })
    resultados.sort(key=lambda x: x["nome"])
    return resultados[:50]


@router.get("/uf/{uf}")
async def listar_municipios_uf(uf: str):
    """Lista todos os municípios de um estado."""
    municipios = await _get_municipios_uf(uf.upper())
    return [{"nome": m["nome"], "codigo_ibge": m["codigo_ibge"], "uf": uf.upper()} for m in municipios]


@router.get("/{codigo_ibge}")
async def detalhe_municipio(codigo_ibge: str):
    """Retorna dados básicos de um município pelo código IBGE."""
    # UF = primeiros 2 dígitos do código IBGE
    uf_code = codigo_ibge[:2]
    uf_map = {
        "11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
        "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL",
        "28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP",
        "41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"
    }
    uf = uf_map.get(uf_code, "SP")
    municipios = await _get_municipios_uf(uf)
    municipio = next((m for m in municipios if m["codigo_ibge"] == codigo_ibge), None)
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    # Busca população (Censo 2022 tabela 9514, fallback estimativa 6579) e área
    populacao = None
    area_km2 = None
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # População: Censo 2022, tabela 9514, var 93
            r = await client.get(
                f"{IBGE_SIDRA}/agregados/9514/periodos/2022/variaveis/93",
                params={"localidades": f"N6[{codigo_ibge}]"}
            )
            if r.status_code == 200:
                data = r.json()
                series = data[0]["resultados"][0]["series"][0]["serie"]
                val = list(series.values())[-1]
                if val and val not in ("-", "..."):
                    populacao = int(float(str(val).replace(",", ".")))
        except Exception:
            pass

        if not populacao:
            try:
                # Fallback: estimativa anual 6579
                r = await client.get(
                    f"{IBGE_SIDRA}/agregados/6579/periodos/2021/variaveis/9324",
                    params={"localidades": f"N6[{codigo_ibge}]"}
                )
                if r.status_code == 200:
                    data = r.json()
                    series = data[0]["resultados"][0]["series"][0]["serie"]
                    populacao = int(list(series.values())[-1])
            except Exception:
                pass

        try:
            # Área territorial via IBGE localidades API
            r2 = await client.get(
                f"{IBGE_V1}/localidades/municipios/{codigo_ibge}"
            )
            if r2.status_code == 200:
                data2 = r2.json()
                area_raw = data2.get("area")
                if area_raw:
                    area_km2 = float(str(area_raw).replace(",", "."))
        except Exception:
            pass

    return {
        "codigo_ibge": codigo_ibge,
        "nome": municipio["nome"],
        "uf": uf,
        "populacao": populacao,
        "area_km2": area_km2,
        "densidade": round(populacao / area_km2, 1) if populacao and area_km2 else None,
    }
