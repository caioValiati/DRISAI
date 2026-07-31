export type Perfil = 'ADMIN' | 'AGRONOMO'

export type StatusAmostra = 'RASCUNHO' | 'AGUARDANDO_REVISAO' | 'CONCLUIDA'

export type Classificacao = 'DEFICIENTE' | 'EQUILIBRIO' | 'EXCESSO'

export interface Usuario {
  id: string
  nome: string
  email: string
  perfil: Perfil
  registro_crea: string | null
  ativo: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: Usuario
}

export interface RelacaoDual {
  media: number
  dp: number
  cv: number
  variancia?: number | null
  n_observacoes?: number | null
}

export interface ImpactoVinculo {
  entidade: string
  ativos: number
  inativos: number
}

export interface ImpactoVinculos {
  vinculos: ImpactoVinculo[]
  amostras_vinculadas: number
}

export interface NormaDris {
  id: string
  cultura: string
  estadio_fenologico: string
  matriz_relacoes_duais: Record<string, RelacaoDual>
  ativa: boolean
}

export interface Insumo {
  id: string
  nome_comercial: string
  fabricante: string
  culturas_autorizadas: string[]
  concentracao_nutricional: Record<string, number>
  ativo: boolean
}

export interface Produtor {
  id: string
  nome_razao: string
  cpf_cnpj: string
  telefone: string | null
  email: string | null
  ativo: boolean
  agronomo_nome: string | null
}

export interface Propriedade {
  id: string
  produtor_id: string
  nome_fazenda: string
  municipio_uf: string
  area_total_ha: string
  ativo: boolean
  produtor_nome: string | null
  agronomo_nome: string | null
}

export interface Talhao {
  id: string
  propriedade_id: string
  identificacao: string
  tamanho_ha: string
  historico_culturas: string | null
  ativo: boolean
  propriedade_nome: string | null
  agronomo_nome: string | null
}

export interface IndiceNutricional {
  elemento: string
  valor_laboratorio: string
  indice_dris_calculado: string | null
  classificacao: Classificacao | null
}

export interface Recomendacao {
  texto_rascunho_ia: string | null
  texto_final_editado: string | null
  data_emissao: string | null
}

export interface AmostraResumo {
  id: string
  talhao_id: string
  norma_dris_id: string
  data_coleta: string
  status: StatusAmostra
  valor_ibn: string | null
  talhao_nome: string | null
  propriedade_nome: string | null
  cultura_norma: string | null
}

export interface AmostraDetalhe extends AmostraResumo {
  indices: IndiceNutricional[]
  recomendacao: Recomendacao | null
}

// Ordem canônica dos nutrientes (Quadro 40 do DERS)
export const NUTRIENTES = ['N', 'P', 'K', 'Ca', 'Mg', 'S', 'Zn', 'B', 'Cu', 'Fe', 'Mn'] as const

export const NOMES_NUTRIENTES: Record<string, string> = {
  N: 'Nitrogênio',
  P: 'Fósforo',
  K: 'Potássio',
  Ca: 'Cálcio',
  Mg: 'Magnésio',
  S: 'Enxofre',
  Zn: 'Zinco',
  B: 'Boro',
  Cu: 'Cobre',
  Fe: 'Ferro',
  Mn: 'Manganês',
}
