from app.schemas.registro import PomodoroCreate

# Flag adicionada à lista de penalidades quando o bloco é inválido (< 20 min).
# Outros módulos (ex.: diagnostico_service) usam essa flag para reconhecer sessões inválidas
# sem depender de "pontuacao == 0".
PENALIDADE_SESSAO_INVALIDA = "sessao_invalida_abaixo_20min"

# Penalidades aplicadas sobre a pontuação da própria sessão
_PENALIDADE_PAUSA_CURTA = 0.25   # pausa < 5 min: -25%
_PENALIDADE_PAUSA_LONGA = 0.40   # pausa > 15 min: -40%
_PENALIDADE_SESSAO_LONGA = 0.20  # sessão > 45 min: -20%

_AVISO_SESSAO_LONGA = "Sessão acima de 45 minutos. Considere uma pausa para evitar fadiga mental."


def calcular(dados: PomodoroCreate) -> dict:
    """Calcula pontuação e metadados de uma sessão Pomodoro."""
    peso, valida = _peso_da_sessao(dados.tempo_minutos)

    if not valida:
        return {
            "pontuacao": 0.0,
            "peso": peso,
            "penalidades_aplicadas": [PENALIDADE_SESSAO_INVALIDA],
            "aviso": None,
        }

    # Nota do bloco = foco × 2. O peso da duração não entra aqui — só na
    # média ponderada agregada do diagnóstico Pomodoro.
    pontuacao = float(dados.nivel_foco * 2)
    penalidades: list[str] = []
    aviso: str | None = None

    if dados.tempo_minutos > 45:
        aviso = _AVISO_SESSAO_LONGA
        penalidades.append("sessao_longa_-20%")
        pontuacao *= 1 - _PENALIDADE_SESSAO_LONGA

    if dados.tempo_pausa_minutos is not None:
        pontuacao, p_pausa = _aplicar_penalidade_pausa(pontuacao, dados.tempo_pausa_minutos)
        penalidades.extend(p_pausa)

    return {
        "pontuacao": round(max(pontuacao, 0.0), 2),
        "peso": peso,
        "penalidades_aplicadas": penalidades,
        "aviso": aviso,
    }


def _peso_da_sessao(tempo: int) -> tuple[int, bool]:
    """Retorna (peso, é_válida) com base na duração do bloco Pomodoro."""
    if tempo < 20:
        return 1, False
    if tempo <= 25:
        return 1, True
    if tempo <= 39:
        return 2, True
    if tempo <= 45:
        return 3, True
    # Acima de 45 min: válida, mas peso cai para 1 (e ainda toma a penalidade de sessão longa).
    return 1, True


def _aplicar_penalidade_pausa(pontuacao: float, pausa: int) -> tuple[float, list[str]]:
    """Reduz a pontuação caso a pausa fuja da faixa recomendada (5–15 min)."""
    if pausa < 5:
        return pontuacao * (1 - _PENALIDADE_PAUSA_CURTA), ["pausa_curta_-25%"]
    if pausa > 15:
        return pontuacao * (1 - _PENALIDADE_PAUSA_LONGA), ["pausa_longa_-40%"]
    return pontuacao, []
