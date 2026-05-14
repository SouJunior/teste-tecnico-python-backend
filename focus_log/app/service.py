from sqlalchemy.orm import Session
from . import repository, schemas
from typing import Optional, Dict, List
from datetime import date, timedelta
from collections import defaultdict

def atualizar_status_gamificacao(db: Session):
    """
    Atualiza a sequência de dias de foco (streak).

    Args:
        db (Session): A sessão do banco de dados.
    """
    status_app = repository.get_status_app(db)
    if not status_app:
        status_app = repository.create_status_app(db)

    hoje = date.today()
    data_ultimo_registro = status_app.data_ultimo_registro.date() if status_app.data_ultimo_registro else None

    if data_ultimo_registro == hoje:
        return # Já atualizado hoje

    if data_ultimo_registro == hoje - timedelta(days=1):
        status_app.sequencia_atual += 1
    else:
        status_app.sequencia_atual = 1 # Reinicia a sequência

    if status_app.sequencia_atual > status_app.sequencia_maxima:
        status_app.sequencia_maxima = status_app.sequencia_atual
    
    status_app.data_ultimo_registro = hoje
    db.commit()

def obter_status_app(db: Session) -> schemas.StatusOut:
    """
    Obtém o status de gamificação formatado para o schema de saída.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        schemas.StatusOut: O status de gamificação.
    """
    status_app = repository.get_status_app(db)
    if not status_app:
        status_app = repository.create_status_app(db)

    mensagem = "Você ainda não registrou nenhuma sessão de foco. Registre a primeira para começar sua sequência!"
    if status_app.sequencia_atual == 1:
        mensagem = f"Parabéns por iniciar sua sequência! Você está há {status_app.sequencia_atual} dia focado. Continue amanhã! 🔥"
    elif status_app.sequencia_atual > 1:
        mensagem = f"Incrível! Você mantém uma sequência de {status_app.sequencia_atual} dias. Sua consistência é a chave para a produtividade. 🚀"
    
    # Mensagem especial se a sequência máxima foi batida
    if status_app.sequencia_atual > 0 and status_app.sequencia_atual == status_app.sequencia_maxima:
        mensagem += " E você acaba de bater seu recorde pessoal!"


    return schemas.StatusOut(
        sequencia_atual=status_app.sequencia_atual,
        sequencia_maxima=status_app.sequencia_maxima,
        mensagem=mensagem
    )


def analisar_tags(db: Session) -> schemas.AnaliseTagsOut:
    """
    Analisa as tags e as correlaciona com o nível de foco.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        schemas.AnaliseTagsOut: A análise de tags.
    """
    registros = repository.get_all_registros_foco(db)
    if not registros:
        return schemas.AnaliseTagsOut(tags_alto_foco={}, tags_baixo_foco={})

    tags_foco: Dict[str, List[int]] = defaultdict(list)

    for r in registros:
        if r.tags:
            for tag in r.tags.split(','):
                tag_limpa = tag.strip().lower()
                if tag_limpa:
                    tags_foco[tag_limpa].append(r.nivel_foco)

    media_tags = {tag: sum(niveis) / len(niveis) for tag, niveis in tags_foco.items()}

    tags_alto_foco = {tag: round(media, 2) for tag, media in sorted(media_tags.items(), key=lambda item: item[1], reverse=True) if media >= 3.5}
    tags_baixo_foco = {tag: round(media, 2) for tag, media in sorted(media_tags.items(), key=lambda item: item[1]) if media < 3.0}

    return schemas.AnaliseTagsOut(
        tags_alto_foco=dict(list(tags_alto_foco.items())[:5]), # Limita a 5
        tags_baixo_foco=dict(list(tags_baixo_foco.items())[:5]) # Limita a 5
    )

def gerar_feedback(media: float, total_minutos: int) -> str:
    """
    Gera uma mensagem de feedback detalhada e didática baseada na performance.

    Args:
        media (float): A média do nível de foco.
        total_minutos (int): O total de minutos focados.

    Returns:
        str: A mensagem de feedback.
    """
    if media < 2:
        return "Sua média de foco está muito baixa, indicando muitas distrações. Tente usar a técnica Pomodoro (25 min de foco, 5 de pausa) e desligue as notificações. 🔕"
    if media < 3:
        return "Seu foco está abaixo do ideal. Isso pode ser sinal de cansaço. Pausas um pouco mais longas ou um café podem ajudar a recarregar. ☕"
    if media < 4 and total_minutos < 60:
        return "Você está fazendo sessões curtas com foco mediano. Para entrar em 'flow', tente criar blocos de tempo de pelo menos 25 minutos contínuos. ⏱️"
    if media < 4:
        return "Seu progresso é razoável! O próximo passo é identificar as principais fontes de distração durante as sessões e tentar eliminá-las. 🎯"
    if media >= 4 and total_minutos >= 120:
        return "Excelente! Você teve uma maratona produtiva de alto nível, mantendo o foco por um longo período. Continue assim! 🚀"
    if media >= 4:
        return "Ótimo trabalho mantendo um foco de alta qualidade! Se você conseguir encaixar mais blocos de tempo como este, seu dia será extremamente produtivo. 💪"
    return "Continue registrando suas sessões para receber feedbacks cada vez mais precisos e acompanhar sua evolução."


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
