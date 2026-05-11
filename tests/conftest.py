"""
Fixtures globais dos testes.

`isolated_database` (autouse) redireciona o SQLite para um arquivo temporário por teste.
`client` expõe a app FastAPI com esse banco já inicializado.
"""

import pytest


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch, tmp_path):
    """SQLite limpo por teste; não usa data/produtividade.db da máquina."""
    from app.storage import database

    db_path = tmp_path / "test_produtividade.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.inicializar()
    yield


@pytest.fixture
def client(isolated_database):  # noqa: ARG001 — ordem explícita: BD antes do TestClient
    """Cliente HTTP contra `app.main` (lifespan inicializa as tabelas no tmp)."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
