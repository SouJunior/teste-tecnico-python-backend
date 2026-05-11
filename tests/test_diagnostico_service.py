"""
Testes do agregado de diagnóstico.

`_resumo_pomodoro` é interno, mas permite validar a média Σ(nota x peso)/Σ(pesos)
sem HTTP. Um teste chama `gerar_diagnostico` com SQLite (fixture `isolated_database`).
"""

from app.services import diagnostico_service
from app.services.pomodoro_service import PENALIDADE_SESSAO_INVALIDA
from app.storage import database


def test_resumo_pomodoro_media_ponderada():
    """Mesmo dia, 3 blocos validos => total_sessoes=1; media ponderada (8x2 + 7,5x3 + 10x3)/8."""
    registros = [
        {
            "metodo": "pomodoro",
            "pontuacao": 8.0,
            "peso": 2,
            "penalidades_aplicadas": [],
            "criado_em": "2026-05-10",
        },
        {
            "metodo": "pomodoro",
            "pontuacao": 7.5,
            "peso": 3,
            "penalidades_aplicadas": [],
            "criado_em": "2026-05-10",
        },
        {
            "metodo": "pomodoro",
            "pontuacao": 10.0,
            "peso": 3,
            "penalidades_aplicadas": [],
            "criado_em": "2026-05-10",
        },
    ]
    r = diagnostico_service._resumo_pomodoro(registros)
    assert r["blocos_registrados"] == 3
    assert r["total_sessoes"] == 1
    assert r["sessoes_validas"] == 3
    assert r["sessoes_invalidas"] == 0
    assert r["media_ponderada"] == 8.56


def test_resumo_pomodoro_sessao_invalida_por_flag():
    """Conta como inválida pela flag PENALIDADE_SESSAO_INVALIDA, não só por nota zero."""
    registros = [
        {
            "metodo": "pomodoro",
            "pontuacao": 0.0,
            "peso": 1,
            "penalidades_aplicadas": [PENALIDADE_SESSAO_INVALIDA],
            "criado_em": "2026-05-10",
        },
    ]
    r = diagnostico_service._resumo_pomodoro(registros)
    assert r["sessoes_invalidas"] == 1
    assert r["sessoes_validas"] == 0


def test_gerar_diagnostico_com_registro_no_banco():
    """Caminho integral: INSERT + leitura + lista cronológica e total_sessões."""
    database.insert(
        {
            "metodo": "pomodoro",
            "nivel_foco": 4,
            "tempo_minutos": 35,
            "comentario": "x",
            "pontuacao": 8.0,
            "penalidades_aplicadas": [],
            "criado_em": "2026-05-01",
        }
    )
    d = diagnostico_service.gerar_diagnostico()
    assert d["total_sessoes"] == 1
    assert len(d["sessoes_no_periodo"]) == 1
    assert d["sessoes_no_periodo"][0]["dia"] == "2026-05-01"
