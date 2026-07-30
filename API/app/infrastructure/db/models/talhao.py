import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, BaseModelMixin


class Talhao(Base, BaseModelMixin):
    __tablename__ = "talhao"

    propriedade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("propriedade.id"), nullable=False, index=True
    )
    identificacao: Mapped[str] = mapped_column(String(120), nullable=False)
    tamanho_ha: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    historico_culturas: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    propriedade: Mapped["Propriedade"] = relationship(back_populates="talhoes")  # noqa: F821
