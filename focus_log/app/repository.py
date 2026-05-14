from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from typing import List, Optional

def create_registro_foco(db: Session, registro: schemas.RegistroFocoCreate) -> models.RegistroFoco:
    """
    Cria um novo registro de foco no banco de dados.

    Args:
        db (Session): A sessão do banco de dados.
        registro (schemas.RegistroFocoCreate): Os dados do registro a ser criado.

    Returns:
        models.RegistroFoco: O registro de foco criado.
    """
    db_registro = models.RegistroFoco(**registro.model_dump())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    return db_registro

def get_all_registros_foco(db: Session) -> List[models.RegistroFoco]:
    """
    Obtém todos os registros de foco do banco de dados.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        List[models.RegistroFoco]: Uma lista de todos os registros de foco.
    """
    return db.query(models.RegistroFoco).all()

def get_total_registros(db: Session) -> int:
    """
    Obtém o número total de registros de foco.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        int: O número total de registros.
    """
    return db.query(models.RegistroFoco).count()

def get_media_nivel_foco(db: Session) -> Optional[float]:
    """
    Calcula a média do nível de foco.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        Optional[float]: A média do nível de foco ou None se não houver registros.
    """
    return db.query(func.avg(models.RegistroFoco.nivel_foco)).scalar()

def get_tempo_total_minutos(db: Session) -> int:
    """
    Calcula o tempo total em minutos de todos os registros.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        int: O tempo total em minutos.
    """
    return db.query(func.sum(models.RegistroFoco.tempo_minutos)).scalar() or 0

def get_melhor_sessao(db: Session) -> Optional[models.RegistroFoco]:
    """
    Obtém a sessão com o maior nível de foco.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        Optional[models.RegistroFoco]: A melhor sessão de foco ou None.
    """
    return db.query(models.RegistroFoco).order_by(models.RegistroFoco.nivel_foco.desc()).first()

def get_pior_sessao(db: Session) -> Optional[models.RegistroFoco]:
    """
    Obtém a sessão com o menor nível de foco.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        Optional[models.RegistroFoco]: A pior sessão de foco ou None.
    """
    return db.query(models.RegistroFoco).order_by(models.RegistroFoco.nivel_foco.asc()).first()

def get_distribuicao_categorias(db: Session) -> dict:
    """
    Obtém a distribuição de registros por categoria.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        dict: Um dicionário com a contagem de registros por categoria.
    """
    dist = (
        db.query(models.RegistroFoco.categoria, func.count(models.RegistroFoco.id))
        .group_by(models.RegistroFoco.categoria)
        .all()
    )
    return {categoria.name: count for categoria, count in dist}
