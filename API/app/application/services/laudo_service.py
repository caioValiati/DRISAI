"""Emissão do laudo técnico (RF013).

Monta o documento a partir do que já está persistido na amostra, de modo que a
reemissão devolva sempre o mesmo conteúdo — condição da rastreabilidade exigida
pela RN006.
"""

import uuid

from sqlalchemy.orm import Session

from app.application.services.amostra_service import AmostraService
from app.domain.enums import StatusAmostra
from app.domain.exceptions import DominioError
from app.infrastructure.db.models import Usuario
from app.infrastructure.laudo.pdf import DadosLaudo, gerar_laudo_pdf


class LaudoService:
    def __init__(self, db: Session):
        self.db = db
        self.amostras = AmostraService(db)

    def emitir_pdf(self, amostra_id: uuid.UUID, usuario: Usuario) -> tuple[bytes, str]:
        amostra = self.amostras.obter(amostra_id, usuario)
        if amostra.status != StatusAmostra.CONCLUIDA:
            raise DominioError(
                "O laudo só pode ser emitido depois que o diagnóstico for concluído."
            )

        recomendacao = amostra.recomendacao
        texto = (recomendacao.texto_final_editado if recomendacao else None) or ""
        if not texto.strip():
            raise DominioError("A amostra concluída não possui texto de recomendação.")

        talhao = amostra.talhao
        propriedade = talhao.propriedade
        produtor = propriedade.produtor
        agronomo = produtor.agronomo

        dados = DadosLaudo(
            agronomo_nome=agronomo.nome,
            agronomo_crea=agronomo.registro_crea,
            produtor=produtor.nome_razao,
            propriedade=propriedade.nome_fazenda,
            municipio_uf=propriedade.municipio_uf,
            talhao=talhao.identificacao,
            cultura=amostra.norma.cultura,
            estadio_fenologico=amostra.norma.estadio_fenologico,
            data_coleta=amostra.data_coleta.strftime("%d/%m/%Y"),
            data_emissao=recomendacao.data_emissao if recomendacao else None,
            ibn=float(amostra.valor_ibn or 0),
            indices=[
                {
                    "elemento": indice.elemento,
                    "teor": float(indice.valor_laboratorio),
                    "indice": float(indice.indice_dris_calculado or 0),
                    "classificacao": indice.classificacao.value if indice.classificacao else "",
                }
                for indice in amostra.indices
            ],
            texto_recomendacao=texto,
            insumos=[
                {
                    "nome_comercial": sugestao.insumo.nome_comercial,
                    "fabricante": sugestao.insumo.fabricante,
                    "composicao": sugestao.insumo.concentracao_nutricional,
                    "score": float(sugestao.match_score or 0),
                }
                for sugestao in (recomendacao.insumos_sugeridos if recomendacao else [])
            ],
        )

        nome_arquivo = (
            f"laudo-dris-{talhao.identificacao}-"
            f"{amostra.data_coleta.strftime('%Y-%m-%d')}.pdf"
        ).replace(" ", "-").replace("/", "-")
        return gerar_laudo_pdf(dados), nome_arquivo
