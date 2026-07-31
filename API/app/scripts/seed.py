"""Seed de dados iniciais: usuário ADMIN, a norma DRIS de validação e o
catálogo de insumos de teste.

Uso: uv run python -m app.scripts.seed
"""

from app.core.security import hash_senha
from app.domain.enums import PerfilUsuario
from app.infrastructure.db.models import Insumo, NormaDris, Usuario
from app.infrastructure.db.session import SessionLocal
from sqlalchemy import select

ADMIN_EMAIL = "admin@drisai.com.br"
ADMIN_SENHA = "Admin@123456"

# Teores médios da população de alta produtividade (Figura 1, colunas x/s²/s/c.v./n).
# Macronutrientes em g/kg e micronutrientes em mg/kg — as mesmas unidades em que
# as relações duais abaixo foram calculadas.
TEORES_REFERENCIA_SOJA = {
    "N": 42.49, "P": 3.17, "K": 23.02, "Ca": 7.16, "Mg": 3.97, "S": 2.45,
    "B": 47.16, "Cu": 6.78, "Fe": 149.76, "Mn": 38.69, "Zn": 43.04,
}

# Norma DRIS para soja no estádio R2 — sul do Maranhão (HOOGERHEIDE, 2005,
# Figura 1), transcrita integralmente: as 55 relações duais possíveis entre os
# 11 nutrientes, cada uma na orientação escolhida pelo estudo.
#
# O CV publicado é a fonte de verdade do cálculo: em relações de média pequena
# (ex.: Ca/Fe = 0,05) a média e o desvio-padrão vêm arredondados em duas casas,
# então recalcular o CV a partir deles distorceria o resultado.
NORMA_SOJA = {
    "N/K": {"media": 1.83, "variancia": 0.03, "dp": 0.17, "cv": 9.38, "n_observacoes": 19},
    "N/S": {"media": 17.36, "variancia": 3.96, "dp": 1.99, "cv": 11.46, "n_observacoes": 24},
    "N/B": {"media": 0.91, "variancia": 0.01, "dp": 0.09, "cv": 9.59, "n_observacoes": 24},
    "N/Cu": {"media": 6.50, "variancia": 1.24, "dp": 1.11, "cv": 17.12, "n_observacoes": 24},
    "N/Zn": {"media": 1.02, "variancia": 0.03, "dp": 0.17, "cv": 16.14, "n_observacoes": 21},
    "P/N": {"media": 0.07, "variancia": 0.00, "dp": 0.01, "cv": 14.20, "n_observacoes": 25},
    "P/K": {"media": 0.14, "variancia": 0.00, "dp": 0.02, "cv": 13.17, "n_observacoes": 22},
    "P/Ca": {"media": 0.43, "variancia": 0.01, "dp": 0.08, "cv": 17.71, "n_observacoes": 22},
    "P/Mg": {"media": 0.78, "variancia": 0.01, "dp": 0.09, "cv": 11.29, "n_observacoes": 23},
    "P/S": {"media": 1.26, "variancia": 0.02, "dp": 0.15, "cv": 11.76, "n_observacoes": 22},
    "P/Cu": {"media": 0.48, "variancia": 0.01, "dp": 0.11, "cv": 23.06, "n_observacoes": 20},
    "P/B": {"media": 0.07, "variancia": 0.00, "dp": 0.01, "cv": 10.02, "n_observacoes": 20},
    "K/B": {"media": 0.50, "variancia": 0.00, "dp": 0.05, "cv": 9.72, "n_observacoes": 23},
    "K/Cu": {"media": 3.50, "variancia": 0.34, "dp": 0.58, "cv": 16.57, "n_observacoes": 22},
    "Ca/N": {"media": 0.17, "variancia": 0.00, "dp": 0.02, "cv": 13.29, "n_observacoes": 16},
    "Ca/K": {"media": 0.33, "variancia": 0.00, "dp": 0.05, "cv": 13.84, "n_observacoes": 19},
    "Ca/Mg": {"media": 1.76, "variancia": 0.04, "dp": 0.20, "cv": 11.12, "n_observacoes": 25},
    "Ca/S": {"media": 2.88, "variancia": 0.19, "dp": 0.44, "cv": 15.31, "n_observacoes": 19},
    "Ca/B": {"media": 0.15, "variancia": 0.00, "dp": 0.02, "cv": 13.55, "n_observacoes": 23},
    "Ca/Cu": {"media": 1.07, "variancia": 0.07, "dp": 0.26, "cv": 24.48, "n_observacoes": 19},
    "Ca/Fe": {"media": 0.05, "variancia": 0.00, "dp": 0.01, "cv": 15.34, "n_observacoes": 22},
    "Ca/Zn": {"media": 0.16, "variancia": 0.00, "dp": 0.02, "cv": 11.59, "n_observacoes": 23},
    "Mg/N": {"media": 0.09, "variancia": 0.00, "dp": 0.01, "cv": 12.48, "n_observacoes": 25},
    "Mg/K": {"media": 0.17, "variancia": 0.00, "dp": 0.02, "cv": 13.78, "n_observacoes": 27},
    "Mg/B": {"media": 0.09, "variancia": 0.00, "dp": 0.01, "cv": 8.38, "n_observacoes": 26},
    "Mg/Cu": {"media": 0.60, "variancia": 0.02, "dp": 0.12, "cv": 20.63, "n_observacoes": 27},
    "S/K": {"media": 0.11, "variancia": 0.00, "dp": 0.02, "cv": 13.68, "n_observacoes": 14},
    "S/Mg": {"media": 0.64, "variancia": 0.01, "dp": 0.08, "cv": 12.56, "n_observacoes": 19},
    "S/B": {"media": 0.06, "variancia": 0.00, "dp": 0.01, "cv": 10.85, "n_observacoes": 16},
    "S/Cu": {"media": 0.34, "variancia": 0.01, "dp": 0.07, "cv": 20.42, "n_observacoes": 20},
    "B/Cu": {"media": 7.15, "variancia": 2.14, "dp": 1.46, "cv": 20.49, "n_observacoes": 22},
    "Fe/N": {"media": 3.48, "variancia": 0.42, "dp": 0.65, "cv": 18.68, "n_observacoes": 24},
    "Fe/P": {"media": 47.03, "variancia": 55.74, "dp": 7.47, "cv": 15.88, "n_observacoes": 20},
    "Fe/K": {"media": 6.71, "variancia": 1.58, "dp": 1.26, "cv": 18.75, "n_observacoes": 24},
    "Fe/Mg": {"media": 36.21, "variancia": 28.97, "dp": 5.38, "cv": 14.86, "n_observacoes": 26},
    "Fe/S": {"media": 62.11, "variancia": 110.76, "dp": 10.52, "cv": 16.94, "n_observacoes": 23},
    "Fe/B": {"media": 3.16, "variancia": 0.23, "dp": 0.48, "cv": 15.03, "n_observacoes": 26},
    "Fe/Cu": {"media": 22.66, "variancia": 38.45, "dp": 6.20, "cv": 27.36, "n_observacoes": 25},
    "Fe/Zn": {"media": 3.56, "variancia": 0.55, "dp": 0.74, "cv": 20.84, "n_observacoes": 22},
    "Mn/N": {"media": 0.86, "variancia": 0.05, "dp": 0.23, "cv": 26.40, "n_observacoes": 31},
    "Mn/P": {"media": 11.50, "variancia": 9.59, "dp": 3.10, "cv": 26.93, "n_observacoes": 27},
    "Mn/K": {"media": 1.60, "variancia": 0.14, "dp": 0.38, "cv": 23.49, "n_observacoes": 27},
    "Mn/Ca": {"media": 5.55, "variancia": 2.98, "dp": 1.73, "cv": 31.10, "n_observacoes": 29},
    "Mn/Mg": {"media": 10.02, "variancia": 6.51, "dp": 2.55, "cv": 25.46, "n_observacoes": 35},
    "Mn/S": {"media": 15.77, "variancia": 14.62, "dp": 3.82, "cv": 24.25, "n_observacoes": 28},
    "Mn/Fe": {"media": 0.27, "variancia": 0.01, "dp": 0.08, "cv": 30.79, "n_observacoes": 31},
    "Mn/Zn": {"media": 0.92, "variancia": 0.07, "dp": 0.26, "cv": 27.87, "n_observacoes": 28},
    "Mn/Cu": {"media": 5.43, "variancia": 1.77, "dp": 1.33, "cv": 24.52, "n_observacoes": 33},
    "Mn/B": {"media": 0.86, "variancia": 0.04, "dp": 0.21, "cv": 23.99, "n_observacoes": 29},
    "Zn/P": {"media": 13.70, "variancia": 4.40, "dp": 2.10, "cv": 15.30, "n_observacoes": 21},
    "Zn/K": {"media": 1.94, "variancia": 0.08, "dp": 0.28, "cv": 14.45, "n_observacoes": 15},
    "Zn/Mg": {"media": 10.74, "variancia": 1.41, "dp": 1.19, "cv": 11.06, "n_observacoes": 24},
    "Zn/S": {"media": 16.53, "variancia": 5.39, "dp": 2.32, "cv": 14.04, "n_observacoes": 19},
    "Zn/B": {"media": 0.90, "variancia": 0.02, "dp": 0.13, "cv": 14.11, "n_observacoes": 22},
    "Zn/Cu": {"media": 6.65, "variancia": 3.23, "dp": 1.80, "cv": 27.00, "n_observacoes": 17}
}

