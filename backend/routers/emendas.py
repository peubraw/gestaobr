"""
Finanças municipais via SICONFI (Tesouro Nacional) — RREO Anexo 01 (receitas).
Substitui emendas do Portal da Transparência, que bloqueia requests de servidor.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

SICONFI_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"

CONTAS_RELEVANTES = {
    "ReceitasExcetoIntraOrcamentarias",
    "ReceitasTributarias",
    "ReceitasTransferencias",
    "ReceitasTransferenciasUniao",
    "ReceitasTransferenciasEstados",
    "ReceitasCapital",
    "ReceitasCorrentes",
}


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _to_float(valor: object) -> float | None:
    try:
        if valor in (None, "", "-"):
            return None
        return float(str(valor).replace(",", "."))
    except Exception:
        return None


@router.get("/{ibge}")
async def emendas_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        params = {
            "an_exercicio": 2023,
            "in_periodicidade": "B",
            "nr_periodo": 6,
            "co_tipo_demonstrativo": "RREO",
            "no_anexo": "RREO-Anexo 01",
            "co_esfera": "M",
            "co_poder": "E",
            "id_ente": ibge,
        }

        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.get(
                SICONFI_URL,
                params=params,
                headers={"Accept": "application/json"},
            )

        if response.status_code != 200:
            return {
                "disponivel": False,
                "erro": f"Falha ao consultar SICONFI ({response.status_code})",
                "fonte": "SICONFI — Tesouro Nacional",
            }

        payload = response.json()
        items = payload.get("items", [])

        if not items:
            return {
                "disponivel": False,
                "erro": "Sem dados disponíveis para este município no SICONFI",
                "fonte": "SICONFI — Tesouro Nacional",
            }

        meta = items[0]
        populacao = meta.get("populacao")
        municipio = meta.get("instituicao", "")
        uf = meta.get("uf", "")
        exercicio = meta.get("exercicio", 2023)

        # Filter: realized revenues (coluna = RECEITAS REALIZADAS)
        realizadas = [i for i in items if i.get("coluna") == "RECEITAS REALIZADAS"]

        resumo: list[dict] = []
        receita_total: float | None = None

        for item in realizadas:
            cod = item.get("cod_conta", "")
            valor = _to_float(item.get("valor"))
            conta = str(item.get("conta", "")).strip()

            if cod == "ReceitasExcetoIntraOrcamentarias":
                receita_total = valor

            if cod in CONTAS_RELEVANTES and valor is not None:
                resumo.append({
                    "conta": conta,
                    "cod": cod,
                    "valor": valor,
                })

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "municipio": municipio,
            "uf": uf,
            "exercicio": exercicio,
            "populacao": populacao,
            "receita_total_realizada": receita_total,
            "receita_per_capita": round(receita_total / populacao, 2) if receita_total and populacao else None,
            "resumo_receitas": resumo[:8],
            "fonte": "SICONFI — Tesouro Nacional (RREO Anexo 01)",
        }
    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "SICONFI — Tesouro Nacional"}
