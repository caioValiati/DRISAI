"""Geração do laudo técnico em PDF (RF013).

Reproduz o protótipo do DERS (Figuras 20 e 21): cabeçalho do responsável
técnico, identificação do atendimento, gráfico e tabela dos índices DRIS e o
texto final validado pelo agrônomo.
"""

import io
from dataclasses import dataclass
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.infrastructure.laudo.grafico import gerar_grafico_radial

VERDE = colors.HexColor("#2e7d32")
CINZA = colors.HexColor("#666666")

CORES_CLASSIFICACAO = {
    "DEFICIENTE": colors.HexColor("#c62828"),
    "EXCESSO": colors.HexColor("#ef6c00"),
    "EQUILIBRIO": colors.HexColor("#2e7d32"),
}

ROTULOS_CLASSIFICACAO = {
    "DEFICIENTE": "Deficiente",
    "EXCESSO": "Excesso",
    "EQUILIBRIO": "Equilíbrio",
}


@dataclass(frozen=True)
class DadosLaudo:
    agronomo_nome: str
    agronomo_crea: str | None
    produtor: str
    propriedade: str
    municipio_uf: str
    talhao: str
    cultura: str
    estadio_fenologico: str
    data_coleta: str
    data_emissao: datetime | None
    ibn: float
    indices: list[dict]  # elemento, teor, indice, classificacao
    texto_recomendacao: str
    insumos: list[dict]  # nome_comercial, fabricante, composicao, score


def _estilos():
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "TituloLaudo", parent=base["Title"], fontSize=16, textColor=VERDE, spaceAfter=2
        ),
        "subtitulo": ParagraphStyle(
            "Subtitulo", parent=base["Normal"], fontSize=9, textColor=CINZA, alignment=1
        ),
        "secao": ParagraphStyle(
            "Secao", parent=base["Heading2"], fontSize=11, textColor=VERDE,
            spaceBefore=8, spaceAfter=4,
        ),
        "corpo": ParagraphStyle(
            "Corpo", parent=base["Normal"], fontSize=9.5, leading=14, alignment=TA_JUSTIFY
        ),
    }


def _tabela_identificacao(dados: DadosLaudo, estilos) -> Table:
    linhas = [
        ["Produtor", dados.produtor, "Propriedade", dados.propriedade],
        ["Município/UF", dados.municipio_uf, "Talhão", dados.talhao],
        [
            "Cultura",
            f"{dados.cultura} ({dados.estadio_fenologico})",
            "Data da coleta",
            dados.data_coleta,
        ],
    ]
    tabela = Table(linhas, colWidths=[3 * cm, 5.6 * cm, 3 * cm, 5.4 * cm])
    tabela.setStyle(
        TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TEXTCOLOR", (0, 0), (0, -1), CINZA),
            ("TEXTCOLOR", (2, 0), (2, -1), CINZA),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#eeeeee")),
        ])
    )
    return tabela


def _tabela_indices(dados: DadosLaudo) -> Table:
    cabecalho = ["Nutriente", "Teor", "Índice DRIS", "Classificação"]
    linhas = [cabecalho]
    for indice in dados.indices:
        linhas.append([
            indice["elemento"],
            f"{indice['teor']:.2f}",
            f"{indice['indice']:+.2f}",
            ROTULOS_CLASSIFICACAO.get(indice["classificacao"], "—"),
        ])

    # A soma precisa caber na célula da composição lado a lado com o gráfico
    tabela = Table(linhas, colWidths=[2.1 * cm, 1.9 * cm, 2.2 * cm, 2.6 * cm])
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), VERDE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9f7")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
    ]
    # Destaca a classificação de cada nutriente na cor correspondente
    for posicao, indice in enumerate(dados.indices, start=1):
        cor = CORES_CLASSIFICACAO.get(indice["classificacao"])
        if cor:
            estilo.append(("TEXTCOLOR", (3, posicao), (3, posicao), cor))
    tabela.setStyle(TableStyle(estilo))
    return tabela


