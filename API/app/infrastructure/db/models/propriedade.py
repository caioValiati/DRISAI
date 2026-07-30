import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, BaseModelMixin


class Propriedade(Base, BaseModelMixin):
    __tablename__ = "propriedade"

    produtor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produtor.id"), nullable=False, index=True
    )
    nome_fazenda: Mapped[str] = mapped_column(String(255), nullable=False)
    municipio_uf: Mapped[str] = mapped_column(String(120), nullable=False)
    area_total_ha: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    produtor: Mapped["Produtor"] = relationship(back_populates="propriedades")  # noqa: F821
    talhoes: Mapped[list["Talhao"]] = relationship(back_populates="propriedade")  # noqa: F821
