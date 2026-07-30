import { useEffect, useMemo, useState } from 'react'
import { Form, Input, InputNumber, Modal, Select } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { PaginaListagem } from '@/shared/components/PaginaListagem'
import { AcoesLinha } from '@/shared/components/AcoesLinha'
import { TagAtivo } from '@/shared/components/TagStatus'
import { useCrud } from '@/shared/hooks/useCrud'
import { api } from '@/shared/api/client'
import type { Propriedade, Talhao } from '@/shared/types'

interface FormularioTalhao {
  propriedade_id: string
  identificacao: string
  tamanho_ha: number
  historico_culturas?: string
}

/** RF008 — Manter Talhões, subdivisões de plantio das propriedades. */
export function TalhoesPage() {
  const { listagem, criar, atualizar, inativar } = useCrud<Talhao, FormularioTalhao>(
    'talhoes',
    'Talhão',
  )
  const [form] = Form.useForm<FormularioTalhao>()
  const [emEdicao, setEmEdicao] = useState<Talhao | null>(null)
  const [modalAberto, setModalAberto] = useState(false)

  const { data: propriedades } = useQuery({
    queryKey: ['propriedades'],
    queryFn: async () => (await api.get<Propriedade[]>('/propriedades')).data,
  })

  const opcoesPropriedades = useMemo(
    () =>
      (propriedades ?? [])
        .filter((p) => p.ativo || p.id === emEdicao?.propriedade_id)
        .map((p) => ({ value: p.id, label: `${p.nome_fazenda} — ${p.produtor_nome ?? ''}` })),
    [propriedades, emEdicao],
  )

  useEffect(() => {
    if (!modalAberto) return
    form.setFieldsValue({
      propriedade_id: emEdicao?.propriedade_id,
      identificacao: emEdicao?.identificacao ?? '',
      tamanho_ha: emEdicao ? Number(emEdicao.tamanho_ha) : undefined,
      historico_culturas: emEdicao?.historico_culturas ?? '',
    })
  }, [modalAberto, emEdicao, form])

  async function salvar() {
    const valores = await form.validateFields()
    const dados = { ...valores, historico_culturas: valores.historico_culturas || undefined }
    if (emEdicao) {
      await atualizar.mutateAsync({ id: emEdicao.id, dados })
    } else {
      await criar.mutateAsync(dados)
    }
    setModalAberto(false)
  }

  return (
    <>
      <PaginaListagem<Talhao>
        titulo="Talhões"
        descricao="Subdivisões de plantio das propriedades da sua carteira."
        textoBotaoNovo="Novo Talhão"
        aoClicarNovo={() => {
          setEmEdicao(null)
          setModalAberto(true)
        }}
        loading={listagem.isLoading}
        dataSource={listagem.data}
        columns={[
          { title: 'Identificação', dataIndex: 'identificacao' },
          {
            title: 'Propriedade',
            dataIndex: 'propriedade_nome',
            render: (v: string | null) => v || '—',
          },
          {
            title: 'Tamanho (ha)',
            dataIndex: 'tamanho_ha',
            align: 'right',
            render: (valor: string) =>
              Number(valor).toLocaleString('pt-BR', { minimumFractionDigits: 2 }),
          },
          {
            title: 'Histórico de culturas',
            dataIndex: 'historico_culturas',
            ellipsis: true,
            render: (v: string | null) => v || '—',
          },
          { title: 'Situação', render: (_, item) => <TagAtivo ativo={item.ativo} /> },
          {
            title: 'Ações',
            width: 110,
            render: (_, item) => (
              <AcoesLinha
                rotulo="talhão"
                ativo={item.ativo}
                aoEditar={() => {
                  setEmEdicao(item)
                  setModalAberto(true)
                }}
                aoInativar={() => inativar.mutate(item.id)}
              />
            ),
          },
        ]}
      />

      <Modal
        open={modalAberto}
        title={emEdicao ? 'Editar Talhão' : 'Novo Talhão'}
        okText={emEdicao ? 'Salvar' : 'Cadastrar'}
        cancelText="Cancelar"
        destroyOnHidden
        confirmLoading={criar.isPending || atualizar.isPending}
        onOk={salvar}
        onCancel={() => setModalAberto(false)}
      >
        <Form form={form} layout="vertical" requiredMark={false}>
          <Form.Item
            name="propriedade_id"
            label="Propriedade"
            rules={[{ required: true, message: 'Selecione a propriedade.' }]}
          >
            <Select
              placeholder="Selecione"
              options={opcoesPropriedades}
              showSearch
              optionFilterProp="label"
            />
          </Form.Item>

          <Form.Item
            name="identificacao"
            label="Identificação"
            rules={[{ required: true, message: 'Informe a identificação do talhão.' }]}
          >
            <Input placeholder="Ex.: Talhão 01" />
          </Form.Item>

          <Form.Item
            name="tamanho_ha"
            label="Tamanho (ha)"
            rules={[{ required: true, message: 'Informe o tamanho.' }]}
          >
            <InputNumber min={0.01} step={0.1} style={{ width: '100%' }} placeholder="120,00" />
          </Form.Item>

          <Form.Item name="historico_culturas" label="Histórico de culturas">
            <Input.TextArea rows={3} placeholder="Ex.: Soja 24/25, milho safrinha 25" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
