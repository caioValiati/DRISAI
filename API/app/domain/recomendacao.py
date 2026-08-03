"""Motor de recomendação de insumos (RF011, etapa determinística).

Implementa o cruzamento vetorial descrito no DERS: o desequilíbrio detectado
pelo DRIS vira um *vetor de necessidade agronômica*, o catálogo de insumos vira
*vetores de solução* e o grau de aderência entre eles ranqueia os produtos.

Módulo de domínio puro: sem ORM, framework ou chamadas de rede — o que mantém a
regra auditável e testável isoladamente, requisito de um laudo com valor técnico.
"""

import math
from dataclasses import dataclass

from app.domain.enums import ClassificacaoNutriente


@dataclass(frozen=True)
class InsumoCandidato:
    """Insumo do catálogo, já desacoplado da camada de persistência."""

    id: str
    nome_comercial: str
    fabricante: str
    culturas_autorizadas: list[str]
    concentracao_nutricional: dict[str, float]


@dataclass(frozen=True)
class InsumoRanqueado:
    insumo: InsumoCandidato
    score: float
    nutrientes_atendidos: list[str]


def _cosseno(a: dict[str, float], b: dict[str, float]) -> float:
    chaves = set(a) | set(b)
    produto = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in chaves)
    norma_a = math.sqrt(sum(v * v for v in a.values()))
    norma_b = math.sqrt(sum(v * v for v in b.values()))
    if norma_a == 0 or norma_b == 0:
        return 0.0
    return produto / (norma_a * norma_b)


def montar_vetor_necessidade(
    indices: dict[str, float],
    classificacoes: dict[str, ClassificacaoNutriente],
) -> dict[str, float]:
    """Traduz os índices DRIS em demanda por nutriente.

    Só nutrientes classificados como deficientes entram, com peso igual à
    severidade da carência (o módulo do índice). Nutrientes em equilíbrio ou
    excesso não geram demanda.
    """
    return {
        nutriente: abs(indice)
        for nutriente, indice in indices.items()
        if classificacoes.get(nutriente) == ClassificacaoNutriente.DEFICIENTE and indice < 0
    }


def _penalidade_por_excesso(
    concentracao: dict[str, float],
    classificacoes: dict[str, ClassificacaoNutriente],
) -> float:
    """Fração da formulação dedicada a nutrientes que já estão em excesso.

    Recomendar um produto rico num nutriente excedente agrava o desequilíbrio,
    então essa fração desconta o score do insumo.
    """
    total = sum(concentracao.values())
    if total <= 0:
        return 0.0
    excedente = sum(
        valor
        for nutriente, valor in concentracao.items()
        if classificacoes.get(nutriente) == ClassificacaoNutriente.EXCESSO
    )
    return excedente / total


def ranquear_insumos(
    indices: dict[str, float],
    classificacoes: dict[str, ClassificacaoNutriente],
    catalogo: list[InsumoCandidato],
    cultura: str,
    limite: int = 5,
) -> list[InsumoRanqueado]:
    """Ordena os insumos mais aderentes ao diagnóstico da amostra.

    O catálogo recebido já deve conter apenas insumos ativos (RN004); aqui
    filtramos ainda pela cultura autorizada, conforme o cadastro do produto.
    """
    necessidade = montar_vetor_necessidade(indices, classificacoes)
    if not necessidade:
        return []

    ranqueados: list[InsumoRanqueado] = []
    for insumo in catalogo:
        if cultura not in insumo.culturas_autorizadas:
            continue
        afinidade = _cosseno(necessidade, insumo.concentracao_nutricional)
        if afinidade <= 0:
            continue
        score = afinidade * (1 - _penalidade_por_excesso(
            insumo.concentracao_nutricional, classificacoes
        ))
        if score <= 0:
            continue
        atendidos = [n for n in necessidade if insumo.concentracao_nutricional.get(n, 0) > 0]
        ranqueados.append(
            InsumoRanqueado(
                insumo=insumo,
                score=round(score * 100, 2),
                nutrientes_atendidos=sorted(atendidos),
            )
        )

    ranqueados.sort(key=lambda r: r.score, reverse=True)
    return ranqueados[:limite]
