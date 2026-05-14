from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, repository
from ..database import get_db

router = APIRouter()

@router.post("/registro-foco", response_model=schemas.RegistroFocoOut, status_code=status.HTTP_201_CREATED)
def criar_registro_foco(
    registro: schemas.RegistroFocoCreate, db: Session = Depends(get_db)
):
    """
    Cria um novo registro de foco.

    - Valida a entrada com Pydantic.
    - Persiste os dados no banco.
    - Retorna o registro criado com status 201.
    """
    try:
        return repository.create_registro_foco(db=db, registro=registro)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": "Erro interno. Tente novamente."},
        )
