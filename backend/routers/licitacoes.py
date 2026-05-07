"""
Licitações municipais via PNCP — endpoint /v1/contratacoes/proposta.
Retorna licitações com propostas abertas filtrando por codigoMunicipioIbge.
Sem autenticação necessária. Cobertura nacional (todos os 5.570 municípios).
"""
import httpx
from datetime import date, timedelta
from fastapi import APIRouter

router = APIRouter()

PNCP_BASE = "https://pncp.gov.br/api/consulta/v1"
PNCP_PORTAL = "https://pncp.gov.br/app/editais"


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _fmt_data(d: date) -> str:
    return d.strftime("%Y%m%d")


def _parse_licitacao(item: dict, link_pncp: str) -> dict:
    numero = item.get("numeroControlePNCP", "")
    orgao = item.get("orgaoEntidade", {}).get("razaoSocial", "")
    unidade = item.get("unidadeOrgao", {}).get("nomeUnidade", orgao)
    data_abertura = item.get("dataAberturaProposta", "")
    data_encerramento = item.get("dataEncerramentoProposta", "")
    valor = item.get("valorTotalEstimado")
    modalidade = item.get("modalidadeNome", "")
    objeto = item.get("objetoCompra", "")
    link_sistema = item.get("linkSistemaOrigem") or link_pncp

    return {
        "numero_controle": numero,
        "titulo": objeto[:120] if objeto else "—",
        "objeto": objeto,
        "orgao": unidade,
        "modalidade": modalidade,
        "valor": valor if valor and valor > 0 else None,
        "data_abertura": data_abertura[:10] if data_abertura else None,
        "data_encerramento": data_encerramento[:10] if data_encerramento else None,
        "ano": item.get("anoCompra"),
        "url": link_sistema,
    }


@router.get("/{ibge}")
async def licitacoes_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        link_pncp = f"{PNCP_PORTAL}?municipio={ibge}"
        hoje = date.today()
        # proposta: busca licitações com proposta aberta (dataInicial <= hoje <= dataFinal)
        # Janela: 90 dias atrás até 180 dias à frente
        data_ini = _fmt_data(hoje - timedelta(days=90))
        data_fim = _fmt_data(hoje + timedelta(days=180))

        licitacoes = []
        total_registros = 0

        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(
                f"{PNCP_BASE}/contratacoes/proposta",
                params={
                    "dataInicial": data_ini,
                    "dataFinal": data_fim,
                    "codigoMunicipioIbge": ibge,
                    "pagina": 1,
                    "tamanhoPagina": 10,
                },
                headers={"Accept": "application/json"},
            )

            if r.status_code == 200:
                payload = r.json()
                total_registros = payload.get("totalRegistros", 0)
                items = payload.get("data", [])
                licitacoes = [_parse_licitacao(i, link_pncp) for i in items]
            elif r.status_code in (404, 204):
                # Município sem licitações abertas no período — normal
                pass
            else:
                # Falha na API — retorna link sem dados individuais
                return {
                    "disponivel": True,
                    "codigo_ibge": ibge,
                    "total": 0,
                    "licitacoes": [],
                    "link_pncp": link_pncp,
                    "nota": "Consulte o portal PNCP para licitações deste município.",
                    "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
                }

        return {
            "disponivel": True,
            "codigo_ibge": ibge,
            "total": total_registros,
            "licitacoes": licitacoes,
            "link_pncp": link_pncp,
            "fonte": "PNCP — Portal Nacional de Contratações Públicas (Lei 14.133/2021)",
        }

    except Exception as e:
        return {
            "disponivel": False,
            "erro": str(e),
            "link_pncp": f"{PNCP_PORTAL}?municipio={ibge}",
            "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
        }
