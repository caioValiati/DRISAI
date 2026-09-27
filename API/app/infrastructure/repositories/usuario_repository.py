import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def obter_por_id(self, usuario_id: uuid.UUID) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)

    def obter_por_email(self, email: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.email == email))

    def adicionar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.flush()
        return usuario