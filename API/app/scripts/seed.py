"""Seed de dados iniciais: usuário ADMIN e a norma DRIS de validação do projeto.

Uso: uv run python -m app.scripts.seed
"""

from app.core.security import hash_senha
from app.domain.enums import PerfilUsuario
from app.infrastructure.db.models import NormaDris, Usuario
from app.infrastructure.db.session import SessionLocal
from sqlalchemy import select

ADMIN_EMAIL = "admin@drisai.com.br"
ADMIN_SENHA = "Admin@123456"

# Norma DRIS para soja em R2 — sul do Maranhão (HOOGERHEIDE, 2005), citada no DERS
# como base de validação. Valores de exemplo estruturados no formato do sistema;
# substituir pelos valores integrais da Figura 1 quando forem transcritos.
NORMA_SOJA = {
    "N/P": {"media": 10.94, "dp": 1.31, "cv": 11.98},
    "N/K": {"media": 2.60, "dp": 0.42, "cv": 16.15},
    "K/P": {"media": 4.31, "dp": 0.87, "cv": 20.19},
    "Ca/P": {"media": 3.12, "dp": 0.77, "cv": 24.68},
    "Ca/Mg": {"media": 2.51, "dp": 0.51, "cv": 20.32},
    "N/S": {"media": 17.32, "dp": 3.24, "cv": 18.71},
    "P/S": {"media": 1.59, "dp": 0.28, "cv": 17.61},
    "K/Ca": {"media": 1.45, "dp": 0.41, "cv": 28.28},
    "Mg/S": {"media": 1.61, "dp": 0.37, "cv": 22.98},
    "Fe/Mn": {"media": 2.09, "dp": 0.85, "cv": 40.67},
    "Zn/B": {"media": 0.85, "dp": 0.29, "cv": 34.12},
    "Cu/Zn": {"media": 0.28, "dp": 0.09, "cv": 32.14},
}


def executar() -> None:
    db = SessionLocal()
    try:
        if not db.scalar(select(Usuario).where(Usuario.email == ADMIN_EMAIL)):
            db.add(
                Usuario(
                    perfil=PerfilUsuario.ADMIN,
                    nome="Administrador DRISAI",
                    email=ADMIN_EMAIL,
                    senha_hash=hash_senha(ADMIN_SENHA),
                )
            )
            print(f"Admin criado: {ADMIN_EMAIL} / {ADMIN_SENHA}")
        else:
            print("Admin já existe — nada a fazer.")

        if not db.scalar(select(NormaDris).where(NormaDris.cultura == "Soja")):
            db.add(
                NormaDris(
                    cultura="Soja",
                    estadio_fenologico="R2",
                    matriz_relacoes_duais=NORMA_SOJA,
                )
            )
            print("Norma DRIS de Soja (R2) criada.")
        else:
            print("Norma de Soja já existe — nada a fazer.")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    executar()
