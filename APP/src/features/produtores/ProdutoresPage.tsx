import { useEffect, useState } from 'react'
import { Form, Input, Modal } from 'antd'
import { PaginaListagem } from '@/shared/components/PaginaListagem'
import { AcoesLinha } from '@/shared/components/AcoesLinha'
import { TagAtivo } from '@/shared/components/TagStatus'
import { useCrud } from '@/shared/hooks/useCrud'
import type { Produtor } from '@/shared/types'

interface FormularioProdutor {
  nome_razao: string
  cpf_cnpj: string
  telefone?: string
  email?: string
}

/** Formata CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00) para exibição. */
function formatarDocumento(documento: string) {
  const digitos = documento.replace(/\D/g, '')
  if (digitos.length === 11) {
    return digitos.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  }
  if (digitos.length === 14) {
    return digitos.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
  }
  return documento
}

/** RF006 — Manter Produtores (carteira do agrônomo). */
export function ProdutoresPage() {
  const { listagem, criar, atualizar, inativar } = useCrud<Produtor, FormularioProdutor>(
    'produtores',
    'Produtor',
  )
  const [form] = Form.useForm<FormularioProdutor>()
  const [emEdicao, setEmEdicao] = useState<Produtor | null>(null)
  const [modalAberto, setModalAberto] = useState(false)

  useEffect(() => {
    if (!modalAberto) return
    form.setFieldsValue({
      nome_razao: emEdicao?.nome_razao ?? '',
      cpf_cnpj: emEdicao ? formatarDocumento(emEdicao.cpf_cnpj) : '',
      telefone: emEdicao?.telefone ?? '',
      email: emEdicao?.email ?? '',
    })
  }, [modalAberto, emEdicao, form])

  async function salvar() {
    const valores = await form.validateFields()
    const dados = {
      ...valores,
      telefone: valores.telefone || undefined,
      email: valores.email || undefined,
    }
    if (emEdicao) {
      await atualizar.mutateAsync({ id: emEdicao.id, dados })
    } else {
      await criar.mutateAsync(dados)
    }
    setModalAberto(false)
  }

  return (
    <>
      <PaginaListagem<Produtor>
        titulo="Produtores"
        descricao="Carteira de produtores rurais atendidos por você."
        textoBotaoNovo="Novo Produtor"
        aoClicarNovo={() => {
          setEmEdicao(null)
          setModalAberto(true)
        }}
        loading={listagem.isLoading}
        dataSource={listagem.data}
        columns={[
          { title: 'Nome / Razão social', dataIndex: 'nome_razao' },
          {
            title: 'CPF / CNPJ',
            dataIndex: 'cpf_cnpj',
            render: (documento: string) => formatarDocumento(documento),
          },
          { title: 'Telefone', dataIndex: 'telefone', render: (v: string | null) => v || '—' },
          { title: 'E-mail', dataIndex: 'email', render: (v: string | null) => v || '—' },
          { title: 'Situação', render: (_, produtor) => <TagAtivo ativo={produtor.ativo} /> },
          {
            title: 'Ações',
            width: 110,
            render: (_, produtor) => (
              <AcoesLinha
                rotulo="produtor"
                ativo={produtor.ativo}
                aoEditar={() => {
                  setEmEdicao(produtor)
                  setModalAberto(true)
                }}
                aoInativar={() => inativar.mutate(produtor.id)}
              />
            ),
          },
        ]}
      />

      <Modal
        open={modalAberto}
        title={emEdicao ? 'Editar Produtor' : 'Novo Produtor'}
        okText={emEdicao ? 'Salvar' : 'Cadastrar'}
        cancelText="Cancelar"
        destroyOnHidden
        confirmLoading={criar.isPending || atualizar.isPending}
        onOk={salvar}
        onCancel={() => setModalAberto(false)}
      >
        <Form form={form} layout="vertical" requiredMark={false}>
          <Form.Item
            name="nome_razao"
            label="Nome completo / Razão social"
            rules={[{ required: true, min: 3, message: 'Informe o nome ou razão social.' }]}
          >
            <Input placeholder="Ex.: Fazendas Boa Safra LTDA" />
          </Form.Item>

          <Form.Item
            name="cpf_cnpj"
            label="CPF / CNPJ"
            rules={[
              { required: true, message: 'Informe o CPF ou CNPJ.' },
              {
                validator: (_, valor) => {
                  const digitos = (valor ?? '').replace(/\D/g, '')
                  return digitos.length === 11 || digitos.length === 14
                    ? Promise.resolve()
                    : Promise.reject(new Error('CPF deve ter 11 dígitos e CNPJ, 14.'))
                },
              },
            ]}
          >
            <Input placeholder="Somente números ou formatado" />
          </Form.Item>

          <Form.Item name="telefone" label="Telefone">
            <Input placeholder="(64) 99999-8888" />
          </Form.Item>

          <Form.Item name="email" label="E-mail" rules={[{ type: 'email', message: 'E-mail inválido.' }]}>
            <Input placeholder="contato@produtor.com" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
