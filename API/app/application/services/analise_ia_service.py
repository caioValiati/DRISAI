"""Orquestra a análise prévia da amostra (RF011).

Roda em duas etapas independentes: o matching de insumos, determinístico e
sempre disponível, e a redação do rascunho pelo LLM, que pode falhar. Uma falha
na segunda etapa não descarta a primeira — é o fluxo alternativo A1 do DERS.
"""

import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.enums import ClassificacaoNutriente
from app.domain.ia import (
    ContextoLaudo,
    InsumoSugerido,
    RedacaoIndisponivelError,
    RedatorDeLaudo,
)
from app.domain.recomendacao import InsumoCandidato, ranquear_insumos
from app.infrastructure.db.models import AmostraFoliar, Insumo, Recomendacao, RecomendacaoInsumo
from app.infrastructure.ia.groq_redator import GroqRedator

logger = logging.getLogger(__name__)


def redator_padrao() -> RedatorDeLaudo:
    settings = get_settings()
    print("KEY: " + settings.groq_api_key)
    return GroqRedator(api_key=settings.groq_api_key, modelo=settings.groq_model)


class AnaliseIaService:
    def __init__(self, db: Session, redator: RedatorDeLaudo | None = None):
        self.db = db
        self.redator = redator or redator_padrao()

    def _catalogo_ativo(self) -> tuple[list[InsumoCandidato], dict[str, Insumo]]:
        """Catálogo elegível como candidatos de domínio + os registros de origem.

        Guardar os objetos do ORM permite associá-los diretamente à sugestão, o
        que já deixa o relacionamento carregado para a resposta da API.
        """
        # RN004 — apenas insumos comercialmente ativos e validados pela plataforma
        insumos = list(self.db.scalars(select(Insumo).where(Insumo.ativo.is_(True))))
        candidatos = [
            InsumoCandidato(
                id=str(i.id),
                nome_comercial=i.nome_comercial,
                fabricante=i.fabricante,
                culturas_autorizadas=list(i.culturas_autorizadas),
                concentracao_nutricional=dict(i.concentracao_nutricional),
            )
            for i in insumos
        ]
        return candidatos, {str(i.id): i for i in insumos}

    def analisar(self, amostra: AmostraFoliar) -> None:
        """Preenche a recomendação da amostra com o matching e o rascunho."""
        indices = {
            i.elemento: float(i.indice_dris_calculado)
            for i in amostra.indices
            if i.indice_dris_calculado is not None
        }
        classificacoes = {
            i.elemento: i.classificacao for i in amostra.indices if i.classificacao
        }
        teores = {i.elemento: float(i.valor_laboratorio) for i in amostra.indices}
        cultura = amostra.norma.cultura

        catalogo, registros = self._catalogo_ativo()
        ranqueados = ranquear_insumos(indices, classificacoes, catalogo, cultura=cultura)

        if amostra.recomendacao is None:
            amostra.recomendacao = Recomendacao()
        recomendacao = amostra.recomendacao

        # Reprocessar a amostra substitui a sugestão anterior por completo
        recomendacao.insumos_sugeridos.clear()
        for posicao in ranqueados:
            recomendacao.insumos_sugeridos.append(
                RecomendacaoInsumo(
                    insumo=registros[posicao.insumo.id],
                    match_score=Decimal(str(posicao.score)),
                )
            )

        contexto = ContextoLaudo(
            cultura=cultura,
            estadio_fenologico=amostra.norma.estadio_fenologico,
            talhao=amostra.talhao.identificacao,
            propriedade=amostra.talhao.propriedade.nome_fazenda,
            produtor=amostra.talhao.propriedade.produtor.nome_razao,
            data_coleta=amostra.data_coleta.strftime("%d/%m/%Y"),
            ibn=float(amostra.valor_ibn or 0),
            indices=indices,
            classificacoes={n: c.value for n, c in classificacoes.items()},
            teores=teores,
            insumos=[
                InsumoSugerido(
                    nome_comercial=p.insumo.nome_comercial,
                    fabricante=p.insumo.fabricante,
                    composicao=p.insumo.concentracao_nutricional,
                    score=p.score,
                    nutrientes_atendidos=p.nutrientes_atendidos,
                )
                for p in ranqueados
            ],
        )

        try:
            recomendacao.texto_rascunho_ia = self.redator.redigir(contexto)
            recomendacao.falha_ia = None
        except RedacaoIndisponivelError as erro:
            # A1 — mantém a indicação matemática e o ranking de insumos, e
            # sinaliza para a tela que o campo de texto ficará em branco
            logger.info("Rascunho automático indisponível: %s", erro)
            recomendacao.texto_rascunho_ia = None
            recomendacao.falha_ia = str(erro)


def nutrientes_deficientes(amostra: AmostraFoliar) -> list[str]:
    return [
        i.elemento
        for i in amostra.indices
        if i.classificacao == ClassificacaoNutriente.DEFICIENTE
    ]
