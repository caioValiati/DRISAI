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
}
