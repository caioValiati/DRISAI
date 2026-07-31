"""Router de Amostras Foliares — RF009, RF010, RF012 e conclusão (RN006)."""

import uuid

from fastapi import APIRouter, Response, status

from app.api.v1.schemas.amostras import (
    AmostraDetalheResponse,
    AmostraRequest,
    AmostraResumoResponse,
    AtualizarRecomendacaoRequest,
)
from app.application.services.amostra_service import AmostraService
from app.application.services.laudo_service import LaudoService
from app.core.deps import CurrentUser, DbSession

router = APIRouter(prefix="/amostras", tags=["Amostras Foliares"])


def _preencher_contexto(resposta, amostra):
    resposta.talhao_nome = amostra.talhao.identificacao if amostra.talhao else None
    resposta.propriedade_nome = (
        amostra.talhao.propriedade.nome_fazenda if amostra.talhao else None
    )
    resposta.cultura_norma = amostra.norma.cultura if amostra.norma else None
    return resposta


@router.get("", response_model=list[AmostraResumoResponse])
def listar_amostras(db: DbSession, usuario: CurrentUser):
    return [
        _preencher_contexto(AmostraResumoResponse.model_validate(a), a)
        for a in AmostraService(db).listar(usuario)
    ]


@router.get("/{amostra_id}", response_model=AmostraDetalheResponse)
def obter_amostra(amostra_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    amostra = AmostraService(db).obter(amostra_id, usuario)
    return _preencher_contexto(AmostraDetalheResponse.model_validate(amostra), amostra)


@router.post("", response_model=AmostraDetalheResponse, status_code=status.HTTP_201_CREATED)
def criar_amostra(dados: AmostraRequest, db: DbSession, usuario: CurrentUser):
    """Botão "Processar Análise DRIS" (Quadro 41): persiste e calcula (RF010)."""
    amostra = AmostraService(db).criar_e_processar(usuario, dados)
    return _preencher_contexto(AmostraDetalheResponse.model_validate(amostra), amostra)


@router.put("/{amostra_id}", response_model=AmostraDetalheResponse)
def atualizar_amostra(
    amostra_id: uuid.UUID, dados: AmostraRequest, db: DbSession, usuario: CurrentUser
):
    amostra = AmostraService(db).atualizar_e_reprocessar(amostra_id, usuario, dados)
    return _preencher_contexto(AmostraDetalheResponse.model_validate(amostra), amostra)


@router.put("/{amostra_id}/recomendacao", response_model=AmostraDetalheResponse)
def atualizar_recomendacao(
    amostra_id: uuid.UUID,
    dados: AtualizarRecomendacaoRequest,
    db: DbSession,
    usuario: CurrentUser,
):
    amostra = AmostraService(db).atualizar_recomendacao(amostra_id, usuario, dados)
    return _preencher_contexto(AmostraDetalheResponse.model_validate(amostra), amostra)


@router.post("/{amostra_id}/concluir", response_model=AmostraDetalheResponse)
def concluir_amostra(amostra_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    amostra = AmostraService(db).concluir(amostra_id, usuario)
    return _preencher_contexto(AmostraDetalheResponse.model_validate(amostra), amostra)


@router.get("/{amostra_id}/laudo.pdf", response_class=Response)
def emitir_laudo(amostra_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    """RF013 — laudo técnico da amostra concluída, pronto para entrega."""
    pdf, nome_arquivo = LaudoService(db).emitir_pdf(amostra_id, usuario)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )
