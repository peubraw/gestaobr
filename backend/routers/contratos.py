"""
Contratos e licitações via Portal da Transparência (CGU).
"""
import httpx
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

PORTAL_TRANSP = "https://api.portaldatransparencia.gov.br/api-de-dados"


def _headers():
    # API pública, não requer autenticação para dados básicos
    return {"Accept": "application/json"}


@router.get("/{codigo_ibge}")
async def contratos_municipio(
    codigo_ibge: str,
    pagina: int = 1,
    ano: Optional[int] = None,
):
    """
    Retorna contratos firmados com o governo federal no município.
    Dados do Portal da Transparência (CGU).
    """
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            params = {
                "codigoMunicipioIbge": codigo_ibge,
                "pagina": pagina,
            }
            if ano:
                params["dataInicioVigencia"] = f"{ano}-01-01"
                params["dataFimVigencia"] = f"{ano}-12-31"

            r = await client.get(
                f"{PORTAL_TRANSP}/contratos",
                params=params,
                headers=_headers(),
            )
            if r.status_code == 200:
                return {
                    "codigo_ibge": codigo_ibge,
                    "pagina": pagina,
                    "disponivel": True,
                    "dados": r.json(),
                    "fonte": "Portal da Transparência — CGU",
                }
            return {
                "codigo_ibge": codigo_ibge,
                "disponivel": False,
                "status_code": r.status_code,
            }
        except Exception as e:
            return {"codigo_ibge": codigo_ibge, "disponivel": False, "erro": str(e)}


@router.get("/licitacoes/{codigo_ibge}")
async def licitacoes_municipio(codigo_ibge: str, pagina: int = 1):
    """Licitações federais no município."""
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.get(
                f"{PORTAL_TRANSP}/licitacoes",
                params={"codigoMunicipioIbge": codigo_ibge, "pagina": pagina},
                headers=_headers(),
            )
            if r.status_code == 200:
                return {"disponivel": True, "dados": r.json()}
            return {"disponivel": False}
        except Exception:
            return {"disponivel": False}
