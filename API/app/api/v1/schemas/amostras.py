"""Schemas de Amostras Foliares (RF009), índices DRIS (RF010) e revisão (RF012)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class RecomendacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    texto_rascunho_ia: str | None
    texto_final_editado: str | None
    data_emissao: datetime | None


class AmostraDetalheResponse(AmostraResumoResponse):
    indices: list[IndiceNutricionalResponse]
    recomendacao: RecomendacaoResponse | None


class AtualizarRecomendacaoRequest(BaseModel):
    texto_final_editado: str = Field(min_length=1)
