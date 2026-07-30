"""Caso de uso de Amostras Foliares (RF009) com o processamento DRIS (RF010).

O "Processar Análise" do DERS: persiste a amostra, calcula os índices via
motor de domínio e deixa a amostra em AGUARDANDO_REVISAO. Na Fase 2, o
gatilho do RF011 (IA) entra na sequência.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.api.v1.schemas.amostras import AmostraRequest, AtualizarRecomendacaoRequest
from app.domain.dris import calcular_dris
from app.domain.enums import StatusAmostra
from app.domain.exceptions import (
    AmostraImutavelError,
    DominioError,
    RecursoNaoEncontradoError,
)
from app.infrastructure.db.models import AmostraFoliar, IndiceNutricional, Recomendacao
from app.infrastructure.repositories.amostra_repository import AmostraRepository
from app.infrastructure.repositories.cadastros_repository import (
    NormaDrisRepository,
    TalhaoRepository,
)


class AmostraService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AmostraRepository(db)
        self.talhao_repo = TalhaoRepository(db)
        self.norma_repo = NormaDrisRepository(db)

    def listar(self, agronomo_id: uuid.UUID) -> list[AmostraFoliar]:
        return self.repo.listar_do_agronomo(agronomo_id)

    def obter(self, amostra_id: uuid.UUID, agronomo_id: uuid.UUID) -> AmostraFoliar:
        amostra = self.repo.obter_do_agronomo(amostra_id, agronomo_id)
        if not amostra:
            raise RecursoNaoEncontradoError("Amostra não encontrada.")
        return amostra

    def _validar_vinculos(self, dados: AmostraRequest, agronomo_id: uuid.UUID):
        # RN002 — amostra exige talhão da carteira e norma ativa
        if not self.talhao_repo.obter_do_agronomo(dados.talhao_id, agronomo_id):
            raise RecursoNaoEncontradoError("Talhão não encontrado na sua carteira.")
        norma = self.norma_repo.obter_por_id(dados.norma_dris_id)
        if not norma:
            raise RecursoNaoEncontradoError("Norma DRIS não encontrada.")
        if not norma.ativa:
            raise DominioError("A norma selecionada está inativa (RN002).")
        return norma

    def _processar_indices(self, amostra: AmostraFoliar, dados: AmostraRequest, norma) -> None:
        """RF010 — executa o motor de Beaufils e materializa índices + IBN."""
        teores = {n: float(v) for n, v in dados.teores.items()}
        resultado = calcular_dris(teores, norma.matriz_relacoes_duais)

        amostra.indices.clear()
        for elemento, teor in dados.teores.items():
            indice = resultado.indices.get(elemento)
            amostra.indices.append(
                IndiceNutricional(
                    elemento=elemento,
                    valor_laboratorio=teor,
                    indice_dris_calculado=Decimal(str(indice)) if indice is not None else None,
                    classificacao=resultado.classificacoes.get(elemento),
                )
            )
        amostra.valor_ibn = Decimal(str(resultado.ibn))
        amostra.status = StatusAmostra.AGUARDANDO_REVISAO

    def criar_e_processar(self, agronomo_id: uuid.UUID, dados: AmostraRequest) -> AmostraFoliar:
        norma = self._validar_vinculos(dados, agronomo_id)
        amostra = AmostraFoliar(
            talhao_id=dados.talhao_id,
            norma_dris_id=dados.norma_dris_id,
            data_coleta=dados.data_coleta,
        )
        self._processar_indices(amostra, dados, norma)
        amostra.recomendacao = Recomendacao()  # rascunho de IA entra na Fase 2
        self.repo.adicionar(amostra)
        return self.obter(amostra.id, agronomo_id)

    def atualizar_e_reprocessar(
        self, amostra_id: uuid.UUID, agronomo_id: uuid.UUID, dados: AmostraRequest
    ) -> AmostraFoliar:
        amostra = self.obter(amostra_id, agronomo_id)
        if amostra.status == StatusAmostra.CONCLUIDA:
            raise AmostraImutavelError()  # RN006
        norma = self._validar_vinculos(dados, agronomo_id)
        amostra.talhao_id = dados.talhao_id
        amostra.norma_dris_id = dados.norma_dris_id
        amostra.data_coleta = dados.data_coleta
        self._processar_indices(amostra, dados, norma)
        return self.obter(amostra_id, agronomo_id)

    def atualizar_recomendacao(
        self,
        amostra_id: uuid.UUID,
        agronomo_id: uuid.UUID,
        dados: AtualizarRecomendacaoRequest,
    ) -> AmostraFoliar:
        """RF012 — o agrônomo edita o texto da recomendação durante a revisão."""
        amostra = self.obter(amostra_id, agronomo_id)
        if amostra.status == StatusAmostra.CONCLUIDA:
            raise AmostraImutavelError()
        if amostra.recomendacao is None:
            amostra.recomendacao = Recomendacao()
        amostra.recomendacao.texto_final_editado = dados.texto_final_editado
        return amostra

    def concluir(self, amostra_id: uuid.UUID, agronomo_id: uuid.UUID) -> AmostraFoliar:
        """RF013 (parcial) — encerra o ciclo e torna o registro imutável (RN006).

        A geração do PDF do laudo fica para a Fase 2.
        """
        amostra = self.obter(amostra_id, agronomo_id)
        if amostra.status == StatusAmostra.CONCLUIDA:
            raise AmostraImutavelError()
        if amostra.status != StatusAmostra.AGUARDANDO_REVISAO:
            raise DominioError("A amostra precisa estar em revisão para ser concluída.")
        if not amostra.recomendacao or not amostra.recomendacao.texto_final_editado:
            raise DominioError(
                "Escreva o texto final da recomendação antes de concluir (RN005)."
            )
        amostra.status = StatusAmostra.CONCLUIDA
        amostra.recomendacao.data_emissao = datetime.now(timezone.utc)
        return amostra
