import { Tag } from 'antd'
import type { Classificacao, StatusAmostra } from '@/shared/types'

export function TagAtivo({ ativo }: { ativo: boolean }) {
  return <Tag color={ativo ? 'green' : 'default'}>{ativo ? 'Ativo' : 'Inativo'}</Tag>
}

const ROTULOS_STATUS: Record<StatusAmostra, { cor: string; texto: string }> = {
  RASCUNHO: { cor: 'default', texto: 'Rascunho' },
  AGUARDANDO_REVISAO: { cor: 'gold', texto: 'Aguardando revisão' },
  CONCLUIDA: { cor: 'green', texto: 'Concluída' },
}

export function TagStatusAmostra({ status }: { status: StatusAmostra }) {
  const { cor, texto } = ROTULOS_STATUS[status]
  return <Tag color={cor}>{texto}</Tag>
}

const CORES_CLASSIFICACAO: Record<Classificacao, string> = {
  DEFICIENTE: 'red',
  EQUILIBRIO: 'green',
  EXCESSO: 'orange',
}

const TEXTOS_CLASSIFICACAO: Record<Classificacao, string> = {
  DEFICIENTE: 'Deficiente',
  EQUILIBRIO: 'Equilíbrio',
  EXCESSO: 'Excesso',
}

export function TagClassificacao({ classificacao }: { classificacao: Classificacao | null }) {
  if (!classificacao) return <Tag>—</Tag>
  return <Tag color={CORES_CLASSIFICACAO[classificacao]}>{TEXTOS_CLASSIFICACAO[classificacao]}</Tag>
}
