import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.enums import PerfilUsuario


class RegistroRequest(BaseModel):
    nome: str = Field(min_length=3, max_length=255)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    registro_crea: str = Field(min_length=3, max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    registro_crea: str | None
    ativo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class AtualizarPerfilRequest(BaseModel):
    nome: str = Field(min_length=3, max_length=255)
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
