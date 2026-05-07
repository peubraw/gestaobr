"""
Dados de saúde municipal via CNES / Ministério da Saúde.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

CNES_URL = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def saude_municipio(ibge: str):
    try:
        _validar_ibge(ibge)
        ibge6 = ibge[:6]

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                CNES_URL,
                params={"municipio_codigo": ibge6, "limit": 20},
                headers={"Accept": "application/json"},
            )

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar CNES ({response.status_code})",
                "fonte": "CNES / Ministério da Saúde",
            }

        payload = response.json()
        estabelecimentos = payload.get("estabelecimentos", payload if isinstance(payload, list) else [])

        hospitais = 0
        ubs = 0
        laboratorios = 0

        for item in estabelecimentos:
            nome = str(item.get("nome_fantasia") or item.get("nome_razao_social") or "").upper()
            tipo = str(item.get("codigo_tipo_unidade") or "")
            if item.get("estabelecimento_possui_atendimento_hospitalar") == 1 or "HOSP" in nome:
                hospitais += 1
            if tipo == "2" or "UBS" in nome or "UNIDADE BASICA" in nome or "UNIDADE BÁSICA" in nome:
                ubs += 1
            if "LAB" in nome or "LABORATORIO" in nome or "LABORATÓRIO" in nome:
                laboratorios += 1

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total_estabelecimentos": len(estabelecimentos),
            "hospitais": hospitais,
            "ubs": ubs,
            "laboratorios": laboratorios,
            "fonte": "CNES / Ministério da Saúde",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "CNES / Ministério da Saúde"}
