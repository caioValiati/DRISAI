import type { ReactNode } from 'react'
import { App as AntdApp, ConfigProvider, theme } from 'antd'
import ptBR from 'antd/locale/pt_BR'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import { AuthProvider } from './AuthContext'

dayjs.locale('pt-br')

// Dados de cadastro mudam pouco durante uma sessão e toda mutação invalida as
// chaves afetadas (ver useCrud), então vale manter a janela de frescor longa:
// navegar entre os menus reaproveita o cache em vez de refazer as requisições.
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60_000,
      gcTime: 30 * 60_000,
    },
  },
})

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <ConfigProvider
      locale={ptBR}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#2e7d32', // verde agronômico
          borderRadius: 6,
        },
      }}
    >
      <AntdApp>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>{children}</AuthProvider>
        </QueryClientProvider>
      </AntdApp>
    </ConfigProvider>
  )
}
