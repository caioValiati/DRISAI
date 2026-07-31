"""Contrato do redator automático de laudos (RF011, etapa generativa).

O domínio define *o que* precisa ser redigido e recebe o texto pronto; qual
provedor de LLM atende esse contrato é decisão de infraestrutura.
"""

from dataclasses import dataclass, field
from typing import Protocol


class RedacaoIndisponivelError(Exception):
    """Falha ao obter o rascunho — dispara o fluxo alternativo do RF011 A1."""


@dataclass(frozen=True)
class InsumoSugerido:
    nome_comercial: str
    fabricante: str
    composicao: dict[str, float]
    score: float
    nutrientes_atendidos: list[str]


@dataclass(frozen=True)
class ContextoLaudo:
    """Tudo que a redação precisa conhecer sobre a amostra diagnosticada."""

    cultura: str
    estadio_fenologico: str
    talhao: str
    propriedade: str
    produtor: str
    data_coleta: str
    ibn: float
    indices: dict[str, float]
    classificacoes: dict[str, str]
    teores: dict[str, float]
    insumos: list[InsumoSugerido] = field(default_factory=list)


class RedatorDeLaudo(Protocol):
    def redigir(self, contexto: ContextoLaudo) -> str:
        """Devolve o rascunho textual da recomendação.

        Levanta RedacaoIndisponivelError quando não for possível gerar o texto.
        """
        ...
