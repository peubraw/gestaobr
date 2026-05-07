"""
Vereadores e câmara municipal.
Dados via Portal da Transparência + IBGE Munic (pesquisa gestão municipal).
Câmaras municipais individuais não têm API nacional unificada —
usamos o que está disponível via dados abertos federais.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

IBGE_SIDRA = "https://servicodados.ibge.gov.br/api/v3"


@router.get("/{codigo_ibge}")
async def vereadores_municipio(codigo_ibge: str):
    """
    Retorna informações sobre a câmara municipal.
    IBGE Munic traz dados estruturais da câmara (número de vereadores, salários, etc.)
    """
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # IBGE Munic — número de vereadores (agregado 9952, var variada)
            # Pesquisa de Informações Básicas Municipais
            r = await client.get(
                f"{IBGE_SIDRA}/agregados/9952/periodos/2023/variaveis/12278",
                params={"localidades": f"N6[{codigo_ibge}]"}
            )
            n_vereadores = None
            if r.status_code == 200:
                data = r.json()
                try:
                    serie = data[0]["resultados"][0]["series"][0]["serie"]
                    val = list(serie.values())[-1]
                    n_vereadores = int(val) if val and val != "-" else None
                except Exception:
                    pass

            return {
                "codigo_ibge": codigo_ibge,
                "n_vereadores": n_vereadores,
                "aviso": (
                    "Dados individuais de vereadores municipais não estão disponíveis "
                    "via API nacional. Consulte o portal de transparência do município."
                ),
                "fonte": "IBGE — Pesquisa de Informações Básicas Municipais (Munic) 2023",
            }
        except Exception as e:
            return {
                "codigo_ibge": codigo_ibge,
                "n_vereadores": None,
                "aviso": "Dados não disponíveis.",
                "erro": str(e),
            }
