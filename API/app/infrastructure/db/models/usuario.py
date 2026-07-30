from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import PerfilUsuario
from app.infrastructure.db.base import Base, BaseModelMixin


class Usuario(Base, BaseModelMixin):
    __tablename__ = "usuario"

    perfil: Mapped[PerfilUsuario] = mapped_column(
        Enum(PerfilUsuario, name="perfil_usuario"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Nulo quando perfil = ADMIN (MER, Figura 27)
    registro_crea: Mapped[str | None] = mapped_column(String(50))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
