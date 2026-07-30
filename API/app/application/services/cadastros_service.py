"""Casos de uso dos CRUDs de curadoria (RF004/RF005) e carteira (RF006–RF008)."""

import uuid

from sqlalchemy.orm import Session

from app.api.v1.schemas.cadastros import (
    InsumoRequest,
    NormaDrisRequest,
    ProdutorRequest,
    PropriedadeRequest,
    TalhaoRequest,
)
from app.domain.exceptions import ConflitoError, RecursoNaoEncontradoError
from app.infrastructure.db.models import Insumo, NormaDris, Produtor, Propriedade, Talhao
from app.infrastructure.repositories.cadastros_repository import (
    InsumoRepository,
    NormaDrisRepository,
    ProdutorRepository,
    PropriedadeRepository,
    TalhaoRepository,
)


class NormaDrisService:
    def __init__(self, db: Session):
        self.repo = NormaDrisRepository(db)

    def listar(self) -> list[NormaDris]:
        return self.repo.listar()

    def criar(self, dados: NormaDrisRequest) -> NormaDris:
        return self.repo.adicionar(
            NormaDris(
                cultura=dados.cultura,
                estadio_fenologico=dados.estadio_fenologico,
                matriz_relacoes_duais={
                    rel: params.model_dump() for rel, params in dados.matriz_relacoes_duais.items()
                },
            )
        )

    def _obter(self, norma_id: uuid.UUID) -> NormaDris:
        norma = self.repo.obter_por_id(norma_id)
        if not norma:
            raise RecursoNaoEncontradoError("Norma DRIS não encontrada.")
        return norma

    def atualizar(self, norma_id: uuid.UUID, dados: NormaDrisRequest) -> NormaDris:
        norma = self._obter(norma_id)
        norma.cultura = dados.cultura
        norma.estadio_fenologico = dados.estadio_fenologico
        norma.matriz_relacoes_duais = {
            rel: params.model_dump() for rel, params in dados.matriz_relacoes_duais.items()
        }
        return norma

    def inativar(self, norma_id: uuid.UUID) -> None:
        # RF004 A1 — impede uso em novas amostras, preserva o histórico
        self._obter(norma_id).ativa = False


class InsumoService:
    def __init__(self, db: Session):
        self.repo = InsumoRepository(db)

    def listar(self) -> list[Insumo]:
        return self.repo.listar()

    def criar(self, dados: InsumoRequest) -> Insumo:
        return self.repo.adicionar(Insumo(**dados.model_dump()))

    def _obter(self, insumo_id: uuid.UUID) -> Insumo:
        insumo = self.repo.obter_por_id(insumo_id)
        if not insumo:
            raise RecursoNaoEncontradoError("Insumo não encontrado.")
        return insumo

    def atualizar(self, insumo_id: uuid.UUID, dados: InsumoRequest) -> Insumo:
        insumo = self._obter(insumo_id)
        for campo, valor in dados.model_dump().items():
            setattr(insumo, campo, valor)
        return insumo

    def inativar(self, insumo_id: uuid.UUID) -> None:
        self._obter(insumo_id).ativo = False


class ProdutorService:
    def __init__(self, db: Session):
        self.repo = ProdutorRepository(db)

    def listar(self, agronomo_id: uuid.UUID) -> list[Produtor]:
        return self.repo.listar_do_agronomo(agronomo_id)

    def criar(self, agronomo_id: uuid.UUID, dados: ProdutorRequest) -> Produtor:
        if self.repo.obter_por_documento(dados.cpf_cnpj, agronomo_id):
            raise ConflitoError("CPF/CNPJ já cadastrado na sua carteira.")  # RF006 A3
        return self.repo.adicionar(Produtor(agronomo_id=agronomo_id, **dados.model_dump()))

    def _obter(self, produtor_id: uuid.UUID, agronomo_id: uuid.UUID) -> Produtor:
        produtor = self.repo.obter_do_agronomo(produtor_id, agronomo_id)
        if not produtor:
            raise RecursoNaoEncontradoError("Produtor não encontrado.")
        return produtor

    def atualizar(
        self, produtor_id: uuid.UUID, agronomo_id: uuid.UUID, dados: ProdutorRequest
    ) -> Produtor:
        produtor = self._obter(produtor_id, agronomo_id)
        existente = self.repo.obter_por_documento(dados.cpf_cnpj, agronomo_id)
        if existente and existente.id != produtor_id:
            raise ConflitoError("CPF/CNPJ já cadastrado na sua carteira.")
        for campo, valor in dados.model_dump().items():
            setattr(produtor, campo, valor)
        return produtor

    def inativar(self, produtor_id: uuid.UUID, agronomo_id: uuid.UUID) -> None:
        self._obter(produtor_id, agronomo_id).ativo = False


