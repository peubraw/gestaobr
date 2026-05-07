"""
Dados ambientais municipais via IBGE Localidades, Malhas e mapa de biomas.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

IBGE_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
IBGE_MALHAS = "https://servicodados.ibge.gov.br/api/v3/malhas/municipios"
IBGE_BIOMA = "https://mapasinterativos.ibge.gov.br/arcgis/rest/services/BIOMA/MapServer/0/query"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _parse_float(valor):
    try:
        if valor in (None, "", "-"):
            return None
        return float(str(valor).replace(",", "."))
    except Exception:
        return None


@router.get("/{ibge}")
async def meio_ambiente_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            municipio_response = await client.get(
                f"{IBGE_LOCALIDADES}/{ibge}",
                headers={"Accept": "application/json"},
            )
            if municipio_response.status_code != 200:
                return {
                    "disponivel": False,
                    "erro": f"Município não encontrado no IBGE ({municipio_response.status_code})",
                    "fonte": "IBGE",
                }

            metadados_response = await client.get(
                f"{IBGE_MALHAS}/{ibge}/metadados",
                headers={"Accept": "application/json"},
            )

            bioma = None
            area_km2 = None
            if metadados_response.status_code == 200:
                metadados = metadados_response.json()
                if isinstance(metadados, list) and metadados:
                    area_km2 = _parse_float(metadados[0].get("area", {}).get("dimensao"))
                    centroide = metadados[0].get("centroide", {})
                    longitude = centroide.get("longitude")
                    latitude = centroide.get("latitude")
                    if longitude is not None and latitude is not None:
                        bioma_response = await client.get(
                            IBGE_BIOMA,
                            params={
                                "f": "json",
                                "geometry": f"{longitude},{latitude}",
                                "geometryType": "esriGeometryPoint",
                                "inSR": 4674,
                                "spatialRel": "esriSpatialRelIntersects",
                                "outFields": "NOME",
                                "returnGeometry": "false",
                            },
                            headers={"Accept": "application/json"},
                        )
                        if bioma_response.status_code == 200:
                            payload = bioma_response.json()
                            features = payload.get("features") or []
                            if features:
                                bioma = features[0].get("attributes", {}).get("NOME")

        return {
            "disponivel": bioma is not None or area_km2 is not None,
            "codigo_ibge": ibge,
            "bioma": bioma,
            "area_km2": area_km2,
            "fonte": "IBGE Localidades / IBGE Malhas / IBGE Biomas",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "IBGE"}
