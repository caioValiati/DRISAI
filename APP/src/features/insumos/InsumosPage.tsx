import { useEffect, useMemo, useState } from 'react'
import { Col, Form, Input, InputNumber, Modal, Row, Select, Tag, Typography } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { PaginaListagem } from '@/shared/components/PaginaListagem'
import { AcoesLinha } from '@/shared/components/AcoesLinha'
import { TagAtivo } from '@/shared/components/TagStatus'
import { useCrud } from '@/shared/hooks/useCrud'
import { api } from '@/shared/api/client'
import { NOMES_NUTRIENTES, NUTRIENTES, type Insumo, type NormaDris } from '@/shared/types'

interface FormularioInsumo {
  nome_comercial: string
  fabricante: string
  culturas_autorizadas: string[]
  concentracao_nutricional: Record<string, number>
}

/** RF005 — Manter Insumos (exclusivo do Administrador). */
export function InsumosPage() {
  const { listagem, criar, atualizar, inativar, reativar } = useCrud<Insumo, FormularioInsumo>(
    'insumos',
    'Insumo',
  )
  const [form] = Form.useForm()
  const [emEdicao, setEmEdicao] = useState<Insumo | null>(null)
  const [modalAberto, setModalAberto] = useState(false)

  // As culturas autorizadas vêm das normas cadastradas (Quadro 28 do DERS)
  const { data: normas } = useQuery({
    queryKey: ['normas'],
    queryFn: async () => (await api.get<NormaDris[]>('/normas')).data,
  })

  const opcoesCulturas = useMemo(() => {
    const culturas = new Set((normas ?? []).map((n) => n.cultura))
    return [...culturas].map((c) => ({ value: c, label: c }))
  }, [normas])

  useEffect(() => {
    if (!modalAberto) return
    form.setFieldsValue({
      nome_comercial: emEdicao?.nome_comercial ?? '',
      fabricante: emEdicao?.fabricante ?? '',
      culturas_autorizadas: emEdicao?.culturas_autorizadas ?? [],
      ...Object.fromEntries(
        NUTRIENTES.map((n) => [`nutriente_${n}`, emEdicao?.concentracao_nutricional?.[n]]),
      ),
    })
  }, [modalAberto, emEdicao, form])

  async function salvar() {
    const valores = await form.validateFields()
    const concentracao: Record<string, number> = {}
    for (const nutriente of NUTRIENTES) {
      const valor = valores[`nutriente_${nutriente}`]
      if (valor !== undefined && valor !== null && valor !== '') {
        concentracao[nutriente] = Number(valor)
      }
    }
    const dados: FormularioInsumo = {
      nome_comercial: valores.nome_comercial,
      fabricante: valores.fabricante,
      culturas_autorizadas: valores.culturas_autorizadas,
      concentracao_nutricional: concentracao,
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
      <PaginaListagem<Insumo>
        titulo="Catálogo de Insumos"
        descricao="Produtos em conformidade regulatória disponíveis para recomendação (RN004)."
        textoBotaoNovo="Novo Insumo"
        aoClicarNovo={() => {
          setEmEdicao(null)
          setModalAberto(true)
        }}
        loading={listagem.isLoading}
        dataSource={listagem.data}
        columns={[
          { title: 'Nome comercial', dataIndex: 'nome_comercial' },
          { title: 'Fabricante', dataIndex: 'fabricante' },
          {
            title: 'Culturas autorizadas',
            render: (_, insumo) => insumo.culturas_autorizadas.map((c) => <Tag key={c}>{c}</Tag>),
          },
          {
            title: 'Composição',
            render: (_, insumo) =>
              Object.entries(insumo.concentracao_nutricional)
                .map(([nutriente, valor]) => `${nutriente} ${valor}%`)
                .join(' · '),
          },
          { title: 'Situação', render: (_, insumo) => <TagAtivo ativo={insumo.ativo} /> },
          {
            title: 'Ações',
            width: 110,
            render: (_, insumo) => (
              <AcoesLinha
                ativo={insumo.ativo}
                aoEditar={() => {
                  setEmEdicao(insumo)
                  setModalAberto(true)
                }}
                aoInativar={() => inativar.mutate(insumo.id)}
                aoReativar={() => reativar.mutate({ id: insumo.id })}
              />
            ),
          },
        ]}
      />

      <Modal
        open={modalAberto}
        title={emEdicao ? 'Editar Insumo' : 'Novo Insumo'}
        okText="Salvar"
        cancelText="Cancelar"
        width={720}
        destroyOnHidden
        confirmLoading={criar.isPending || atualizar.isPending}
        onOk={salvar}
        onCancel={() => setModalAberto(false)}
      >
        <Form form={form} layout="vertical" requiredMark={false}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="nome_comercial"
                label="Nome comercial"
                rules={[{ required: true, min: 2, message: 'Informe o nome comercial.' }]}
              >
                <Input placeholder="Ex.: NutriFol Zn" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="fabricante"
                label="Fabricante"
                rules={[{ required: true, min: 2, message: 'Informe o fabricante.' }]}
              >
                <Input placeholder="Ex.: AgroQuímica S.A." />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="culturas_autorizadas"
            label="Culturas autorizadas"
            rules={[{ required: true, message: 'Selecione ao menos uma cultura.' }]}
          >
            <Select
              mode="multiple"
              placeholder="Selecione as culturas"
              options={opcoesCulturas}
            />
          </Form.Item>

          <Typography.Text strong>Concentração nutricional (%)</Typography.Text>
          <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 8 }}>
            Preencha apenas os nutrientes presentes na formulação.
          </Typography.Paragraph>
          <Row gutter={[12, 0]}>
            {NUTRIENTES.map((nutriente) => (
              <Col span={6} key={nutriente}>
                <Form.Item
                  name={`nutriente_${nutriente}`}
                  label={`${nutriente} — ${NOMES_NUTRIENTES[nutriente]}`}
                >
                  <InputNumber min={0} max={100} step={0.1} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            ))}
          </Row>
        </Form>
      </Modal>
    </>
  )
}
