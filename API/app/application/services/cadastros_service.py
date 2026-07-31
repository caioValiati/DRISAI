"""Casos de uso dos CRUDs de curadoria (RF004/RF005) e carteira (RF006–RF008).

Inativação e reativação seguem a hierarquia Produtor → Propriedade → Talhão:
inativar um registro propaga aos descendentes, e reativar um descendente exige
que a cadeia acima esteja ativa. Amostras nunca são inativadas — são ativos
históricos (RN006) —, mas entram na prévia de impacto como informação.
"""

import uuid

from sqlalchemy.orm import Session

from app.api.v1.schemas.cadastros import (
    ImpactoVinculo,
    ImpactoVinculosResponse,
    InsumoRequest,
    NormaDrisRequest,
    ProdutorRequest,
    PropriedadeRequest,
    TalhaoRequest,
)
from app.application.escopo import escopo_de
from app.domain.exceptions import ConflitoError, DominioError, RecursoNaoEncontradoError
from app.infrastructure.db.models import (
    Insumo,
    NormaDris,
    Produtor,
    Propriedade,
    Talhao,
    Usuario,
)
from app.infrastructure.repositories.amostra_repository import AmostraRepository
from app.infrastructure.repositories.cadastros_repository import (
    InsumoRepository,
    NormaDrisRepository,
    ProdutorRepository,
    PropriedadeRepository,
    TalhaoRepository,
)


class NormaDrisService:
    def __init__(self, db: Session):
        self.repo = NormaDrisRepository(db)

    def listar(self) -> list[NormaDris]:
        return self.repo.listar()

    def criar(self, dados: NormaDrisRequest) -> NormaDris:
        return self.repo.adicionar(
            NormaDris(
                cultura=dados.cultura,
                estadio_fenologico=dados.estadio_fenologico,
                matriz_relacoes_duais={
                    rel: params.model_dump(exclude_none=True)
                    for rel, params in dados.matriz_relacoes_duais.items()
                },
            )
        )

    def _obter(self, norma_id: uuid.UUID) -> NormaDris:
        norma = self.repo.obter_por_id(norma_id)
        if not norma:
            raise RecursoNaoEncontradoError("Norma DRIS não encontrada.")
        return norma

    def atualizar(self, norma_id: uuid.UUID, dados: NormaDrisRequest) -> NormaDris:
        norma = self._obter(norma_id)
        norma.cultura = dados.cultura
        norma.estadio_fenologico = dados.estadio_fenologico
        norma.matriz_relacoes_duais = {
            rel: params.model_dump(exclude_none=True)
            for rel, params in dados.matriz_relacoes_duais.items()
        }
        return norma

    def inativar(self, norma_id: uuid.UUID) -> None:
        # RF004 A1 — impede uso em novas amostras, preserva o histórico
        self._obter(norma_id).ativa = False

    def reativar(self, norma_id: uuid.UUID) -> None:
        self._obter(norma_id).ativa = True


class InsumoService:
    def __init__(self, db: Session):
        self.repo = InsumoRepository(db)

    def listar(self) -> list[Insumo]:
        return self.repo.listar()

    def criar(self, dados: InsumoRequest) -> Insumo:
        return self.repo.adicionar(Insumo(**dados.model_dump()))

    def _obter(self, insumo_id: uuid.UUID) -> Insumo:
        insumo = self.repo.obter_por_id(insumo_id)
        if not insumo:
            raise RecursoNaoEncontradoError("Insumo não encontrado.")
        return insumo

    def atualizar(self, insumo_id: uuid.UUID, dados: InsumoRequest) -> Insumo:
        insumo = self._obter(insumo_id)
        for campo, valor in dados.model_dump().items():
            setattr(insumo, campo, valor)
        return insumo

    def inativar(self, insumo_id: uuid.UUID) -> None:
        self._obter(insumo_id).ativo = False

    def reativar(self, insumo_id: uuid.UUID) -> None:
        self._obter(insumo_id).ativo = True


def _contar(itens, ativo: bool) -> int:
    return sum(1 for item in itens if item.ativo is ativo)


