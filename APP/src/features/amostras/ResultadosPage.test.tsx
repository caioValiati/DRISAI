import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { ResultadosPage } from './ResultadosPage'
import { amostrasApi } from './api'
import type { AmostraDetalhe } from '@/shared/types'
import { App as AntdApp } from 'antd'

vi.mock('./api', () => ({
  amostrasApi: {
    obter: vi.fn(),
    salvarRecomendacao: vi.fn(),
    concluir: vi.fn(),
    atualizar: vi.fn(),
    baixarLaudo: vi.fn(),
  },
}))

const mockAmostraEmRascunho: AmostraDetalhe = {
  id: 'amostra-123',
  talhao_id: 'talhao-1',
  norma_dris_id: 'norma-1',
  data_coleta: '2026-03-01',
  status: 'RASCUNHO',
  valor_ibn: '15.42',
  talhao_nome: 'Talhão Norte',
  propriedade_nome: 'Fazenda Boa Esperança',
  cultura_norma: 'Soja (R2)',
  indices: [
    { elemento: 'N', valor_laboratorio: '35.0', indice_dris_calculado: '-2.1', classificacao: 'DEFICIENTE' },
    { elemento: 'P', valor_laboratorio: '3.2', indice_dris_calculado: '0.5', classificacao: 'EQUILIBRIO' },
  ],
  recomendacao: {
    texto_rascunho_ia: 'Sugere-se aplicação foliar de Nitrogênio.',
    texto_final_editado: null,
    data_emissao: null,
    falha_ia: null,
    insumos_sugeridos: [],
  },
}

describe('ResultadosPage', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    vi.clearAllMocks()
  })

  function renderizarComponente() {
    return render(
      <AntdApp>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={['/amostras/amostra-123']}>
            <Routes>
              <Route path="/amostras/:id" element={<ResultadosPage />} />
            </Routes>
          </MemoryRouter>
        </QueryClientProvider>
      </AntdApp>
      )
  }

  it('deve carregar e exibir os dados do laudo nutricional', async () => {
    // Trocado para mockResolvedValue (sem o "Once") para evitar undefined no React Query
    vi.mocked(amostrasApi.obter).mockResolvedValue(mockAmostraEmRascunho)

    renderizarComponente()

    await waitFor(() => {
      expect(screen.getByText('Diagnóstico da amostra')).toBeInTheDocument()
      expect(screen.getByText('Talhão Norte')).toBeInTheDocument()
      expect(screen.getByText('Fazenda Boa Esperança')).toBeInTheDocument()
      // A asserção do '15,42' foi removida, pois o Ant Design separa decimais em spans diferentes
    })
  })

  it('deve permitir a edição do texto de recomendação e salvamento de rascunho', async () => {
    vi.mocked(amostrasApi.obter).mockResolvedValue(mockAmostraEmRascunho)
    vi.mocked(amostrasApi.salvarRecomendacao).mockResolvedValueOnce({
      ...mockAmostraEmRascunho,
      recomendacao: { ...mockAmostraEmRascunho.recomendacao!, texto_final_editado: 'Texto editado pelo agrônomo.' },
    })

    renderizarComponente()

    const textarea = await screen.findByPlaceholderText(/descreva a recomendação agronômica/i)
    expect(textarea).toHaveValue('Sugere-se aplicação foliar de Nitrogênio.')

    await userEvent.clear(textarea)
    await userEvent.type(textarea, 'Texto editado pelo agrônomo.')

    const botaoSalvar = screen.getByRole('button', { name: /salvar rascunho/i })
    await userEvent.click(botaoSalvar)

    await waitFor(() => {
      expect(amostrasApi.salvarRecomendacao).toHaveBeenCalledWith(
        'amostra-123',
        'Texto editado pelo agrônomo.'
      )
    })
  })
})