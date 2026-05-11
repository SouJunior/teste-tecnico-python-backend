from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database
from .database import engine, get_db
from .service import PerformanceService # <-- Importação do seu serviço

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Foco e Produtividade",
    description="Sistema para registro de logs de performance e diagnóstico de flow.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/registro-foco", response_model=schemas.RegistroFocoResponse, status_code=status.HTTP_201_CREATED)
def registrar_foco(item: schemas.RegistroFocoCreate, db: Session = Depends(get_db)):
    novo_log = models.RegistroFoco(**item.dict())
    db.add(novo_log)
    db.commit()
    db.refresh(novo_log)
    return novo_log

@app.get("/diagnostico-produtividade", response_model=schemas.DiagnosticoOut)
def obter_diagnostico(db: Session = Depends(get_db)):
    # 1. Busca os dados no banco
    registros = db.query(models.RegistroFoco).all()
    
    # 2. Delega a lógica para o Service
    resultado = PerformanceService.gerar_diagnostico(registros)
    
    # 3. Trata o erro ou retorna o sucesso
    if not resultado:
        raise HTTPException(
            status_code=404, 
            detail="Nenhum registro encontrado para gerar diagnóstico."
        )

    return resultado

@app.get("/")
def read_root():
    return {"message": "API de Performance Online. Acesse http://127.0.0.1:8000/docs."}