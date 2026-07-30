import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, BaseModelMixin


class Produtor(Base, BaseModelMixin):
    __tablename__ = "produtor"
    # RF006 A3 — unicidade do documento dentro da carteira de cada agrônomo
    __table_args__ = (UniqueConstraint("agronomo_id", "cpf_cnpj", name="uq_produtor_agronomo_doc"),)

    agronomo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False, index=True
    )
    nome_razao: Mapped[str] = mapped_column(String(255), nullable=False)
    cpf_cnpj: Mapped[str] = mapped_column(String(18), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    propriedades: Mapped[list["Propriedade"]] = relationship(back_populates="produtor")  # noqa: F821
