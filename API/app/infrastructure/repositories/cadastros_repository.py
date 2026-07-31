"""Repositórios dos agregados de curadoria e da carteira do agrônomo.

As consultas de carteira recebem um `agronomo_id` opcional: quando informado,
restringem o resultado àquela carteira (multi-tenancy do Agrônomo); quando
`None`, não filtram — é a visão global do Administrador.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.db.models import (
    Insumo,
    NormaDris,
    Produtor,
    Propriedade,
    Talhao,
)


class NormaDrisRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[NormaDris]:
        return list(self.db.scalars(select(NormaDris).order_by(NormaDris.cultura)))

    def obter_por_id(self, norma_id: uuid.UUID) -> NormaDris | None:
        return self.db.get(NormaDris, norma_id)

    def adicionar(self, norma: NormaDris) -> NormaDris:
        self.db.add(norma)
        self.db.flush()
        return norma


class InsumoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Insumo]:
        return list(self.db.scalars(select(Insumo).order_by(Insumo.nome_comercial)))

    def obter_por_id(self, insumo_id: uuid.UUID) -> Insumo | None:
        return self.db.get(Insumo, insumo_id)

    def adicionar(self, insumo: Insumo) -> Insumo:
        self.db.add(insumo)
        self.db.flush()
        return insumo


class ProdutorRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, agronomo_id: uuid.UUID | None) -> list[Produtor]:
        query = select(Produtor).options(joinedload(Produtor.agronomo))
        if agronomo_id:
            query = query.where(Produtor.agronomo_id == agronomo_id)
        return list(self.db.scalars(query.order_by(Produtor.nome_razao)))

    def obter(self, produtor_id: uuid.UUID, agronomo_id: uuid.UUID | None) -> Produtor | None:
        query = select(Produtor).where(Produtor.id == produtor_id)
        if agronomo_id:
            query = query.where(Produtor.agronomo_id == agronomo_id)
        return self.db.scalar(query)

    def obter_por_documento(self, cpf_cnpj: str, agronomo_id: uuid.UUID) -> Produtor | None:
        """A unicidade do documento é sempre avaliada dentro de uma carteira."""
        return self.db.scalar(
            select(Produtor).where(
                Produtor.cpf_cnpj == cpf_cnpj, Produtor.agronomo_id == agronomo_id
            )
        )

    def adicionar(self, produtor: Produtor) -> Produtor:
        self.db.add(produtor)
        self.db.flush()
        return produtor


class PropriedadeRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, agronomo_id: uuid.UUID | None) -> list[Propriedade]:
        query = select(Propriedade).options(
            joinedload(Propriedade.produtor).joinedload(Produtor.agronomo)
        )
        if agronomo_id:
            query = query.join(Produtor).where(Produtor.agronomo_id == agronomo_id)
        return list(self.db.scalars(query.order_by(Propriedade.nome_fazenda)))

    def obter(
        self, propriedade_id: uuid.UUID, agronomo_id: uuid.UUID | None
    ) -> Propriedade | None:
        query = select(Propriedade).where(Propriedade.id == propriedade_id)
        if agronomo_id:
            query = query.join(Produtor).where(Produtor.agronomo_id == agronomo_id)
        return self.db.scalar(query)

    def adicionar(self, propriedade: Propriedade) -> Propriedade:
        self.db.add(propriedade)
        self.db.flush()
        return propriedade


class TalhaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, agronomo_id: uuid.UUID | None) -> list[Talhao]:
        query = select(Talhao).options(
            joinedload(Talhao.propriedade)
            .joinedload(Propriedade.produtor)
            .joinedload(Produtor.agronomo)
        )
        if agronomo_id:
            query = query.join(Propriedade).join(Produtor).where(
                Produtor.agronomo_id == agronomo_id
            )
        return list(self.db.scalars(query.order_by(Talhao.identificacao)))

    def obter(self, talhao_id: uuid.UUID, agronomo_id: uuid.UUID | None) -> Talhao | None:
        query = select(Talhao).where(Talhao.id == talhao_id)
        if agronomo_id:
            query = query.join(Propriedade).join(Produtor).where(
                Produtor.agronomo_id == agronomo_id
            )
        return self.db.scalar(query)

    def adicionar(self, talhao: Talhao) -> Talhao:
        self.db.add(talhao)
        self.db.flush()
        return talhao
