"""Testes do motor de recomendação de insumos (RF011, etapa determinística)."""

from app.domain.enums import ClassificacaoNutriente as C
from app.domain.recomendacao import (
    InsumoCandidato,
    montar_vetor_necessidade,
    ranquear_insumos,
)

ZINCO = InsumoCandidato(
    id="1", nome_comercial="Zinco Concentrado 20", fabricante="Teste",
    culturas_autorizadas=["Soja"], concentracao_nutricional={"Zn": 20.0},
)
ZN_B = InsumoCandidato(
    id="2", nome_comercial="NutriSoja Zn-B", fabricante="Teste",
    culturas_autorizadas=["Soja"], concentracao_nutricional={"Zn": 10.0, "B": 2.5},
)
POTASSIO = InsumoCandidato(
    id="3", nome_comercial="Fosfito de Potássio", fabricante="Teste",
    culturas_autorizadas=["Soja"], concentracao_nutricional={"P": 30.0, "K": 20.0},
)
SO_MILHO = InsumoCandidato(
    id="4", nome_comercial="Zinco para Milho", fabricante="Teste",
    culturas_autorizadas=["Milho"], concentracao_nutricional={"Zn": 20.0},
)

CATALOGO = [ZINCO, ZN_B, POTASSIO, SO_MILHO]


def test_vetor_de_necessidade_usa_apenas_deficientes():
    indices = {"Zn": -8.0, "K": 4.0, "N": -0.5}
    classificacoes = {"Zn": C.DEFICIENTE, "K": C.EXCESSO, "N": C.EQUILIBRIO}

    assert montar_vetor_necessidade(indices, classificacoes) == {"Zn": 8.0}


def test_insumo_mais_aderente_a_deficiencia_lidera_o_ranking():
    resultado = ranquear_insumos(
        {"Zn": -8.0}, {"Zn": C.DEFICIENTE}, CATALOGO, cultura="Soja"
    )

    assert resultado[0].insumo.nome_comercial == "Zinco Concentrado 20"
    assert resultado[0].nutrientes_atendidos == ["Zn"]
    # O produto que dilui o zinco com boro fica atrás do zinco puro
    assert resultado[1].insumo.nome_comercial == "NutriSoja Zn-B"
    assert resultado[0].score > resultado[1].score


def test_insumo_nao_autorizado_para_a_cultura_fica_de_fora():
    """RN004 — a recomendação é restrita ao catálogo válido para a cultura."""
    resultado = ranquear_insumos(
        {"Zn": -8.0}, {"Zn": C.DEFICIENTE}, CATALOGO, cultura="Soja"
    )

    assert all(r.insumo.id != SO_MILHO.id for r in resultado)


def test_insumo_sem_nutriente_deficiente_nao_e_sugerido():
    resultado = ranquear_insumos(
        {"Zn": -8.0}, {"Zn": C.DEFICIENTE}, [POTASSIO], cultura="Soja"
    )

    assert resultado == []


def test_amostra_equilibrada_nao_gera_recomendacao():
    resultado = ranquear_insumos(
        {"Zn": 0.4, "K": -0.2}, {"Zn": C.EQUILIBRIO, "K": C.EQUILIBRIO},
        CATALOGO, cultura="Soja",
    )

    assert resultado == []


def test_nutriente_em_excesso_penaliza_o_score():
    """Um produto que carrega nutriente já excedente agrava o desequilíbrio."""
    classificacoes = {"P": C.DEFICIENTE, "K": C.EXCESSO}

    so_fosforo = InsumoCandidato(
        id="5", nome_comercial="Fósforo puro", fabricante="Teste",
        culturas_autorizadas=["Soja"], concentracao_nutricional={"P": 30.0},
    )
    resultado = ranquear_insumos(
        {"P": -6.0, "K": 6.0}, classificacoes, [so_fosforo, POTASSIO], cultura="Soja"
    )

    assert resultado[0].insumo.nome_comercial == "Fósforo puro"
    assert resultado[1].insumo.nome_comercial == "Fosfito de Potássio"
    assert resultado[1].score < resultado[0].score


def test_deficiencia_mais_severa_orienta_a_escolha():
    """Com duas carências, o insumo alinhado à mais grave lidera."""
    catalogo = [ZINCO, ZN_B]
    # B bem mais deficiente que Zn favorece o produto que traz os dois
    resultado = ranquear_insumos(
        {"Zn": -3.0, "B": -12.0},
        {"Zn": C.DEFICIENTE, "B": C.DEFICIENTE},
        catalogo,
        cultura="Soja",
    )

    assert resultado[0].insumo.nome_comercial == "NutriSoja Zn-B"


def test_ranking_respeita_o_limite_solicitado():
    resultado = ranquear_insumos(
        {"Zn": -8.0}, {"Zn": C.DEFICIENTE}, CATALOGO, cultura="Soja", limite=1
    )

    assert len(resultado) == 1
