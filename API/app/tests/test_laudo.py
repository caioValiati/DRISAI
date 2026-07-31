"""Testes da geração do laudo em PDF (RF013)."""

from datetime import datetime

from app.infrastructure.laudo.pdf import DadosLaudo, gerar_laudo_pdf

INDICES = [
    {"elemento": "N", "teor": 42.49, "indice": 0.92, "classificacao": "EQUILIBRIO"},
    {"elemento": "P", "teor": 3.17, "indice": 1.15, "classificacao": "EQUILIBRIO"},
    {"elemento": "Zn", "teor": 20.0, "indice": -6.91, "classificacao": "DEFICIENTE"},
    {"elemento": "Mn", "teor": 19.0, "indice": -3.51, "classificacao": "DEFICIENTE"},
    {"elemento": "Fe", "teor": 149.76, "indice": 3.62, "classificacao": "EXCESSO"},
]


def _dados(**sobrescritas) -> DadosLaudo:
    padrao = dict(
        agronomo_nome="Agrônomo Teste",
        agronomo_crea="GO-12345",
        produtor="Fazendas Boa Safra LTDA",
        propriedade="Fazenda Santa Rita",
        municipio_uf="Rio Verde/GO",
        talhao="Talhão 01",
        cultura="Soja",
        estadio_fenologico="R2",
        data_coleta="28/07/2026",
        data_emissao=datetime(2026, 7, 31, 20, 0),
        ibn=20.85,
        indices=INDICES,
        texto_recomendacao="Primeiro parágrafo.\nSegundo parágrafo.",
        insumos=[
            {
                "nome_comercial": "Zinco Concentrado 20",
                "fabricante": "Mineral Prime",
                "composicao": {"Zn": 20.0},
                "score": 89.16,
            }
        ],
    )
    padrao.update(sobrescritas)
    return DadosLaudo(**padrao)


def test_laudo_gera_pdf_valido():
    pdf = gerar_laudo_pdf(_dados())

    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(pdf) > 10_000  # o gráfico embutido garante um tamanho mínimo


def test_laudo_cabe_em_uma_pagina():
    """O rodapé é desenhado no canvas justamente para não empurrar página extra."""
    pdf = gerar_laudo_pdf(_dados())

    assert pdf.count(b"/Type /Page\n") <= 1 or b"/Count 1" in pdf


def test_laudo_sem_insumos_nao_quebra():
    """Amostra equilibrada não gera sugestões e o laudo omite a seção."""
    pdf = gerar_laudo_pdf(_dados(insumos=[]))

    assert pdf.startswith(b"%PDF-")


def test_laudo_sem_crea_usa_apenas_o_nome():
    pdf = gerar_laudo_pdf(_dados(agronomo_crea=None))

    assert pdf.startswith(b"%PDF-")
