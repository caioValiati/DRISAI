import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

# Descobre o caminho absoluto para a raiz do projeto (onde o .env fica)
# Como este arquivo está em app/core/config.py, subimos 3 níveis (.parent)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    # Passamos o caminho absoluto fixo para evitar erros de subprocessos no Windows
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = ["http://localhost:5173"]
    cookie_secure: bool = False
    
    # RF011 — redação automática do laudo. Sem chave configurada o sistema segue
    # operando pelo fluxo alternativo A1, apenas sem o rascunho textual.
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # API KEY do Resend
    resend_api_key: str = (
        ""  # Valor padrão vazio ou None se não for obrigatório
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
