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


class StatusApp(Base):
    """
    Modelo da tabela `status_app` para gamificação.
    Armazena a sequência de dias com registros.
    """
    __tablename__ = "status_app"

    id = Column(Integer, primary_key=True)
    sequencia_atual = Column(Integer, default=0)
    sequencia_maxima = Column(Integer, default=0)
    data_ultimo_registro = Column(DateTime, nullable=True)


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
