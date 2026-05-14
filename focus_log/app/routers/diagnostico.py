from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, service
from ..database import get_db

router = APIRouter()

@router.get("/diagnostico-produtividade", response_model=schemas.DiagnosticoOut)
def obter_diagnostico(db: Session = Depends(get_db)):
    """
    Gera um diagnóstico completo da produtividade.

    - Se o banco estiver vazio, retorna uma mensagem amigável.
    - Caso contrário, calcula todas as métricas e retorna o diagnóstico.
    """
    try:
        diagnostico = service.obter_diagnostico_completo(db)
        if not diagnostico:
            return {"mensagem": "Nenhum registro ainda. Registre sua primeira sessão de foco!"}
        return diagnostico
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": "Erro interno. Tente novamente."},
        )