class PropriedadeService:
    def __init__(self, db: Session):
        self.repo = PropriedadeRepository(db)
        self.produtor_repo = ProdutorRepository(db)

    def listar(self, agronomo_id: uuid.UUID) -> list[Propriedade]:
        return self.repo.listar_do_agronomo(agronomo_id)

    def _validar_produtor(self, produtor_id: uuid.UUID, agronomo_id: uuid.UUID) -> None:
        # RN002 — o vínculo hierárquico é obrigatório e restrito à carteira do agrônomo
        if not self.produtor_repo.obter_do_agronomo(produtor_id, agronomo_id):
            raise RecursoNaoEncontradoError("Produtor não encontrado na sua carteira.")

    def criar(self, agronomo_id: uuid.UUID, dados: PropriedadeRequest) -> Propriedade:
        self._validar_produtor(dados.produtor_id, agronomo_id)
        return self.repo.adicionar(Propriedade(**dados.model_dump()))

    def _obter(self, propriedade_id: uuid.UUID, agronomo_id: uuid.UUID) -> Propriedade:
        propriedade = self.repo.obter_do_agronomo(propriedade_id, agronomo_id)
        if not propriedade:
            raise RecursoNaoEncontradoError("Propriedade não encontrada.")
        return propriedade

    def atualizar(
        self, propriedade_id: uuid.UUID, agronomo_id: uuid.UUID, dados: PropriedadeRequest
    ) -> Propriedade:
        propriedade = self._obter(propriedade_id, agronomo_id)
        self._validar_produtor(dados.produtor_id, agronomo_id)
        for campo, valor in dados.model_dump().items():
            setattr(propriedade, campo, valor)
        return propriedade

    def inativar(self, propriedade_id: uuid.UUID, agronomo_id: uuid.UUID) -> None:
        self._obter(propriedade_id, agronomo_id).ativo = False


class TalhaoService:
    def __init__(self, db: Session):
        self.repo = TalhaoRepository(db)
        self.propriedade_repo = PropriedadeRepository(db)

    def listar(self, agronomo_id: uuid.UUID) -> list[Talhao]:
        return self.repo.listar_do_agronomo(agronomo_id)

    def _validar_propriedade(self, propriedade_id: uuid.UUID, agronomo_id: uuid.UUID) -> None:
        if not self.propriedade_repo.obter_do_agronomo(propriedade_id, agronomo_id):
            raise RecursoNaoEncontradoError("Propriedade não encontrada na sua carteira.")

    def criar(self, agronomo_id: uuid.UUID, dados: TalhaoRequest) -> Talhao:
        self._validar_propriedade(dados.propriedade_id, agronomo_id)
        return self.repo.adicionar(Talhao(**dados.model_dump()))

    def _obter(self, talhao_id: uuid.UUID, agronomo_id: uuid.UUID) -> Talhao:
        talhao = self.repo.obter_do_agronomo(talhao_id, agronomo_id)
        if not talhao:
            raise RecursoNaoEncontradoError("Talhão não encontrado.")
        return talhao

    def atualizar(
        self, talhao_id: uuid.UUID, agronomo_id: uuid.UUID, dados: TalhaoRequest
    ) -> Talhao:
        talhao = self._obter(talhao_id, agronomo_id)
        self._validar_propriedade(dados.propriedade_id, agronomo_id)
        for campo, valor in dados.model_dump().items():
            setattr(talhao, campo, valor)
        return talhao

    def inativar(self, talhao_id: uuid.UUID, agronomo_id: uuid.UUID) -> None:
        self._obter(talhao_id, agronomo_id).ativo = False
