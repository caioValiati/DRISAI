"""Repositórios dos agregados de curadoria e da carteira do agrônomo.

Todas as consultas da carteira são obrigatoriamente escopadas pelo
`agronomo_id` (multi-tenancy — MER: PRODUTOR.agronomo_id).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

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

    def listar_do_agronomo(self, agronomo_id: uuid.UUID) -> list[Produtor]:
        return list(
            self.db.scalars(
                select(Produtor)
                .where(Produtor.agronomo_id == agronomo_id)
                .order_by(Produtor.nome_razao)
            )
        )

    def obter_do_agronomo(self, produtor_id: uuid.UUID, agronomo_id: uuid.UUID) -> Produtor | None:
        return self.db.scalar(
            select(Produtor).where(
                Produtor.id == produtor_id, Produtor.agronomo_id == agronomo_id
            )
        )

    def obter_por_documento(self, cpf_cnpj: str, agronomo_id: uuid.UUID) -> Produtor | None:
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

    def listar_do_agronomo(self, agronomo_id: uuid.UUID) -> list[Propriedade]:
        return list(
            self.db.scalars(
                select(Propriedade)
                .join(Produtor)
                .where(Produtor.agronomo_id == agronomo_id)
                .order_by(Propriedade.nome_fazenda)
            )
        )

    def obter_do_agronomo(
        self, propriedade_id: uuid.UUID, agronomo_id: uuid.UUID
    ) -> Propriedade | None:
        return self.db.scalar(
            select(Propriedade)
            .join(Produtor)
            .where(Propriedade.id == propriedade_id, Produtor.agronomo_id == agronomo_id)
        )

    def adicionar(self, propriedade: Propriedade) -> Propriedade:
        self.db.add(propriedade)
        self.db.flush()
        return propriedade


class TalhaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar_do_agronomo(self, agronomo_id: uuid.UUID) -> list[Talhao]:
        return list(
            self.db.scalars(
                select(Talhao)
                .join(Propriedade)
                .join(Produtor)
                .where(Produtor.agronomo_id == agronomo_id)
                .order_by(Talhao.identificacao)
            )
        )

    def obter_do_agronomo(self, talhao_id: uuid.UUID, agronomo_id: uuid.UUID) -> Talhao | None:
        return self.db.scalar(
            select(Talhao)
            .join(Propriedade)
            .join(Produtor)
            .where(Talhao.id == talhao_id, Produtor.agronomo_id == agronomo_id)
        )

    def adicionar(self, talhao: Talhao) -> Talhao:
        self.db.add(talhao)
        self.db.flush()
        return talhao
