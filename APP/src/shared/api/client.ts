import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { LoginResponse } from '@/shared/types'

export const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true, // envia o cookie httpOnly de refresh
})

// O access token é curto e fica só em memória: não é gravado em localStorage,
// evitando exposição a XSS. A sessão sobrevive a reloads via refresh cookie.
let accessToken: string | null = null
let aoPerderSessao: (() => void) | null = null

export function definirAccessToken(token: string | null) {
  accessToken = token
}

export function registrarHandlerDeSessaoExpirada(handler: () => void) {
  aoPerderSessao = handler
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

type RequisicaoComRetry = InternalAxiosRequestConfig & { _retentada?: boolean }

let refreshEmAndamento: Promise<string> | null = null

async function renovarToken(): Promise<string> {
  // Uma única chamada de refresh atende todas as requisições que falharem juntas
  refreshEmAndamento ??= axios
    .post<LoginResponse>('/api/v1/auth/refresh', null, { withCredentials: true })
    .then((resposta) => {
      definirAccessToken(resposta.data.access_token)
      return resposta.data.access_token
    })
    .finally(() => {
      refreshEmAndamento = null
    })
  return refreshEmAndamento
}

api.interceptors.response.use(
  (resposta) => resposta,
  async (erro: AxiosError) => {
    const requisicao = erro.config as RequisicaoComRetry | undefined
    const ehRotaDeAutenticacao = requisicao?.url?.includes('/auth/refresh') ||
      requisicao?.url?.includes('/auth/login')

    if (erro.response?.status === 401 && requisicao && !requisicao._retentada && !ehRotaDeAutenticacao) {
      requisicao._retentada = true
      try {
        const novoToken = await renovarToken()
        requisicao.headers.Authorization = `Bearer ${novoToken}`
        return api(requisicao)
      } catch {
        definirAccessToken(null)
        aoPerderSessao?.()
      }
    }
    return Promise.reject(erro)
  },
)

/** Extrai a mensagem de erro da API no formato usado pelo backend. */
export function mensagemDeErro(erro: unknown, padrao = 'Não foi possível concluir a operação.') {
  if (axios.isAxiosError(erro)) {
    const detalhe = erro.response?.data?.detail
    if (typeof detalhe === 'string') return detalhe
    // Erros de validação do Pydantic vêm como lista de objetos
    if (Array.isArray(detalhe) && detalhe.length > 0) {
      const primeiro = detalhe[0]
      const campo = Array.isArray(primeiro.loc) ? primeiro.loc.slice(1).join('.') : ''
      return campo ? `${campo}: ${primeiro.msg}` : primeiro.msg
    }
  }
  return padrao
}
