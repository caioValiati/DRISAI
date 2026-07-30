import uuid

from sqlalchemy.orm import Session

from app.api.v1.schemas.auth import AtualizarPerfilRequest, LoginRequest, RegistroRequest
from app.core.security import hash_senha, verificar_senha
from app.domain.enums import PerfilUsuario
from app.domain.exceptions import AcessoNegadoError, ConflitoError, RecursoNaoEncontradoError
from app.infrastructure.db.models import Usuario
from app.infrastructure.repositories.usuario_repository import UsuarioRepository


class AuthService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def registrar(self, dados: RegistroRequest) -> Usuario:
        """RF001 — cadastro público sempre cria perfil AGRONOMO; admins são provisionados."""
        if self.repo.obter_por_email(dados.email):
            raise ConflitoError("Já existe uma conta com este e-mail.")
        usuario = Usuario(
            perfil=PerfilUsuario.AGRONOMO,
            nome=dados.nome,
            email=dados.email,
            senha_hash=hash_senha(dados.senha),
            registro_crea=dados.registro_crea,
        )
        return self.repo.adicionar(usuario)

    def autenticar(self, dados: LoginRequest) -> Usuario:
        usuario = self.repo.obter_por_email(dados.email)
        if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
            raise AcessoNegadoError("E-mail ou senha inválidos.")
        if not usuario.ativo:
            raise AcessoNegadoError("Esta conta está desativada.")
        return usuario

    def atualizar_perfil(self, usuario_id: uuid.UUID, dados: AtualizarPerfilRequest) -> Usuario:
        usuario = self.repo.obter_por_id(usuario_id)
        if not usuario:
            raise RecursoNaoEncontradoError("Usuário não encontrado.")
        existente = self.repo.obter_por_email(dados.email)
        if existente and existente.id != usuario_id:
            raise ConflitoError("Já existe uma conta com este e-mail.")
        usuario.nome = dados.nome
        usuario.email = dados.email
        return usuario

    def desativar_conta(self, usuario_id: uuid.UUID) -> None:
        usuario = self.repo.obter_por_id(usuario_id)
        if not usuario:
            raise RecursoNaoEncontradoError("Usuário não encontrado.")
        usuario.ativo = False
