import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decodificar_token
from app.domain.enums import PerfilUsuario
from app.infrastructure.db.models import Usuario
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.usuario_repository import UsuarioRepository

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> Usuario:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado.")
    try:
        payload = decodificar_token(credentials.credentials, tipo_esperado="access")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado.")
    usuario = UsuarioRepository(db).obter_por_id(uuid.UUID(payload["sub"]))
    if not usuario or not usuario.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário inativo ou inexistente.")
    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def _exigir_perfil(perfil: PerfilUsuario):
    def dependencia(usuario: CurrentUser) -> Usuario:
        if usuario.perfil != perfil:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso negado para este perfil.")
        return usuario

    return dependencia


# RF003 — RBAC: Admin cuida da curadoria (normas/insumos); Agrônomo, da consultoria
CurrentAdmin = Annotated[Usuario, Depends(_exigir_perfil(PerfilUsuario.ADMIN))]
CurrentAgronomo = Annotated[Usuario, Depends(_exigir_perfil(PerfilUsuario.AGRONOMO))]
