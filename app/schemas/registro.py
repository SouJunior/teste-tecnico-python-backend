from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class MetodoEnum(str, Enum):
    pomodoro = "pomodoro"
    sessao_unica = "sessao_unica"


class CategoriaEnum(str, Enum):
    coding = "coding"
    reuniao = "reuniao"
    estudo = "estudo"
    outro = "outro"


class _RegistroBase(BaseModel):
    """Campos comuns a todos os métodos (spec original)."""

    model_config = ConfigDict(extra="forbid")

    nivel_foco: int = Field(..., ge=1, le=5, description="Nível de foco: 1 (muito distraído) a 5 (flow)")
    tempo_minutos: int = Field(..., ge=1, description="Duração real da sessão em minutos")
    comentario: str = Field(..., min_length=1, description="O que foi feito ou causou distração")
    categoria: Optional[CategoriaEnum] = Field(None, description="Categoria da sessão")


class PomodoroCreate(_RegistroBase):
    """Contrato exclusivo do método Pomodoro — sessão cíclica com pausa."""

    metodo: Literal["pomodoro"]
    tempo_pausa_minutos: Optional[int] = Field(
        None, ge=0, description="Duração da pausa após esta sessão. Null = última sessão do dia"
    )


class SessaoUnicaCreate(_RegistroBase):
    """Contrato exclusivo do método Sessão Única — bloco contínuo com meta e pausas."""

    metodo: Literal["sessao_unica"]
    meta_minutos: int = Field(..., ge=30, le=720, description="Meta de duração planejada (30 min a 12 h)")
    qtd_pausas: int = Field(..., ge=0, description="Quantidade de pausas realizadas")
    tempo_minutos: int = Field(..., ge=30, le=720, description="Duração real da sessão (30 min a 12 h)")


# Union discriminada pelo campo `metodo` — Pydantic escolhe o schema correto automaticamente
RegistroCreate = Annotated[
    Union[PomodoroCreate, SessaoUnicaCreate],
    Field(discriminator="metodo"),
]


# --- Schemas de resposta ---

class RegistroResponse(BaseModel):
    id: int
    metodo: MetodoEnum
    nivel_foco: int
    tempo_minutos: int
    comentario: str
    categoria: Optional[CategoriaEnum] = None
    tempo_pausa_minutos: Optional[int] = None
    meta_minutos: Optional[int] = None
    qtd_pausas: Optional[int] = None
    pontuacao: float
    peso: Optional[int] = None
    penalidades_aplicadas: list[str]
    aviso: Optional[str] = None
    criado_em: str = Field(..., description="Dia do registro no formato YYYY-MM-DD")


class DiagnosticoPomodoro(BaseModel):
    total_sessoes: int
    blocos_registrados: int
    sessoes_validas: int
    sessoes_invalidas: int
    media_ponderada: float


class DiagnosticoSessaoUnica(BaseModel):
    total_sessoes: int
    media_pontuacao: float


class SessaoNoPeriodo(BaseModel):
    """Cada registro no intervalo filtrado, com o dia para leitura fácil."""

    id: int
    dia: str = Field(..., description="Data da sessão (YYYY-MM-DD)")
    metodo: MetodoEnum
    nivel_foco: int
    tempo_minutos: int
    pontuacao: float
    comentario: str


class DiagnosticoResponse(BaseModel):
    tempo_total_minutos: int
    total_sessoes: int = Field(..., description="Quantidade de sessões no período (todos os métodos)")
    media_foco_geral: float = Field(
        ..., description="Média aritmética do nível de foco (1–5) em todas as sessões"
    )
    media_pontuacao_geral: float = Field(
        ...,
        description="Média aritmética da pontuação de todas as sessões (mistura métodos; escalas diferentes)",
    )
    foco_min: int = Field(..., description="Menor nível de foco registrado no período")
    foco_max: int = Field(..., description="Maior nível de foco registrado no período")
    pontuacao_min: float = Field(..., description="Menor pontuação de sessão no período")
    pontuacao_max: float = Field(..., description="Maior pontuação de sessão no período")
    pomodoro: DiagnosticoPomodoro
    sessao_unica: DiagnosticoSessaoUnica
    mensagem_feedback: str
    sessoes_no_periodo: list[SessaoNoPeriodo] = Field(
        default_factory=list,
        description="Sessões incluídas neste diagnóstico, em ordem cronológica, com dia de cada uma",
    )


class PlanoPomodoroRequest(BaseModel):
    total_sessoes: int = Field(..., ge=1, le=20, description="Quantidade de sessões Pomodoro planejadas para hoje")


class PlanoPomodoroResponse(BaseModel):
    dia: str
    total_sessoes: int
    sessoes_registradas: int
    sessoes_restantes: int


class PomodoroDiaStatusResumo(BaseModel):
    """Plano do dia + contagem de blocos (quando já existe plano salvo)."""

    total_sessoes: int
    sessoes_registradas: int
    sessoes_restantes: int


class RegistroDiaStatusResponse(BaseModel):
    """Estado do dia de referência para liberar ou bloquear o formulário de registro."""

    dia: str
    pomodoro: Optional[PomodoroDiaStatusResumo] = Field(
        None, description="Null se o plano Pomodoro do dia ainda não foi definido"
    )
    sessao_unica_ja_registrada: bool = Field(
        False, description="Só pode existir uma Sessão única por dia de referência"
    )
