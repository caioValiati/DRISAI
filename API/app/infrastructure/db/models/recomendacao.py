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
    texto_rascunho_ia: Mapped[str | None] = mapped_column(Text)
    texto_final_editado: Mapped[str | None] = mapped_column(Text)
    data_emissao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # RF011 A1 — registra por que o rascunho veio vazio, para a tela avisar o
    # agrônomo de que a redação automática ficou indisponível naquele processamento
    falha_ia: Mapped[str | None] = mapped_column(Text)

    amostra: Mapped["AmostraFoliar"] = relationship(back_populates="recomendacao")  # noqa: F821
    # Ordenado pelo score para que a resposta e o laudo sempre apresentem os
    # insumos do mais aderente ao menos aderente
    insumos_sugeridos: Mapped[list["RecomendacaoInsumo"]] = relationship(
        back_populates="recomendacao",
        cascade="all, delete-orphan",
        order_by="RecomendacaoInsumo.match_score.desc()",
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
    insumo: Mapped["Insumo"] = relationship()  # noqa: F821
