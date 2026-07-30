"""Schemas dos CRUDs de curadoria (Normas, Insumos) e carteira (Produtores,
Propriedades, Talhões) — RF004 a RF008."""

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domain.enums import NUTRIENTES


class RelacaoDualParams(BaseModel):
    media: float = Field(gt=0)
    dp: float = Field(gt=0)
    cv: float = Field(gt=0)


class NormaDrisRequest(BaseModel):
    cultura: str = Field(min_length=2, max_length=120)
    estadio_fenologico: str = Field(min_length=1, max_length=120)
    matriz_relacoes_duais: dict[str, RelacaoDualParams]

    @field_validator("matriz_relacoes_duais")
    @classmethod
    def validar_relacoes(cls, matriz):
        if not matriz:
            raise ValueError("A norma deve conter ao menos uma relação dual.")
        for relacao in matriz:
            partes = relacao.split("/")
            if len(partes) != 2 or not all(p in NUTRIENTES for p in partes):
                raise ValueError(
                    f"Relação '{relacao}' inválida: use o formato A/B com nutrientes "
                    f"entre {', '.join(NUTRIENTES)}."
                )
        return matriz


class NormaDrisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cultura: str
    estadio_fenologico: str
    matriz_relacoes_duais: dict[str, RelacaoDualParams]
    ativa: bool


class InsumoRequest(BaseModel):
    nome_comercial: str = Field(min_length=2, max_length=255)
    fabricante: str = Field(min_length=2, max_length=255)
    culturas_autorizadas: list[str] = Field(min_length=1)
    concentracao_nutricional: dict[str, float]

    @field_validator("concentracao_nutricional")
    @classmethod
    def validar_concentracoes(cls, concentracoes):
        if not concentracoes:
            raise ValueError("Informe a concentração de ao menos um nutriente.")
        for nutriente, valor in concentracoes.items():
            if nutriente not in NUTRIENTES:
                raise ValueError(f"Nutriente '{nutriente}' inválido.")
            if valor < 0:
                raise ValueError(f"Concentração de {nutriente} não pode ser negativa.")
        return concentracoes


class InsumoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome_comercial: str
    fabricante: str
    culturas_autorizadas: list[str]
    concentracao_nutricional: dict[str, float]
    ativo: bool


class ProdutorRequest(BaseModel):
    nome_razao: str = Field(min_length=3, max_length=255)
    cpf_cnpj: str = Field(min_length=11, max_length=18)
    telefone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None

    @field_validator("cpf_cnpj")
    @classmethod
    def normalizar_documento(cls, valor: str) -> str:
        digitos = "".join(c for c in valor if c.isdigit())
        if len(digitos) not in (11, 14):
            raise ValueError("CPF deve ter 11 dígitos e CNPJ 14 dígitos.")
        return digitos


class ProdutorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome_razao: str
    cpf_cnpj: str
    telefone: str | None
    email: str | None
    ativo: bool


class PropriedadeRequest(BaseModel):
    produtor_id: uuid.UUID
    nome_fazenda: str = Field(min_length=2, max_length=255)
    municipio_uf: str = Field(min_length=2, max_length=120)
    area_total_ha: Decimal = Field(gt=0)


class PropriedadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    produtor_id: uuid.UUID
    nome_fazenda: str
    municipio_uf: str
    area_total_ha: Decimal
    ativo: bool
    produtor_nome: str | None = None


class TalhaoRequest(BaseModel):
    propriedade_id: uuid.UUID
    identificacao: str = Field(min_length=1, max_length=120)
    tamanho_ha: Decimal = Field(gt=0)
    historico_culturas: str | None = None


class TalhaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    propriedade_id: uuid.UUID
    identificacao: str
    tamanho_ha: Decimal
    historico_culturas: str | None
    ativo: bool
    propriedade_nome: str | None = None
