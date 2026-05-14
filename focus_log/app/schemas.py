from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict
from .models import CategoriaEnum

class RegistroFocoCreate(BaseModel):
    """
    Schema para criação de um novo registro de foco.
    """
    nivel_foco: int = Field(..., ge=1, le=5, description="Nível de foco deve ser entre 1 (muito distraído) e 5 (flow).")
    tempo_minutos: int = Field(..., gt=0, lt=1440, description="Tempo deve ser entre 1 e 1440 minutos.")
    comentario: str = Field(..., min_length=3, max_length=500)
    categoria: CategoriaEnum = Field(default=CategoriaEnum.outro)
    tags: Optional[str] = Field(default=None, max_length=200)

class RegistroFocoOut(BaseModel):
    """
    Schema para saída de um registro de foco.
    """
    id: int
    nivel_foco: int
    tempo_minutos: int
    comentario: str
    categoria: CategoriaEnum
    tags: Optional[str]
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)

class DiagnosticoOut(BaseModel):
    """
    Schema para o diagnóstico de produtividade.
    """
    total_registros: int
    media_nivel_foco: float
    tempo_total_minutos: int
    tempo_formatado: str
    melhor_sessao: RegistroFocoOut
    pior_sessao: RegistroFocoOut
    distribuicao_categorias: Dict[str, int]
    feedback: str
