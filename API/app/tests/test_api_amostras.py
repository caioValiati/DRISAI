# tests/test_api_amostras.py
import uuid
from app.main import app
from app.core.deps import get_current_user
from app.infrastructure.db.models import Usuario, AmostraFoliar
from app.domain.enums import PerfilUsuario, StatusAmostra

# Simula um usuário autenticado
USUARIO_TESTE = Usuario(
    id=uuid.uuid4(),
    nome="Autenticado",
    email="auth@dris.ai",
    perfil=PerfilUsuario.AGRONOMO,
    ativo=True
)

def override_get_current_user():
    return USUARIO_TESTE

# Substitui a dependência real pelo nosso mock temporariamente
app.dependency_overrides[get_current_user] = override_get_current_user

def test_criar_amostra_valida_e_retorna_201(cliente, mocker):
    # Payload válido conforme AmostraRequest
    payload = {
        "talhao_id": str(uuid.uuid4()),
        "norma_dris_id": str(uuid.uuid4()),
        "data_coleta": "2026-03-15",
        "teores": {
            "N": 40.0, "P": 3.0, "K": 20.0, "Ca": 5.0, "Mg": 3.0, 
            "S": 2.0, "Zn": 40.0, "B": 30.0, "Cu": 5.0, "Fe": 100.0, "Mn": 30.0
        }
    }

    # Mock do retorno do AmostraService.criar_e_processar
    amostra_mock = AmostraFoliar(
        id=uuid.uuid4(),
        talhao_id=uuid.UUID(payload["talhao_id"]),
        norma_dris_id=uuid.UUID(payload["norma_dris_id"]),
        data_coleta=payload["data_coleta"],
        status=StatusAmostra.AGUARDANDO_REVISAO,
        valor_ibn=15.42,
        indices=[] # Simplificado para o teste
    )
    
    mock_service = mocker.patch("app.api.v1.routers.amostras.AmostraService")
    instancia_servico = mock_service.return_value
    instancia_servico.criar_e_processar.return_value = amostra_mock

    # Executa a rota protegida
    resposta = cliente.post("/api/v1/amostras", json=payload)

    # Validações
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["status"] == StatusAmostra.AGUARDANDO_REVISAO
    assert dados["valor_ibn"] == "15.42"
    instancia_servico.criar_e_processar.assert_called_once()

def test_criar_amostra_rejeita_teores_incompletos(cliente):
    # Faltam nutrientes obrigatórios (ex: 'N' e 'P')
    payload_invalido = {
        "talhao_id": str(uuid.uuid4()),
        "norma_dris_id": str(uuid.uuid4()),
        "data_coleta": "2026-03-15",
        "teores": {"K": 20.0}
    }

    resposta = cliente.post("/api/v1/amostras", json=payload_invalido)

    # Validação do Pydantic (Erro 422 Unprocessable Entity)
    assert resposta.status_code == 422
    detalhes = resposta.json()["detail"][0]
    assert detalhes["loc"] == ["body", "teores"]
    assert "Teores obrigatórios ausentes" in detalhes["msg"]