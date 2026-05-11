"""
Testes de integração HTTP (FastAPI TestClient).

Usam sempre `dia_referencia` com datas fictícias (2030) para não misturar com o relógio
real. Precisam da fixture `client` (SQLite temporário criado antes da app).
"""

DIA = "2030-01-15"
DIA_MES_OUTRO = "2030-03-10"


def pomodoro_bloco_json(comentario: str = "x", **overrides):
    """Monta um JSON válido para POST /registro-foco método pomodoro; overrides sobrescrevem campos."""
    body = {
        "metodo": "pomodoro",
        "nivel_foco": 4,
        "tempo_minutos": 35,
        "comentario": comentario,
        "tempo_pausa_minutos": 10,
    }
    body.update(overrides)
    return body


def test_status_dia_sem_plano_pomodoro(client):
    """Sem plano ⇒ pomodoro null; sem sessão única ⇒ flag False."""
    r = client.get("/registro-foco/status-dia", params={"dia_referencia": DIA})
    assert r.status_code == 200
    body = r.json()
    assert body["dia"] == DIA
    assert body["pomodoro"] is None
    assert body["sessao_unica_ja_registrada"] is False


def test_post_pomodoro_sem_plano_400(client):
    """Registrar bloco antes de definir plano ⇒ 400 e mensagem fala em plano."""
    r = client.post(
        "/registro-foco",
        params={"dia_referencia": DIA},
        json=pomodoro_bloco_json(comentario="teste"),
    )
    assert r.status_code == 400
    assert "plano" in r.json()["detail"].lower()


def test_fluxo_plano_pomodoro_tres_blocos(client):
    """Plano 3 blocos: três POST 201, o quarto 400 por limite do dia."""
    r = client.post(
        "/pomodoro/plano",
        params={"dia_referencia": DIA},
        json={"total_sessoes": 3},
    )
    assert r.status_code == 200
    assert r.json()["sessoes_restantes"] == 3

    for i in range(3):
        r2 = client.post(
            "/registro-foco",
            params={"dia_referencia": DIA},
            json=pomodoro_bloco_json(comentario=f"bloco {i}"),
        )
        assert r2.status_code == 201, r2.text

    r3 = client.post(
        "/registro-foco",
        params={"dia_referencia": DIA},
        json=pomodoro_bloco_json(comentario="extra"),
    )
    assert r3.status_code == 400


def test_get_plano_404_sem_definir(client):
    """GET plano para um dia onde nunca foi feito POST do plano ⇒ 404."""
    r = client.get("/pomodoro/plano", params={"dia_referencia": "2030-02-01"})
    assert r.status_code == 404


def test_sessao_unica_segundo_registro_mesmo_dia_400(client):
    """Duas sessões únicas no mesmo dia_referencia ⇒ segunda requisição 400."""
    body = {
        "metodo": "sessao_unica",
        "nivel_foco": 4,
        "tempo_minutos": 120,
        "meta_minutos": 120,
        "qtd_pausas": 2,
        "comentario": "primeira",
    }
    assert client.post("/registro-foco", params={"dia_referencia": DIA}, json=body).status_code == 201
    body["comentario"] = "segunda"
    r2 = client.post("/registro-foco", params={"dia_referencia": DIA}, json=body)
    assert r2.status_code == 400
    assert "sessão única" in r2.json()["detail"].lower()


def test_diagnostico_vazio(client):
    """Sem registros no banco ⇒ 200 e total_sessoes=0 no JSON."""
    r = client.get("/diagnostico-produtividade")
    assert r.status_code == 200
    assert r.json()["total_sessoes"] == 0


def test_diagnostico_filtra_por_mes(client):
    """query mes=YYYY-MM conta só registros cuja data cai naquele mês civil."""
    client.post("/pomodoro/plano", params={"dia_referencia": DIA_MES_OUTRO}, json={"total_sessoes": 1})
    assert (
        client.post(
            "/registro-foco",
            params={"dia_referencia": DIA_MES_OUTRO},
            json=pomodoro_bloco_json(),
        ).status_code
        == 201
    )

    mar = client.get("/diagnostico-produtividade", params={"mes": "2030-03"}).json()
    jan = client.get("/diagnostico-produtividade", params={"mes": "2030-01"}).json()

    assert mar["total_sessoes"] == 1
    assert jan["total_sessoes"] == 0


def test_delete_registro_inexistente_404(client):
    """DELETE por id que não existe ⇒ 404."""
    r = client.delete("/registros/99999")
    assert r.status_code == 404


def test_delete_registro_ok(client):
    """Apagar existente ⇒ 200; repetir ⇒ 404."""
    client.post("/pomodoro/plano", params={"dia_referencia": DIA}, json={"total_sessoes": 1})
    rid = client.post(
        "/registro-foco",
        params={"dia_referencia": DIA},
        json=pomodoro_bloco_json(comentario="apagar", tempo_minutos=30),
    ).json()["id"]

    r = client.delete(f"/registros/{rid}")
    assert r.status_code == 200

    r2 = client.delete(f"/registros/{rid}")
    assert r2.status_code == 404


def test_clear_all_limite_diagnostico_e_plano(client):
    """DELETE /registros zera métricas e remove plano Pomodoro do mesmo dia (GET plano → 404)."""
    client.post("/pomodoro/plano", params={"dia_referencia": DIA}, json={"total_sessoes": 1})
    client.post(
        "/registro-foco",
        params={"dia_referencia": DIA},
        json=pomodoro_bloco_json(),
    )
    assert client.delete("/registros").status_code == 200

    d = client.get("/diagnostico-produtividade").json()
    assert d["total_sessoes"] == 0

    r404 = client.get("/pomodoro/plano", params={"dia_referencia": DIA})
    assert r404.status_code == 404
