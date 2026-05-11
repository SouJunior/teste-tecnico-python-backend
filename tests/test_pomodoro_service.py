"""
Testes unitários de pomodoro_service (sem HTTP).

Cobrem peso por duração, nota foco×2, penalidades de pausa/duração e sessão inválida.
"""

import pytest

from app.schemas.registro import PomodoroCreate
from app.services import pomodoro_service


def test_pomodoro_sessao_invalida_menos_20min():
    """Menos de 20 min: nota 0, peso 1, flag PENALIDADE_SESSAO_INVALIDA na lista."""
    dados = PomodoroCreate(
        metodo="pomodoro",
        nivel_foco=5,
        tempo_minutos=15,
        comentario="x",
        tempo_pausa_minutos=10,
    )
    r = pomodoro_service.calcular(dados)
    assert r["pontuacao"] == 0.0
    assert r["peso"] == 1
    assert pomodoro_service.PENALIDADE_SESSAO_INVALIDA in r["penalidades_aplicadas"]


def test_pomodoro_foco_vezes_dois_pausa_ok():
    """35 min ⇒ peso 2; foco 4 ⇒ nota 8; pausa 10 min sem penalidade."""
    dados = PomodoroCreate(
        metodo="pomodoro",
        nivel_foco=4,
        tempo_minutos=35,
        comentario="x",
        tempo_pausa_minutos=10,
    )
    r = pomodoro_service.calcular(dados)
    assert r["pontuacao"] == 8.0
    assert r["peso"] == 2
    assert r["penalidades_aplicadas"] == []


def test_pomodoro_pausa_curta_penalidade():
    """Pausa < 5 min aplica −25% sobre foco×2 (8 × 0,75 = 6)."""
    dados = PomodoroCreate(
        metodo="pomodoro",
        nivel_foco=4,
        tempo_minutos=35,
        comentario="x",
        tempo_pausa_minutos=3,
    )
    r = pomodoro_service.calcular(dados)
    assert r["pontuacao"] == pytest.approx(6.0, rel=1e-6)
    assert "pausa_curta_-25%" in r["penalidades_aplicadas"]


def test_pomodoro_sem_pausa_registrada():
    """Último bloco do dia: tempo_pausa_minutos=null não aplica regra de pausa."""
    dados = PomodoroCreate(
        metodo="pomodoro",
        nivel_foco=5,
        tempo_minutos=40,
        comentario="x",
        tempo_pausa_minutos=None,
    )
    r = pomodoro_service.calcular(dados)
    assert r["pontuacao"] == 10.0
    assert r["peso"] == 3


def test_pomodoro_sessao_longa_acima_45min():
    """Bloco >45 min: válido, peso 1, −20% na nota + aviso de fadiga."""
    dados = PomodoroCreate(
        metodo="pomodoro",
        nivel_foco=5,
        tempo_minutos=50,
        comentario="x",
        tempo_pausa_minutos=10,
    )
    r = pomodoro_service.calcular(dados)
    assert r["peso"] == 1
    assert r["pontuacao"] == pytest.approx(8.0, rel=1e-6)
    assert "sessao_longa_-20%" in r["penalidades_aplicadas"]
    assert r["aviso"]


def test_pomodoro_pausa_longa_penalidade():
    """Pausa > 15 min aplica −40% (8 × 0,6 = 4,8)."""
    dados = PomodoroCreate(
        metodo="pomodoro",
        nivel_foco=4,
        tempo_minutos=35,
        comentario="x",
        tempo_pausa_minutos=16,
    )
    r = pomodoro_service.calcular(dados)
    assert r["pontuacao"] == pytest.approx(4.8, rel=1e-6)
    assert "pausa_longa_-40%" in r["penalidades_aplicadas"]
