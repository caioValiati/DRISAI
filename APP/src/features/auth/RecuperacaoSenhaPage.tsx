import { useState } from 'react'
import { Link } from 'react-router-dom'
import { App, Button, Card, Form, Input, Typography } from 'antd'
import { MailOutlined } from '@ant-design/icons'
import { api, mensagemDeErro } from '@/shared/api/client'

export function RecuperacaoSenhaPage() {
  const { message } = App.useApp()
  const [enviando, setEnviando] = useState(false)
  const [enviado, setEnviado] = useState(false)

  async function aoEnviar(valores: { email: string }) {
    setEnviando(true)
    try {
      await api.post('/auth/forgot-password', { email: valores.email })
      setEnviado(true)
      message.success('Solicitação enviada com sucesso!')
    } catch (erro) {
      message.error(mensagemDeErro(erro, 'Erro ao solicitar recuperação.'))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh', background: '#f5f7f5' }}>
      <Card style={{ width: 400, boxShadow: '0 4px 16px rgba(0,0,0,.06)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Typography.Title level={3} style={{ margin: 0, color: '#2e7d32' }}>
            Recuperação de Senha
          </Typography.Title>
          <Typography.Text type="secondary">
            {enviado
              ? 'Verifique sua caixa de entrada'
              : 'Informe seu e-mail para receber as instruções'}
          </Typography.Text>
        </div>

        {enviado ? (
          <div style={{ textAlign: 'center' }}>
            <Typography.Paragraph>
              Se o e-mail informado estiver cadastrado em nosso sistema, você receberá um link com as instruções para redefinir sua senha.
            </Typography.Paragraph>
            <Link to="/login">Voltar para o Login</Link>
          </div>
        ) : (
          <Form layout="vertical" onFinish={aoEnviar} requiredMark={false}>
            <Form.Item
              name="email"
              label="E-mail"
              rules={[
                { required: true, message: 'Informe o e-mail.' },
                { type: 'email', message: 'E-mail inválido.' },
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="seu@email.com" />
            </Form.Item>

            <Button type="primary" htmlType="submit" block loading={enviando}>
              Enviar e-mail
            </Button>

            <div style={{ textAlign: 'center', marginTop: 16 }}>
              <Link to="/login">Lembrei minha senha</Link>
            </div>
          </Form>
        )}
      </Card>
    </div>
  )
}