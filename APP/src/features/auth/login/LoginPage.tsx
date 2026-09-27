import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { App, Button, Card, Form, Input, Typography } from 'antd'
import { LockOutlined, MailOutlined } from '@ant-design/icons'
import { useAuth } from '@/app/providers/AuthContext'
import { mensagemDeErro } from '@/shared/api/client'

export function LoginPage() {
  const { entrar } = useAuth()
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(valores: { email: string; senha: string }) {
    setEnviando(true)
    try {
      await entrar(valores.email, valores.senha)
      navigate('/', { replace: true })
    } catch (erro) {
      message.error(mensagemDeErro(erro, 'E-mail ou senha inválidos.'))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh', background: '#f5f7f5' }}>
      <Card style={{ width: 400, boxShadow: '0 4px 16px rgba(0,0,0,.06)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Typography.Title level={3} style={{ margin: 0, color: '#2e7d32' }}>
            DRISAI
          </Typography.Title>
          <Typography.Text type="secondary">Diagnóstico nutricional agrícola</Typography.Text>
        </div>

        <Form layout="vertical" onFinish={aoEnviar} requiredMark={false}>
          <Form.Item
            name="email"
            label="E-mail"
            rules={[
              { required: true, message: 'Informe o e-mail.' },
              { type: 'email', message: 'E-mail inválido.' },
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="seu@email.com" autoComplete="email" />
          </Form.Item>

          <Form.Item
            name="senha"
            label="Senha"
            rules={[{ required: true, message: 'Informe a senha.' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Sua senha"
              autoComplete="current-password"
            />
          </Form.Item>
          <div style={{ textAlign: 'right', marginBottom: 16 }}>
            <Link to="/esqueci_senha" style={{ fontSize: 13 }}>
              Esqueceu a senha?
            </Link>
          </div>
          <Button type="primary" htmlType="submit" block loading={enviando}>
            Entrar
          </Button>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Typography.Text type="secondary">Ainda não tem conta? </Typography.Text>
          <Link to="/cadastro">Criar uma conta</Link>
        </div>
      </Card>
    </div>
  )
}
