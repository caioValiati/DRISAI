# DRISAI — Sistema de Gestão Nutricional Agrícola

Sistema web para diagnóstico nutricional de culturas pelo método **DRIS** (Diagnosis and
Recommendation Integrated System), com gestão da carteira de consultoria agronômica e
recomendação de insumos. Projeto de TCC — Engenharia de Software, UniRV.

## Estrutura do monorepo

| Pasta  | Conteúdo                                                        |
| ------ | --------------------------------------------------------------- |
| `API/` | Backend Python — FastAPI, SQLAlchemy 2, Alembic, PostgreSQL (Neon) |
| `APP/` | Frontend React — Vite, TypeScript, Ant Design, TanStack Query   |

## Fase 1 (atual)

- Autenticação JWT (access token + refresh em cookie httpOnly) e RBAC (RF002/RF003)
- CRUDs: Usuários, Normas DRIS, Insumos, Produtores, Propriedades, Talhões e Amostras
  (RF001, RF004–RF009), com soft delete e escopo por agrônomo
- Motor de cálculo DRIS/IBN pelas fórmulas de Beaufils (RF010) em `API/app/domain/dris.py`
- Painel de revisão com gráfico radial, edição da recomendação e conclusão imutável
  (RF012 parcial, RN005/RN006)

A Fase 2 incorporará o motor de ML de matching de insumos, o rascunho por IA generativa
(RF011), a emissão de PDF do laudo (RF013) e a recuperação de senha (RF014).

## Como rodar

Backend (porta 8000):

```bash
cd API && uv sync && uv run alembic upgrade head && uv run python -m app.scripts.seed && uv run uvicorn app.main:app --reload
```

Frontend (porta 5173, com proxy para a API):

```bash
cd APP && npm install && npm run dev
```

Configure `API/.env` a partir de `API/.env.example` com a connection string do banco.
Documentação interativa da API: `http://localhost:8000/docs`.

## Testes

```bash
cd API && uv run pytest
```
