"""
Notícias relevantes para o município via RSS das principais agências brasileiras.
Fontes: Agência Brasil (EBC), Câmara, Senado, G1 Política.
Filtra por nome do município e UF. Quando sem filtro específico, retorna headlines gerais.
"""
import asyncio
import httpx
import xml.etree.ElementTree as ET
from fastapi import APIRouter

router = APIRouter()

RSS_FEEDS = [
    {
        "nome": "Agência Brasil",
        "url": "https://agenciabrasil.ebc.com.br/rss/geral/feed.xml",
        "tipo": "agencia_oficial",
    },
    {
        "nome": "Câmara dos Deputados",
        "url": "https://www.camara.leg.br/noticias/rss",
        "tipo": "legislativo",
    },
    {
        "nome": "Senado Federal",
        "url": "https://www12.senado.leg.br/noticias/rss/ultimas",
        "tipo": "legislativo",
    },
    {
        "nome": "Portal Gov.br",
        "url": "https://www.gov.br/pt-br/noticias/feed",
        "tipo": "governo",
    },
]

# Termos gerais de gestão pública (fallback quando município não aparece nas agências)
KEYWORDS_GESTAO = [
    "prefeitura", "município", "municipal", "gestão pública",
    "investimento", "obras", "licitação", "saúde pública",
    "educação pública", "saneamento", "orçamento", "governo",
]


def _validar_ibge(ibge: str) -> None:
    if not (ibge.isdigit() and len(ibge) == 7):
        raise ValueError("Código IBGE deve ter 7 dígitos")


def _parse_rss(content: bytes, fonte: str, palavras_chave: list[str]) -> list[dict]:
    """Parseia RSS e filtra por palavras-chave."""
    noticias = []
    try:
        root = ET.fromstring(content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # Padrão RSS 2.0
        items = root.findall(".//item")
        for item in items[:30]:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            desc = desc_el.text if desc_el is not None else ""
            combined = f"{title} {desc}".lower()

            # Filtra por palavras-chave (município ou UF)
            if any(kw.lower() in combined for kw in palavras_chave):
                noticias.append({
                    "titulo": title,
                    "link": link_el.text if link_el is not None else "",
                    "data": pub_el.text if pub_el is not None else "",
                    "resumo": (desc or "")[:200].strip(),
                    "fonte": fonte,
                })

        # Atom feed fallback
        if not items:
            entries = root.findall("atom:entry", ns) or root.findall(".//entry")
            for entry in entries[:30]:
                title_el = entry.find("atom:title", ns) or entry.find("title")
                link_el = entry.find("atom:link", ns) or entry.find("link")
                sum_el = entry.find("atom:summary", ns) or entry.find("summary")
                pub_el = entry.find("atom:published", ns) or entry.find("published") or entry.find("updated")

                title = title_el.text if title_el is not None else ""
                summary = sum_el.text if sum_el is not None else ""
                combined = f"{title} {summary}".lower()

                if any(kw.lower() in combined for kw in palavras_chave):
                    href = link_el.get("href", "") if link_el is not None else ""
                    noticias.append({
                        "titulo": title,
                        "link": href,
                        "data": pub_el.text if pub_el is not None else "",
                        "resumo": (summary or "")[:200].strip(),
                        "fonte": fonte,
                    })
    except Exception:
        pass
    return noticias


async def _fetch_feed(client: httpx.AsyncClient, feed: dict, palavras_chave: list[str]) -> list[dict]:
    try:
        resp = await client.get(feed["url"], follow_redirects=True)
        if resp.status_code == 200:
            return _parse_rss(resp.content, feed["nome"], palavras_chave)
    except Exception:
        pass
    return []


@router.get("/{ibge}")
async def noticias_municipio(ibge: str, nome_municipio: str = "", uf: str = ""):
    try:
        _validar_ibge(ibge)

        # Monta palavras-chave: tenta com o nome do município + UF
        palavras_municipio = []
        if nome_municipio:
            palavras_municipio.append(nome_municipio.lower())
            # versão sem a parte após "/" (ex: "São Gonçalo/RJ" → "São Gonçalo")
            palavras_municipio.append(nome_municipio.split("/")[0].strip().lower())
        if uf:
            palavras_municipio.append(uf.lower())

        async with httpx.AsyncClient(timeout=12) as client:
            resultados = await asyncio.gather(
                *[_fetch_feed(client, feed, palavras_municipio if palavras_municipio else KEYWORDS_GESTAO) for feed in RSS_FEEDS],
                return_exceptions=True,
            )

        todas_noticias: list[dict] = []
        for r in resultados:
            if isinstance(r, list):
                todas_noticias.extend(r)

        # Se não encontrou noticias específicas do município, usa headlines gerais
        if not todas_noticias:
            async with httpx.AsyncClient(timeout=12) as client:
                resultados_gerais = await asyncio.gather(
                    *[_fetch_feed(client, feed, KEYWORDS_GESTAO) for feed in RSS_FEEDS[:2]],
                    return_exceptions=True,
                )
            for r in resultados_gerais:
                if isinstance(r, list):
                    todas_noticias.extend(r)

        # Se ainda vazio, pega as 5 primeiras headlines brutas da Agência Brasil
        if not todas_noticias:
            async with httpx.AsyncClient(timeout=12) as client:
                try:
                    resp = await client.get(RSS_FEEDS[0]["url"], follow_redirects=True)
                    if resp.status_code == 200:
                        root = ET.fromstring(resp.content)
                        for item in root.findall(".//item")[:5]:
                            t = item.find("title")
                            l = item.find("link")
                            p = item.find("pubDate")
                            todas_noticias.append({
                                "titulo": t.text if t is not None else "",
                                "link": l.text if l is not None else "",
                                "data": p.text if p is not None else "",
                                "resumo": "",
                                "fonte": "Agência Brasil",
                            })
                except Exception:
                    pass

        todas_noticias = todas_noticias[:10]

        return {
            "disponivel": True,
            "ibge": ibge,
            "municipio": nome_municipio,
            "noticias": todas_noticias,
            "total": len(todas_noticias),
            "fontes_monitoradas": [f["nome"] for f in RSS_FEEDS],
            "fonte": "RSS — Agência Brasil, Câmara, Senado, Gov.br",
        }

    except Exception as e:
        return {
            "disponivel": False,
            "ibge": ibge,
            "erro": str(e),
            "noticias": [],
            "fonte": "RSS — Agência Brasil / EBC",
        }
