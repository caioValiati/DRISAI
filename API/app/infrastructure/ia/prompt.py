"""Montagem do prompt estruturado enviado ao LLM (RF011).

O prompt reúne o diagnóstico matemático e o subconjunto do catálogo já filtrado
pelo motor de matching — a estratégia de RAG descrita no DERS: o modelo redige
apoiado em dados recuperados do sistema, não em conhecimento próprio sobre
produtos.
"""

from app.domain.ia import ContextoLaudo

INSTRUCAO_SISTEMA = """\
Você é um assistente de redação técnica que apoia engenheiros agrônomos na \
elaboração de laudos de diagnose nutricional pelo método DRIS.

Regras que você deve seguir rigorosamente:
1. Escreva em português brasileiro, em registro técnico agronômico, na terceira \
pessoa e em tom objetivo.
2. Cite exclusivamente os insumos da lista fornecida. É proibido mencionar \
qualquer outro produto, marca ou princípio ativo que não esteja nessa lista.
3. Não invente dosagens, épocas de aplicação ou resultados esperados que não \
possam ser deduzidos dos dados recebidos. Quando a dosagem for necessária, \
indique explicitamente que ela deve ser definida pelo engenheiro agrônomo \
responsável.
4. Baseie o diagnóstico nos índices DRIS informados: índices negativos indicam \
deficiência, positivos indicam excesso e valores próximos de zero indicam \
equilíbrio. O IBN expressa o desequilíbrio global da amostra.
5. Não afirme nada sobre produtividade esperada, recomendação de calagem ou \
análise de solo — esses dados não fazem parte da amostra foliar.
6. Produza um rascunho de 3 a 5 parágrafos, sem título, sem listas numeradas e \
sem despedida ou assinatura.

O texto que você produz é um rascunho: o engenheiro agrônomo irá revisá-lo, \
editá-lo e assumir a responsabilidade técnica final."""


def _formatar_diagnostico(contexto: ContextoLaudo) -> str:
    linhas = []
    for nutriente, indice in contexto.indices.items():
        teor = contexto.teores.get(nutriente)
        classificacao = contexto.classificacoes.get(nutriente, "—")
        linhas.append(
            f"- {nutriente}: teor {teor}, índice DRIS {indice:+.2f} ({classificacao})"
        )
    return "\n".join(linhas)


def _formatar_insumos(contexto: ContextoLaudo) -> str:
    if not contexto.insumos:
        return (
            "Nenhum insumo do catálogo apresentou aderência ao diagnóstico. "
            "Não sugira produtos."
        )
    linhas = []
    for insumo in contexto.insumos:
        composicao = ", ".join(f"{n} {v}%" for n, v in insumo.composicao.items())
        atendidos = ", ".join(insumo.nutrientes_atendidos) or "—"
        linhas.append(
            f"- {insumo.nome_comercial} ({insumo.fabricante}): composição {composicao}; "
            f"aderência {insumo.score:.1f}%; atende {atendidos}"
        )
    return "\n".join(linhas)


def montar_prompt(contexto: ContextoLaudo) -> str:
    return f"""\
Dados da amostra foliar diagnosticada:

Cultura: {contexto.cultura} (estádio {contexto.estadio_fenologico})
Produtor: {contexto.produtor}
Propriedade: {contexto.propriedade}
Talhão: {contexto.talhao}
Data da coleta: {contexto.data_coleta}
Índice de Balanço Nutricional (IBN): {contexto.ibn:.2f}

Índices DRIS por nutriente:
{_formatar_diagnostico(contexto)}

Insumos do catálogo oficial aderentes a este diagnóstico, já ordenados por \
aderência calculada pelo sistema:
{_formatar_insumos(contexto)}

Redija o rascunho da recomendação técnica: apresente o estado nutricional geral \
da amostra, destaque o nutriente mais limitante e os demais desvios relevantes, \
relacione os insumos indicados acima às carências identificadas e registre que a \
definição das dosagens e da época de aplicação cabe ao engenheiro agrônomo \
responsável."""
