import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

_password_hash = PasswordHash.recommended()  # Argon2 — atende RNF003


def hash_senha(senha: str) -> str:
    return _password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return _password_hash.verify(senha, senha_hash)


def _criar_token(usuario_id: str, perfil: str, tipo: str, expira_em: timedelta) -> str:
    settings = get_settings()
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": usuario_id,
        "perfil": perfil,
        "tipo": tipo,
        "iat": agora,
        "exp": agora + expira_em,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def criar_access_token(usuario_id: str, perfil: str) -> str:
    settings = get_settings()
    return _criar_token(
        usuario_id, perfil, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )


def criar_refresh_token(usuario_id: str, perfil: str) -> str:
    settings = get_settings()
    return _criar_token(
        usuario_id, perfil, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


def decodificar_token(token: str, tipo_esperado: str) -> dict:
    """Decodifica e valida um JWT. Levanta jwt.InvalidTokenError se inválido/expirado."""
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if payload.get("tipo") != tipo_esperado:
        raise jwt.InvalidTokenError("Tipo de token inesperado")
    return payload
