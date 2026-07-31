import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
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
  Progress,
  Table,
  Tag,
  Typography,
} from "antd";
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  FilePdfOutlined,
  SaveOutlined,
} from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";
import { mensagemDeErro } from "@/shared/api/client";
import {
  TagClassificacao,
  TagStatusAmostra,
} from "@/shared/components/TagStatus";
import { NOMES_NUTRIENTES, type IndiceNutricional } from "@/shared/types";
import { amostrasApi } from "./api";

/**
 * RF012 — Painel de revisão: gráfico radial dos índices DRIS, tabela de
 * classificação, edição do texto de recomendação e conclusão do laudo (RN005/RN006).
 */
export function ResultadosPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [texto, setTexto] = useState("");
  const [confirmandoConclusao, setConfirmandoConclusao] = useState(false);
  const [baixando, setBaixando] = useState(false);

  const consulta = useQuery({
    queryKey: ["amostras", id],
    queryFn: () => amostrasApi.obter(id!),
    enabled: Boolean(id),
  });
  const amostra = consulta.data;

  // Enquanto o agrônomo não editar, o campo parte do rascunho gerado pela IA
  // — que ele revisa e assume como seu antes de concluir (RN005)
  useEffect(() => {
    const recomendacao = amostra?.recomendacao;
    setTexto(
      recomendacao?.texto_final_editado ?? recomendacao?.texto_rascunho_ia ?? "",
    );
  }, [
    amostra?.recomendacao?.texto_final_editado,
    amostra?.recomendacao?.texto_rascunho_ia,
  ]);

  async function baixarLaudo() {
    setBaixando(true);
    try {
      await amostrasApi.baixarLaudo(id!);
    } catch (erro) {
      message.error(mensagemDeErro(erro, "Não foi possível gerar o laudo."));
    } finally {
      setBaixando(false);
    }
  }

  const salvarRascunho = useMutation({
    mutationFn: () => amostrasApi.salvarRecomendacao(id!, texto),
    onSuccess: () => {
      message.success("Rascunho salvo.");
      queryClient.invalidateQueries({ queryKey: ["amostras"] });
    },
    onError: (erro) =>
      message.error(
        mensagemDeErro(erro, "Não foi possível salvar o rascunho."),
      ),
  });

  const concluir = useMutation({
    mutationFn: async () => {
      // RN005 — o texto revisado é salvo antes do fechamento
      await amostrasApi.salvarRecomendacao(id!, texto);
      return amostrasApi.concluir(id!);
    },
    onSuccess: () => {
      message.success("Diagnóstico concluído. O registro agora é imutável.");
      queryClient.invalidateQueries({ queryKey: ["amostras"] });
      setConfirmandoConclusao(false);
    },
    onError: (erro) => {
      message.error(
        mensagemDeErro(erro, "Não foi possível concluir o diagnóstico."),
      );
      setConfirmandoConclusao(false);
    },
  });

  if (consulta.isLoading) {
    return (
      <div style={{ display: "grid", placeItems: "center", minHeight: "50vh" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!amostra) {
    return (
      <Result
        status="404"
        title="Amostra não encontrada"
        extra={
          <Button onClick={() => navigate("/amostras")}>
            Voltar para a listagem
          </Button>
        }
      />
    );
  }

  const concluida = amostra.status === "CONCLUIDA";
  const sugestoes = amostra.recomendacao?.insumos_sugeridos ?? [];
  // Destaca, na composição do insumo, os nutrientes que ele veio corrigir
  const nutrientesDeficientes = new Set(
    amostra.indices
      .filter((indice) => indice.classificacao === "DEFICIENTE")
      .map((indice) => indice.elemento),
  );
  const dadosRadar = amostra.indices.map((indice) => ({
    nutriente: indice.elemento,
    indice:
      indice.indice_dris_calculado !== null
        ? Number(indice.indice_dris_calculado)
        : 0,
  }));

  return (
    <Space orientation="vertical" size={16} style={{ display: "flex" }}>
      <Space wrap style={{ justifyContent: "space-between", display: "flex" }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate("/amostras")}
          >
            Voltar
          </Button>
          <Typography.Title level={4} style={{ margin: 0 }}>
            Diagnóstico da amostra
          </Typography.Title>
          <TagStatusAmostra status={amostra.status} />
        </Space>
        {concluida ? (
          <Button
            type="primary"
            icon={<FilePdfOutlined />}
            loading={baixando}
            onClick={baixarLaudo}
          >
            Baixar laudo em PDF
          </Button>
        ) : (
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
              ? dayjs(amostra.recomendacao.data_emissao).format(
                  "DD/MM/YYYY HH:mm",
                )
              : "—"
          }. O laudo pode ser reemitido a qualquer momento com o mesmo conteúdo.`}
        />
      )}

      {!concluida && amostra.recomendacao?.falha_ia && (
        <Alert
          type="warning"
          showIcon
          title="IA indisponível"
          description={`${amostra.recomendacao.falha_ia} Os índices DRIS e os insumos sugeridos foram calculados normalmente — escreva a recomendação manualmente.`}
        />
      )}

      <Card size="small">
        <Descriptions
          column={{ xs: 1, md: 4 }}
          items={[
            {
              key: "talhao",
              label: "Talhão",
              children: amostra.talhao_nome ?? "—",
            },
            {
              key: "prop",
              label: "Propriedade",
              children: amostra.propriedade_nome ?? "—",
            },
            {
              key: "norma",
              label: "Norma",
              children: amostra.cultura_norma ?? "—",
            },
            {
              key: "data",
              label: "Data da coleta",
              children: dayjs(amostra.data_coleta).format("DD/MM/YYYY"),
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
                styles={{ content: { fontSize: 20, color: "#2e7d32" } }}
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
              Índices próximos de zero indicam equilíbrio; negativos,
              deficiência; positivos, excesso.
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
                  title: "Nutriente",
                  dataIndex: "elemento",
                  render: (e: string) => `${NOMES_NUTRIENTES[e] ?? e} (${e})`,
                },
                {
                  title: "Teor (laudo)",
                  dataIndex: "valor_laboratorio",
                  align: "right",
                  render: (v: string) => Number(v).toFixed(2),
                },
                {
                  title: "Índice DRIS",
                  dataIndex: "indice_dris_calculado",
                  align: "right",
                  render: (v: string | null) =>
                    v !== null ? Number(v).toFixed(2) : "—",
                },
                {
                  title: "Classificação",
                  dataIndex: "classificacao",
                  render: (c) => <TagClassificacao classificacao={c} />,
                },
              ]}
            />
          </Card>
        </Col>
      </Row>

      {sugestoes.length > 0 && (
        <Card
          title="Insumos sugeridos"
          extra={
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              Ranqueados pela aderência entre a composição do produto e as
              carências diagnosticadas, dentro do catálogo autorizado.
            </Typography.Text>
          }
        >
          <Row gutter={[12, 12]}>
            {sugestoes.map((sugestao) => (
              <Col xs={24} sm={12} lg={8} key={sugestao.insumo_id}>
                <Card size="small" style={{ height: "100%" }}>
                  <Space
                    orientation="vertical"
                    size={6}
                    style={{ display: "flex" }}
                  >
                    <Space
                      style={{
                        justifyContent: "space-between",
                        display: "flex",
                        width: "100%",
                      }}
                    >
                      <Typography.Text strong>
                        {sugestao.nome_comercial}
                      </Typography.Text>
                      <Tag color="green">
                        {Number(sugestao.match_score).toFixed(0)}%
                      </Tag>
                    </Space>
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                      {sugestao.fabricante}
                    </Typography.Text>
                    <Progress
                      percent={Number(sugestao.match_score)}
                      showInfo={false}
                      strokeColor="#2e7d32"
                      size="small"
                    />
                    <div>
                      {Object.entries(sugestao.concentracao_nutricional).map(
                        ([nutriente, valor]) => (
                          <Tag
                            key={nutriente}
                            color={
                              nutrientesDeficientes.has(nutriente)
                                ? "green"
                                : undefined
                            }
                          >
                            {nutriente} {valor}%
                          </Tag>
                        ),
                      )}
                    </div>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      <Card
        title="Recomendação técnica"
        extra={
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {amostra.recomendacao?.texto_rascunho_ia
              ? "Rascunho gerado por IA — revise, edite e assuma o texto antes de concluir."
              : "Escreva a recomendação com base nos índices e nos insumos acima."}
          </Typography.Text>
        }
      >
        <Input.TextArea
          rows={10}
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
          Ao concluir, você atesta a validade técnica da recomendação descrita.
          A amostra, os índices calculados e o texto final se tornarão{" "}
          <strong>imutáveis</strong>, sem possibilidade de edição posterior.
        </Typography.Paragraph>
      </Modal>
    </Space>
  );
}
