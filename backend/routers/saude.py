"""
Dados de saúde municipal via CNES / Ministério da Saúde.
A API não filtra por município de forma confiável — buscamos páginas e filtramos localmente.
"""
import asyncio
import httpx
from fastapi import APIRouter

router = APIRouter()

CNES_URL = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
PAGINAS_PARA_BUSCAR = 8
LIMIT_POR_PAGINA = 20


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


async def _buscar_pagina(client: httpx.AsyncClient, offset: int, ibge6: str) -> list[dict]:
    try:
        response = await client.get(
            CNES_URL,
            params={"municipio_codigo": ibge6, "limit": LIMIT_POR_PAGINA, "offset": offset},
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            return []
        payload = response.json()
        return payload.get("estabelecimentos", []) if isinstance(payload, dict) else []
    except Exception:
        return []


@router.get("/{ibge}")
async def saude_municipio(ibge: str):
    try:
        _validar_ibge(ibge)
        ibge6 = ibge[:6]
        codigo_municipio_int = int(ibge6)

        async with httpx.AsyncClient(timeout=30) as client:
            tasks = [
                _buscar_pagina(client, page * LIMIT_POR_PAGINA, ibge6)
                for page in range(PAGINAS_PARA_BUSCAR)
            ]
            resultados = await asyncio.gather(*tasks)

        # Flatten and filter by correct municipio
        todos: list[dict] = []
        for pagina in resultados:
            for item in pagina:
                if item.get("codigo_municipio") == codigo_municipio_int:
                    todos.append(item)

        # Deduplicate by codigo_cnes
        vistos: set[int] = set()
        estabelecimentos: list[dict] = []
        for item in todos:
            cnes = item.get("codigo_cnes")
            if cnes not in vistos:
                vistos.add(cnes)
                estabelecimentos.append(item)

        if not estabelecimentos:
            return {
                "disponivel": False,
                "erro": "Nenhum estabelecimento encontrado para o município",
                "fonte": "CNES / Ministério da Saúde",
            }

        hospitais = 0
        ubs = 0
        laboratorios = 0
        ambulatorios = 0

        for item in estabelecimentos:
            nome = str(item.get("nome_fantasia") or item.get("nome_razao_social") or "").upper()
            tipo = str(item.get("codigo_tipo_unidade") or "")
            possui_hosp = item.get("estabelecimento_possui_atendimento_hospitalar") == 1

            if possui_hosp or "HOSP" in nome:
                hospitais += 1
            if tipo in ("2", "61") or "UBS" in nome or "UNIDADE BASICA" in nome or "UNIDADE BÁSICA" in nome:
                ubs += 1
            if "LAB" in nome or "LABORATORIO" in nome or "LABORATÓRIO" in nome:
                laboratorios += 1
            if item.get("estabelecimento_faz_atendimento_ambulatorial_sus") == "SIM":
                ambulatorios += 1

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total_estabelecimentos": len(estabelecimentos),
            "hospitais": hospitais,
            "ubs": ubs,
            "laboratorios": laboratorios,
            "ambulatorios_sus": ambulatorios,
            "fonte": "CNES / Ministério da Saúde",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "CNES / Ministério da Saúde"}
