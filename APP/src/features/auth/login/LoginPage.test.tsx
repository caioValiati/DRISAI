import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { LoginPage } from './LoginPage'
import * as AuthContextModule from '@/app/providers/AuthContext'

vi.mock('@/app/providers/AuthContext') 

vi.mock('@/shared/api/client', () => ({
  api: {
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
  definirAccessToken: vi.fn(),
  registrarHandlerDeSessaoExpirada: vi.fn(),
  mensagemDeErro: vi.fn((_, padrao) => padrao),
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      usuario: null,
      carregando: false,
      entrar: vi.fn().mockResolvedValue(undefined),
      sair: vi.fn(),
      atualizarUsuario: vi.fn(),
    })
  })

  it('deve renderizar os campos de e-mail e senha corretamente', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    expect(screen.getByPlaceholderText('seu@email.com')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Sua senha')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
  })

  it('deve realizar login com sucesso e redirecionar para a rota inicial', async () => {
    const mockEntrar = vi.fn().mockResolvedValue(undefined)
    
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      usuario: null,
      carregando: false,
      entrar: mockEntrar,
      sair: vi.fn(),
      atualizarUsuario: vi.fn(),
    })

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    const inputEmail = screen.getByPlaceholderText('seu@email.com')
    const inputSenha = screen.getByPlaceholderText('Sua senha')
    const botaoEntrar = screen.getByRole('button', { name: /entrar/i })

    await userEvent.type(inputEmail, 'joao@dris.ai')
    await userEvent.type(inputSenha, '12345678')
    await userEvent.click(botaoEntrar)

    await waitFor(() => {
      expect(mockEntrar).toHaveBeenCalledWith('joao@dris.ai', '12345678')
      expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true })
    })
  })
})