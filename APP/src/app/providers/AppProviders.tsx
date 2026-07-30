import type { ReactNode } from 'react'
import { App as AntdApp, ConfigProvider, theme } from 'antd'
import ptBR from 'antd/locale/pt_BR'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import { AuthProvider } from './AuthContext'

dayjs.locale('pt-br')

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false, staleTime: 30_000 },
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
