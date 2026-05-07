"""
Diário oficial municipal — Querido Diário (OKBR) com fallback para portais municipais.
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

QUERIDO_DIARIO = "https://queridodiario.ok.org.br/api/gazettes"

# Portais conhecidos de Diário Oficial municipal (fallback por IBGE)
PORTAIS_CONHECIDOS: dict[str, dict] = {
    "2408102": {  # Natal-RN
        "nome": "Diário Oficial do Município de Natal",
        "url": "https://natal.rn.gov.br/dom/",
        "url_busca": "https://natal.rn.gov.br/dom/buscar-publicacoes",
    },
    "3550308": {  # São Paulo-SP
        "nome": "Diário Oficial da Cidade de São Paulo",
        "url": "https://diariooficial.prefeitura.sp.gov.br/",
        "url_busca": "https://diariooficial.prefeitura.sp.gov.br/",
    },
    "3304557": {  # Rio de Janeiro-RJ
        "nome": "Diário Oficial do Município do Rio de Janeiro",
        "url": "https://doweb.rio.rj.gov.br/",
        "url_busca": "https://doweb.rio.rj.gov.br/",
    },
    "2927408": {  # Salvador-BA
        "nome": "Diário Oficial do Município de Salvador",
        "url": "https://dom.salvador.ba.gov.br/",
        "url_busca": "https://dom.salvador.ba.gov.br/",
    },
    "2304400": {  # Fortaleza-CE
        "nome": "Diário Oficial do Município de Fortaleza",
        "url": "https://dom.fortaleza.ce.gov.br/",
        "url_busca": "https://dom.fortaleza.ce.gov.br/",
    },
    "3106200": {  # Belo Horizonte-MG
        "nome": "Diário Oficial do Município de Belo Horizonte (DOMB)",
        "url": "https://pbh.gov.br/domb",
        "url_busca": "https://pbh.gov.br/domb",
    },
    "4106902": {  # Curitiba-PR
        "nome": "Diário Oficial do Município de Curitiba",
        "url": "https://www.curitiba.pr.gov.br/diariooficial",
        "url_busca": "https://www.curitiba.pr.gov.br/diariooficial",
    },
    "4314902": {  # Porto Alegre-RS
        "nome": "Diário Oficial de Porto Alegre (DOPA)",
        "url": "http://www.dopa.rs.gov.br/",
        "url_busca": "http://www.dopa.rs.gov.br/",
    },
    "1302603": {  # Manaus-AM
        "nome": "Diário Oficial do Município de Manaus",
        "url": "https://dom.manaus.am.gov.br/",
        "url_busca": "https://dom.manaus.am.gov.br/",
    },
    "1501402": {  # Belém-PA
        "nome": "Diário Oficial do Município de Belém",
        "url": "https://dom.belem.pa.gov.br/",
        "url_busca": "https://dom.belem.pa.gov.br/",
    },
}


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def diario_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        # Tenta Querido Diário primeiro
        gazettes = []
        total = 0
        querido_ok = False

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    QUERIDO_DIARIO,
                    params={"territory_id": ibge, "is_extra_edition": "false", "size": 5},
                    headers={"Accept": "application/json"},
                )
            if resp.status_code == 200 and "application/json" in resp.headers.get("content-type", ""):
                payload = resp.json()
                raw = payload.get("results") or payload.get("gazettes") or []
                if raw:
                    querido_ok = True
                    total = payload.get("count") or len(raw)
                    gazettes = [
                        {
                            "data": item.get("publication_date") or item.get("date"),
                            "url": item.get("url"),
                            "numero_edicao": item.get("edition_number") or item.get("edition"),
                            "resumo": (item.get("excerpts") or [""])[0][:200] if item.get("excerpts") else None,
                        }
                        for item in raw[:5]
                    ]
        except Exception:
            pass

        # Portal conhecido para fallback ou complemento
        portal = PORTAIS_CONHECIDOS.get(ibge)

        if querido_ok:
            return {
                "disponivel": True,
                "codigo_ibge": ibge,
                "total_edicoes_indexadas": total,
                "edicoes_recentes": gazettes,
                "fonte": "Querido Diário / Open Knowledge Brasil",
                "portal_municipal": portal,
            }

        if portal:
            return {
                "disponivel": True,
                "codigo_ibge": ibge,
                "total_edicoes_indexadas": None,
                "edicoes_recentes": [],
                "portal_municipal": portal,
                "fonte": "Portal Municipal (acesso direto)",
                "aviso": "Diário não indexado pelo Querido Diário. Acesse o portal municipal diretamente.",
            }

        # Sem dados — retorna link genérico do Querido Diário
        return {
            "disponivel": False,
            "codigo_ibge": ibge,
            "total_edicoes_indexadas": 0,
            "edicoes_recentes": [],
            "portal_municipal": None,
            "fonte": "Querido Diário / OKBR",
            "aviso": "Diário Oficial não disponível ou não indexado para este município.",
            "link_consulta": f"https://queridodiario.ok.org.br/diarios?territory_id={ibge}",
        }

    except Exception as e:
        return {"disponivel": False, "erro": str(e), "fonte": "Querido Diário / OKBR"}
