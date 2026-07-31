"""Routers dos CRUDs — RF004 a RF008.

Curadoria (Normas/Insumos): escrita restrita ao ADMIN (RN001); leitura liberada
a autenticados, pois o agrônomo seleciona normas/insumos nos seus fluxos.
Carteira (Produtores/Propriedades/Talhões): o Agrônomo mantém a própria carteira
e o Administrador supervisiona todas elas.
"""

import uuid

from fastapi import APIRouter, status

from app.api.v1.schemas.cadastros import (
    ImpactoVinculosResponse,
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
from app.core.deps import CurrentAdmin, CurrentUser, DbSession

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


@normas.patch("/{norma_id}/reativar", status_code=status.HTTP_204_NO_CONTENT)
def reativar_norma(norma_id: uuid.UUID, db: DbSession, _: CurrentAdmin):
    NormaDrisService(db).reativar(norma_id)


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


@insumos.patch("/{insumo_id}/reativar", status_code=status.HTTP_204_NO_CONTENT)
def reativar_insumo(insumo_id: uuid.UUID, db: DbSession, _: CurrentAdmin):
    InsumoService(db).reativar(insumo_id)


# ----------------------------------------------------------------- Produtores

produtores = APIRouter(prefix="/produtores", tags=["Produtores"])


def _produtor_response(produtor) -> ProdutorResponse:
    resposta = ProdutorResponse.model_validate(produtor)
    resposta.agronomo_nome = produtor.agronomo.nome if produtor.agronomo else None
    return resposta


@produtores.get("", response_model=list[ProdutorResponse])
def listar_produtores(db: DbSession, usuario: CurrentUser):
    return [_produtor_response(p) for p in ProdutorService(db).listar(usuario)]


@produtores.post("", response_model=ProdutorResponse, status_code=status.HTTP_201_CREATED)
def criar_produtor(dados: ProdutorRequest, db: DbSession, usuario: CurrentUser):
    return _produtor_response(ProdutorService(db).criar(usuario, dados))


@produtores.put("/{produtor_id}", response_model=ProdutorResponse)
def atualizar_produtor(
    produtor_id: uuid.UUID, dados: ProdutorRequest, db: DbSession, usuario: CurrentUser
):
    return _produtor_response(ProdutorService(db).atualizar(produtor_id, usuario, dados))


@produtores.get("/{produtor_id}/vinculos", response_model=ImpactoVinculosResponse)
def vinculos_produtor(produtor_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    return ProdutorService(db).vinculos(produtor_id, usuario)


@produtores.patch("/{produtor_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_produtor(produtor_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    ProdutorService(db).inativar(produtor_id, usuario)


@produtores.patch("/{produtor_id}/reativar", status_code=status.HTTP_204_NO_CONTENT)
def reativar_produtor(
    produtor_id: uuid.UUID, db: DbSession, usuario: CurrentUser, cascata: bool = False
):
    ProdutorService(db).reativar(produtor_id, usuario, cascata)


# --------------------------------------------------------------- Propriedades

propriedades = APIRouter(prefix="/propriedades", tags=["Propriedades"])


def _propriedade_response(propriedade) -> PropriedadeResponse:
    resposta = PropriedadeResponse.model_validate(propriedade)
    resposta.produtor_nome = propriedade.produtor.nome_razao
    resposta.agronomo_nome = propriedade.produtor.agronomo.nome
    return resposta


@propriedades.get("", response_model=list[PropriedadeResponse])
def listar_propriedades(db: DbSession, usuario: CurrentUser):
    return [_propriedade_response(p) for p in PropriedadeService(db).listar(usuario)]


@propriedades.post("", response_model=PropriedadeResponse, status_code=status.HTTP_201_CREATED)
def criar_propriedade(dados: PropriedadeRequest, db: DbSession, usuario: CurrentUser):
    return _propriedade_response(PropriedadeService(db).criar(usuario, dados))


@propriedades.put("/{propriedade_id}", response_model=PropriedadeResponse)
def atualizar_propriedade(
    propriedade_id: uuid.UUID, dados: PropriedadeRequest, db: DbSession, usuario: CurrentUser
):
    return _propriedade_response(
        PropriedadeService(db).atualizar(propriedade_id, usuario, dados)
    )


@propriedades.get("/{propriedade_id}/vinculos", response_model=ImpactoVinculosResponse)
def vinculos_propriedade(propriedade_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    return PropriedadeService(db).vinculos(propriedade_id, usuario)


@propriedades.patch("/{propriedade_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_propriedade(propriedade_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    PropriedadeService(db).inativar(propriedade_id, usuario)


@propriedades.patch("/{propriedade_id}/reativar", status_code=status.HTTP_204_NO_CONTENT)
def reativar_propriedade(
    propriedade_id: uuid.UUID, db: DbSession, usuario: CurrentUser, cascata: bool = False
):
    PropriedadeService(db).reativar(propriedade_id, usuario, cascata)


# -------------------------------------------------------------------- Talhões

talhoes = APIRouter(prefix="/talhoes", tags=["Talhões"])


def _talhao_response(talhao) -> TalhaoResponse:
    resposta = TalhaoResponse.model_validate(talhao)
    resposta.propriedade_nome = talhao.propriedade.nome_fazenda
    resposta.agronomo_nome = talhao.propriedade.produtor.agronomo.nome
    return resposta


@talhoes.get("", response_model=list[TalhaoResponse])
def listar_talhoes(db: DbSession, usuario: CurrentUser):
    return [_talhao_response(t) for t in TalhaoService(db).listar(usuario)]


@talhoes.post("", response_model=TalhaoResponse, status_code=status.HTTP_201_CREATED)
def criar_talhao(dados: TalhaoRequest, db: DbSession, usuario: CurrentUser):
    return _talhao_response(TalhaoService(db).criar(usuario, dados))


@talhoes.put("/{talhao_id}", response_model=TalhaoResponse)
def atualizar_talhao(
    talhao_id: uuid.UUID, dados: TalhaoRequest, db: DbSession, usuario: CurrentUser
):
    return _talhao_response(TalhaoService(db).atualizar(talhao_id, usuario, dados))


@talhoes.get("/{talhao_id}/vinculos", response_model=ImpactoVinculosResponse)
def vinculos_talhao(talhao_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    return TalhaoService(db).vinculos(talhao_id, usuario)


@talhoes.patch("/{talhao_id}/inativar", status_code=status.HTTP_204_NO_CONTENT)
def inativar_talhao(talhao_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    TalhaoService(db).inativar(talhao_id, usuario)


@talhoes.patch("/{talhao_id}/reativar", status_code=status.HTTP_204_NO_CONTENT)
def reativar_talhao(talhao_id: uuid.UUID, db: DbSession, usuario: CurrentUser):
    TalhaoService(db).reativar(talhao_id, usuario)


router.include_router(normas)
router.include_router(insumos)
router.include_router(produtores)
router.include_router(propriedades)
router.include_router(talhoes)
