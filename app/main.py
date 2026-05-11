from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import registros
from app.storage import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.inicializar()
    yield


app = FastAPI(
    title="API de Foco e Produtividade",
    description=(
        "Sistema inteligente de avaliação de foco e produtividade. "
        "Suporta dois métodos: Pomodoro (sessões cíclicas com pesos) "
        "e Sessão Única (bloco contínuo com análise de pausas)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(registros.router)