def _tabela_insumos(dados: DadosLaudo) -> Table:
    linhas = [["Insumo", "Fabricante", "Composição", "Aderência"]]
    for insumo in dados.insumos:
        composicao = ", ".join(f"{n} {v}%" for n, v in insumo["composicao"].items())
        linhas.append([
            insumo["nome_comercial"],
            insumo["fabricante"],
            composicao,
            f"{insumo['score']:.1f}%",
        ])

    tabela = Table(linhas, colWidths=[4.3 * cm, 3.3 * cm, 6.8 * cm, 2.6 * cm])
    tabela.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3ee")),
            ("TEXTCOLOR", (0, 0), (-1, 0), VERDE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (3, 0), (3, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ])
    )
    return tabela


def _desenhar_rodape(canvas, documento, responsavel: str, emissao: str):
    """Rodapé fixo no pé de cada página, desenhado fora do fluxo do conteúdo.

    Fica no canvas em vez de virar um parágrafo do documento porque, como
    parágrafo, ele empurraria uma página extra sempre que o conteúdo chegasse
    perto do fim da folha.
    """
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(CINZA)
    centro = A4[0] / 2
    canvas.drawCentredString(
        centro,
        1.35 * cm,
        f"Documento emitido em {emissao} pelo DRISAI. Recomendação revisada e "
        f"validada por {responsavel}, responsável técnico pelo laudo.",
    )
    canvas.drawCentredString(centro, 0.95 * cm, f"página {documento.page}")
    canvas.restoreState()


def gerar_laudo_pdf(dados: DadosLaudo) -> bytes:
    buffer = io.BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.9 * cm,
        title=f"Laudo DRIS — {dados.talhao}",
        author=dados.agronomo_nome,
    )
    estilos = _estilos()
    historia = []

    historia.append(Paragraph("Laudo de Diagnose Nutricional", estilos["titulo"]))
    historia.append(
        Paragraph("Sistema Integrado de Diagnose e Recomendação (DRIS)", estilos["subtitulo"])
    )
    responsavel = dados.agronomo_nome
    if dados.agronomo_crea:
        responsavel += f" — CREA {dados.agronomo_crea}"
    historia.append(Paragraph(f"Responsável técnico: {responsavel}", estilos["subtitulo"]))
    historia.append(Spacer(1, 10))

    historia.append(Paragraph("Identificação do atendimento", estilos["secao"]))
    historia.append(_tabela_identificacao(dados, estilos))

    historia.append(Paragraph("Diagnóstico nutricional", estilos["secao"]))
    historia.append(
        Paragraph(
            f"Índice de Balanço Nutricional (IBN): <b>{dados.ibn:.2f}</b>. Índices "
            "negativos apontam deficiência, positivos apontam excesso e valores "
            "próximos de zero indicam equilíbrio entre os nutrientes.",
            estilos["corpo"],
        )
    )
    historia.append(Spacer(1, 8))

    grafico = Image(
        io.BytesIO(gerar_grafico_radial({i["elemento"]: i["indice"] for i in dados.indices})),
        width=7.1 * cm,
        height=7.1 * cm,
    )
    lado_a_lado = Table(
        [[grafico, _tabela_indices(dados)]],
        colWidths=[8.0 * cm, 9.0 * cm],
    )
    lado_a_lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    historia.append(lado_a_lado)

    if dados.insumos:
        historia.append(Paragraph("Insumos avaliados", estilos["secao"]))
        historia.append(_tabela_insumos(dados))

    historia.append(Paragraph("Recomendação técnica", estilos["secao"]))
    for paragrafo in dados.texto_recomendacao.split("\n"):
        if paragrafo.strip():
            historia.append(Paragraph(paragrafo.strip(), estilos["corpo"]))
            historia.append(Spacer(1, 6))

    emissao = (
        dados.data_emissao.strftime("%d/%m/%Y às %H:%M")
        if dados.data_emissao
        else "data não informada"
    )

    def rodape(canvas, doc):
        _desenhar_rodape(canvas, doc, responsavel, emissao)

    documento.build(historia, onFirstPage=rodape, onLaterPages=rodape)
    return buffer.getvalue()
