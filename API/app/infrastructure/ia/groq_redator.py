"""Adaptador do redator de laudos sobre a API da Groq.

A Groq expõe uma interface compatível com a da OpenAI, então basta um POST em
/chat/completions. Manter o cliente aqui — e não no domínio — permite trocar de
provedor ou usar um dublê nos testes sem tocar na regra de negócio.
"""

import logging

import httpx

from app.domain.ia import ContextoLaudo, RedacaoIndisponivelError
from app.infrastructure.ia.prompt import INSTRUCAO_SISTEMA, montar_prompt

logger = logging.getLogger(__name__)


class GroqRedator:
    def __init__(
        self,
        api_key: str,
        modelo: str,
        base_url: str = "https://api.groq.com/openai/v1",
        timeout: float = 45.0,
    ):
        self.api_key = api_key
        self.modelo = modelo
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def redigir(self, contexto: ContextoLaudo) -> str:
        if not self.api_key:
            raise RedacaoIndisponivelError("Chave de API da Groq não configurada.")

        try:
            resposta = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.modelo,
                    "messages": [
                        {"role": "system", "content": INSTRUCAO_SISTEMA},
                        {"role": "user", "content": montar_prompt(contexto)},
                    ],
                    # Temperatura baixa: laudo técnico pede texto previsível
                    "temperature": 0.3,
                    "max_tokens": 900,
                },
                timeout=self.timeout,
            )
            resposta.raise_for_status()
            dados = resposta.json()
            texto = dados["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as erro:
            logger.warning("Groq respondeu %s: %s", erro.response.status_code, erro.response.text)
            raise RedacaoIndisponivelError(
                f"A API de IA respondeu com erro {erro.response.status_code}."
            ) from erro
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as erro:
            logger.warning("Falha ao consultar a Groq: %s", erro)
            raise RedacaoIndisponivelError(
                "Não foi possível comunicar com a API de IA."
            ) from erro

        if not texto:
            raise RedacaoIndisponivelError("A API de IA devolveu um texto vazio.")
        return texto
