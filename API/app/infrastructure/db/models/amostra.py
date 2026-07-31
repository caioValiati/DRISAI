import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ClassificacaoNutriente, StatusAmostra
from app.infrastructure.db.base import Base, BaseModelMixin


class AmostraFoliar(Base, BaseModelMixin):
    __tablename__ = "amostra_foliar"

    talhao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("talhao.id"), nullable=False, index=True
    )
    norma_dris_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("norma_dris.id"), nullable=False
    )
    data_coleta: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[StatusAmostra] = mapped_column(
        Enum(StatusAmostra, name="status_amostra"),
        nullable=False,
        default=StatusAmostra.RASCUNHO,
    )
    valor_ibn: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    # Cópia da matriz de relações duais vigente no momento do cálculo. Sem ela,
    # editar uma norma tornaria os índices de laudos antigos irreproduzíveis,
    # quebrando a rastreabilidade exigida pela RN006.
    norma_snapshot: Mapped[dict | None] = mapped_column(JSONB)

    talhao: Mapped["Talhao"] = relationship()  # noqa: F821
    norma: Mapped["NormaDris"] = relationship()  # noqa: F821
    indices: Mapped[list["IndiceNutricional"]] = relationship(
        back_populates="amostra", cascade="all, delete-orphan"
    )
    recomendacao: Mapped["Recomendacao | None"] = relationship(  # noqa: F821
        back_populates="amostra", uselist=False, cascade="all, delete-orphan"
    )


class IndiceNutricional(Base, BaseModelMixin):
    __tablename__ = "indice_nutricional"
    __table_args__ = (
        UniqueConstraint("amostra_foliar_id", "elemento", name="uq_indice_amostra_elemento"),
    )

    amostra_foliar_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("amostra_foliar.id"), nullable=False, index=True
    )
    elemento: Mapped[str] = mapped_column(String(5), nullable=False)  # N, P, K, ...
    valor_laboratorio: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    indice_dris_calculado: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    classificacao: Mapped[ClassificacaoNutriente | None] = mapped_column(
        Enum(ClassificacaoNutriente, name="classificacao_nutriente")
    )

    amostra: Mapped["AmostraFoliar"] = relationship(back_populates="indices")
