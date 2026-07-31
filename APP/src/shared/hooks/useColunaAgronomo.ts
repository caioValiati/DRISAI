import { useAuth } from '@/app/providers/AuthContext'

interface RegistroComAgronomo {
  agronomo_nome: string | null
}

/**
 * O Administrador supervisiona as carteiras de todos os agrônomos, então
 * precisa saber de quem é cada registro. Para o Agrônomo a coluna é redundante.
 */
export function useColunaAgronomo<T extends RegistroComAgronomo>() {
  const { usuario } = useAuth()
  if (usuario?.perfil !== 'ADMIN') return []
  return [
    {
      title: 'Agrônomo responsável',
      dataIndex: 'agronomo_nome',
      render: (valor: string | null) => valor || '—',
    },
  ] as { title: string; dataIndex: keyof T & string; render: (v: string | null) => string }[]
}

/** Escolhe o texto de apoio da listagem conforme o alcance do perfil. */
export function useDescricaoCarteira() {
  const { usuario } = useAuth()
  return (paraAgronomo: string, paraAdmin: string) =>
    usuario?.perfil === 'ADMIN' ? paraAdmin : paraAgronomo
}
