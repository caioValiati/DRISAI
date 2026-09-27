import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { App, Button, Card, Form, Input, Typography } from 'antd'
import { LockOutlined } from '@ant-design/icons'
import { api, mensagemDeErro } from '@/shared/api/client'

export function RedefinirSenhaPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(valores: { novaSenha: string }) {
    if (!token) {
      message.error('Token inválido ou ausente na URL.')
      return
    }

    setEnviando(true)
    try {
      await api.post('/auth/redefinir_senha', {
        token,
        new_password: valores.novaSenha,
      })
      message.success('Senha redefinida com sucesso!')
      navigate('/login', { replace: true })
    } catch (erro) {
      message.error(mensagemDeErro(erro, 'Erro ao redefinir a senha.'))
    } finally {
      setEnviando(false)
    }
  }

  if (!token) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh', background: '#f5f7f5' }}>
        <Card style={{ width: 400, textAlign: 'center' }}>
          <Typography.Title level={4} type="danger">
            Link Inválido
          </Typography.Title>
          <Typography.Paragraph>
            Nenhum token de redefinição foi fornecido. Por favor, solicite um novo link.
          </Typography.Paragraph>
          <Link to="/esqueci_senha">Solicitar novo link</Link>
        </Card>
      </div>
    )
  }

  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh', background: '#f5f7f5' }}>
      <Card style={{ width: 400, boxShadow: '0 4px 16px rgba(0,0,0,.06)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Typography.Title level={3} style={{ margin: 0, color: '#2e7d32' }}>
            Nova Senha
          </Typography.Title>
          <Typography.Text type="secondary">Crie uma nova senha para sua conta</Typography.Text>
        </div>

        <Form layout="vertical" onFinish={aoEnviar} requiredMark={false}>
          <Form.Item
            name="novaSenha"
            label="Nova Senha"
            rules={[
              { required: true, message: 'Informe a nova senha.' },
              { min: 6, message: 'A senha deve ter pelo menos 6 caracteres.' },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Sua nova senha" />
          </Form.Item>

          <Form.Item
            name="confirmarSenha"
            label="Confirme a Nova Senha"
            dependencies={['novaSenha']}
            rules={[
              { required: true, message: 'Confirme sua senha.' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('novaSenha') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('As senhas não coincidem.'))
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Repita a nova senha" />
          </Form.Item>

          <Button type="primary" htmlType="submit" block loading={enviando}>
            Redefinir Senha
          </Button>
        </Form>
      </Card>
    </div>
  )
}