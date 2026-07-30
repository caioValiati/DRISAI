from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routers import amostras, auth, cadastros
from app.core.config import get_settings
from app.domain.exceptions import DominioError

app = FastAPI(
    title="DRISAI API",
    description="Sistema de gestão nutricional agrícola — método DRIS",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,  # necessário para o cookie httpOnly de refresh
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DominioError)
def tratar_erro_dominio(_: Request, exc: DominioError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensagem})


app.include_router(auth.router, prefix="/api/v1")
app.include_router(cadastros.router, prefix="/api/v1")
app.include_router(amostras.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Infra"])
def health():
    return {"status": "ok"}
