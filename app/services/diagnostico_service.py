from typing import Optional

from app.services.pomodoro_service import PENALIDADE_SESSAO_INVALIDA
from app.storage import database

_MENSAGENS_FEEDBACK = [
    (2.0, "Muita distração hoje. Tente ambientes mais silenciosos e sessões mais curtas."),
    (3.0, "Foco abaixo do ideal. Experimente o método Pomodoro para estruturar melhor seu ritmo."),
    (4.0, "Bom ritmo! Ajuste suas pausas para chegar ao próximo nível de desempenho."),
    (4.5, "Ótima performance! Você está perto do estado de flow."),
]
_MENSAGEM_FLOW = "Estado de flow! Maratona produtiva de alto nível. Continue assim."
_MENSAGEM_VAZIA = "Nenhuma sessão registrada ainda. Comece sua primeira sessão!"


def gerar_diagnostico(mes: Optional[str] = None) -> dict:
    registros = database.get_all(mes=mes)
    if not registros:
        return _diagnostico_vazio()

    pomodoros = [r for r in registros if r["metodo"] == "pomodoro"]
    sessoes_unicas = [r for r in registros if r["metodo"] == "sessao_unica"]

    pontuacoes = [float(r["pontuacao"]) for r in registros]
    focos = [r["nivel_foco"] for r in registros]
    media_foco = sum(focos) / len(focos)
    # No domínio, "sessão" Pomodoro = um dia (pode ter vários blocos no mesmo dia).
    total_sessoes_estudo = len(sessoes_unicas) + len({r["criado_em"] for r in pomodoros})

    return {
        "tempo_total_minutos": sum(r["tempo_minutos"] for r in registros),
        "total_sessoes": total_sessoes_estudo,
        "media_foco_geral": round(media_foco, 2),
        "media_pontuacao_geral": round(sum(pontuacoes) / len(pontuacoes), 2),
        "foco_min": min(focos),
        "foco_max": max(focos),
        "pontuacao_min": round(min(pontuacoes), 2),
        "pontuacao_max": round(max(pontuacoes), 2),
        "pomodoro": _resumo_pomodoro(pomodoros),
        "sessao_unica": _resumo_sessao_unica(sessoes_unicas),
        "mensagem_feedback": _mensagem_por_media(media_foco),
        "sessoes_no_periodo": _lista_sessoes_com_dia(registros),
    }


def _resumo_pomodoro(registros: list[dict]) -> dict:
    if not registros:
        return {
            "total_sessoes": 0,
            "blocos_registrados": 0,
            "sessoes_validas": 0,
            "sessoes_invalidas": 0,
            "media_ponderada": 0.0,
        }

    invalidas = sum(1 for r in registros if PENALIDADE_SESSAO_INVALIDA in r["penalidades_aplicadas"])
    validas = len(registros) - invalidas
    dias_pomodoro = {r["criado_em"] for r in registros}

    soma_pesos = sum(int(r["peso"] or 0) for r in registros)
    soma_nota_peso = sum(float(r["pontuacao"]) * int(r["peso"] or 0) for r in registros)
    media_ponderada = soma_nota_peso / soma_pesos if soma_pesos > 0 else 0.0

    return {
        "total_sessoes": len(dias_pomodoro),
        "blocos_registrados": len(registros),
        "sessoes_validas": validas,
        "sessoes_invalidas": invalidas,
        "media_ponderada": round(media_ponderada, 2),
    }


def _resumo_sessao_unica(registros: list[dict]) -> dict:
    if not registros:
        return {"total_sessoes": 0, "media_pontuacao": 0.0}

    media = sum(r["pontuacao"] for r in registros) / len(registros)
    return {
        "total_sessoes": len(registros),
        "media_pontuacao": round(media, 2),
    }


def _mensagem_por_media(media: float) -> str:
    for limite, mensagem in _MENSAGENS_FEEDBACK:
        if media < limite:
            return mensagem
    return _MENSAGEM_FLOW


def _lista_sessoes_com_dia(registros: list[dict]) -> list[dict]:
    # `criado_em` é guardado como YYYY-MM-DD, então a ordenação lexicográfica é cronológica.
    ordenados = sorted(registros, key=lambda r: r["criado_em"])
    return [
        {
            "id": r["id"],
            "dia": r["criado_em"],
            "metodo": r["metodo"],
            "nivel_foco": r["nivel_foco"],
            "tempo_minutos": r["tempo_minutos"],
            "pontuacao": float(r["pontuacao"]),
            "comentario": r["comentario"],
        }
        for r in ordenados
    ]


def _diagnostico_vazio() -> dict:
    return {
        "tempo_total_minutos": 0,
        "total_sessoes": 0,
        "media_foco_geral": 0.0,
        "media_pontuacao_geral": 0.0,
        "foco_min": 0,
        "foco_max": 0,
        "pontuacao_min": 0.0,
        "pontuacao_max": 0.0,
        "pomodoro": {
            "total_sessoes": 0,
            "blocos_registrados": 0,
            "sessoes_validas": 0,
            "sessoes_invalidas": 0,
            "media_ponderada": 0.0,
        },
        "sessao_unica": {"total_sessoes": 0, "media_pontuacao": 0.0},
        "mensagem_feedback": _MENSAGEM_VAZIA,
        "sessoes_no_periodo": [],
    }
