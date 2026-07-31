"""Testes unitários do motor DRIS (RF010) — domínio puro, sem banco."""

import pytest

from app.domain.dris import _funcao_relacao, calcular_dris
from app.domain.enums import NUTRIENTES, ClassificacaoNutriente
from app.scripts.seed import NORMA_SOJA, TEORES_REFERENCIA_SOJA

# Norma sintética com três nutrientes para validação manual dos cálculos
NORMA = {
    "N/P": {"media": 10.0, "dp": 2.0, "cv": 20.0},
    "N/K": {"media": 2.0, "dp": 0.4, "cv": 20.0},
    "K/P": {"media": 5.0, "dp": 1.0, "cv": 20.0},
}


def test_amostra_identica_a_norma_gera_indices_zero_e_ibn_zero():
    # Teores que reproduzem exatamente as relações da norma: N/P=10, N/K=2, K/P=5
    resultado = calcular_dris({"N": 50.0, "P": 5.0, "K": 25.0}, NORMA)
    assert resultado.indices == {"N": 0.0, "P": 0.0, "K": 0.0}
    assert resultado.ibn == 0.0
    assert all(c == ClassificacaoNutriente.EQUILIBRIO for c in resultado.classificacoes.values())


def test_deficiencia_gera_indice_negativo_e_classificacao():
    # N pela metade → relações N/P e N/K caem → N é o nutriente mais limitante
    resultado = calcular_dris({"N": 25.0, "P": 5.0, "K": 25.0}, NORMA)
    assert resultado.indices["N"] < 0
    assert resultado.classificacoes["N"] == ClassificacaoNutriente.DEFICIENTE
    # Os demais compensam com índices positivos (a soma dos índices é ~0 no DRIS)
    assert resultado.indices["P"] > 0
    assert resultado.indices["K"] > 0


def test_limite_explicito_sobrescreve_criterio_automatico():
    teores = {"N": 25.0, "P": 5.0, "K": 25.0}
    # Com limiar folgado, nenhum nutriente é apontado como fora do equilíbrio
    resultado = calcular_dris(teores, NORMA, limite_equilibrio=50.0)
    assert all(
        c == ClassificacaoNutriente.EQUILIBRIO for c in resultado.classificacoes.values()
    )


def test_ibn_e_a_soma_dos_modulos_dos_indices():
    resultado = calcular_dris({"N": 30.0, "P": 6.0, "K": 20.0}, NORMA)
    assert resultado.ibn == pytest.approx(
        sum(abs(i) for i in resultado.indices.values()), abs=0.01
    )


def test_funcao_relacao_simetrica_em_torno_da_media():
    # Acima da média → positiva; abaixo → negativa
    assert _funcao_relacao(12.0, 10.0, 20.0) > 0
    assert _funcao_relacao(8.0, 10.0, 20.0) < 0
    assert _funcao_relacao(10.0, 10.0, 20.0) == 0.0


def test_relacao_invertida_na_norma_e_usada_com_sinal_trocado():
    # Norma só com P/N: um N alto deve derrubar a relação e gerar índice N positivo
    norma = {"P/N": {"media": 0.1, "dp": 0.02, "cv": 20.0}}
    resultado = calcular_dris({"N": 100.0, "P": 5.0}, norma)
    assert resultado.indices["N"] > 0
    assert resultado.indices["P"] < 0


def test_teor_invalido_levanta_erro():
    with pytest.raises(ValueError):
        calcular_dris({"N": 0.0, "P": 5.0, "K": 25.0}, NORMA)


def test_norma_incompativel_levanta_erro():
    with pytest.raises(ValueError):
        calcular_dris({"Ca": 1.0, "Mg": 1.0}, NORMA)


# --------------------------------------------------------------------------
# Validação contra a norma real do projeto: soja em R2, sul do Maranhão
# (HOOGERHEIDE, 2005, Figura 1) — 55 relações duais entre os 11 nutrientes.
# --------------------------------------------------------------------------


def test_norma_real_cobre_todos_os_pares_de_nutrientes():
    from itertools import combinations

    pares_norma = {frozenset(rel.split("/")) for rel in NORMA_SOJA}
    pares_possiveis = {frozenset(p) for p in combinations(NUTRIENTES, 2)}
    assert pares_norma == pares_possiveis
    assert len(NORMA_SOJA) == 55  # nenhuma dupla repetida em orientação invertida


def test_amostra_igual_a_media_da_norma_fica_equilibrada():
    """Teores idênticos às médias da população de referência devem gerar
    índices próximos de zero — o desvio residual vem apenas do arredondamento
    dos valores publicados."""
    resultado = calcular_dris(TEORES_REFERENCIA_SOJA, NORMA_SOJA)

    assert all(abs(indice) < 1 for indice in resultado.indices.values()), resultado.indices
    assert resultado.ibn < 2
    # Nenhum nutriente pode ser apontado como deficiente/excessivo: o resíduo é
    # ruído do arredondamento da norma, não desequilíbrio nutricional
    assert all(
        c == ClassificacaoNutriente.EQUILIBRIO for c in resultado.classificacoes.values()
    ), resultado.classificacoes


def test_soma_dos_indices_dris_e_proxima_de_zero():
    """Propriedade estrutural do método: cada f(A/B) entra positiva no índice de
    A e negativa no de B, então o somatório dos índices se anula."""
    teores = dict(TEORES_REFERENCIA_SOJA, Zn=20.0, Mn=15.0)
    resultado = calcular_dris(teores, NORMA_SOJA)

    assert sum(resultado.indices.values()) == pytest.approx(0.0, abs=0.5)


def test_deficiencia_severa_e_apontada_com_a_norma_real():
    # Zn a menos da metade da média da norma (43,04 -> 18) deve ser o mais limitante
    teores = dict(TEORES_REFERENCIA_SOJA, Zn=18.0)
    resultado = calcular_dris(teores, NORMA_SOJA)

    assert resultado.classificacoes["Zn"] == ClassificacaoNutriente.DEFICIENTE
    assert resultado.indices["Zn"] == min(resultado.indices.values())


def test_ibn_cresce_com_o_grau_de_desequilibrio():
    equilibrada = calcular_dris(TEORES_REFERENCIA_SOJA, NORMA_SOJA)
    desequilibrada = calcular_dris(dict(TEORES_REFERENCIA_SOJA, Zn=18.0, P=1.5), NORMA_SOJA)

    assert desequilibrada.ibn > equilibrada.ibn
