import { api } from '@/shared/api/client'
import type { AmostraDetalhe, AmostraResumo } from '@/shared/types'

export interface FormularioAmostra {
  talhao_id: string
  norma_dris_id: string
  data_coleta: string
  teores: Record<string, number>
}

export const amostrasApi = {
  listar: async () => (await api.get<AmostraResumo[]>('/amostras')).data,
  obter: async (id: string) => (await api.get<AmostraDetalhe>(`/amostras/${id}`)).data,
  criar: async (dados: FormularioAmostra) =>
    (await api.post<AmostraDetalhe>('/amostras', dados)).data,
  atualizar: async (id: string, dados: FormularioAmostra) =>
    (await api.put<AmostraDetalhe>(`/amostras/${id}`, dados)).data,
  salvarRecomendacao: async (id: string, texto: string) =>
    (await api.put<AmostraDetalhe>(`/amostras/${id}/recomendacao`, { texto_final_editado: texto }))
      .data,
  concluir: async (id: string) =>
    (await api.post<AmostraDetalhe>(`/amostras/${id}/concluir`)).data,

  /** RF013 — baixa o laudo da amostra concluída. */
  baixarLaudo: async (id: string) => {
    const resposta = await api.get(`/amostras/${id}/laudo.pdf`, { responseType: 'blob' })
    const nome =
      /filename="(.+)"/.exec(resposta.headers['content-disposition'] ?? '')?.[1] ??
      `laudo-${id}.pdf`
    const url = URL.createObjectURL(resposta.data as Blob)
    const link = document.createElement('a')
    link.href = url
    link.download = nome
    link.click()
    URL.revokeObjectURL(url)
  },
}
