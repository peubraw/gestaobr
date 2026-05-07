"""
Indicadores de mortalidade e segurança pública via IBGE SIDRA.
- Tabela 2683: Óbitos registrados (total)
- Tabela 2684: Óbitos registrados por sexo
- Tabela 2685: Óbitos ocorridos (para taxa)
Nota: dados de homicídio por município não estão disponíveis em API pública aberta.
"""
import asyncio
import httpx
from fastapi import APIRouter

router = APIRouter()

SIDRA_VALUES = "https://apisidra.ibge.gov.br/values"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _parse_float(valor: object) -> float | None:
    try:
        if valor in (None, "", "-", "...", "X"):
            return None
        return float(str(valor).replace(",", "."))
    except Exception:
        return None


async def _fetch_sidra(client: httpx.AsyncClient, tabela: str, ibge: str) -> list[dict]:
    """Busca dados de uma tabela SIDRA para o município."""
    try:
        r = await client.get(
            f"{SIDRA_VALUES}/t/{tabela}/n6/{ibge}/v/all/p/last",
            headers={"Accept": "application/json"},
        )
        if r.status_code != 200:
            return []
        data = r.json()
        return data[1:] if isinstance(data, list) and len(data) > 1 else []
    except Exception:
        return []


@router.get("/{ibge}")
async def seguranca_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        async with httpx.AsyncClient(timeout=20) as client:
            rows_2683, rows_2685 = await asyncio.gather(
                _fetch_sidra(client, "2683", ibge),  # óbitos registrados
                _fetch_sidra(client, "2685", ibge),  # óbitos ocorridos (outra metodologia)
            )

        # Tabela 2683 — óbitos registrados totais
        obitos_registrados: float | None = None
        ano_registro: str | None = None
        for row in rows_2683:
            v = _parse_float(row.get("V"))
            d2n = str(row.get("D2N", ""))
            if v is not None and "percentual" not in d2n.lower():
                obitos_registrados = v
                ano_registro = str(row.get("D3N", ""))
                break

        # Tabela 2685 — óbitos ocorridos
        obitos_ocorridos: float | None = None
        ano_ocorrido: str | None = None
        for row in rows_2685:
            v = _parse_float(row.get("V"))
            d2n = str(row.get("D2N", ""))
            if v is not None and "percentual" not in d2n.lower():
                obitos_ocorridos = v
                ano_ocorrido = str(row.get("D3N", ""))
                break

        obitos_principal = obitos_registrados or obitos_ocorridos
        ano_principal = ano_registro or ano_ocorrido

        return {
            "disponivel": obitos_principal is not None,
            "codigo_ibge": ibge,
            "obitos_registrados": obitos_registrados,
            "obitos_ocorridos": obitos_ocorridos,
            "total_obitos": obitos_principal,
            "ano": ano_principal,
            "nota": (
                "Óbitos registrados no município (SIM/IBGE). "
                "Dados de criminalidade por município não disponíveis em API pública."
            ),
            "fonte": "IBGE SIDRA — SIM (Sistema de Informação sobre Mortalidade)",
            "fonte_seguranca": "SINESP/MJ — dados municipais não disponíveis via API aberta",
        }
    except Exception as e:
        return {
            "disponivel": False,
            "erro": str(e),
            "fonte": "IBGE SIDRA — SIM",
        }
