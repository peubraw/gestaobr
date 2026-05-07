# pyright: reportAny=false, reportExplicitAny=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportArgumentType=false, reportIndexIssue=false
import asyncio
import json
import os
from collections.abc import Mapping
from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

BACKEND_INTERNAL_URL = os.getenv("BACKEND_INTERNAL_URL", "http://localhost:8000").rstrip("/")
COPILOT_PROXY_URL = "http://localhost:7800/v1/chat/completions"
DEFAULT_MODEL = "claude-haiku-4.5"


class ChatHistoricoItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    pergunta: str = Field(..., min_length=1)
    historico: list[ChatHistoricoItem] = Field(default_factory=list)


def _as_dict(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _format_numero(valor: object, casas: int = 1, sufixo: str = "") -> str:
    if valor is None:
        return "Não disponível"
    try:
        numero = float(valor)
        if casas == 0:
            texto = f"{numero:,.0f}"
        else:
            texto = f"{numero:,.{casas}f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{texto}{sufixo}"
    except Exception:
        return str(valor)


def _format_inteiro(valor: object) -> str:
    if valor is None:
        return "Não disponível"
    try:
        return f"{int(valor):,}".replace(",", ".")
    except Exception:
        return str(valor)


def _resumir_orcamento(orcamento: dict[str, object] | None) -> dict[str, object]:
    if not orcamento:
        return {"disponivel": False}
    return {
        "ano": orcamento.get("ano"),
        "disponivel": orcamento.get("disponivel", False),
        "fonte": orcamento.get("fonte"),
        "resumo": (orcamento.get("resumo") or [])[:5],
    }


def _resumir_contratos(contratos: dict[str, object] | None) -> dict[str, object]:
    if not contratos:
        return {"disponivel": False}
    dados = contratos.get("dados")
    itens = _as_list(dados)
    return {
        "disponivel": contratos.get("disponivel", False),
        "fonte": contratos.get("fonte"),
        "quantidade_itens_pagina": len(itens),
        "amostra": itens[:3],
    }


async def _buscar_json(client: httpx.AsyncClient, path: str) -> dict[str, object] | None:
    response = await client.get(f"{BACKEND_INTERNAL_URL}{path}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    if response.status_code != 200:
        return None
    try:
        return _as_dict(response.json())
    except Exception:
        return None


def _montar_system_prompt(ibge: str, municipio: dict[str, object], indicadores: dict[str, object] | None, vereadores: dict[str, object] | None, orcamento: dict[str, object] | None, contratos: dict[str, object] | None) -> str:
    indicadores = indicadores or {}
    vereadores = vereadores or {}
    orcamento_resumido = _resumir_orcamento(orcamento)
    contratos_resumidos = _resumir_contratos(contratos)

    nome = municipio.get("nome", "Município não identificado")
    uf = municipio.get("uf", "UF não identificada")
    populacao = _format_inteiro(municipio.get("populacao"))
    area = _format_numero(municipio.get("area_km2"), 1, " km²")
    densidade = _format_numero(municipio.get("densidade"), 1, " hab/km²")
    pib_per_capita = _format_numero(indicadores.get("pib_per_capita"), 2)
    analfabetismo = _format_numero(indicadores.get("analfabetismo_pct"), 2, "%")
    esgoto = _format_numero(indicadores.get("esgoto_pct"), 2, "%")
    lixo = _format_numero(indicadores.get("lixo_pct"), 2, "%")
    n_vereadores = _format_inteiro(vereadores.get("n_vereadores"))

    return f"""
Você é a IA Gestora Municipal do GestãoBR, especialista em gestão pública brasileira.

Atue com tom formal, técnico e governamental. Responda sempre em português do Brasil.
Baseie-se estritamente nos dados fornecidos abaixo. Não invente indicadores nem conclua além das evidências.
Quando houver lacunas, informe explicitamente que o dado não está disponível.
Sempre que pertinente, cite as fontes informadas na base de dados.

DADOS DO MUNICÍPIO: {nome} - {uf} (IBGE: {ibge})
- População: {populacao} habitantes
- Área: {area}
- Densidade: {densidade}
- PIB per capita: R$ {pib_per_capita}
- Taxa de analfabetismo: {analfabetismo}
- Cobertura de esgoto: {esgoto}
- Coleta de lixo: {lixo}
- Número de vereadores: {n_vereadores}

FONTES PRINCIPAIS
- Dados básicos do município: endpoint interno /municipios/{ibge}
- Indicadores socioeconômicos: {json.dumps(indicadores.get("fontes", {}), ensure_ascii=False)}
- Câmara municipal: {vereadores.get("fonte", "Não disponível")}
- Orçamento: {orcamento_resumido.get("fonte", "Não disponível")}
- Contratos: {contratos_resumidos.get("fonte", "Não disponível")}

DADOS INTERNOS ADICIONAIS DISPONÍVEIS
Município:
{json.dumps(municipio, ensure_ascii=False, indent=2)}

Indicadores:
{json.dumps(indicadores, ensure_ascii=False, indent=2)}

Vereadores:
{json.dumps(vereadores, ensure_ascii=False, indent=2)}

Orçamento resumido:
{json.dumps(orcamento_resumido, ensure_ascii=False, indent=2)}

Contratos resumidos:
{json.dumps(contratos_resumidos, ensure_ascii=False, indent=2)}

INSTRUÇÕES DE RESPOSTA
- Responda com objetividade, clareza e precisão técnica.
- Priorize implicações para gestão pública municipal.
- Quando fizer recomendações, conecte-as diretamente aos dados observados.
- Se a pergunta exigir dado ausente, diga isso com clareza e sugira próximo passo de análise.
""".strip()


def _extrair_conteudo_llm(payload: dict[str, object]) -> str:
    choices = _as_list(payload.get("choices"))
    if not choices:
        return ""
    message = _as_dict(choices[0])
    content = message.get("message")
    if content is not None:
        message = _as_dict(content)
        content = message.get("content", "")
    else:
        content = message.get("content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        partes: list[str] = []
        for item in content:
            item_dict = _as_dict(item)
            if item_dict.get("type") == "text":
                texto = item_dict.get("text", "")
                if isinstance(texto, str):
                    partes.append(texto)
        return "\n".join(parte for parte in partes if parte).strip()

    return ""


@router.post("/{ibge}")
async def chat_municipio(ibge: str, body: ChatRequest):
    historico = body.historico[-10:]

    async with httpx.AsyncClient(timeout=30) as client:
        municipio = await _buscar_json(client, f"/municipios/{ibge}")
        indicadores, vereadores, orcamento, contratos = await asyncio.gather(
            _buscar_json(client, f"/indicadores/{ibge}"),
            _buscar_json(client, f"/vereadores/{ibge}"),
            _buscar_json(client, f"/orcamento/{ibge}"),
            _buscar_json(client, f"/contratos/{ibge}"),
        )

        system_prompt = _montar_system_prompt(
            ibge=ibge,
            municipio=municipio or {},
            indicadores=indicadores,
            vereadores=vereadores,
            orcamento=orcamento,
            contratos=contratos,
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(item.model_dump() for item in historico)
        messages.append({"role": "user", "content": body.pergunta})

        try:
            response = await client.post(
                COPILOT_PROXY_URL,
                json={
                    "model": DEFAULT_MODEL,
                    "messages": messages,
                    "temperature": 0.2,
                    "stream": False,
                },
            )
        except httpx.HTTPError:
            raise HTTPException(
                status_code=503,
                detail="Serviço de IA indisponível no momento. Verifique o copilot-proxy em http://localhost:7800.",
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA indisponível no momento. O copilot-proxy não respondeu com sucesso.",
        )

    payload = _as_dict(response.json())
    resposta = _extrair_conteudo_llm(payload)
    if not resposta:
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA indisponível no momento. Resposta vazia recebida do modelo.",
        )

    usage = _as_dict(payload.get("usage"))
    total_tokens = usage.get("total_tokens")
    tokens_usados = int(total_tokens) if isinstance(total_tokens, int) else None
    if tokens_usados is None:
        prompt_tokens_raw = usage.get("prompt_tokens")
        completion_tokens_raw = usage.get("completion_tokens")
        prompt_tokens = int(prompt_tokens_raw) if isinstance(prompt_tokens_raw, int) else 0
        completion_tokens = int(completion_tokens_raw) if isinstance(completion_tokens_raw, int) else 0
        tokens_usados = prompt_tokens + completion_tokens or None

    return {
        "resposta": resposta,
        "modelo": payload.get("model") or DEFAULT_MODEL,
        "tokens_usados": tokens_usados,
    }
