"""Schemas de Amostras Foliares (RF009), índices DRIS (RF010) e revisão (RF012)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import AliasPath, BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import NUTRIENTES, ClassificacaoNutriente, StatusAmostra


class AmostraRequest(BaseModel):
    talhao_id: uuid.UUID
    norma_dris_id: uuid.UUID
    data_coleta: date
    # Teores foliares dos 11 nutrientes (Quadro 40 do DERS)
    teores: dict[str, Decimal]

    @field_validator("teores")
    @classmethod
    def validar_teores(cls, teores):
        faltantes = [n for n in NUTRIENTES if n not in teores]
        if faltantes:
            raise ValueError(f"Teores obrigatórios ausentes: {', '.join(faltantes)}.")
        extras = [n for n in teores if n not in NUTRIENTES]
        if extras:
            raise ValueError(f"Nutrientes desconhecidos: {', '.join(extras)}.")
        invalidos = [n for n, v in teores.items() if v <= 0]
        if invalidos:
            raise ValueError(f"Teores devem ser maiores que zero: {', '.join(invalidos)}.")
        return teores


class IndiceNutricionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    elemento: str
    valor_laboratorio: Decimal
    indice_dris_calculado: Decimal | None
    classificacao: ClassificacaoNutriente | None


class AmostraResumoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    talhao_id: uuid.UUID
    norma_dris_id: uuid.UUID
    data_coleta: date
    status: StatusAmostra
    valor_ibn: Decimal | None
    talhao_nome: str | None = None
    propriedade_nome: str | None = None
    cultura_norma: str | None = None


class InsumoSugeridoResponse(BaseModel):
    """Insumo ranqueado pelo motor de matching (RF011).

    Achata a associativa `recomendacao_insumo` com os dados do próprio insumo,
    poupando o cliente de uma segunda consulta ao catálogo.
    """

    model_config = ConfigDict(from_attributes=True)

    # Lido do próprio insumo: a chave estrangeira da associativa só é populada
    # no flush, e a resposta é montada antes disso no fluxo de processamento
    insumo_id: uuid.UUID = Field(validation_alias=AliasPath("insumo", "id"))
    nome_comercial: str = Field(validation_alias=AliasPath("insumo", "nome_comercial"))
    fabricante: str = Field(validation_alias=AliasPath("insumo", "fabricante"))
    concentracao_nutricional: dict[str, float] = Field(
        validation_alias=AliasPath("insumo", "concentracao_nutricional")
    )
    match_score: Decimal


class RecomendacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    texto_rascunho_ia: str | None
    texto_final_editado: str | None
    data_emissao: datetime | None
    # Preenchido quando a redação automática falha (RF011 A1)
    falha_ia: str | None = None
    insumos_sugeridos: list[InsumoSugeridoResponse] = []


class AmostraDetalheResponse(AmostraResumoResponse):
    indices: list[IndiceNutricionalResponse]
    recomendacao: RecomendacaoResponse | None


class AtualizarRecomendacaoRequest(BaseModel):
    texto_final_editado: str = Field(min_length=1)
