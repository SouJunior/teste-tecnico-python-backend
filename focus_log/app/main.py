from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .database import engine, Base
from .routers import registro, diagnostico, analise

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Focus Log API",
    description="Uma API para registrar e analisar sessões de foco, com gamificação e análise inteligente.",
    version="2.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler global para erros de validação do Pydantic.
    """
    detalhes = []
    for error in exc.errors():
        campo = " -> ".join(map(str, error["loc"]))
        mensagem = error["msg"]
        detalhes.append({"campo": campo, "mensagem": mensagem})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"erro": "Dados inválidos", "detalhes": detalhes},
    )

app.include_router(registro.router, tags=["Registros de Foco"])
app.include_router(diagnostico.router, tags=["Diagnóstico de Produtividade"])
app.include_router(analise.router)

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Bem-vindo à Focus Log API v2! Acesse /docs para a documentação."}
