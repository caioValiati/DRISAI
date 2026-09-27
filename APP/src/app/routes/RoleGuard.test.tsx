import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi, describe, it, expect } from 'vitest'
import { RoleGuard } from './RoleGuard'
import * as AuthContextModule from '@/app/providers/AuthContext'

vi.mock('@/app/providers/AuthContext')

describe('RoleGuard', () => {
  it('deve redirecionar para /login se o usuário não estiver autenticado', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      usuario: null,
      carregando: false,
      entrar: vi.fn(),
      sair: vi.fn(),
      atualizarUsuario: vi.fn(),
    })

    render(
      <MemoryRouter initialEntries={['/normas']}>
        <Routes>
          <Route path="/login" element={<div>Tela de Login</div>} />
          <Route element={<RoleGuard perfis={['ADMIN']} />}>
            <Route path="/normas" element={<div>Página de Normas</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('Tela de Login')).toBeInTheDocument()
  })

  it('deve exibir mensagem de "Acesso Negado" se perfil não for autorizado', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      usuario: { id: '1', nome: 'Agrônomo Teste', email: 'agronomo@test.com', perfil: 'AGRONOMO', registro_crea: '123', ativo: true },
      carregando: false,
      entrar: vi.fn(),
      sair: vi.fn(),
      atualizarUsuario: vi.fn(),
    })

    render(
      <MemoryRouter initialEntries={['/normas']}>
        <Routes>
          <Route element={<RoleGuard perfis={['ADMIN']} />}>
            <Route path="/normas" element={<div>Página de Normas</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('Acesso Negado')).toBeInTheDocument()
    expect(screen.getByText('Seu perfil não tem permissão para acessar este módulo.')).toBeInTheDocument()
  })

  it('deve conceder acesso se o perfil for permitido', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      usuario: { id: '2', nome: 'Admin Teste', email: 'admin@test.com', perfil: 'ADMIN', registro_crea: null, ativo: true },
      carregando: false,
      entrar: vi.fn(),
      sair: vi.fn(),
      atualizarUsuario: vi.fn(),
    })

    render(
      <MemoryRouter initialEntries={['/normas']}>
        <Routes>
          <Route element={<RoleGuard perfis={['ADMIN']} />}>
            <Route path="/normas" element={<div>Página de Normas</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('Página de Normas')).toBeInTheDocument()
  })
})