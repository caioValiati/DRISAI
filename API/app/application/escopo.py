"""Regra de visibilidade dos registros de carteira.

O Administrador supervisiona a plataforma inteira: enxerga e mantém os registros
de todos os agrônomos. O Agrônomo enxerga apenas a própria carteira.
"""

import uuid

from app.domain.enums import PerfilUsuario
from app.infrastructure.db.models import Usuario


def escopo_de(usuario: Usuario) -> uuid.UUID | None:
    """Devolve o `agronomo_id` usado como filtro, ou None quando não há filtro."""
    return None if usuario.perfil == PerfilUsuario.ADMIN else usuario.id
