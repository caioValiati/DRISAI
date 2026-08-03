import { useEffect, useMemo, useState } from "react";
import { Form, Input, InputNumber, Modal, Select } from "antd";
import { useQuery } from "@tanstack/react-query";
import { PaginaListagem } from "@/shared/components/PaginaListagem";
import { AcoesLinha } from "@/shared/components/AcoesLinha";
import { ModalVinculos } from "@/shared/components/ModalVinculos";
import { TagAtivo } from "@/shared/components/TagStatus";
import { useCrud } from "@/shared/hooks/useCrud";
import { useAcoesRegistro } from "@/shared/hooks/useAcoesRegistro";
import {
  useColunaAgronomo,
  useDescricaoCarteira,
} from "@/shared/hooks/useColunaAgronomo";
import { api } from "@/shared/api/client";
import type { Produtor, Propriedade } from "@/shared/types";

interface FormularioPropriedade {
  produtor_id: string;
  nome_fazenda: string;
  municipio_uf: string;
  area_total_ha: number;
}

/** RF007 — Manter Propriedades, sempre vinculadas a um produtor (RN002). */
export function PropriedadesPage() {
  const crud = useCrud<Propriedade, FormularioPropriedade>(
    "propriedades",
    "Propriedade",
  );
  const { listagem, criar, atualizar } = crud;
  const acoes = useAcoesRegistro<Propriedade>(
    crud,
    "propriedade",
    (p) => p.nome_fazenda,
  );
  const colunaAgronomo = useColunaAgronomo<Propriedade>();
  const descricaoCarteira = useDescricaoCarteira();
  const [form] = Form.useForm<FormularioPropriedade>();
  const [emEdicao, setEmEdicao] = useState<Propriedade | null>(null);
  const [modalAberto, setModalAberto] = useState(false);

  const { data: produtores } = useQuery({
    queryKey: ["produtores"],
    queryFn: async () => (await api.get<Produtor[]>("/produtores")).data,
  });

  // Só produtores ativos podem receber novas propriedades
  const opcoesProdutores = useMemo(
    () =>
      (produtores ?? [])
        .filter((p) => p.ativo || p.id === emEdicao?.produtor_id)
        .map((p) => ({ value: p.id, label: p.nome_razao })),
    [produtores, emEdicao],
  );

  useEffect(() => {
    if (!modalAberto) return;
    form.setFieldsValue({
      produtor_id: emEdicao?.produtor_id,
      nome_fazenda: emEdicao?.nome_fazenda ?? "",
      municipio_uf: emEdicao?.municipio_uf ?? "",
      area_total_ha: emEdicao ? Number(emEdicao.area_total_ha) : undefined,
    });
  }, [modalAberto, emEdicao, form]);

  async function salvar() {
    const valores = await form.validateFields();
    if (emEdicao) {
      await atualizar.mutateAsync({ id: emEdicao.id, dados: valores });
    } else {
      await criar.mutateAsync(valores);
    }
    setModalAberto(false);
  }

  return (
    <>
      <PaginaListagem<Propriedade>
        titulo="Propriedades"
        descricao={descricaoCarteira(
          "Fazendas vinculadas aos produtores da sua carteira.",
          "Fazendas de todas as carteiras da plataforma.",
        )}
        textoBotaoNovo="Nova Propriedade"
        aoClicarNovo={() => {
          setEmEdicao(null);
          setModalAberto(true);
        }}
        loading={listagem.isLoading}
        dataSource={listagem.data}
        columns={[
          { title: "Propriedade", dataIndex: "nome_fazenda" },
          {
            title: "Produtor",
            dataIndex: "produtor_nome",
            render: (v: string | null) => v || "—",
          },
          { title: "Município / UF", dataIndex: "municipio_uf" },
          {
            title: "Área total (ha)",
            dataIndex: "area_total_ha",
            align: "right",
            render: (valor: string) =>
              Number(valor).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              }),
          },
          ...colunaAgronomo,
          {
            title: "Situação",
            render: (_, item) => <TagAtivo ativo={item.ativo} />,
          },
          {
            title: "Ações",
            width: 110,
            render: (_, item) => (
              <AcoesLinha
                ativo={item.ativo}
                aoEditar={() => {
                  setEmEdicao(item);
                  setModalAberto(true);
                }}
                aoInativar={() => acoes.pedirInativacao(item)}
                aoReativar={() => acoes.pedirReativacao(item)}
              />
            ),
          },
        ]}
      />

      <ModalVinculos {...acoes.propsModal} />

      <Modal
        open={modalAberto}
        title={emEdicao ? "Editar Propriedade" : "Nova Propriedade"}
        okText={emEdicao ? "Salvar" : "Cadastrar"}
        cancelText="Cancelar"
        destroyOnHidden
        confirmLoading={criar.isPending || atualizar.isPending}
        onOk={salvar}
        onCancel={() => setModalAberto(false)}
      >
        <Form form={form} layout="vertical" requiredMark={false}>
          <Form.Item
            name="produtor_id"
            label="Produtor"
            rules={[{ required: true, message: "Selecione o produtor." }]}
          >
            <Select
              placeholder="Selecione"
              options={opcoesProdutores}
              showSearch
              optionFilterProp="label"
            />
          </Form.Item>

          <Form.Item
            name="nome_fazenda"
            label="Nome da propriedade"
            rules={[
              {
                required: true,
                min: 2,
                message: "Informe o nome da propriedade.",
              },
            ]}
          >
            <Input placeholder="Ex.: Fazenda Santa Rita" />
          </Form.Item>

          <Form.Item
            name="municipio_uf"
            label="Município / UF"
            rules={[
              {
                required: true,
                min: 2,
                message: "Informe o município e a UF.",
              },
            ]}
          >
            <Input placeholder="Ex.: Rio Verde/GO" />
          </Form.Item>

          <Form.Item
            name="area_total_ha"
            label="Área total (ha)"
            rules={[{ required: true, message: "Informe a área total." }]}
          >
            <InputNumber
              decimalSeparator=","
              min={0.01}
              step={0.1}
              style={{ width: "100%" }}
              placeholder="850,50"
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
