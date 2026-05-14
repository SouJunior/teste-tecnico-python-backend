import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    func,
)
from .database import Base

class CategoriaEnum(str, enum.Enum):
    coding = "coding"
    reuniao = "reuniao"
    estudo = "estudo"
    outro = "outro"

class RegistroFoco(Base):
    """
    Modelo da tabela `registros_foco`.
    """
    __tablename__ = "registros_foco"

    id = Column(Integer, primary_key=True, index=True)
    nivel_foco = Column(Integer, nullable=False)
    tempo_minutos = Column(Integer, nullable=False)
    comentario = Column(String(500), nullable=False)
    categoria = Column(Enum(CategoriaEnum), default=CategoriaEnum.outro, nullable=False)
    tags = Column(String(200), nullable=True)
    criado_em = Column(DateTime, default=func.now(), nullable=False)
