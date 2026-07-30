from enum import StrEnum


class PerfilUsuario(StrEnum):
    ADMIN = "ADMIN"
    AGRONOMO = "AGRONOMO"


class StatusAmostra(StrEnum):
    RASCUNHO = "RASCUNHO"
    AGUARDANDO_REVISAO = "AGUARDANDO_REVISAO"
    CONCLUIDA = "CONCLUIDA"


class ClassificacaoNutriente(StrEnum):
    DEFICIENTE = "DEFICIENTE"
    EQUILIBRIO = "EQUILIBRIO"
    EXCESSO = "EXCESSO"


# Ordem canônica dos 11 nutrientes do DERS (Quadro 40)
NUTRIENTES = ["N", "P", "K", "Ca", "Mg", "S", "Zn", "B", "Cu", "Fe", "Mn"]
