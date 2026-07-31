import { App } from 'antd'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, mensagemDeErro } from '@/shared/api/client'
import type { ImpactoVinculos } from '@/shared/types'

/**
 * Listas afetadas indiretamente por uma mutação, por causa da hierarquia
 * Produtor → Propriedade → Talhão → Amostra: inativar um produtor, por exemplo,
 * inativa em cascata os descendentes, então os caches deles ficam obsoletos.
 */
const CHAVES_DEPENDENTES: Record<string, string[]> = {
  produtores: ['propriedades', 'talhoes', 'amostras'],
  propriedades: ['talhoes', 'amostras'],
  talhoes: ['amostras'],
  normas: ['amostras'],
  insumos: [],
}

/**
 * Encapsula o padrão de CRUD repetido em todos os módulos do DERS:
 * listar, criar, editar, inativar e reativar, com invalidação de cache e
 * feedback ao usuário.
 */
export function useCrud<TRegistro extends { id: string }, TFormulario>(
  recurso: string,
  rotulo: string,
) {
  const queryClient = useQueryClient()
  const { message } = App.useApp()
  const chave = [recurso]

  const listagem = useQuery({
    queryKey: chave,
    queryFn: async () => (await api.get<TRegistro[]>(`/${recurso}`)).data,
  })

  function invalidar() {
    queryClient.invalidateQueries({ queryKey: chave })
    for (const dependente of CHAVES_DEPENDENTES[recurso] ?? []) {
      queryClient.invalidateQueries({ queryKey: [dependente] })
    }
  }

  function aoFalhar(padrao: string) {
    return (erro: unknown) => message.error(mensagemDeErro(erro, padrao))
  }

  function comSucesso(texto: string) {
    return () => {
      message.success(texto)
      invalidar()
    }
  }

  const criar = useMutation({
    mutationFn: async (dados: TFormulario) =>
      (await api.post<TRegistro>(`/${recurso}`, dados)).data,
    onSuccess: comSucesso(`${rotulo} cadastrado com sucesso.`),
    onError: aoFalhar('Não foi possível cadastrar o registro.'),
  })

  const atualizar = useMutation({
    mutationFn: async ({ id, dados }: { id: string; dados: TFormulario }) =>
      (await api.put<TRegistro>(`/${recurso}/${id}`, dados)).data,
    onSuccess: comSucesso(`${rotulo} atualizado com sucesso.`),
    onError: aoFalhar('Não foi possível atualizar o registro.'),
  })

  const inativar = useMutation({
    mutationFn: async (id: string) => api.patch(`/${recurso}/${id}/inativar`),
    onSuccess: comSucesso(`${rotulo} inativado com sucesso.`),
    onError: aoFalhar('Não foi possível inativar o registro.'),
  })

  const reativar = useMutation({
    mutationFn: async ({ id, cascata }: { id: string; cascata?: boolean }) =>
      api.patch(`/${recurso}/${id}/reativar`, null, {
        params: cascata ? { cascata: true } : undefined,
      }),
    onSuccess: comSucesso(`${rotulo} reativado com sucesso.`),
    onError: aoFalhar('Não foi possível reativar o registro.'),
  })

  /** Busca a prévia de impacto exibida antes de inativar ou reativar. */
  async function obterVinculos(id: string): Promise<ImpactoVinculos | null> {
    try {
      return (await api.get<ImpactoVinculos>(`/${recurso}/${id}/vinculos`)).data
    } catch {
      // Recursos sem hierarquia (normas, insumos) não expõem o endpoint
      return null
    }
  }

  return { listagem, criar, atualizar, inativar, reativar, obterVinculos }
}
