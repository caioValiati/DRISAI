import uuid

import jwt
from fastapi import APIRouter, BackgroundTasks, Cookie, HTTPException, Response, status

from app.domain.exceptions import RecursoNaoEncontradoError
from app.infrastructure.email.email_service import EmailService
from app.api.v1.schemas.auth import (
    AtualizarPerfilRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegistroRequest,
    ResetPasswordRequest,
    TokenResponse,
    UsuarioResponse,
)
from app.application.services.auth_service import AuthService
from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.core.security import criar_access_token, criar_refresh_token, decodificar_token, criar_password_reset_token, hash_senha
from app.infrastructure.repositories.usuario_repository import UsuarioRepository

router = APIRouter(prefix="/auth", tags=["Autenticação"])
email_service = EmailService()

_REFRESH_COOKIE = "drisai_refresh"


def _definir_cookie_refresh(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 3600,
        path="/api/v1/auth",
    )

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    data: ForgotPasswordRequest,
    db: DbSession,
    background_tasks: BackgroundTasks,
):
    auth_service = AuthService(db)

    try:
        token = auth_service.solicitar_recuperacao_senha(data.email)

        background_tasks.add_task(
            email_service.send_reset_password_email, data.email, token
        )
    except RecursoNaoEncontradoError:
        pass

    return {
        "message": "Se o e-mail estiver cadastrado, as instruções foram enviadas."
    }


@router.post("/redefinir_senha", status_code=status.HTTP_200_OK)
def reset_password(data: ResetPasswordRequest, db: DbSession):
    auth_service = AuthService(db)

    auth_service.redefinir_senha(
        token=data.token, nova_senha=data.new_password
    )

    return {"message": "Senha redefinida com sucesso!"}

@router.post("/registrar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(dados: RegistroRequest, db: DbSession):
    return AuthService(db).registrar(dados)


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: DbSession, response: Response):
    usuario = AuthService(db).autenticar(dados)
    _definir_cookie_refresh(
        response, criar_refresh_token(str(usuario.id), usuario.perfil.value)
    )
    return TokenResponse(
        access_token=criar_access_token(str(usuario.id), usuario.perfil.value),
        usuario=UsuarioResponse.model_validate(usuario),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    db: DbSession,
    response: Response,
    drisai_refresh: str | None = Cookie(default=None),
):
    if not drisai_refresh:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token ausente.")
    try:
        payload = decodificar_token(drisai_refresh, tipo_esperado="refresh")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido ou expirado.")
    usuario = UsuarioRepository(db).obter_por_id(uuid.UUID(payload["sub"]))
    if not usuario or not usuario.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário inativo ou inexistente.")
    # Rotação do refresh token a cada uso
    _definir_cookie_refresh(
        response, criar_refresh_token(str(usuario.id), usuario.perfil.value)
    )
    return TokenResponse(
        access_token=criar_access_token(str(usuario.id), usuario.perfil.value),
        usuario=UsuarioResponse.model_validate(usuario),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(_REFRESH_COOKIE, path="/api/v1/auth")


@router.get("/me", response_model=UsuarioResponse)
def meu_perfil(usuario: CurrentUser):
    return usuario


@router.put("/me", response_model=UsuarioResponse)
def atualizar_perfil(dados: AtualizarPerfilRequest, usuario: CurrentUser, db: DbSession):
    return AuthService(db).atualizar_perfil(usuario.id, dados)


@router.post("/me/desativar", status_code=status.HTTP_204_NO_CONTENT)
def desativar_conta(usuario: CurrentUser, db: DbSession, response: Response):
    AuthService(db).desativar_conta(usuario.id)
    response.delete_cookie(_REFRESH_COOKIE, path="/api/v1/auth")
