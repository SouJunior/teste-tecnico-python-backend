from app.schemas.registro import SessaoUnicaCreate

# Recomendação: 1 pausa de 5 min por hora trabalhada
_PAUSAS_POR_HORA = 1


def calcular(dados: SessaoUnicaCreate) -> dict:
    """Calcula pontuação e metadados de uma Sessão Única."""
    # Regra: foco x 2 x (% da meta cumprida). Ex.: meta 100, real 90 -> 0.9.
    percentual_cumprido = min(dados.tempo_minutos / dados.meta_minutos, 1.0)
    pontuacao_base = dados.nivel_foco * 2 * percentual_cumprido

    fator_penalidade, descricao_penalidade = _penalidade_pausas(
        dados.tempo_minutos, dados.qtd_pausas
    )

    penalidades: list[str] = []
    if fator_penalidade > 0:
        penalidades.append(descricao_penalidade)

    pontuacao_final = round(max(pontuacao_base * (1 - fator_penalidade), 0.0), 2)

    return {
        "pontuacao": pontuacao_final,
        "peso": None,
        "penalidades_aplicadas": penalidades,
        "aviso": None,
    }


def _penalidade_pausas(tempo_minutos: int, qtd_pausas: int) -> tuple[float, str]:
    """
    Penalidade conforme o desvio entre as pausas realizadas e o ideal
    (1 pausa por hora trabalhada).
    """
    pausas_ideais = (tempo_minutos / 60) * _PAUSAS_POR_HORA
    if pausas_ideais == 0:
        return 0.0, ""

    desvio = abs(qtd_pausas - pausas_ideais) / pausas_ideais

    if desvio <= 1 / 3:
        return 0.0, ""
    if desvio <= 0.50:
        return 0.10, "pausas_fora_do_ideal_-10%"
    if desvio <= 0.86:
        return 0.40, "pausas_fora_do_ideal_-40%"
    return 0.70, "pausas_fora_do_ideal_-70%"