class ProdutorService:
    def __init__(self, db: Session):
        self.repo = ProdutorRepository(db)
        self.amostra_repo = AmostraRepository(db)

    def listar(self, usuario: Usuario) -> list[Produtor]:
        return self.repo.listar(escopo_de(usuario))

    def criar(self, usuario: Usuario, dados: ProdutorRequest) -> Produtor:
        # O registro pertence a quem o cadastrou, inclusive quando é o Administrador
        if self.repo.obter_por_documento(dados.cpf_cnpj, usuario.id):
            raise ConflitoError("CPF/CNPJ já cadastrado nesta carteira.")  # RF006 A3
        return self.repo.adicionar(Produtor(agronomo_id=usuario.id, **dados.model_dump()))

    def _obter(self, produtor_id: uuid.UUID, usuario: Usuario) -> Produtor:
        produtor = self.repo.obter(produtor_id, escopo_de(usuario))
        if not produtor:
            raise RecursoNaoEncontradoError("Produtor não encontrado.")
        return produtor

    def atualizar(
        self, produtor_id: uuid.UUID, usuario: Usuario, dados: ProdutorRequest
    ) -> Produtor:
        produtor = self._obter(produtor_id, usuario)
        # A duplicidade é checada na carteira do dono do registro, não na de quem edita
        existente = self.repo.obter_por_documento(dados.cpf_cnpj, produtor.agronomo_id)
        if existente and existente.id != produtor_id:
            raise ConflitoError("CPF/CNPJ já cadastrado nesta carteira.")
        for campo, valor in dados.model_dump().items():
            setattr(produtor, campo, valor)
        return produtor

    def _talhoes(self, produtor: Produtor) -> list[Talhao]:
        return [t for p in produtor.propriedades for t in p.talhoes]

    def vinculos(self, produtor_id: uuid.UUID, usuario: Usuario) -> ImpactoVinculosResponse:
        produtor = self._obter(produtor_id, usuario)
        talhoes = self._talhoes(produtor)
        return ImpactoVinculosResponse(
            vinculos=[
                ImpactoVinculo(
                    entidade="Propriedades",
                    ativos=_contar(produtor.propriedades, True),
                    inativos=_contar(produtor.propriedades, False),
                ),
                ImpactoVinculo(
                    entidade="Talhões",
                    ativos=_contar(talhoes, True),
                    inativos=_contar(talhoes, False),
                ),
            ],
            amostras_vinculadas=self.amostra_repo.contar_por_talhoes([t.id for t in talhoes]),
        )

    def inativar(self, produtor_id: uuid.UUID, usuario: Usuario) -> None:
        produtor = self._obter(produtor_id, usuario)
        produtor.ativo = False
        for propriedade in produtor.propriedades:
            propriedade.ativo = False
            for talhao in propriedade.talhoes:
                talhao.ativo = False

    def reativar(self, produtor_id: uuid.UUID, usuario: Usuario, cascata: bool) -> None:
        produtor = self._obter(produtor_id, usuario)
        produtor.ativo = True
        if not cascata:
            return
        for propriedade in produtor.propriedades:
            propriedade.ativo = True
            for talhao in propriedade.talhoes:
                talhao.ativo = True


