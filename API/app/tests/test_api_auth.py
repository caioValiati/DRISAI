# tests/test_api_auth.py
from unittest.mock import MagicMock
from app.infrastructure.db.models import Usuario
from app.domain.enums import PerfilUsuario
from app.domain.exceptions import AcessoNegadoError

def test_login_sucesso_retorna_token_e_define_cookie(cliente, mocker):
    usuario_mock = Usuario(
        id="123e4567-e89b-12d3-a456-426614174000",
        nome="Agrônomo Teste",
        email="teste@dris.ai",
        perfil=PerfilUsuario.AGRONOMO,
        ativo=True,
    )
    
    mock_auth_service = mocker.patch("app.api.v1.routers.auth.AuthService")
    instancia_servico = mock_auth_service.return_value
    instancia_servico.autenticar.return_value = usuario_mock

    resposta = cliente.post(
        "/api/v1/auth/login", 
        json={"email": "teste@dris.ai", "senha": "senha_correta"}
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert "access_token" in dados
    assert dados["token_type"] == "bearer"
    assert dados["usuario"]["email"] == "teste@dris.ai"
    
    assert "drisai_refresh" in resposta.cookies

def test_login_falha_retorna_401(cliente, mocker):
    mock_auth_service = mocker.patch("app.api.v1.routers.auth.AuthService")
    instancia_servico = mock_auth_service.return_value
    instancia_servico.autenticar.side_effect = AcessoNegadoError("E-mail ou senha inválidos.")

    resposta = cliente.post(
        "/api/v1/auth/login", 
        json={"email": "errado@dris.ai", "senha": "errada"}
    )

    assert resposta.status_code == 403
    assert resposta.json() == {"detail": "E-mail ou senha inválidos."}