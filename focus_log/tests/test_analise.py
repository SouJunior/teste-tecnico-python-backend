import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from datetime import date, timedelta

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analise.db"
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

# --- Testes de Gamificação ---

def test_status_inicial(client):
    """Testa o status inicial da gamificação com banco vazio."""
    response = client.get("/analise/status")
    assert response.status_code == 200
    data = response.json()
    assert data["sequencia_atual"] == 0
    assert data["sequencia_maxima"] == 0
    assert "Comece hoje" in data["mensagem"]

def test_sequencia_de_foco(client):
    """Testa a lógica de contagem de sequência (streak)."""
    # Dia 1
    client.post("/registro-foco", json={"nivel_foco": 4, "tempo_minutos": 50, "comentario": "d1"})
    
    response = client.get("/analise/status")
    data = response.json()
    assert data["sequencia_atual"] == 1
    assert data["sequencia_maxima"] == 1

    # Adulterando o banco para simular o dia seguinte
    from app.models import StatusApp
    db = TestingSessionLocal()
    status_app = db.query(StatusApp).first()
    status_app.data_ultimo_registro = date.today() - timedelta(days=1)
    db.commit()
    db.close()

    # Dia 2
    client.post("/registro-foco", json={"nivel_foco": 4, "tempo_minutos": 50, "comentario": "d2"})
    response = client.get("/analise/status")
    data = response.json()
    assert data["sequencia_atual"] == 2
    assert data["sequencia_maxima"] == 2

# --- Testes de Análise de Tags ---

def test_analise_tags_vazio(client):
    """Testa a análise de tags com banco vazio."""
    response = client.get("/analise/tags")
    assert response.status_code == 200
    assert response.json() == {"tags_alto_foco": {}, "tags_baixo_foco": {}}

def test_analise_tags_com_dados(client):
    """Testa a correlação de tags com o nível de foco."""
    client.post("/registro-foco", json={"nivel_foco": 5, "tempo_minutos": 90, "comentario": "c", "tags": "python, backend"})
    client.post("/registro-foco", json={"nivel_foco": 4, "tempo_minutos": 60, "comentario": "c", "tags": "python, estudo"})
    client.post("/registro-foco", json={"nivel_foco": 2, "tempo_minutos": 30, "comentario": "c", "tags": "reuniao, cansado"})
    client.post("/registro-foco", json={"nivel_foco": 1, "tempo_minutos": 15, "comentario": "c", "tags": "cansado"})

    response = client.get("/analise/tags")
    assert response.status_code == 200
    data = response.json()

    assert "python" in data["tags_alto_foco"]
    assert data["tags_alto_foco"]["python"] == 4.5

    assert "cansado" in data["tags_baixo_foco"]
    assert data["tags_baixo_foco"]["cansado"] == 1.5
