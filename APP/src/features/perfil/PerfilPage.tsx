import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { App, Button, Card, Descriptions, Form, Input, Modal, Space, Typography } from 'antd'
import { useAuth } from '@/app/providers/AuthContext'
import { api, mensagemDeErro } from '@/shared/api/client'
import type { Usuario } from '@/shared/types'

/** RF001 — visualização, edição de dados cadastrais e desativação da conta. */
export function PerfilPage() {
  const { usuario, atualizarUsuario, sair } = useAuth()
  const { message } = App.useApp()
  const navigate = useNavigate()
  const [salvando, setSalvando] = useState(false)
  const [confirmandoDesativacao, setConfirmandoDesativacao] = useState(false)

  async function salvar(valores: { nome: string; email: string }) {
    setSalvando(true)
    try {
      const { data } = await api.put<Usuario>('/auth/me', valores)
      atualizarUsuario(data)
      message.success('Dados atualizados com sucesso.')
    } catch (erro) {
      message.error(mensagemDeErro(erro, 'Não foi possível salvar as alterações.'))
    } finally {
      setSalvando(false)
    }
  }

  async function desativarConta() {
    try {
      await api.post('/auth/me/desativar')
      message.success('Conta desativada.')
      await sair()
      navigate('/login')
    } catch (erro) {
      message.error(mensagemDeErro(erro, 'Não foi possível desativar a conta.'))
    }
  }

  return (
    <Card style={{ maxWidth: 720 }}>
      <Typography.Title level={4} style={{ marginTop: 0 }}>
        Meu perfil
      </Typography.Title>

      <Descriptions column={1} size="small" style={{ marginBottom: 24 }}>
        <Descriptions.Item label="Perfil de acesso">
          {usuario?.perfil === 'ADMIN' ? 'Administrador' : 'Engenheiro Agrônomo'}
        </Descriptions.Item>
        {usuario?.registro_crea && (
          <Descriptions.Item label="Registro CREA">{usuario.registro_crea}</Descriptions.Item>
        )}
      </Descriptions>

      <Form
        layout="vertical"
        initialValues={{ nome: usuario?.nome, email: usuario?.email }}
        onFinish={salvar}
        requiredMark={false}
      >
        <Form.Item
          name="nome"
          label="Nome completo"
          rules={[{ required: true, min: 3, message: 'Informe o nome completo.' }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          name="email"
          label="E-mail"
          rules={[
            { required: true, message: 'Informe o e-mail.' },
            { type: 'email', message: 'E-mail inválido.' },
          ]}
        >
          <Input />
        </Form.Item>

        <Space>
          <Button type="primary" htmlType="submit" loading={salvando}>
            Salvar alterações
          </Button>
          <Button danger onClick={() => setConfirmandoDesativacao(true)}>
            Desativar conta
          </Button>
        </Space>
      </Form>

      <Modal
        open={confirmandoDesativacao}
        title="Desativar conta"
        okText="Desativar conta"
        cancelText="Cancelar"
        okButtonProps={{ danger: true }}
        onOk={desativarConta}
        onCancel={() => setConfirmandoDesativacao(false)}
      >
        <Typography.Paragraph>
          Sua conta será desativada e você perderá o acesso ao sistema. Os registros já
          cadastrados são preservados no histórico.
        </Typography.Paragraph>
      </Modal>
    </Card>
  )
}
