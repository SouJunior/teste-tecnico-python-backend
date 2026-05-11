from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine, get_db

# Cria as tabelas no banco de dados SQLite ao iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Foco e Produtividade",
    description="Sistema para registro de logs de performance e diagnóstico de flow.",
    version="1.0.0"
)


# --- Endpoints ---
@app.post("/registro-foco", response_model=schemas.RegistroFocoResponse, status_code=status.HTTP_201_CREATED)
def registrar_foco(item: schemas.RegistroFocoCreate, db: Session = Depends(get_db)):
    
    novo_log = models.RegistroFoco(**item.dict())
    
    db.add(novo_log)
    db.commit()
    db.refresh(novo_log)
    return novo_log


@app.get("/diagnostico-produtividade", response_model=schemas.DiagnosticoOut)
def obter_diagnostico(db: Session = Depends(get_db)):

    registros = db.query(models.RegistroFoco).all()
    
    if not registros:
        raise HTTPException(
            status_code=404, 
            detail="Nenhum registro encontrado para gerar diagnóstico."
        )

    # Cálculos básicos
    total_minutos = sum(r.tempo_minutos for r in registros)
    media_foco = sum(r.nivel_foco for r in registros) / len(registros)
    
    # Lógica de Feedback
    if media_foco >= 4.5:
        feedback = "Incrível! Você está em estado de flow constante. Continue assim!"
    elif media_foco > 3.0:
        feedback = "Você teve uma boa performance. Tente reduzir pequenas distrações."
    elif media_foco >= 2.5:
        feedback = "Produtividade mediana. Talvez pausas mais longas ajudem a recuperar o foco."
    else:
        feedback = "Alerta de distração: Sugerimos desligar notificações e usar a técnica Pomodoro."

    return {
        "media_foco": round(media_foco, 2),
        "tempo_total_focado": total_minutos,
        "total_sessoes": len(registros),
        "mensagem_feedback": feedback
    }

@app.get("/")
def read_root():
    return {"message": "API de Performance Online. Acesse /docs para documentação."}