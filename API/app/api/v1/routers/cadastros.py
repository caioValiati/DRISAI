"""Routers dos CRUDs — RF004 a RF008.

Curadoria (Normas/Insumos): escrita restrita ao ADMIN (RN001); leitura liberada
a autenticados, pois o agrônomo seleciona normas/insumos nos seus fluxos.
Carteira (Produtores/Propriedades/Talhões): exclusiva do AGRONOMO.
"""

import uuid

from fastapi import APIRouter, status

from app.api.v1.schemas.cadastros import (
    InsumoRequest,
    InsumoResponse,
    NormaDrisRequest,
    NormaDrisResponse,
    ProdutorRequest,
    ProdutorResponse,
    PropriedadeRequest,
    PropriedadeResponse,
    TalhaoRequest,
    TalhaoResponse,
)
from app.application.services.cadastros_service import (
    InsumoService,
    NormaDrisService,
    ProdutorService,
    PropriedadeService,
    TalhaoService,
)
from app.core.deps import CurrentAdmin, CurrentAgronomo, CurrentUser, DbSession

router = APIRouter()

# ---------------------------------------------------------------- Normas DRIS

normas = APIRouter(prefix="/normas", tags=["Normas DRIS"])


@normas.get("", response_model=list[NormaDrisResponse])
def listar_normas(db: DbSession, _: CurrentUser):
    return NormaDrisService(db).listar()


@normas.post("", response_model=NormaDrisResponse, status_code=status.HTTP_201_CREATED)
def criar_norma(dados: NormaDrisRequest, db: DbSession, _: CurrentAdmin):
    return NormaDrisService(db).criar(dados)


@normas.put("/{norma_id}", response_model=NormaDrisResponse)
def atualizar_norma(norma_id: uuid.UUID, dados: NormaDrisRequest, db: DbSession, _: CurrentAdmin):
    return NormaDrisService(db).atualizar(norma_id, dados)


@normas.patch("/{norma_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_norma(norma_id: uuid.UUID, db: DbSession, _: CurrentAdmin):
    NormaDrisService(db).inativar(norma_id)


# -------------------------------------------------------------------- Insumos

insumos = APIRouter(prefix="/insumos", tags=["Insumos"])


@insumos.get("", response_model=list[InsumoResponse])
def listar_insumos(db: DbSession, _: CurrentUser):
    return InsumoService(db).listar()


@insumos.post("", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
def criar_insumo(dados: InsumoRequest, db: DbSession, _: CurrentAdmin):
    return InsumoService(db).criar(dados)


@insumos.put("/{insumo_id}", response_model=InsumoResponse)
def atualizar_insumo(insumo_id: uuid.UUID, dados: InsumoRequest, db: DbSession, _: CurrentAdmin):
    return InsumoService(db).atualizar(insumo_id, dados)


@insumos.patch("/{insumo_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_insumo(insumo_id: uuid.UUID, db: DbSession, _: CurrentAdmin):
    InsumoService(db).inativar(insumo_id)


# ----------------------------------------------------------------- Produtores

produtores = APIRouter(prefix="/produtores", tags=["Produtores"])


@produtores.get("", response_model=list[ProdutorResponse])
def listar_produtores(db: DbSession, agronomo: CurrentAgronomo):
    return ProdutorService(db).listar(agronomo.id)


@produtores.post("", response_model=ProdutorResponse, status_code=status.HTTP_201_CREATED)
def criar_produtor(dados: ProdutorRequest, db: DbSession, agronomo: CurrentAgronomo):
    return ProdutorService(db).criar(agronomo.id, dados)


@produtores.put("/{produtor_id}", response_model=ProdutorResponse)
def atualizar_produtor(
    produtor_id: uuid.UUID, dados: ProdutorRequest, db: DbSession, agronomo: CurrentAgronomo
):
    return ProdutorService(db).atualizar(produtor_id, agronomo.id, dados)


@produtores.patch("/{produtor_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_produtor(produtor_id: uuid.UUID, db: DbSession, agronomo: CurrentAgronomo):
    ProdutorService(db).inativar(produtor_id, agronomo.id)


# --------------------------------------------------------------- Propriedades

propriedades = APIRouter(prefix="/propriedades", tags=["Propriedades"])


def _propriedade_response(p) -> PropriedadeResponse:
    resposta = PropriedadeResponse.model_validate(p)
    resposta.produtor_nome = p.produtor.nome_razao
    return resposta


@propriedades.get("", response_model=list[PropriedadeResponse])
def listar_propriedades(db: DbSession, agronomo: CurrentAgronomo):
    return [_propriedade_response(p) for p in PropriedadeService(db).listar(agronomo.id)]


@propriedades.post("", response_model=PropriedadeResponse, status_code=status.HTTP_201_CREATED)
def criar_propriedade(dados: PropriedadeRequest, db: DbSession, agronomo: CurrentAgronomo):
    return _propriedade_response(PropriedadeService(db).criar(agronomo.id, dados))


@propriedades.put("/{propriedade_id}", response_model=PropriedadeResponse)
def atualizar_propriedade(
    propriedade_id: uuid.UUID, dados: PropriedadeRequest, db: DbSession, agronomo: CurrentAgronomo
):
    return _propriedade_response(
        PropriedadeService(db).atualizar(propriedade_id, agronomo.id, dados)
    )


@propriedades.patch("/{propriedade_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_propriedade(propriedade_id: uuid.UUID, db: DbSession, agronomo: CurrentAgronomo):
    PropriedadeService(db).inativar(propriedade_id, agronomo.id)


# -------------------------------------------------------------------- Talhões

talhoes = APIRouter(prefix="/talhoes", tags=["Talhões"])


def _talhao_response(t) -> TalhaoResponse:
    resposta = TalhaoResponse.model_validate(t)
    resposta.propriedade_nome = t.propriedade.nome_fazenda
    return resposta


@talhoes.get("", response_model=list[TalhaoResponse])
def listar_talhoes(db: DbSession, agronomo: CurrentAgronomo):
    return [_talhao_response(t) for t in TalhaoService(db).listar(agronomo.id)]


@talhoes.post("", response_model=TalhaoResponse, status_code=status.HTTP_201_CREATED)
def criar_talhao(dados: TalhaoRequest, db: DbSession, agronomo: CurrentAgronomo):
    return _talhao_response(TalhaoService(db).criar(agronomo.id, dados))


@talhoes.put("/{talhao_id}", response_model=TalhaoResponse)
def atualizar_talhao(
    talhao_id: uuid.UUID, dados: TalhaoRequest, db: DbSession, agronomo: CurrentAgronomo
):
    return _talhao_response(TalhaoService(db).atualizar(talhao_id, agronomo.id, dados))


@talhoes.patch("/{talhao_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_talhao(talhao_id: uuid.UUID, db: DbSession, agronomo: CurrentAgronomo):
    TalhaoService(db).inativar(talhao_id, agronomo.id)


router.include_router(normas)
router.include_router(insumos)
router.include_router(produtores)
router.include_router(propriedades)
router.include_router(talhoes)
