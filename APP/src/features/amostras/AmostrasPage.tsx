import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  App,
  Button,
  Col,
  DatePicker,
  Divider,
  Form,
  InputNumber,
  Modal,
  Row,
  Select,
  Tooltip,
  Typography,
} from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import dayjs, { type Dayjs } from 'dayjs'
import { PaginaListagem } from '@/shared/components/PaginaListagem'
import { useDescricaoCarteira } from '@/shared/hooks/useColunaAgronomo'
import { TagStatusAmostra } from '@/shared/components/TagStatus'
import { api, mensagemDeErro } from '@/shared/api/client'
import {
  NOMES_NUTRIENTES,
  NUTRIENTES,
  type AmostraResumo,
  type NormaDris,
  type Talhao,
} from '@/shared/types'
import { amostrasApi, type FormularioAmostra } from './api'

/** RF009 — Manter Amostras: entrada dos laudos laboratoriais e disparo do DRIS. */
export function AmostrasPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const descricaoCarteira = useDescricaoCarteira()
  const [modalAberto, setModalAberto] = useState(false)

  const listagem = useQuery({ queryKey: ['amostras'], queryFn: amostrasApi.listar })

  const { data: talhoes } = useQuery({
    queryKey: ['talhoes'],
    queryFn: async () => (await api.get<Talhao[]>('/talhoes')).data,
  })
  const { data: normas } = useQuery({
    queryKey: ['normas'],
    queryFn: async () => (await api.get<NormaDris[]>('/normas')).data,
  })

  const opcoesTalhoes = useMemo(
    () =>
      (talhoes ?? [])
        .filter((t) => t.ativo)
        .map((t) => ({ value: t.id, label: `${t.identificacao} — ${t.propriedade_nome ?? ''}` })),
    [talhoes],
  )

  // RN002 — apenas normas ativas podem ser usadas em novas amostras
  const opcoesNormas = useMemo(
    () =>
      (normas ?? [])
        .filter((n) => n.ativa)
        .map((n) => ({ value: n.id, label: `${n.cultura} (${n.estadio_fenologico})` })),
    [normas],
  )

  useEffect(() => {
    if (modalAberto) {
      form.resetFields()
      form.setFieldValue('data_coleta', dayjs())
    }
  }, [modalAberto, form])

  const processar = useMutation({
    mutationFn: amostrasApi.criar,
    onSuccess: (amostra) => {
      message.success('Amostra processada: índices DRIS e IBN calculados.')
      queryClient.invalidateQueries({ queryKey: ['amostras'] })
      setModalAberto(false)
      navigate(`/amostras/${amostra.id}`)
    },
    onError: (erro) => message.error(mensagemDeErro(erro, 'Não foi possível processar a amostra.')),
  })

  async function aoProcessar() {
    const valores = await form.validateFields()
    const teores: Record<string, number> = {}
    for (const nutriente of NUTRIENTES) {
      teores[nutriente] = valores[`teor_${nutriente}`]
    }
    const dados: FormularioAmostra = {
      talhao_id: valores.talhao_id,
      norma_dris_id: valores.norma_dris_id,
      data_coleta: (valores.data_coleta as Dayjs).format('YYYY-MM-DD'),
      teores,
    }
    processar.mutate(dados)
  }

  return (
    <>
      <PaginaListagem<AmostraResumo>
        titulo="Amostras foliares"
        descricao={descricaoCarteira("Lançamento de laudos laboratoriais e acompanhamento dos diagnósticos.", "Diagnósticos de todas as carteiras da plataforma.")}
        textoBotaoNovo="Nova Amostra"
        aoClicarNovo={() => setModalAberto(true)}
        loading={listagem.isLoading}
        dataSource={listagem.data}
        columns={[
          {
            title: 'Data da coleta',
            dataIndex: 'data_coleta',
            render: (data: string) => dayjs(data).format('DD/MM/YYYY'),
          },
          { title: 'Talhão', dataIndex: 'talhao_nome', render: (v: string | null) => v ?? '—' },
          {
            title: 'Propriedade',
            dataIndex: 'propriedade_nome',
            render: (v: string | null) => v ?? '—',
          },
          { title: 'Norma', dataIndex: 'cultura_norma', render: (v: string | null) => v ?? '—' },
          {
            title: 'IBN',
            dataIndex: 'valor_ibn',
            align: 'right',
            render: (v: string | null) => (v !== null ? Number(v).toFixed(2) : '—'),
          },
          { title: 'Status', render: (_, amostra) => <TagStatusAmostra status={amostra.status} /> },
          {
            title: 'Ações',
            width: 90,
            render: (_, amostra) => (
              <Tooltip title="Ver resultados e revisar">
                <Button
                  size="small"
                  icon={<EyeOutlined />}
                  onClick={() => navigate(`/amostras/${amostra.id}`)}
                />
              </Tooltip>
            ),
          },
        ]}
      />

      <Modal
        open={modalAberto}
        title="Nova Amostra Foliar"
        okText="Processar Análise DRIS"
        cancelText="Cancelar"
        width={760}
        destroyOnHidden
        confirmLoading={processar.isPending}
        onOk={aoProcessar}
        onCancel={() => setModalAberto(false)}
      >
        <Form form={form} layout="vertical" requiredMark={false}>
          <Row gutter={16}>
            <Col span={9}>
              <Form.Item
                name="talhao_id"
                label="Talhão"
                rules={[{ required: true, message: 'Selecione o talhão.' }]}
              >
                <Select
                  placeholder="Selecione"
                  options={opcoesTalhoes}
                  showSearch
                  optionFilterProp="label"
                />
              </Form.Item>
            </Col>
            <Col span={9}>
              <Form.Item
                name="norma_dris_id"
                label="Norma de referência"
                rules={[{ required: true, message: 'Selecione a norma DRIS.' }]}
              >
                <Select placeholder="Selecione" options={opcoesNormas} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="data_coleta"
                label="Data da coleta"
                rules={[{ required: true, message: 'Informe a data.' }]}
              >
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" maxDate={dayjs()} />
              </Form.Item>
            </Col>
          </Row>

          <Divider style={{ margin: '8px 0 16px' }} />
          <Typography.Text strong>Parâmetros nutricionais do laudo laboratorial</Typography.Text>
          <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 8 }}>
            Macronutrientes em g/kg e micronutrientes em mg/kg, conforme o laudo.
          </Typography.Paragraph>

          <Row gutter={[12, 0]}>
            {NUTRIENTES.map((nutriente) => (
              <Col span={6} key={nutriente}>
                <Form.Item
                  name={`teor_${nutriente}`}
                  label={`${NOMES_NUTRIENTES[nutriente]} (${nutriente})`}
                  rules={[
                    { required: true, message: 'Obrigatório.' },
                    {
                      validator: (_, v) =>
                        v === undefined || v > 0
                          ? Promise.resolve()
                          : Promise.reject(new Error('Deve ser > 0.')),
                    },
                  ]}
                >
                  <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            ))}
          </Row>
        </Form>
      </Modal>
    </>
  )
}
