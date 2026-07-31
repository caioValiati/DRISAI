class DominioError(Exception):
    """Erro de regra de negócio. Convertido em HTTP 4xx na camada de API."""

    status_code = 400

    def __init__(self, mensagem: str):
        self.mensagem = mensagem
        super().__init__(mensagem)


class RecursoNaoEncontradoError(DominioError):
    status_code = 404


class ConflitoError(DominioError):
    """Violação de unicidade (ex.: CPF/CNPJ já cadastrado — RF006 A3)."""

    status_code = 409


class AmostraImutavelError(DominioError):
    """RN006 — amostra concluída não pode ser alterada."""

    status_code = 409

    def __init__(self):
        super().__init__("Amostra concluída é imutável e não pode ser alterada.")


class AcessoNegadoError(DominioError):
    status_code = 403
