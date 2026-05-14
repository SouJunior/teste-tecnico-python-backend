from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, repository, service
from ..database import get_db

router = APIRouter()

@router.post("/registro-foco", response_model=schemas.RegistroFocoOut, status_code=status.HTTP_201_CREATED)
def criar_registro_foco(
    registro: schemas.RegistroFocoCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cria um novo registro de foco.

    - Valida a entrada com Pydantic.
    - Persiste os dados no banco.
    - Adiciona uma tarefa em background para atualizar a gamificação.
    - Retorna o registro criado com status 201.
    """
    try:
        db_registro = repository.create_registro_foco(db=db, registro=registro)
        background_tasks.add_task(service.atualizar_status_gamificacao, db)
        return db_registro
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": "Erro interno. Tente novamente."},
        )
