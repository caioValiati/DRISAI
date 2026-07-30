import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import {
  api,
  definirAccessToken,
  registrarHandlerDeSessaoExpirada,
} from '@/shared/api/client'
import type { LoginResponse, Usuario } from '@/shared/types'

interface AuthContextValue {
  usuario: Usuario | null
  carregando: boolean
  entrar: (email: string, senha: string) => Promise<void>
  sair: () => Promise<void>
  atualizarUsuario: (usuario: Usuario) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [carregando, setCarregando] = useState(true)
  const queryClient = useQueryClient()

  const limparSessao = useCallback(() => {
    definirAccessToken(null)
    setUsuario(null)
    queryClient.clear()
  }, [queryClient])

  // Restaura a sessão a partir do cookie httpOnly de refresh ao abrir o app
  useEffect(() => {
    registrarHandlerDeSessaoExpirada(limparSessao)
    api
      .post<LoginResponse>('/auth/refresh')
      .then(({ data }) => {
        definirAccessToken(data.access_token)
        setUsuario(data.usuario)
      })
      .catch(() => limparSessao())
      .finally(() => setCarregando(false))
  }, [limparSessao])

  const entrar = useCallback(async (email: string, senha: string) => {
    const { data } = await api.post<LoginResponse>('/auth/login', { email, senha })
    definirAccessToken(data.access_token)
    setUsuario(data.usuario)
  }, [])

  const sair = useCallback(async () => {
    try {
      await api.post('/auth/logout')
    } finally {
      limparSessao()
    }
  }, [limparSessao])

  const valor = useMemo(
    () => ({ usuario, carregando, entrar, sair, atualizarUsuario: setUsuario }),
    [usuario, carregando, entrar, sair],
  )

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const contexto = useContext(AuthContext)
  if (!contexto) throw new Error('useAuth deve ser usado dentro de AuthProvider')
  return contexto
}
