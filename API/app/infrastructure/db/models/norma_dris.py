from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, BaseModelMixin


class NormaDris(Base, BaseModelMixin):
    __tablename__ = "norma_dris"

    cultura: Mapped[str] = mapped_column(String(120), nullable=False)
    estadio_fenologico: Mapped[str] = mapped_column(String(120), nullable=False)
    # {"N/P": {"media": 10.9, "dp": 1.31, "cv": 12.0}, ...} — média, desvio-padrão
    # e CV por relação dual (Quadro 25 do DERS + Figura 1 de Hoogerheide, 2005)
    matriz_relacoes_duais: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