# Catálogo de teste controlado (DERS, seção 1): produtos fictícios com composições
# típicas de formulações foliares, usados para exercitar o motor de recomendação
# sem depender de bulas comerciais reais. Concentrações em % (m/m).
INSUMOS_TESTE = [
    {
        "nome_comercial": "NutriSoja Zn-B",
        "fabricante": "AgroTeste Insumos",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"Zn": 10.0, "B": 2.5},
    },
    {
        "nome_comercial": "Manganês Foliar 12",
        "fabricante": "AgroTeste Insumos",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"Mn": 12.0, "S": 5.0},
    },
    {
        "nome_comercial": "Fosfito de Potássio 30-20",
        "fabricante": "Verdecampo Nutrição",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"P": 30.0, "K": 20.0},
    },
    {
        "nome_comercial": "Cálcio-Boro Premium",
        "fabricante": "Verdecampo Nutrição",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"Ca": 15.0, "B": 1.5},
    },
    {
        "nome_comercial": "Sulfato de Magnésio Solúvel",
        "fabricante": "Mineral Prime",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"Mg": 9.5, "S": 12.0},
    },
    {
        "nome_comercial": "Micromix Completo",
        "fabricante": "Mineral Prime",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {
            "Zn": 6.0, "B": 1.0, "Cu": 1.5, "Fe": 3.0, "Mn": 4.0,
        },
    },
    {
        "nome_comercial": "Cobre Quelatizado EDTA",
        "fabricante": "Quelatos do Brasil",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"Cu": 8.0},
    },
    {
        "nome_comercial": "Ferro Quelatizado EDDHA",
        "fabricante": "Quelatos do Brasil",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"Fe": 6.0},
    },
    {
        "nome_comercial": "Nitrogênio Foliar 20",
        "fabricante": "AgroTeste Insumos",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"N": 20.0, "S": 3.0},
    },
    {
        "nome_comercial": "Zinco Concentrado 20",
        "fabricante": "Mineral Prime",
        "culturas_autorizadas": ["Soja"],
        "concentracao_nutricional": {"Zn": 20.0},
    },
]


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

        # A norma publicada é dado de referência controlado: o seed a mantém
        # sincronizada com a Figura 1 mesmo que já exista no banco.
        norma = db.scalar(
            select(NormaDris).where(
                NormaDris.cultura == "Soja", NormaDris.estadio_fenologico == "R2"
            )
        )
        if norma is None:
            db.add(
                NormaDris(
                    cultura="Soja",
                    estadio_fenologico="R2",
                    matriz_relacoes_duais=NORMA_SOJA,
                )
            )
            print(f"Norma DRIS de Soja (R2) criada com {len(NORMA_SOJA)} relações duais.")
        elif norma.matriz_relacoes_duais != NORMA_SOJA:
            anterior = len(norma.matriz_relacoes_duais)
            norma.matriz_relacoes_duais = NORMA_SOJA
            print(
                f"Norma DRIS de Soja (R2) atualizada: {anterior} -> "
                f"{len(NORMA_SOJA)} relações duais (Figura 1 integral)."
            )
        else:
            print("Norma de Soja (R2) já está sincronizada com a Figura 1.")

        criados = 0
        for dados in INSUMOS_TESTE:
            existe = db.scalar(
                select(Insumo).where(Insumo.nome_comercial == dados["nome_comercial"])
            )
            if not existe:
                db.add(Insumo(**dados))
                criados += 1
        print(
            f"Insumos de teste: {criados} criado(s), "
            f"{len(INSUMOS_TESTE) - criados} já existente(s)."
        )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    executar()
