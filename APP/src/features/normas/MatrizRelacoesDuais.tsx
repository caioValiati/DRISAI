import { useMemo, useState } from "react";
import {
  Button,
  Empty,
  InputNumber,
  Popconfirm,
  Select,
  Space,
  Table,
  Typography,
} from "antd";
import { DeleteOutlined, PlusOutlined, TableOutlined } from "@ant-design/icons";
import { NUTRIENTES, type RelacaoDual } from "@/shared/types";

type Matriz = Record<string, RelacaoDual>;

interface MatrizRelacoesDuaisProps {
  value?: Matriz;
  onChange?: (valor: Matriz) => void;
}

const RELACAO_PADRAO: RelacaoDual = { media: 1, dp: 0.1, cv: 10 };

/** Combinações A/B sem repetição, na ordem canônica dos nutrientes. */
function todasAsRelacoes(): string[] {
  const pares: string[] = [];
  for (let i = 0; i < NUTRIENTES.length; i++) {
    for (let j = i + 1; j < NUTRIENTES.length; j++) {
      pares.push(`${NUTRIENTES[i]}/${NUTRIENTES[j]}`);
    }
  }
  return pares;
}

/**
 * Editor das relações duais da Norma DRIS (Quadro 25 do DERS).
 *
 * As normas publicadas variam no conjunto de relações que trazem, então o
 * usuário pode montar a matriz par a par ou gerar de uma vez as 55 combinações
 * dos 11 nutrientes e editar os valores.
 *
 * CV e variância são derivados de média e desvio-padrão a cada edição, mas
 * continuam editáveis para quando a norma publicar valores próprios.
 */
export function MatrizRelacoesDuais({
  value = {},
  onChange,
}: MatrizRelacoesDuaisProps) {
  const [numerador, setNumerador] = useState<string>();
  const [denominador, setDenominador] = useState<string>();

  const linhas = useMemo(
    () =>
      Object.entries(value).map(([relacao, params]) => ({
        relacao,
        ...params,
      })),
    [value],
  );

  function adicionarRelacao() {
    if (!numerador || !denominador || numerador === denominador) return;
    const chave = `${numerador}/${denominador}`;
    if (value[chave]) return;
    onChange?.({ ...value, [chave]: { ...RELACAO_PADRAO } });
    setNumerador(undefined);
    setDenominador(undefined);
  }

  function inserirTodas() {
    const completa: Matriz = {};
    for (const relacao of todasAsRelacoes()) {
      completa[relacao] = value[relacao] ?? { ...RELACAO_PADRAO };
    }
    onChange?.(completa);
  }

  function alterarCampo(
    relacao: string,
    campo: keyof RelacaoDual,
    novoValor: number | null,
  ) {
    const atual: RelacaoDual = {
      ...value[relacao],
      [campo]: novoValor ?? undefined,
    };
    if (campo === "media" || campo === "dp") {
      const media = atual.media ?? 0;
      const dp = atual.dp ?? 0;
      atual.cv = media > 0 ? Number(((100 * dp) / media).toFixed(2)) : 0;
      atual.variancia = Number((dp * dp).toFixed(4));
    }
    onChange?.({ ...value, [relacao]: atual });
  }

  function remover(relacao: string) {
    const copia = { ...value };
    delete copia[relacao];
    onChange?.(copia);
  }

  const opcoes = NUTRIENTES.map((n) => ({ value: n, label: n }));

  function colunaNumerica(
    titulo: string,
    campo: keyof RelacaoDual,
    props: { min?: number; step?: number; precision?: number } = {},
  ) {
    return {
      title: titulo,
      width: 120,
      render: (_: unknown, linha: RelacaoDual & { relacao: string }) => (
        <InputNumber
          decimalSeparator=","
          min={props.min ?? 0}
          step={props.step ?? 0.01}
          precision={props.precision}
          value={linha[campo] as number | undefined}
          style={{ width: "100%" }}
          onChange={(v) => alterarCampo(linha.relacao, campo, v)}
        />
      ),
    };
  }

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
        <Button icon={<TableOutlined />} onClick={inserirTodas}>
          Inserir todas as relações ({todasAsRelacoes().length})
        </Button>
        {linhas.length > 0 && (
          <Popconfirm
            title="Remover todas as relações?"
            okText="Remover"
            cancelText="Cancelar"
            okButtonProps={{ danger: true }}
            onConfirm={() => onChange?.({})}
          >
            <Button danger>Limpar</Button>
          </Popconfirm>
        )}
      </Space>

      {linhas.length === 0 ? (
        <Empty
          description="Nenhuma relação dual cadastrada"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      ) : (
        <Table
          size="small"
          rowKey="relacao"
          pagination={false}
          scroll={{ y: 320, x: "max-content" }}
          dataSource={linhas}
          columns={[
            {
              title: "Relação",
              dataIndex: "relacao",
              width: 90,
              fixed: "left",
              render: (relacao: string) => (
                <Typography.Text strong>{relacao}</Typography.Text>
              ),
            },
            colunaNumerica("Média", "media", { min: 0.0001 }),
            colunaNumerica("Desvio-padrão", "dp", { min: 0.0001 }),
            colunaNumerica("CV (%)", "cv", { min: 0.0001 }),
            colunaNumerica("Variância", "variancia"),
            colunaNumerica("Nº observações", "n_observacoes", {
              step: 1,
              precision: 0,
            }),
            {
              title: "",
              width: 50,
              fixed: "right",
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
  );
}
