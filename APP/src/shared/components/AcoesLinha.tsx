import { Button, Popconfirm, Space, Tooltip } from 'antd'
import { EditOutlined, StopOutlined } from '@ant-design/icons'

interface AcoesLinhaProps {
  ativo: boolean
  aoEditar: () => void
  aoInativar: () => void
  rotulo: string
}

/** Botões "Editar" e "Inativar" presentes em todas as listagens do DERS. */
export function AcoesLinha({ ativo, aoEditar, aoInativar, rotulo }: AcoesLinhaProps) {
  return (
    <Space>
      <Tooltip title="Editar">
        <Button size="small" icon={<EditOutlined />} onClick={aoEditar} />
      </Tooltip>
      <Popconfirm
        title={`Inativar ${rotulo}`}
        description="O registro deixa de ficar disponível para novos usos, mas o histórico é preservado."
        okText="Inativar"
        cancelText="Cancelar"
        okButtonProps={{ danger: true }}
        onConfirm={aoInativar}
        disabled={!ativo}
      >
        <Tooltip title={ativo ? 'Inativar' : 'Registro já inativo'}>
          <Button size="small" danger icon={<StopOutlined />} disabled={!ativo} />
        </Tooltip>
      </Popconfirm>
    </Space>
  )
}
