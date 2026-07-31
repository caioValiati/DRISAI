"""Gráfico radial dos índices DRIS para o laudo (RF013).

Renderizado no servidor para que o PDF possa ser reemitido a qualquer momento
a partir dos dados persistidos, sem depender do navegador que originou o pedido.
"""

import io
import math

import matplotlib

matplotlib.use("Agg")  # backend sem display, obrigatório no servidor
import matplotlib.pyplot as plt  # noqa: E402

VERDE = "#2e7d32"


def gerar_grafico_radial(indices: dict[str, float]) -> bytes:
    """Devolve um PNG com o perfil nutricional da amostra."""
    nutrientes = list(indices)
    valores = [indices[n] for n in nutrientes]

    # Fecha o polígono repetindo o primeiro ponto
    angulos = [n / len(nutrientes) * 2 * math.pi for n in range(len(nutrientes))]
    angulos += angulos[:1]
    valores += valores[:1]

    figura, eixo = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})
    eixo.plot(angulos, valores, color=VERDE, linewidth=2)
    eixo.fill(angulos, valores, color=VERDE, alpha=0.25)

    # Linha do zero: referência visual do equilíbrio nutricional
    eixo.plot(angulos, [0] * len(angulos), color="#999999", linewidth=1, linestyle="--")

    eixo.set_xticks(angulos[:-1])
    eixo.set_xticklabels(nutrientes, fontsize=10)
    eixo.tick_params(axis="y", labelsize=8)
    eixo.grid(color="#dddddd")

    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(figura)
    return buffer.getvalue()
