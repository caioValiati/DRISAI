import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  App,
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Input,
  Modal,
  Result,
  Row,
  Space,
  Spin,
  Statistic,
  Table,
  Typography,
} from 'antd'
import { ArrowLeftOutlined, CheckCircleOutlined, SaveOutlined } from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from 'recharts'
import { mensagemDeErro } from '@/shared/api/client'
import { TagClassificacao, TagStatusAmostra } from '@/shared/components/TagStatus'
import { NOMES_NUTRIENTES, type IndiceNutricional } from '@/shared/types'
import { amostrasApi } from './api'

/**
 * RF012 — Painel de revisão: gráfico radial dos índices DRIS, tabela de
 * classificação, edição do texto de recomendação e conclusão do laudo (RN005/RN006).
 */
export function ResultadosPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { message } = App.useApp()
  const [texto, setTexto] = useState('')
  const [confirmandoConclusao, setConfirmandoConclusao] = useState(false)

  const consulta = useQuery({
    queryKey: ['amostras', id],
    queryFn: () => amostrasApi.obter(id!),
    enabled: Boolean(id),
  })
  const amostra = consulta.data

  useEffect(() => {
    setTexto(amostra?.recomendacao?.texto_final_editado ?? '')
  }, [amostra?.recomendacao?.texto_final_editado])

  const salvarRascunho = useMutation({
    mutationFn: () => amostrasApi.salvarRecomendacao(id!, texto),
    onSuccess: () => {
      message.success('Rascunho salvo.')
      queryClient.invalidateQueries({ queryKey: ['amostras'] })
    },
    onError: (erro) => message.error(mensagemDeErro(erro, 'Não foi possível salvar o rascunho.')),
  })

  const concluir = useMutation({
    mutationFn: async () => {
      // RN005 — o texto revisado é salvo antes do fechamento
      await amostrasApi.salvarRecomendacao(id!, texto)
      return amostrasApi.concluir(id!)
    },
    onSuccess: () => {
      message.success('Diagnóstico concluído. O registro agora é imutável (RN006).')
      queryClient.invalidateQueries({ queryKey: ['amostras'] })
      setConfirmandoConclusao(false)
    },
    onError: (erro) => {
      message.error(mensagemDeErro(erro, 'Não foi possível concluir o diagnóstico.'))
      setConfirmandoConclusao(false)
    },
  })

  if (consulta.isLoading) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', minHeight: '50vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!amostra) {
    return (
      <Result
        status="404"
        title="Amostra não encontrada"
        extra={<Button onClick={() => navigate('/amostras')}>Voltar para a listagem</Button>}
      />
    )
  }

  const concluida = amostra.status === 'CONCLUIDA'
  const dadosRadar = amostra.indices.map((indice) => ({
    nutriente: indice.elemento,
    indice: indice.indice_dris_calculado !== null ? Number(indice.indice_dris_calculado) : 0,
  }))

  return (
    <Space orientation="vertical" size={16} style={{ display: 'flex' }}>
      <Space wrap style={{ justifyContent: 'space-between', display: 'flex' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/amostras')}>
            Voltar
          </Button>
          <Typography.Title level={4} style={{ margin: 0 }}>
            Diagnóstico da amostra
          </Typography.Title>
          <TagStatusAmostra status={amostra.status} />
        </Space>
        {!concluida && (
          <Space>
            <Button
              icon={<SaveOutlined />}
              loading={salvarRascunho.isPending}
              onClick={() => salvarRascunho.mutate()}
            >
              Salvar rascunho
            </Button>
            <Button
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={() => setConfirmandoConclusao(true)}
            >
              Concluir diagnóstico
            </Button>
          </Space>
        )}
      </Space>

      {concluida && (
        <Alert
          type="success"
          showIcon
          title="Diagnóstico concluído"
          description={`Registro imutável desde ${
            amostra.recomendacao?.data_emissao
              ? dayjs(amostra.recomendacao.data_emissao).format('DD/MM/YYYY HH:mm')
              : '—'
          }. A geração do PDF do laudo será disponibilizada na Fase 2.`}
        />
      )}

      <Card size="small">
        <Descriptions
          column={{ xs: 1, md: 4 }}
          items={[
            { key: 'talhao', label: 'Talhão', children: amostra.talhao_nome ?? '—' },
            { key: 'prop', label: 'Propriedade', children: amostra.propriedade_nome ?? '—' },
            { key: 'norma', label: 'Norma', children: amostra.cultura_norma ?? '—' },
            {
              key: 'data',
              label: 'Data da coleta',
              children: dayjs(amostra.data_coleta).format('DD/MM/YYYY'),
            },
          ]}
        />
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="Equilíbrio nutricional (índices DRIS)"
            extra={
              <Statistic
                title="IBN"
                value={amostra.valor_ibn ? Number(amostra.valor_ibn) : 0}
                precision={2}
                styles={{ content: { fontSize: 20, color: '#2e7d32' } }}
              />
            }
          >
            <ResponsiveContainer width="100%" height={340}>
              <RadarChart data={dadosRadar}>
                <PolarGrid />
                <PolarAngleAxis dataKey="nutriente" />
                <PolarRadiusAxis />
                <Radar
                  name="Índice DRIS"
                  dataKey="indice"
                  stroke="#2e7d32"
                  fill="#2e7d32"
                  fillOpacity={0.35}
                />
              </RadarChart>
            </ResponsiveContainer>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              Índices próximos de zero indicam equilíbrio; negativos, deficiência; positivos,
              excesso.
            </Typography.Text>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Índices por nutriente">
            <Table<IndiceNutricional>
              size="small"
              rowKey="elemento"
              pagination={false}
              dataSource={amostra.indices}
              columns={[
                {
                  title: 'Nutriente',
                  dataIndex: 'elemento',
                  render: (e: string) => `${NOMES_NUTRIENTES[e] ?? e} (${e})`,
                },
                {
                  title: 'Teor (laudo)',
                  dataIndex: 'valor_laboratorio',
                  align: 'right',
                  render: (v: string) => Number(v).toFixed(2),
                },
                {
                  title: 'Índice DRIS',
                  dataIndex: 'indice_dris_calculado',
                  align: 'right',
                  render: (v: string | null) => (v !== null ? Number(v).toFixed(2) : '—'),
                },
                {
                  title: 'Classificação',
                  dataIndex: 'classificacao',
                  render: (c) => <TagClassificacao classificacao={c} />,
                },
              ]}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="Recomendação técnica"
        extra={
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            O rascunho automático por IA será incorporado na Fase 2 — escreva a recomendação
            com base nos índices acima.
          </Typography.Text>
        }
      >
        <Input.TextArea
          rows={8}
          value={texto}
          disabled={concluida}
          onChange={(evento) => setTexto(evento.target.value)}
          placeholder="Descreva a recomendação agronômica: produtos, dosagens, época e forma de aplicação..."
        />
      </Card>

      <Modal
        open={confirmandoConclusao}
        title="Confirmação de responsabilidade técnica"
        okText="Assumo a responsabilidade — Concluir"
        cancelText="Cancelar"
        confirmLoading={concluir.isPending}
        onOk={() => concluir.mutate()}
        onCancel={() => setConfirmandoConclusao(false)}
      >
        <Typography.Paragraph>
          Ao concluir, você atesta a validade técnica da recomendação descrita. A amostra, os
          índices calculados e o texto final se tornarão <strong>imutáveis</strong> (RN006), sem
          possibilidade de edição posterior.
        </Typography.Paragraph>
      </Modal>
    </Space>
  )
}
