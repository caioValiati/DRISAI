import json
import numpy as np
import pandas as pd

# Configuração de semente de aleatoriedade
np.random.seed(42)

# ==========================================
# 1. MAPEAMENTO DE GARANTIAS DOS PRODUTOS
# ==========================================
# Concentrações percentuais (% p/p ou g/100g) dos insumos comerciais
GARANTIAS_PRODUTOS = {
    "QUIMIFOL 30 N": {
        "N": 30.0,
        "P2O5": 0.0,
        "K2O": 0.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 0.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
    "K-FOL": {
        "N": 0.0,
        "P2O5": 10.0,
        "K2O": 40.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 2.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
    "SULFATO DE Mn 31%": {
        "N": 0.0,
        "P2O5": 0.0,
        "K2O": 0.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 18.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 31.0,
        "Zn": 0.0,
    },
    "BORO 15": {
        "N": 0.0,
        "P2O5": 0.0,
        "K2O": 0.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 0.0,
        "B": 15.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
    "SULFATO DE ZINCO": {
        "N": 0.0,
        "P2O5": 0.0,
        "K2O": 0.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 10.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 20.0,
    },
    "MAP PURIFICADO": {
        "N": 12.0,
        "P2O5": 61.0,
        "K2O": 0.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 0.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
    "CLORETO DE POTASSIO": {
        "N": 0.0,
        "P2O5": 0.0,
        "K2O": 60.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 0.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
    "SULFAMAG": {
        "N": 0.0,
        "P2O5": 0.0,
        "K2O": 22.0,
        "Ca": 0.0,
        "Mg": 18.0,
        "S": 22.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
    "COBALTO E MOLIBDENIO": {
        "N": 0.0,
        "P2O5": 0.0,
        "K2O": 0.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 0.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
    "NENHUM": {
        "N": 0.0,
        "P2O5": 0.0,
        "K2O": 0.0,
        "Ca": 0.0,
        "Mg": 0.0,
        "S": 0.0,
        "B": 0.0,
        "Cu": 0.0,
        "Fe": 0.0,
        "Mn": 0.0,
        "Zn": 0.0,
    },
}

# ==========================================
# 2. PARÂMETROS DE DISTRIBUIÇÃO DA SOJA (R1-R3)
# ==========================================
# Faixas normais para a cultura da soja no Brasil (Embrapa)
NUTRIENTES_FAIXAS = {
    # Macros (g/kg)
    "N_gkg": (35.0, 55.0, 45.0, 4.0),
    "P_gkg": (2.5, 5.0, 3.8, 0.5),
    "K_gkg": (17.0, 25.0, 20.0, 2.0),
    "Ca_gkg": (4.0, 12.0, 8.0, 1.5),
    "Mg_gkg": (3.0, 10.0, 5.5, 1.0),
    "S_gkg": (2.5, 5.0, 3.5, 0.4),
    # Micros (mg/kg)
    "B_mgkg": (25.0, 60.0, 40.0, 6.0),
    "Cu_mgkg": (10.0, 30.0, 15.0, 3.0),
    "Fe_mgkg": (50.0, 300.0, 120.0, 25.0),
    "Mn_mgkg": (30.0, 150.0, 75.0, 15.0),
    "Zn_mgkg": (20.0, 60.0, 35.0, 6.0),
}

PRODUTO_POR_NUTRIENTE = {
    "N": "QUIMIFOL 30 N",
    "P": "MAP PURIFICADO",
    "K": "K-FOL",
    "Ca": "NENHUM",
    "Mg": "SULFAMAG",
    "S": "SULFAMAG",
    "B": "BORO 15",
    "Cu": "NENHUM",
    "Fe": "NENHUM",
    "Mn": "SULFATO DE Mn 31%",
    "Zn": "SULFATO DE ZINCO",
}


# ==========================================
# 3. GERADOR SINTÉTICO DE DADOS DRIS
# ==========================================
def gerador_amostras_soja(n_amostras=500):
    dados = []

    for i in range(1, n_amostras + 1):
        amostra_id = f"AM-{i:04d}"

        # Teores Foliares
        teores = {}
        for nut, (vmin, vmax, mean, std) in NUTRIENTES_FAIXAS.items():
            val = np.random.normal(mean, std)
            teores[nut] = np.round(np.clip(val, vmin * 0.7, vmax * 1.3), 2)

        # Índices DRIS (Derivados do balanço dos teores)
        # Valores negativos = Deficiência; Positivos = Excesso; ~0 = Equilíbrio
        dris_indices = {}
        nutrientes_chaves = [
            "N",
            "P",
            "K",
            "Ca",
            "Mg",
            "S",
            "B",
            "Cu",
            "Fe",
            "Mn",
            "Zn",
        ]

        for nut in nutrientes_chaves:
            col_teor = f"{nut}_gkg" if nut in ["N", "P", "K", "Ca", "Mg", "S"] else f"{nut}_mgkg"
            _, _, mean, std = NUTRIENTES_FAIXAS[col_teor]
            teor_atual = teores[col_teor]
            # Índice DRIS proporcional ao desvio padronizado com escala realista (-30 a +30)
            idx = ((teor_atual - mean) / std) * 12.0
            dris_indices[f"I_{nut}"] = np.round(idx, 2)

        # Cálculo do IBN (Índice de Balanço Nutricional)
        ibn = np.round(
            sum(abs(val) for val in dris_indices.values()), 2
        )

        # Identificação da maior limitação por deficiência (Menor Índice DRIS)
        nutriente_mais_deficiente = min(
            dris_indices, key=dris_indices.get
        ).replace("I_", "")
        menor_indice = dris_indices[f"I_{nutriente_mais_deficiente}"]

        # Tomada de Decisão de Recomendação
        # Se o menor índice DRIS for inferior a -5.0, recomenda-se correção
        if menor_indice < -5.0:
            prod_recomendado = PRODUTO_POR_NUTRIENTE.get(
                nutriente_mais_deficiente, "NENHUM"
            )
            dose_ha = (
                np.round(np.random.uniform(1.5, 4.0), 1)
                if prod_recomendado != "NENHUM"
                else 0.0
            )
            correcao_aplicada = True if prod_recomendado != "NENHUM" else False
        else:
            prod_recomendado = "NENHUM"
            dose_ha = 0.0
            correcao_aplicada = False

        # Extração das Garantias Químicas do Insumo
        garantias = GARANTIAS_PRODUTOS.get(
            prod_recomendado, GARANTIAS_PRODUTOS["NENHUM"]
        )

        # ==========================================
        # 4. MODELAGEM DA PRODUTIVIDADE (TARGET)
        # ==========================================
        # Potencial produtivo base da lavoura em sacas/ha
        potencial_base_sc = 76.0

        # Penalidade proporcional ao desequilíbrio nutricional (IBN)
        penalidade_ibn = 0.28 * ibn

        # Recuperação do rendimento via adubação corretiva adequada
        recuperacao = 0.0
        if correcao_aplicada:
            # Efeito positivo proporcional à severidade do déficit corrigido
            recuperacao = abs(menor_indice) * 0.45 * (1.0 + (dose_ha / 10.0))

        # Ruído aleatório (clima, solo, manejo)
        ruido = np.random.normal(0, 2.5)

        # Produtividade calculada em Sacas e Quilogramas por Hectare
        prod_sc_ha = potencial_base_sc - penalidade_ibn + recuperacao + ruido
        prod_sc_ha = np.round(np.clip(prod_sc_ha, 38.0, 82.0), 2)
        prod_kg_ha = np.round(prod_sc_ha * 60.0, 2)

        # Compilação do registro unificado
        row = {
            "Amostra_ID": amostra_id,
            "IBN": ibn,
            "Produto_Recomendado": prod_recomendado,
            "Dose_L_Kg_ha": dose_ha,
            "Correcao_Efetuada": int(correcao_aplicada),
            "Produtividade_sc_ha": prod_sc_ha,
            "Produtividade_kg_ha": prod_kg_ha,
        }

        # Adiciona teores foliares
        row.update(teores)
        # Adiciona índices DRIS
        row.update(dris_indices)
        # Adiciona garantias do produto recomendado
        for g_nut, g_val in garantias.items():
            row[f"Garantia_{g_nut}_pct"] = g_val

        # Adiciona coluna JSON com todas as garantias
        row["Garantias_JSON"] = json.dumps(garantias)

        dados.append(row)

    return pd.DataFrame(dados)


# ==========================================
# 5. EXECUÇÃO E EXPORTAÇÃO
# ==========================================
df_final = gerador_amostras_soja(n_amostras=500)

# Reordenação de colunas para ingestão em Machine Learning
colunas_chave = [
    "Amostra_ID",
    "N_gkg",
    "P_gkg",
    "K_gkg",
    "Ca_gkg",
    "Mg_gkg",
    "S_gkg",
    "B_mgkg",
    "Cu_mgkg",
    "Fe_mgkg",
    "Mn_mgkg",
    "Zn_mgkg",
    "I_N",
    "I_P",
    "I_K",
    "I_Ca",
    "I_Mg",
    "I_S",
    "I_B",
    "I_Cu",
    "I_Fe",
    "I_Mn",
    "I_Zn",
    "IBN",
    "Produto_Recomendado",
    "Dose_L_Kg_ha",
    "Garantia_N_pct",
    "Garantia_P2O5_pct",
    "Garantia_K2O_pct",
    "Garantia_Ca_pct",
    "Garantia_Mg_pct",
    "Garantia_S_pct",
    "Garantia_B_pct",
    "Garantia_Cu_pct",
    "Garantia_Fe_pct",
    "Garantia_Mn_pct",
    "Garantia_Zn_pct",
    "Garantias_JSON",
    "Produtividade_sc_ha",
    "Produtividade_kg_ha",  # Target Principal
]

df_final = df_final[colunas_chave]
df_final.to_csv("dataset_soja_dris_ml_500.csv", index=False)