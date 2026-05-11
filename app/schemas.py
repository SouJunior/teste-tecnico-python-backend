from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base para campos comuns
class RegistroFocoBase(BaseModel):
    nivel_foco: float = Field(
        ..., 
        ge=1.0, 
        le=5.0, 
        description="O nível de foco deve ser entre 1 (distraído) e 5 (flow)."
    )
    tempo_minutos: int = Field(
        ..., 
        gt=0, 
        description="O tempo de sessão deve ser maior que zero."
    )
    comentario: str
    categoria: Optional[str] = "Geral"

# Schema para criação 
class RegistroFocoCreate(RegistroFocoBase):
    pass

# Schema para resposta 
class RegistroFocoResponse(RegistroFocoBase):
    id: int
    data_registro: datetime

    class Config:
        from_attributes = True # Permite que o Pydantic leia modelos do SQLAlchemy

# Schema para o Diagnóstico Inteligente
class DiagnosticoOut(BaseModel):
    media_foco: float
    tempo_total_focado: int
    total_sessoes: int
    mensagem_feedback: str