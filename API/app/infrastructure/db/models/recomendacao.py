import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, BaseModelMixin


class Recomendacao(Base, BaseModelMixin):
    __tablename__ = "recomendacao"

    # Relacionamento 1:1 com a amostra (MER, Figura 27)
    amostra_foliar_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("amostra_foliar.id"), nullable=False, unique=True
    )
    texto_rascunho_ia: Mapped[str | None] = mapped_column(Text)  # preenchido na Fase 2
    texto_final_editado: Mapped[str | None] = mapped_column(Text)
    data_emissao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    amostra: Mapped["AmostraFoliar"] = relationship(back_populates="recomendacao")  # noqa: F821
    insumos_sugeridos: Mapped[list["RecomendacaoInsumo"]] = relationship(
        back_populates="recomendacao", cascade="all, delete-orphan"
    )


class RecomendacaoInsumo(Base, BaseModelMixin):
    """Associativa N:N com o match_score do motor de ML (preenchida na Fase 2)."""

    __tablename__ = "recomendacao_insumo"

    recomendacao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recomendacao.id"), nullable=False, index=True
    )
    insumo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("insumo.id"), nullable=False
    )
    match_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    recomendacao: Mapped["Recomendacao"] = relationship(back_populates="insumos_sugeridos")
