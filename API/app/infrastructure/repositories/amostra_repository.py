import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.db.models import AmostraFoliar, Produtor, Propriedade, Talhao


class AmostraRepository:
    def __init__(self, db: Session):
        self.db = db

    def _query_escopada(self, agronomo_id: uuid.UUID | None):
        query = select(AmostraFoliar)
        if agronomo_id:
            query = (
                query.join(Talhao)
                .join(Propriedade)
                .join(Produtor)
                .where(Produtor.agronomo_id == agronomo_id)
            )
        return query

    def listar(self, agronomo_id: uuid.UUID | None) -> list[AmostraFoliar]:
        return list(
            self.db.scalars(
                self._query_escopada(agronomo_id).order_by(AmostraFoliar.data_coleta.desc())
            )
        )

    def obter(self, amostra_id: uuid.UUID, agronomo_id: uuid.UUID | None) -> AmostraFoliar | None:
        return self.db.scalar(
            self._query_escopada(agronomo_id)
            .where(AmostraFoliar.id == amostra_id)
            .options(
                selectinload(AmostraFoliar.indices),
                selectinload(AmostraFoliar.recomendacao),
            )
        )

    def contar_por_talhoes(self, talhao_ids: list[uuid.UUID]) -> int:
        if not talhao_ids:
            return 0
        return len(
            list(
                self.db.scalars(
                    select(AmostraFoliar.id).where(AmostraFoliar.talhao_id.in_(talhao_ids))
                )
            )
        )

    def adicionar(self, amostra: AmostraFoliar) -> AmostraFoliar:
        self.db.add(amostra)
        self.db.flush()
        return amostra
