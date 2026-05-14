from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, service
from ..database import get_db

router = APIRouter(
    prefix="/analise",
    tags=["Análise e Gamificação"]
)

@router.get("/status", response_model=schemas.StatusOut)
def get_status(db: Session = Depends(get_db)):
    """
    Obtém o status de gamificação do usuário.

    Retorna a sequência atual de dias com registros, a sequência máxima
    e uma mensagem motivacional.
    """
    return service.obter_status_app(db)

@router.get("/tags", response_model=schemas.AnaliseTagsOut)
def get_analise_tags(db: Session = Depends(get_db)):
    """
    Analisa as tags e as correlaciona com o nível de foco.

    Retorna um dicionário com as tags mais associadas a sessões de
    alto e baixo foco, ajudando a identificar padrões de produtividade.
    """
    return service.analisar_tags(db)
