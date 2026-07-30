import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { Result, Spin } from 'antd'
import { useAuth } from '@/app/providers/AuthContext'
import type { Perfil } from '@/shared/types'

/** RF003 — bloqueia acesso direto por URL a módulos fora do perfil do usuário. */
export function RoleGuard({ perfis }: { perfis?: Perfil[] }) {
  const { usuario, carregando } = useAuth()
  const location = useLocation()

  if (carregando) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', minHeight: '60vh' }}>
        <Spin size="large" description="Carregando sessão..." />
      </div>
    )
  }

  if (!usuario) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (perfis && !perfis.includes(usuario.perfil)) {
    return (
      <Result
        status="403"
        title="Acesso Negado"
        subTitle="Seu perfil não tem permissão para acessar este módulo."
      />
    )
  }

  return <Outlet />
}
