import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.db.models import AmostraFoliar, Produtor, Propriedade, Talhao


class AmostraRepository:
    def __init__(self, db: Session):
        self.db = db

    def _query_escopada(self, agronomo_id: uuid.UUID):
        return (
            select(AmostraFoliar)
            .join(Talhao)
            .join(Propriedade)
            .join(Produtor)
            .where(Produtor.agronomo_id == agronomo_id)
        )

    def listar_do_agronomo(self, agronomo_id: uuid.UUID) -> list[AmostraFoliar]:
        return list(
            self.db.scalars(
                self._query_escopada(agronomo_id).order_by(AmostraFoliar.data_coleta.desc())
            )
        )

    def obter_do_agronomo(
        self, amostra_id: uuid.UUID, agronomo_id: uuid.UUID
    ) -> AmostraFoliar | None:
        return self.db.scalar(
            self._query_escopada(agronomo_id)
            .where(AmostraFoliar.id == amostra_id)
            .options(
                selectinload(AmostraFoliar.indices),
                selectinload(AmostraFoliar.recomendacao),
            )
        )

    def adicionar(self, amostra: AmostraFoliar) -> AmostraFoliar:
        self.db.add(amostra)
        self.db.flush()
        return amostra
