"""
Vereadores e câmara municipal.
O número de vereadores é determinado por faixas populacionais definidas pelo
Supremo Tribunal Federal (RE 197.917) e legislação municipal brasileira.
Não existe API nacional unificada com dados individuais de vereadores municipais.
"""
from fastapi import APIRouter

router = APIRouter()


def _n_vereadores_por_populacao(pop: int | None) -> int | None:
    """
    Calcula o número mínimo de vereadores conforme faixas populacionais (STF RE 197.917).
    Retorna None se a população for desconhecida.
    """
    if not pop or pop <= 0:
        return None
    tabela = [
        (15_000, 9),
        (30_000, 11),
        (50_000, 13),
        (80_000, 15),
        (120_000, 17),
        (160_000, 19),
        (300_000, 21),
        (450_000, 23),
        (600_000, 25),
        (750_000, 27),
        (900_000, 29),
        (1_050_000, 31),
        (1_200_000, 33),
        (1_350_000, 35),
        (1_500_000, 37),
        (1_800_000, 39),
        (2_400_000, 41),
        (3_000_000, 43),
        (4_000_000, 45),
        (5_000_000, 47),
        (6_000_000, 49),
        (7_000_000, 51),
        (8_000_000, 53),
        (float("inf"), 55),
    ]
    for limite, n in tabela:
        if pop <= limite:
            return n
    return 55


@router.get("/{codigo_ibge}")
async def vereadores_municipio(codigo_ibge: str):
    """
    Retorna o número de vereadores calculado conforme lei brasileira (STF RE 197.917).
    Dados individuais de vereadores não estão disponíveis via API nacional.
    """
    import httpx

    # Busca população para calcular o número de vagas
    populacao = None
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(
                "https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93",
                params={"localidades": f"N6[{codigo_ibge}]"}
            )
            if r.status_code == 200:
                data = r.json()
                val = list(data[0]["resultados"][0]["series"][0]["serie"].values())[-1]
                if val and val not in ("-", "..."):
                    populacao = int(float(str(val).replace(",", ".")))
        except Exception:
            pass

    n_vereadores = _n_vereadores_por_populacao(populacao)

    return {
        "codigo_ibge": codigo_ibge,
        "disponivel": n_vereadores is not None,
        "n_vereadores": n_vereadores,
        "populacao": populacao,
        "fonte": "Cálculo conforme STF RE 197.917 — faixas populacionais (Censo 2022)",
        "aviso": (
            "Número de vagas calculado por faixa populacional (lei brasileira). "
            "Dados individuais não disponíveis via API nacional."
        ) if n_vereadores else "População não encontrada para calcular vagas.",
    }
