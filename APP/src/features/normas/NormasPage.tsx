import { useEffect, useState } from 'react'
import { Form, Input, Modal, Tag } from 'antd'
import { PaginaListagem } from '@/shared/components/PaginaListagem'
import { AcoesLinha } from '@/shared/components/AcoesLinha'
import { TagAtivo } from '@/shared/components/TagStatus'
import { useCrud } from '@/shared/hooks/useCrud'
import type { NormaDris, RelacaoDual } from '@/shared/types'
import { MatrizRelacoesDuais } from './MatrizRelacoesDuais'

interface FormularioNorma {
  cultura: string
  estadio_fenologico: string
  matriz_relacoes_duais: Record<string, RelacaoDual>
}

/** RF004 — Manter Normas DRIS (exclusivo do Administrador). */
export function NormasPage() {
  const { listagem, criar, atualizar, inativar } = useCrud<NormaDris, FormularioNorma>(
    'normas',
    'Norma',
  )
  const [form] = Form.useForm<FormularioNorma>()
  const [emEdicao, setEmEdicao] = useState<NormaDris | null>(null)
  const [modalAberto, setModalAberto] = useState(false)

  useEffect(() => {
    if (!modalAberto) return
    form.setFieldsValue(
      emEdicao
        ? {
            cultura: emEdicao.cultura,
            estadio_fenologico: emEdicao.estadio_fenologico,
            matriz_relacoes_duais: emEdicao.matriz_relacoes_duais,
          }
        : { cultura: '', estadio_fenologico: '', matriz_relacoes_duais: {} },
    )
  }, [modalAberto, emEdicao, form])

  function abrirModal(norma: NormaDris | null) {
    setEmEdicao(norma)
    setModalAberto(true)
  }

  async function salvar() {
    const valores = await form.validateFields()
    if (emEdicao) {
      await atualizar.mutateAsync({ id: emEdicao.id, dados: valores })
    } else {
      await criar.mutateAsync(valores)
    }
    setModalAberto(false)
  }

  return (
    <>
      <PaginaListagem<NormaDris>
        titulo="Normas DRIS"
        descricao="Padrões de referência usados no diagnóstico nutricional das amostras."
        textoBotaoNovo="Nova Norma"
        aoClicarNovo={() => abrirModal(null)}
        loading={listagem.isLoading}
        dataSource={listagem.data}
        columns={[
          { title: 'Cultura', dataIndex: 'cultura' },
          { title: 'Estádio fenológico', dataIndex: 'estadio_fenologico' },
          {
            title: 'Relações duais',
            render: (_, norma) => <Tag>{Object.keys(norma.matriz_relacoes_duais).length} relações</Tag>,
          },
          {
            title: 'Situação',
            render: (_, norma) => <TagAtivo ativo={norma.ativa} />,
          },
          {
            title: 'Ações',
            width: 110,
            render: (_, norma) => (
              <AcoesLinha
                rotulo="norma"
                ativo={norma.ativa}
                aoEditar={() => abrirModal(norma)}
                aoInativar={() => inativar.mutate(norma.id)}
              />
            ),
          },
        ]}
      />

      <Modal
        open={modalAberto}
        title={emEdicao ? 'Editar Norma DRIS' : 'Nova Norma DRIS'}
        okText="Salvar"
        cancelText="Cancelar"
        width={760}
        destroyOnHidden
        confirmLoading={criar.isPending || atualizar.isPending}
        onOk={salvar}
        onCancel={() => setModalAberto(false)}
      >
        <Form form={form} layout="vertical" requiredMark={false}>
          <Form.Item
            name="cultura"
            label="Cultura"
            rules={[{ required: true, min: 2, message: 'Informe a cultura.' }]}
          >
            <Input placeholder="Ex.: Soja" />
          </Form.Item>

          <Form.Item
            name="estadio_fenologico"
            label="Estádio fenológico"
            rules={[{ required: true, message: 'Informe o estádio fenológico.' }]}
          >
            <Input placeholder="Ex.: R2" />
          </Form.Item>

          <Form.Item
            name="matriz_relacoes_duais"
            label="Relações duais da norma"
            rules={[
              {
                validator: (_, valor) =>
                  valor && Object.keys(valor).length > 0
                    ? Promise.resolve()
                    : Promise.reject(new Error('Cadastre ao menos uma relação dual.')),
              },
            ]}
          >
            <MatrizRelacoesDuais />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
