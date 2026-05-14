from sqlalchemy.orm import Session
from . import repository, schemas
from typing import Optional

def gerar_feedback(media: float, total_minutos: int) -> str:
    """
    Gera uma mensagem de feedback baseada na performance.

    Args:
        media (float): A média do nível de foco.
        total_minutos (int): O total de minutos focados.

    Returns:
        str: A mensagem de feedback.
    """
    if media < 2:
        return "Muitas distrações. Tente Pomodoro e desligue notificações. 🔕"
    if media < 3:
        return "Foco abaixo do ideal. Pausas mais longas podem ajudar. ☕"
    if media < 4 and total_minutos < 60:
        return "Sessões curtas e foco mediano. Tente blocos de 25 min contínuos. ⏱️"
    if media < 4:
        return "Progresso razoável! Identifique distrações e elimine. 🎯"
    if media >= 4 and total_minutos >= 120:
        return "Maratona produtiva de alto nível! 🚀"
    if media >= 4:
        return "Ótimo foco! Mais blocos e você terá um dia excelente. 💪"
    return "Continue registrando para receber feedbacks mais precisos."

def formatar_tempo(minutos: int) -> str:
    """
    Formata minutos em uma string 'Xh Ymin'.

    Args:
        minutos (int): O total de minutos.

    Returns:
        str: A string formatada.
    """
    if minutos is None:
        return "0min"
    h = minutos // 60
    m = minutos % 60
    if h > 0:
        return f"{h}h {m}min"
    return f"{m}min"

def obter_diagnostico_completo(db: Session) -> Optional[schemas.DiagnosticoOut]:
    """
    Cria o objeto de diagnóstico completo com todos os dados.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        Optional[schemas.DiagnosticoOut]: O objeto de diagnóstico ou None se não houver dados.
    """
    total_registros = repository.get_total_registros(db)
    if total_registros == 0:
        return None

    media_nivel_foco = repository.get_media_nivel_foco(db)
    tempo_total_minutos = repository.get_tempo_total_minutos(db)
    melhor_sessao = repository.get_melhor_sessao(db)
    pior_sessao = repository.get_pior_sessao(db)
    distribuicao_categorias = repository.get_distribuicao_categorias(db)

    feedback = gerar_feedback(media_nivel_foco, tempo_total_minutos)
    tempo_formatado = formatar_tempo(tempo_total_minutos)

    return schemas.DiagnosticoOut(
        total_registros=total_registros,
        media_nivel_foco=round(media_nivel_foco, 2),
        tempo_total_minutos=tempo_total_minutos,
        tempo_formatado=tempo_formatado,
        melhor_sessao=melhor_sessao,
        pior_sessao=pior_sessao,
        distribuicao_categorias=distribuicao_categorias,
        feedback=feedback,
    )
