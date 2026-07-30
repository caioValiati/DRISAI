import { App } from 'antd'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, mensagemDeErro } from '@/shared/api/client'

/**
 * Encapsula o padrão de CRUD repetido em todos os módulos do DERS:
 * listar, criar, editar e inativar, com invalidação de cache e feedback ao usuário.
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

  function aoFalhar(padrao: string) {
    return (erro: unknown) => message.error(mensagemDeErro(erro, padrao))
  }

  const criar = useMutation({
    mutationFn: async (dados: TFormulario) =>
      (await api.post<TRegistro>(`/${recurso}`, dados)).data,
    onSuccess: () => {
      message.success(`${rotulo} cadastrado com sucesso.`)
      queryClient.invalidateQueries({ queryKey: chave })
    },
    onError: aoFalhar(`Não foi possível cadastrar o registro.`),
  })

  const atualizar = useMutation({
    mutationFn: async ({ id, dados }: { id: string; dados: TFormulario }) =>
      (await api.put<TRegistro>(`/${recurso}/${id}`, dados)).data,
    onSuccess: () => {
      message.success(`${rotulo} atualizado com sucesso.`)
      queryClient.invalidateQueries({ queryKey: chave })
    },
    onError: aoFalhar(`Não foi possível atualizar o registro.`),
  })

  const inativar = useMutation({
    mutationFn: async (id: string) => api.patch(`/${recurso}/${id}/inativar`),
    onSuccess: () => {
      message.success(`${rotulo} inativado com sucesso.`)
      queryClient.invalidateQueries({ queryKey: chave })
    },
    onError: aoFalhar(`Não foi possível inativar o registro.`),
  })

  return { listagem, criar, atualizar, inativar }
}
