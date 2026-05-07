"""
Dados de saúde municipal via CNES / Ministério da Saúde.
Usa filtro direto por codigo_tipo_unidade para cada categoria:
- Tipo 2  = Centro de Saúde / UBS
- Tipo 1  = Posto de Saúde
- Tipo 70 = Centro de Apoio à Saúde da Família
- Tipo 71 = UBS Fluvial
- Tipo 5  = Hospital Geral
- Tipo 7  = Hospital Especializado
- Tipo 15 = Unidade Mista
- Tipo 39 = Laboratório / Apoio Diagnóstico
- Tipo 32 = UPA (Unidade de Pronto Atendimento)
"""
import asyncio
import httpx
from fastapi import APIRouter

router = APIRouter()

CNES_URL = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
LIMIT = 200  # Max por request — suficiente para contar totais


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


async def _contar_tipo(client: httpx.AsyncClient, ibge6: str, tipo: int) -> int:
    """Retorna o total de estabelecimentos de um tipo específico."""
    try:
        response = await client.get(
            CNES_URL,
            params={
                "codigo_municipio": ibge6,
                "codigo_tipo_unidade": tipo,
                "limit": LIMIT,
                "offset": 0,
            },
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            return 0
        payload = response.json()
        items = payload.get("estabelecimentos", []) if isinstance(payload, dict) else []
        return len(items)
    except Exception:
        return 0


async def _contar_ambulatorios_sus(client: httpx.AsyncClient, ibge6: str) -> int:
    """Conta estabelecimentos que fazem atendimento ambulatorial SUS (qualquer tipo)."""
    try:
        # Busca página 1 — sem filtro de tipo, mas com SUS = SIM
        response = await client.get(
            CNES_URL,
            params={
                "codigo_municipio": ibge6,
                "estabelecimento_faz_atendimento_ambulatorial_sus": "SIM",
                "limit": LIMIT,
            },
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            return 0
        payload = response.json()
        items = payload.get("estabelecimentos", []) if isinstance(payload, dict) else []
        return len(items)
    except Exception:
        return 0


@router.get("/{ibge}")
async def saude_municipio(ibge: str):
    try:
        _validar_ibge(ibge)
        ibge6 = ibge[:6]

        async with httpx.AsyncClient(timeout=30) as client:
            (
                ubs_cs,      # tipo 2 = Centro de Saúde / UBS
                ubs_posto,   # tipo 1 = Posto de Saúde
                ubs_capsf,   # tipo 70 = Centro de Apoio à Saúde da Família
                ubs_fluvial, # tipo 71 = UBS Fluvial
                hosp_geral,  # tipo 5 = Hospital Geral
                hosp_espec,  # tipo 7 = Hospital Especializado
                hosp_misto,  # tipo 15 = Unidade Mista
                laboratorios,# tipo 39 = Lab / Apoio Diagnóstico
                upa,         # tipo 32 = UPA
                ambulatorios,# atendimento ambulatorial SUS
            ) = await asyncio.gather(
                _contar_tipo(client, ibge6, 2),
                _contar_tipo(client, ibge6, 1),
                _contar_tipo(client, ibge6, 70),
                _contar_tipo(client, ibge6, 71),
                _contar_tipo(client, ibge6, 5),
                _contar_tipo(client, ibge6, 7),
                _contar_tipo(client, ibge6, 15),
                _contar_tipo(client, ibge6, 39),
                _contar_tipo(client, ibge6, 32),
                _contar_ambulatorios_sus(client, ibge6),
            )

        total_ubs = ubs_cs + ubs_posto + ubs_capsf + ubs_fluvial
        total_hospitais = hosp_geral + hosp_espec + hosp_misto

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total_hospitais": total_hospitais,
            "hospitais_gerais": hosp_geral,
            "hospitais_especializados": hosp_espec,
            "unidades_mistas": hosp_misto,
            "total_ubs": total_ubs,
            "ubs_centro_saude": ubs_cs,
            "ubs_postos": ubs_posto,
            "upa": upa,
            "laboratorios": laboratorios,
            "ambulatorios_sus": ambulatorios,
            "fonte": "CNES / Ministério da Saúde",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "CNES / Ministério da Saúde"}
