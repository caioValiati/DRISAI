"""Testes unitários do motor DRIS (RF010) — domínio puro, sem banco."""

import pytest

from app.domain.dris import _funcao_relacao, calcular_dris
from app.domain.enums import ClassificacaoNutriente

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
