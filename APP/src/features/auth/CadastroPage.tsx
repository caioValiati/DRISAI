import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { App, Button, Card, Form, Input, Typography } from 'antd'
import { api, mensagemDeErro } from '@/shared/api/client'

interface FormularioCadastro {
  nome: string
  registro_crea: string
  email: string
  senha: string
}

export function CadastroPage() {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(valores: FormularioCadastro) {
    setEnviando(true)
    try {
      await api.post('/auth/registrar', valores)
      message.success('Cadastro concluído com sucesso! Faça login para continuar.')
      navigate('/login')
    } catch (erro) {
      message.error(mensagemDeErro(erro, 'Não foi possível criar a conta.'))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh', background: '#f5f7f5' }}>
      <Card style={{ width: 440, boxShadow: '0 4px 16px rgba(0,0,0,.06)' }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          Criar uma conta
        </Typography.Title>
        <Typography.Paragraph type="secondary">
          O cadastro é destinado a engenheiros agrônomos.
        </Typography.Paragraph>

        <Form layout="vertical" onFinish={aoEnviar} requiredMark={false}>
          <Form.Item
            name="nome"
            label="Nome completo"
            rules={[{ required: true, min: 3, message: 'Informe seu nome completo.' }]}
          >
            <Input placeholder="Nome do profissional" />
          </Form.Item>

          <Form.Item
            name="registro_crea"
            label="Registro CREA"
            rules={[{ required: true, min: 3, message: 'Informe o registro no CREA.' }]}
          >
            <Input placeholder="Ex.: GO-123456" />
          </Form.Item>

          <Form.Item
            name="email"
            label="E-mail"
            rules={[
              { required: true, message: 'Informe o e-mail.' },
              { type: 'email', message: 'E-mail inválido.' },
            ]}
          >
            <Input placeholder="seu@email.com" autoComplete="email" />
          </Form.Item>

          <Form.Item
            name="senha"
            label="Senha"
            rules={[{ required: true, min: 8, message: 'A senha deve ter ao menos 8 caracteres.' }]}
          >
            <Input.Password placeholder="Mínimo de 8 caracteres" autoComplete="new-password" />
          </Form.Item>

          <Button type="primary" htmlType="submit" block loading={enviando}>
            Criar conta
          </Button>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Link to="/login">Voltar para o login</Link>
        </div>
      </Card>
    </div>
  )
}
