import type { ReactNode } from 'react'
import { Button, Card, Space, Table, Typography } from 'antd'
import type { TableProps } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

interface PaginaListagemProps<T> extends Pick<TableProps<T>, 'columns' | 'dataSource' | 'loading'> {
  titulo: string
  descricao?: string
  textoBotaoNovo?: string
  aoClicarNovo?: () => void
  acoesExtras?: ReactNode
}

/**
 * Estrutura comum a todas as telas de listagem do DERS: cabeçalho, botão de
 * novo registro e tabela paginada.
 */
export function PaginaListagem<T extends { id: string }>({
  titulo,
  descricao,
  textoBotaoNovo,
  aoClicarNovo,
  acoesExtras,
  ...tabela
}: PaginaListagemProps<T>) {
  return (
    <Card>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 16,
          gap: 16,
          flexWrap: 'wrap',
        }}
      >
        <div>
          <Typography.Title level={4} style={{ margin: 0 }}>
            {titulo}
          </Typography.Title>
          {descricao && <Typography.Text type="secondary">{descricao}</Typography.Text>}
        </div>
        <Space>
          {acoesExtras}
          {aoClicarNovo && (
            <Button type="primary" icon={<PlusOutlined />} onClick={aoClicarNovo}>
              {textoBotaoNovo ?? 'Novo'}
            </Button>
          )}
        </Space>
      </div>

      <Table<T>
        rowKey="id"
        scroll={{ x: 'max-content' }}
        pagination={{ pageSize: 10, showSizeChanger: false }}
        {...tabela}
      />
    </Card>
  )
}
