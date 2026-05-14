import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sobrescrever a dependência get_db para usar o banco de teste
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """
    Fixture para criar um cliente de teste e gerenciar o banco de dados.
    """
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

# --- Testes para o endpoint POST /registro-foco ---

def test_criar_registro_foco_sucesso(client):
    """
    Testa a criação de um registro de foco com dados válidos.
    """
    response = client.post(
        "/registro-foco",
        json={
            "nivel_foco": 4,
            "tempo_minutos": 45,
            "comentario": "Desenvolvimento da API",
            "categoria": "coding",
            "tags": "backend,fastapi"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nivel_foco"] == 4
    assert data["comentario"] == "Desenvolvimento da API"
    assert "id" in data
    assert "criado_em" in data

@pytest.mark.parametrize("nivel_foco_invalido", [0, 6, -1])
def test_criar_registro_foco_nivel_invalido(client, nivel_foco_invalido):
    """
    Testa a criação com nível de foco fora do range (1-5).
    """
    response = client.post(
        "/registro-foco",
        json={"nivel_foco": nivel_foco_invalido, "tempo_minutos": 30, "comentario": "Teste"},
    )
    assert response.status_code == 422

@pytest.mark.parametrize("tempo_invalido", [0, -10, 1441])
def test_criar_registro_foco_tempo_invalido(client, tempo_invalido):
    """
    Testa a criação com tempo em minutos fora do range permitido.
    """
    response = client.post(
        "/registro-foco",
        json={"nivel_foco": 3, "tempo_minutos": tempo_invalido, "comentario": "Teste"},
    )
    assert response.status_code == 422

def test_criar_registro_foco_comentario_curto(client):
    """
    Testa a criação com um comentário muito curto.
    """
    response = client.post(
        "/registro-foco",
        json={"nivel_foco": 3, "tempo_minutos": 25, "comentario": "ab"},
    )
    assert response.status_code == 422
