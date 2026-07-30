import { useMemo, useState } from 'react'
import { Button, Empty, InputNumber, Select, Space, Table, Typography } from 'antd'
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons'
import { NUTRIENTES, type RelacaoDual } from '@/shared/types'

type Matriz = Record<string, RelacaoDual>

interface MatrizRelacoesDuaisProps {
  value?: Matriz
  onChange?: (valor: Matriz) => void
}

/**
 * Editor das relações duais da Norma DRIS (Quadro 25 do DERS).
 *
 * Uma matriz completa com 11 nutrientes teria 55 pares; na prática a norma
 * publicada traz apenas um subconjunto. Por isso o agrônomo adiciona as
 * relações que existem na norma, informando média, desvio-padrão e CV.
 * O CV é derivado automaticamente de média e desvio-padrão.
 */
export function MatrizRelacoesDuais({ value = {}, onChange }: MatrizRelacoesDuaisProps) {
  const [numerador, setNumerador] = useState<string>()
  const [denominador, setDenominador] = useState<string>()

  const linhas = useMemo(
    () => Object.entries(value).map(([relacao, params]) => ({ relacao, ...params })),
    [value],
  )

  function adicionarRelacao() {
    if (!numerador || !denominador || numerador === denominador) return
    const chave = `${numerador}/${denominador}`
    if (value[chave]) return
    onChange?.({ ...value, [chave]: { media: 1, dp: 0.1, cv: 10 } })
    setNumerador(undefined)
    setDenominador(undefined)
  }

  function alterarCampo(relacao: string, campo: keyof RelacaoDual, novoValor: number | null) {
    if (novoValor === null) return
    const atual = { ...value[relacao], [campo]: novoValor }
    // CV = 100 * dp / média — mantido consistente sempre que média ou dp mudam
    if (campo === 'media' || campo === 'dp') {
      atual.cv = atual.media > 0 ? Number(((100 * atual.dp) / atual.media).toFixed(2)) : 0
    }
    onChange?.({ ...value, [relacao]: atual })
  }

  function remover(relacao: string) {
    const copia = { ...value }
    delete copia[relacao]
    onChange?.(copia)
  }

  const opcoes = NUTRIENTES.map((n) => ({ value: n, label: n }))

  return (
    <div>
      <Space style={{ marginBottom: 12 }} wrap>
        <Select
          placeholder="Nutriente A"
          style={{ width: 120 }}
          options={opcoes}
          value={numerador}
          onChange={setNumerador}
        />
        <Typography.Text strong>/</Typography.Text>
        <Select
          placeholder="Nutriente B"
          style={{ width: 120 }}
          options={opcoes.filter((o) => o.value !== numerador)}
          value={denominador}
          onChange={setDenominador}
        />
        <Button
          icon={<PlusOutlined />}
          onClick={adicionarRelacao}
          disabled={!numerador || !denominador}
        >
          Adicionar relação
        </Button>
      </Space>

      {linhas.length === 0 ? (
        <Empty description="Nenhuma relação dual cadastrada" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        <Table
          size="small"
          rowKey="relacao"
          pagination={false}
          scroll={{ y: 320 }}
          dataSource={linhas}
          columns={[
            {
              title: 'Relação',
              dataIndex: 'relacao',
              width: 100,
              render: (relacao: string) => <Typography.Text strong>{relacao}</Typography.Text>,
            },
            {
              title: 'Média',
              width: 130,
              render: (_, linha) => (
                <InputNumber
                  min={0.0001}
                  step={0.01}
                  value={linha.media}
                  style={{ width: '100%' }}
                  onChange={(v) => alterarCampo(linha.relacao, 'media', v)}
                />
              ),
            },
            {
              title: 'Desvio-padrão',
              width: 130,
              render: (_, linha) => (
                <InputNumber
                  min={0.0001}
                  step={0.01}
                  value={linha.dp}
                  style={{ width: '100%' }}
                  onChange={(v) => alterarCampo(linha.relacao, 'dp', v)}
                />
              ),
            },
            {
              title: 'CV (%)',
              width: 130,
              render: (_, linha) => (
                <InputNumber
                  min={0.0001}
                  step={0.01}
                  value={linha.cv}
                  style={{ width: '100%' }}
                  onChange={(v) => alterarCampo(linha.relacao, 'cv', v)}
                />
              ),
            },
            {
              title: '',
              width: 50,
              render: (_, linha) => (
                <Button
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => remover(linha.relacao)}
                />
              ),
            },
          ]}
        />
      )}
    </div>
  )
}