class PropriedadeService:
    def __init__(self, db: Session):
        self.repo = PropriedadeRepository(db)
        self.produtor_repo = ProdutorRepository(db)
        self.amostra_repo = AmostraRepository(db)

    def listar(self, usuario: Usuario) -> list[Propriedade]:
        return self.repo.listar(escopo_de(usuario))

    def _validar_produtor(self, produtor_id: uuid.UUID, usuario: Usuario) -> Produtor:
        # RN002 — o vínculo hierárquico é obrigatório e precisa estar visível ao usuário
        produtor = self.produtor_repo.obter(produtor_id, escopo_de(usuario))
        if not produtor:
            raise RecursoNaoEncontradoError("Produtor não encontrado.")
        if not produtor.ativo:
            raise DominioError(
                f"O produtor {produtor.nome_razao} está inativo. Reative-o antes de "
                "vincular propriedades."
            )
        return produtor

    def criar(self, usuario: Usuario, dados: PropriedadeRequest) -> Propriedade:
        self._validar_produtor(dados.produtor_id, usuario)
        return self.repo.adicionar(Propriedade(**dados.model_dump()))

    def _obter(self, propriedade_id: uuid.UUID, usuario: Usuario) -> Propriedade:
        propriedade = self.repo.obter(propriedade_id, escopo_de(usuario))
        if not propriedade:
            raise RecursoNaoEncontradoError("Propriedade não encontrada.")
        return propriedade

    def atualizar(
        self, propriedade_id: uuid.UUID, usuario: Usuario, dados: PropriedadeRequest
    ) -> Propriedade:
        propriedade = self._obter(propriedade_id, usuario)
        if dados.produtor_id != propriedade.produtor_id:
            self._validar_produtor(dados.produtor_id, usuario)
        for campo, valor in dados.model_dump().items():
            setattr(propriedade, campo, valor)
        return propriedade

    def vinculos(self, propriedade_id: uuid.UUID, usuario: Usuario) -> ImpactoVinculosResponse:
        propriedade = self._obter(propriedade_id, usuario)
        return ImpactoVinculosResponse(
            vinculos=[
                ImpactoVinculo(
                    entidade="Talhões",
                    ativos=_contar(propriedade.talhoes, True),
                    inativos=_contar(propriedade.talhoes, False),
                )
            ],
            amostras_vinculadas=self.amostra_repo.contar_por_talhoes(
                [t.id for t in propriedade.talhoes]
            ),
        )

    def inativar(self, propriedade_id: uuid.UUID, usuario: Usuario) -> None:
        propriedade = self._obter(propriedade_id, usuario)
        propriedade.ativo = False
        for talhao in propriedade.talhoes:
            talhao.ativo = False

    def reativar(self, propriedade_id: uuid.UUID, usuario: Usuario, cascata: bool) -> None:
        propriedade = self._obter(propriedade_id, usuario)
        self._validar_produtor(propriedade.produtor_id, usuario)
        propriedade.ativo = True
        if not cascata:
            return
        for talhao in propriedade.talhoes:
            talhao.ativo = True


class TalhaoService:
    def __init__(self, db: Session):
        self.repo = TalhaoRepository(db)
        self.propriedade_repo = PropriedadeRepository(db)
        self.amostra_repo = AmostraRepository(db)

    def listar(self, usuario: Usuario) -> list[Talhao]:
        return self.repo.listar(escopo_de(usuario))

    def _validar_propriedade(self, propriedade_id: uuid.UUID, usuario: Usuario) -> Propriedade:
        propriedade = self.propriedade_repo.obter(propriedade_id, escopo_de(usuario))
        if not propriedade:
            raise RecursoNaoEncontradoError("Propriedade não encontrada.")
        if not propriedade.ativo:
            raise DominioError(
                f"A propriedade {propriedade.nome_fazenda} está inativa. Reative-a antes "
                "de vincular talhões."
            )
        return propriedade

    def criar(self, usuario: Usuario, dados: TalhaoRequest) -> Talhao:
        self._validar_propriedade(dados.propriedade_id, usuario)
        return self.repo.adicionar(Talhao(**dados.model_dump()))

    def _obter(self, talhao_id: uuid.UUID, usuario: Usuario) -> Talhao:
        talhao = self.repo.obter(talhao_id, escopo_de(usuario))
        if not talhao:
            raise RecursoNaoEncontradoError("Talhão não encontrado.")
        return talhao

    def atualizar(self, talhao_id: uuid.UUID, usuario: Usuario, dados: TalhaoRequest) -> Talhao:
        talhao = self._obter(talhao_id, usuario)
        if dados.propriedade_id != talhao.propriedade_id:
            self._validar_propriedade(dados.propriedade_id, usuario)
        for campo, valor in dados.model_dump().items():
            setattr(talhao, campo, valor)
        return talhao

    def vinculos(self, talhao_id: uuid.UUID, usuario: Usuario) -> ImpactoVinculosResponse:
        talhao = self._obter(talhao_id, usuario)
        return ImpactoVinculosResponse(
            vinculos=[],
            amostras_vinculadas=self.amostra_repo.contar_por_talhoes([talhao.id]),
        )

    def inativar(self, talhao_id: uuid.UUID, usuario: Usuario) -> None:
        self._obter(talhao_id, usuario).ativo = False

    def reativar(self, talhao_id: uuid.UUID, usuario: Usuario, cascata: bool = False) -> None:
        talhao = self._obter(talhao_id, usuario)
        self._validar_propriedade(talhao.propriedade_id, usuario)
        talhao.ativo = True
