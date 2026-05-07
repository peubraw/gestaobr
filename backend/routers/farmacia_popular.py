"""
Farmácia Popular — farmácias credenciadas no município.
API: https://apidadosabertos.saude.gov.br/farmacias-populares/
Fallback: dados.gov.br / Ministério da Saúde
"""
import httpx
from fastapi import APIRouter

router = APIRouter()

FARM_BASE = "https://apidadosabertos.saude.gov.br/farmacias-populares/estabelecimentos"

# Medicamentos gratuitos no programa
MEDICAMENTOS_GRATUITOS = [
    "Metformina (diabetes)",
    "Glibenclamida (diabetes)",
    "Captopril (hipertensão)",
    "Hidroclorotiazida (hipertensão)",
    "Atenolol (hipertensão)",
    "Sinvastatina (colesterol)",
    "Levotiroxina (tireoide)",
    "Salbutamol (asma)",
    "Budesonida (asma)",
    "Anticoncepcional oral",
]

MEDICAMENTOS_SUBSIDIADOS = [
    "Insulina NPH (diabetes)",
    "Insulina Regular (diabetes)",
    "Losartana (hipertensão)",
    "Anlodipino (hipertensão)",
    "Omeprazol (gastrite)",
    "Amoxicilina (infecções)",
    "Rosuvastatina (colesterol)",
    "Furosemida (insuficiência cardíaca)",
    "AAS 100mg (prevenção cardiovascular)",
    "Fluoxetina (depressão)",
    "Clonazepam (ansiedade)",
    "Amitriptilina (depressão)",
]


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


@router.get("/{ibge}")
async def farmacia_popular_municipio(ibge: str):
    try:
        _validar_ibge(ibge)

        farmacias = []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # Tenta endpoint com municipioIBGE
                for param_key in ["municipioIBGE", "municipio_codigo", "co_municipio_ibge", "ibge"]:
                    resp = await client.get(
                        FARM_BASE,
                        params={param_key: ibge, "limit": 20},
                        headers={"Accept": "application/json"},
                    )
                    if resp.status_code == 200:
                        ct = resp.headers.get("content-type", "")
                        if "json" in ct:
                            data = resp.json()
                            items = data if isinstance(data, list) else data.get("data", data.get("estabelecimentos", []))
                            if items:
                                for item in items[:20]:
                                    farmacias.append({
                                        "nome": item.get("noEstabelecimento") or item.get("nome") or item.get("no_estabelecimento"),
                                        "endereco": item.get("dsLogradouro") or item.get("endereco") or item.get("ds_logradouro"),
                                        "bairro": item.get("noBairro") or item.get("bairro") or item.get("no_bairro"),
                                        "telefone": item.get("nuTelefone") or item.get("telefone"),
                                        "cnpj": item.get("noCnpj") or item.get("cnpj"),
                                    })
                                break
        except Exception:
            pass

        link_busca = f"https://www.gov.br/farmaciaecuidados/pt-br/farmacias-populares/lista-de-farmacias"
        link_remedios = "https://www.gov.br/farmaciaecuidados/pt-br/acesso-a-informacao/acoes-e-programas/farmacia-popular/medicamentos-disponiveis"

        return {
            "disponivel": True,
            "ibge": ibge,
            "farmacias_credenciadas": farmacias,
            "total_farmacias": len(farmacias),
            "medicamentos_gratuitos": MEDICAMENTOS_GRATUITOS,
            "medicamentos_subsidiados": MEDICAMENTOS_SUBSIDIADOS,
            "link_portal": link_busca,
            "link_medicamentos": link_remedios,
            "fonte": "Farmácia Popular / Ministério da Saúde",
            "aviso": f"{'Farmácias encontradas.' if farmacias else 'Consulte o portal para localizar farmácias credenciadas no município.'}",
        }

    except Exception as e:
        return {
            "disponivel": False,
            "ibge": ibge,
            "erro": str(e),
            "medicamentos_gratuitos": MEDICAMENTOS_GRATUITOS,
            "medicamentos_subsidiados": MEDICAMENTOS_SUBSIDIADOS,
            "link_portal": "https://www.gov.br/farmaciaecuidados/pt-br/farmacias-populares/lista-de-farmacias",
            "fonte": "Farmácia Popular / Ministério da Saúde",
        }
