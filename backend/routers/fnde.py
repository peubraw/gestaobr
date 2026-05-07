"""
Repasses do FNDE ao município via API de Repasses Constitucionais.
Cobre: Salário-Educação, PNATE, PNAE (merenda), PDDE, PNLD.
API: https://www.fnde.gov.br/fndesite/index.php/consultas/repasses/historico-de-repasses/api/
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

FNDE_BASE = "https://www.fnde.gov.br/fndesite/index.php/consultas/repasses/historico-de-repasses/api/dados"

PROGRAMAS = [
    {"codigo": "SALARIOEDUC", "nome": "Salário-Educação", "descricao": "Quota municipal do Salário-Educação"},
    {"codigo": "PNAE", "nome": "PNAE (Merenda Escolar)", "descricao": "Programa Nacional de Alimentação Escolar"},
    {"codigo": "PNATE", "nome": "PNATE (Transporte Escolar)", "descricao": "Programa Nacional de Apoio ao Transporte Escolar"},
    {"codigo": "PDDE", "nome": "PDDE (Dinheiro Direto na Escola)", "descricao": "Programa Dinheiro Direto na Escola"},
]


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _ibge6(ibge: str) -> str:
    """FNDE usa código IBGE de 6 dígitos (sem o dígito verificador)."""
    return ibge[:6]


@router.get("/{ibge}")
async def fnde_municipio(ibge: str, ano: int = 2024):
    try:
        _validar_ibge(ibge)
        ibge6 = _ibge6(ibge)
        uf_codigo = ibge[:2]

        repasses = []
        valor_total = 0.0

        async with httpx.AsyncClient(timeout=20) as client:
            # Busca repasses consolidados do município
            try:
                resp = await client.get(
                    FNDE_BASE,
                    params={
                        "anoMesInicio": f"{ano}01",
                        "anoMesFim": f"{ano}12",
                        "codigoUF": uf_codigo,
                        "codigoMunicipio": ibge6,
                    },
                    headers={"Accept": "application/json"},
                )
                if resp.status_code == 200:
                    ct = resp.headers.get("content-type", "")
                    if "json" in ct:
                        data = resp.json()
                        items = data if isinstance(data, list) else data.get("data", data.get("repasses", []))
                        for item in items[:20]:
                            valor = item.get("vlRepasse") or item.get("valor") or item.get("vl_repasse") or 0
                            programa = item.get("noPrograma") or item.get("programa") or item.get("no_programa", "")
                            mes = item.get("nuMes") or item.get("mes") or ""
                            repasses.append({
                                "programa": programa,
                                "mes": mes,
                                "valor": float(valor) if valor else 0,
                            })
                            valor_total += float(valor) if valor else 0
            except Exception:
                pass

        # Fallback: link direto para consulta no portal FNDE
        link_fnde = f"https://www.fnde.gov.br/fndesite/index.php/consultas/repasses/historico-de-repasses?codigoMunicipio={ibge6}&ano={ano}"

        # Monta repasses com links individuais para o frontend
        repasses_com_links = []
        for prog in PROGRAMAS:
            repasses_com_links.append({
                "programa": prog["nome"],
                "descricao": prog["descricao"],
                "link": f"https://www.fnde.gov.br/fndesite/index.php/consultas/repasses/historico-de-repasses?codigoMunicipio={ibge6}&ano={ano}",
            })
        # Se conseguiu dados reais, adiciona valores
        for rep in repasses:
            for rpl in repasses_com_links:
                if rpl["programa"].lower() in (rep.get("programa") or "").lower():
                    rpl["valor_referencia"] = rep.get("valor")
                    break

        return {
            "disponivel": True,
            "ibge": ibge,
            "ano": ano,
            "repasses": repasses_com_links,
            "valor_total_ano": valor_total,
            "total_transferencias": len(repasses),
            "link_fnde": link_fnde,
            "fonte": "FNDE / Ministério da Educação",
        }

    except Exception as e:
        ibge6 = ibge[:6] if len(ibge) >= 6 else ibge
        repasses_fallback = [
            {"programa": p["nome"], "descricao": p["descricao"], "link": f"https://www.fnde.gov.br/fndesite/index.php/consultas/repasses/historico-de-repasses?codigoMunicipio={ibge6}&ano={ano}"}
            for p in PROGRAMAS
        ]
        return {
            "disponivel": False,
            "ibge": ibge,
            "erro": str(e),
            "repasses": repasses_fallback,
            "link_fnde": f"https://www.fnde.gov.br/fndesite/index.php/consultas/repasses/historico-de-repasses",
            "fonte": "FNDE / Ministério da Educação",
        }
