import { useEffect, useState } from 'react'
import { Alert, Checkbox, Modal, Spin, Typography } from 'antd'
import type { ImpactoVinculos } from '@/shared/types'

export type AcaoVinculo = 'inativar' | 'reativar'

interface ModalVinculosProps {
  aberto: boolean
  acao: AcaoVinculo
  rotulo: string
  nomeRegistro: string
  carregarVinculos: () => Promise<ImpactoVinculos | null>
  aoConfirmar: (cascata: boolean) => void
  aoCancelar: () => void
  confirmando: boolean
}

/** O backend devolve o nome da entidade no plural; aqui ajustamos a concordância. */
const SINGULAR: Record<string, string> = {
  Propriedades: 'propriedade',
  Talhões: 'talhão',
}

function descrever(vinculos: ImpactoVinculos, acao: AcaoVinculo) {
  const chave = acao === 'inativar' ? 'ativos' : 'inativos'
  return vinculos.vinculos
    .filter((v) => v[chave] > 0)
    .map((v) => {
      const quantidade = v[chave]
      const nome =
        quantidade === 1 ? (SINGULAR[v.entidade] ?? v.entidade.toLowerCase()) : v.entidade.toLowerCase()
      return `${quantidade} ${nome}`
    })
}

/**
 * Confirmação de inativação/reativação mostrando o impacto na hierarquia
 * Produtor → Propriedade → Talhão antes de o usuário decidir.
 */
export function ModalVinculos({
  aberto,
  acao,
  rotulo,
  nomeRegistro,
  carregarVinculos,
  aoConfirmar,
  aoCancelar,
  confirmando,
}: ModalVinculosProps) {
  const [vinculos, setVinculos] = useState<ImpactoVinculos | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [cascata, setCascata] = useState(true)

  useEffect(() => {
    if (!aberto) return
    setCascata(true)
    setCarregando(true)
    carregarVinculos()
      .then(setVinculos)
      .finally(() => setCarregando(false))
    // carregarVinculos muda a cada render do pai; o gatilho é a abertura do modal
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [aberto])

  const afetados = vinculos ? descrever(vinculos, acao) : []
  const inativando = acao === 'inativar'

  return (
    <Modal
      open={aberto}
      title={`${inativando ? 'Inativar' : 'Reativar'} ${rotulo}`}
      okText={inativando ? 'Inativar' : 'Reativar'}
      cancelText="Cancelar"
      okButtonProps={{ danger: inativando }}
      confirmLoading={confirmando}
      onOk={() => aoConfirmar(cascata)}
      onCancel={aoCancelar}
    >
      {carregando ? (
        <Spin />
      ) : (
        <>
          <Typography.Paragraph>
            {inativando ? 'Inativar' : 'Reativar'} <strong>{nomeRegistro}</strong>?
          </Typography.Paragraph>

          {afetados.length > 0 && (
            <Alert
              type={inativando ? 'warning' : 'info'}
              showIcon
              style={{ marginBottom: 12 }}
              title={
                inativando
                  ? `Esta ação também inativa ${afetados.join(' e ')}`
                  : `Existem ${afetados.join(' e ')} inativos vinculados`
              }
              description={
                inativando
                  ? 'Os registros vinculados deixam de ficar disponíveis para novas amostras.'
                  : 'Escolha abaixo se eles devem voltar a ficar disponíveis junto com este registro.'
              }
            />
          )}

          {!inativando && afetados.length > 0 && (
            <Checkbox checked={cascata} onChange={(e) => setCascata(e.target.checked)}>
              Reativar também os registros vinculados
            </Checkbox>
          )}

          {vinculos && vinculos.amostras_vinculadas > 0 && (
            <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginTop: 12 }}>
              {vinculos.amostras_vinculadas === 1
                ? '1 amostra já registrada permanece inalterada'
                : `${vinculos.amostras_vinculadas} amostras já registradas permanecem inalteradas`}{' '}
              — o histórico de diagnósticos é preservado.
            </Typography.Paragraph>
          )}
        </>
      )}
    </Modal>
  )
}
