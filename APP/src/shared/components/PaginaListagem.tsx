import type { ReactNode } from 'react'
import { Button, Card, Space, Table, Typography } from 'antd'
import type { TableProps } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import './table.css'

interface PaginaListagemProps<T> extends Pick<TableProps<T>, 'columns' | 'dataSource' | 'loading'> {
  titulo: string
  descricao?: string
  textoBotaoNovo?: string
  aoClicarNovo?: () => void
  acoesExtras?: ReactNode
}

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
        size='small'
        scroll={{ x: 'max-content', y: '50vh' }} 
        pagination={{ pageSize: 10, showSizeChanger: false }}
        rowClassName={(_, index) => (index % 2 === 0 ? 'linha-par' : 'linha-impar')}
        {...tabela}
      />
    </Card>
  )
}