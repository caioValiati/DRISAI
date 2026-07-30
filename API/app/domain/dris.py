"""Motor de cálculo DRIS/IBN (RF010) — método de Beaufils (1973).

Módulo de domínio puro: sem dependência de framework, ORM ou banco.

A norma DRIS é um dicionário {"A/B": {"media": float, "dp": float, "cv": float}},
onde "A/B" é a relação dual entre dois nutrientes, `media` é a média da relação na
população de alta produtividade, `dp` o desvio-padrão e `cv` o coeficiente de
variação em porcentagem (cv = 100 * dp / media).
"""

from dataclasses import dataclass

from app.domain.enums import ClassificacaoNutriente


@dataclass(frozen=True)
class ResultadoDris:
    indices: dict[str, float]  # índice DRIS por nutriente
    classificacoes: dict[str, ClassificacaoNutriente]
    ibn: float  # Índice de Balanço Nutricional = soma dos módulos dos índices


def _funcao_relacao(valor_amostra: float, media_norma: float, cv_norma: float) -> float:
    """Função de relação f(A/B) de Beaufils (WALWORTH; SUMNER, 1987).

    Compara a relação dual observada na amostra com a média da norma,
    ponderando pelo CV da norma (relações mais estáveis pesam mais).
    """
    if valor_amostra <= 0 or media_norma <= 0 or cv_norma <= 0:
        raise ValueError("Relações duais e parâmetros da norma devem ser positivos.")
    if valor_amostra >= media_norma:
        return (valor_amostra / media_norma - 1.0) * (100.0 / cv_norma)
    return (1.0 - media_norma / valor_amostra) * (100.0 / cv_norma)


def calcular_dris(
    teores: dict[str, float],
    norma: dict[str, dict[str, float]],
    limite_equilibrio: float | None = None,
) -> ResultadoDris:
    """Calcula os índices DRIS de cada nutriente e o IBN da amostra.

    - `teores`: teor foliar de cada nutriente (ex.: {"N": 45.2, "P": 2.8, ...}).
    - `norma`: relações duais da norma, ex.: {"N/P": {"media": 10.9, "dp": 1.3, "cv": 12.0}}.
    - `limite_equilibrio`: limiar de classificação. Quando omitido, usa a média dos
      módulos dos índices (IBN/n) — critério auto-normalizado que destaca os
      nutrientes mais limitantes independentemente da escala da norma.

    O índice de um nutriente A é a média das funções de relação em que A participa:
    f(A/X) entra com sinal positivo e f(X/A) com sinal negativo.
    """
    funcoes: dict[str, float] = {}
    for relacao, params in norma.items():
        num, den = relacao.split("/")
        if num not in teores or den not in teores:
            continue
        if teores[num] <= 0 or teores[den] <= 0:
            raise ValueError(f"Teor de {num} ou {den} inválido (deve ser > 0).")
        cv = params.get("cv") or (100.0 * params["dp"] / params["media"])
        funcoes[relacao] = _funcao_relacao(teores[num] / teores[den], params["media"], cv)

    if not funcoes:
        raise ValueError("A norma não possui relações duais compatíveis com a amostra.")

    indices: dict[str, float] = {}
    for nutriente in teores:
        soma, n_relacoes = 0.0, 0
        for relacao, f in funcoes.items():
            num, den = relacao.split("/")
            if num == nutriente:
                soma += f
                n_relacoes += 1
            elif den == nutriente:
                soma -= f
                n_relacoes += 1
        if n_relacoes:
            indices[nutriente] = round(soma / n_relacoes, 2)

    ibn = round(sum(abs(i) for i in indices.values()), 2)
    limite = limite_equilibrio if limite_equilibrio is not None else ibn / len(indices)

    classificacoes = {}
    for nutriente, indice in indices.items():
        if indice < -limite:
            classificacoes[nutriente] = ClassificacaoNutriente.DEFICIENTE
        elif indice > limite:
            classificacoes[nutriente] = ClassificacaoNutriente.EXCESSO
        else:
            classificacoes[nutriente] = ClassificacaoNutriente.EQUILIBRIO

    return ResultadoDris(indices=indices, classificacoes=classificacoes, ibn=ibn)
