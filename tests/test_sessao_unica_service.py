"""
Testes unitários de sessao_unica_service (sem HTTP).

Cobrem cumprimento de meta em %, teto ao passar da meta e penalidades por número de pausas.
"""

import pytest

from app.schemas.registro import SessaoUnicaCreate
from app.services import sessao_unica_service


def test_sessao_unica_base_meta_cumprida_total():
    """Tempo ≥ meta com foco 5 e ritmo de pausa ok ⇒ nota máxima (10)."""
    dados = SessaoUnicaCreate(
        metodo="sessao_unica",
        nivel_foco=5,
        tempo_minutos=120,
        meta_minutos=120,
        qtd_pausas=2,
        comentario="x",
    )
    r = sessao_unica_service.calcular(dados)
    assert r["pontuacao"] == 10.0
    assert r["peso"] is None
    assert r["penalidades_aplicadas"] == []


def test_sessao_unica_meta_parcial():
    """Metade do tempo combinado ⇒ metade da nota máxima (4×2×0,5 = 4)."""
    dados = SessaoUnicaCreate(
        metodo="sessao_unica",
        nivel_foco=4,
        tempo_minutos=60,
        meta_minutos=120,
        qtd_pausas=1,
        comentario="x",
    )
    r = sessao_unica_service.calcular(dados)
    assert r["pontuacao"] == pytest.approx(4.0, rel=1e-6)


def test_sessao_unica_acima_da_meta_nao_ganha_bonus():
    """Tempo acima da meta não aumenta acima do 100% nem sofre penalidade de pausa neste cenário (~10% de desvio, margem até 33%)."""
    dados = SessaoUnicaCreate(
        metodo="sessao_unica",
        nivel_foco=5,
        tempo_minutos=200,
        meta_minutos=100,
        qtd_pausas=3,
        comentario="x",
    )
    r = sessao_unica_service.calcular(dados)
    assert r["pontuacao"] == 10.0
    assert r["penalidades_aplicadas"] == []


def test_sessao_unica_penalidade_pausas_forte():
    """2 h de trabalho ⇒ ~2 pausas ideais; 0 pausas ⇒ desvio grande ⇒ −70% na nota após tempo×foco."""
    dados = SessaoUnicaCreate(
        metodo="sessao_unica",
        nivel_foco=5,
        tempo_minutos=120,
        meta_minutos=120,
        qtd_pausas=0,
        comentario="x",
    )
    r = sessao_unica_service.calcular(dados)
    assert r["pontuacao"] == pytest.approx(3.0, rel=1e-6)
    assert "pausas_fora_do_ideal_-70%" in r["penalidades_aplicadas"]
