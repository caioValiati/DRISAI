import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect } from 'vitest'
import { MatrizRelacoesDuais } from './MatrizRelacoesDuais'

describe('MatrizRelacoesDuais', () => {
  it('deve adicionar todas as relações padrão ao clicar no botão de inserção em massa', async () => {
    const handleChange = vi.fn()

    render(<MatrizRelacoesDuais value={{}} onChange={handleChange} />)

    const botaoInserirTodas = screen.getByRole('button', {
      name: /inserir todas as relações/i,
    })

    await userEvent.click(botaoInserirTodas)

    expect(handleChange).toHaveBeenCalled()
    const chamadaObj = handleChange.mock.calls[0][0]
    expect(Object.keys(chamadaObj).length).toBe(55)
    expect(chamadaObj['N/P']).toEqual({ media: 1, dp: 0.1, cv: 10 })
  })

  it('deve recalcular CV (%) e Variância ao alterar Média ou Desvio-Padrão', async () => {
    const handleChange = vi.fn()
    const valorInicial = {
      'N/P': { media: 10, dp: 2, cv: 20, variancia: 4 },
    }

    debugger

    render(<MatrizRelacoesDuais value={valorInicial} onChange={handleChange} />)

    const inputs = screen.getAllByRole('spinbutton')
    const inputMedia = inputs[0]

    await userEvent.clear(inputMedia)
    await userEvent.type(inputMedia, '20,00')

    expect(handleChange).toHaveBeenCalled()
    const ultimaChamada = handleChange.mock.calls.length - 1
    const valorAtualizado = handleChange.mock.calls[ultimaChamada][0]

    expect(valorAtualizado['N/P'].cv).toBe(10)
    expect(valorAtualizado['N/P'].variancia).toBe(4)
  })
})