import { useState } from 'react'
import type { AcaoVinculo } from '@/shared/components/ModalVinculos'
import type { ImpactoVinculos } from '@/shared/types'

interface CrudParcial {
  inativar: { mutateAsync: (id: string) => Promise<unknown>; isPending: boolean }
  reativar: {
    mutateAsync: (v: { id: string; cascata?: boolean }) => Promise<unknown>
    isPending: boolean
  }
  obterVinculos: (id: string) => Promise<ImpactoVinculos | null>
}

/**
 * Liga as listagens ao ModalVinculos: guarda o registro alvo, a ação pedida e
 * despacha a mutação escolhida com ou sem cascata.
 */
export function useAcoesRegistro<T extends { id: string }>(
  crud: CrudParcial,
  rotulo: string,
  nomeDe: (registro: T) => string,
) {
  const [alvo, setAlvo] = useState<{ registro: T; acao: AcaoVinculo } | null>(null)

  async function confirmar(cascata: boolean) {
    if (!alvo) return
    try {
      if (alvo.acao === 'inativar') {
        await crud.inativar.mutateAsync(alvo.registro.id)
      } else {
        await crud.reativar.mutateAsync({ id: alvo.registro.id, cascata })
      }
      setAlvo(null)
    } catch {
      // A mensagem de erro já é exibida pelo onError da mutação
    }
  }

  return {
    pedirInativacao: (registro: T) => setAlvo({ registro, acao: 'inativar' }),
    pedirReativacao: (registro: T) => setAlvo({ registro, acao: 'reativar' }),
    propsModal: {
      aberto: alvo !== null,
      acao: alvo?.acao ?? ('inativar' as AcaoVinculo),
      rotulo,
      nomeRegistro: alvo ? nomeDe(alvo.registro) : '',
      carregarVinculos: () =>
        alvo ? crud.obterVinculos(alvo.registro.id) : Promise.resolve(null),
      confirmando: crud.inativar.isPending || crud.reativar.isPending,
      aoConfirmar: confirmar,
      aoCancelar: () => setAlvo(null),
    },
  }
}
