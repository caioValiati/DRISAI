import { Button, Space, Tooltip } from 'antd'
import { CheckCircleOutlined, EditOutlined, StopOutlined } from '@ant-design/icons'

interface AcoesLinhaProps {
  ativo: boolean
  aoEditar: () => void
  aoInativar: () => void
  aoReativar: () => void
}

/** Botões "Editar" e "Inativar/Reativar" presentes em todas as listagens. */
export function AcoesLinha({ ativo, aoEditar, aoInativar, aoReativar }: AcoesLinhaProps) {
  return (
    <Space>
      <Tooltip title="Editar">
        <Button size="small" icon={<EditOutlined />} onClick={aoEditar} />
      </Tooltip>
      {ativo ? (
        <Tooltip title="Inativar">
          <Button size="small" danger icon={<StopOutlined />} onClick={aoInativar} />
        </Tooltip>
      ) : (
        <Tooltip title="Reativar">
          <Button
            size="small"
            icon={<CheckCircleOutlined />}
            style={{ color: '#2e7d32', borderColor: '#2e7d32' }}
            onClick={aoReativar}
          />
        </Tooltip>
      )}
    </Space>
  )
}
