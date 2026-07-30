from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, BaseModelMixin


class Insumo(Base, BaseModelMixin):
    __tablename__ = "insumo"

    nome_comercial: Mapped[str] = mapped_column(String(255), nullable=False)
    fabricante: Mapped[str] = mapped_column(String(255), nullable=False)
    # Lista de culturas (nomes) para as quais o insumo é autorizado (Quadro 28)
    culturas_autorizadas: Mapped[list] = mapped_column(JSONB, nullable=False)
    # {"N": 10.0, "P": 5.0, ...} — concentração percentual por nutriente
    concentracao_nutricional: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
