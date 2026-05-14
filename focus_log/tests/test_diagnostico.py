import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Reutilizando a configuração do banco de dados de teste de test_registro
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

# --- Testes para o endpoint GET /diagnostico-produtividade ---

def test_diagnostico_banco_vazio(client):
    """
    Testa o GET em /diagnostico-produtividade com o banco de dados vazio.
    """
    response = client.get("/diagnostico-produtividade")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Nenhum registro ainda. Registre sua primeira sessão de foco!"}

def test_diagnostico_com_dados(client):
    """
    Testa o GET em /diagnostico-produtividade após inserir alguns registros.
    """
    # Inserir dados de teste
    client.post("/registro-foco", json={"nivel_foco": 5, "tempo_minutos": 90, "comentario": "Deep work em feature X", "categoria": "coding"})
    client.post("/registro-foco", json={"nivel_foco": 2, "tempo_minutos": 30, "comentario": "Reunião de alinhamento", "categoria": "reuniao"})
    client.post("/registro-foco", json={"nivel_foco": 4, "tempo_minutos": 50, "comentario": "Estudo de documentação", "categoria": "estudo"})

    response = client.get("/diagnostico-produtividade")
    assert response.status_code == 200
    data = response.json()

    # Verificar os campos principais
    assert data["total_registros"] == 3
    assert data["tempo_total_minutos"] == 170
    assert data["tempo_formatado"] == "2h 50min"
    assert data["media_nivel_foco"] == round((5 + 2 + 4) / 3, 2)
    
    # Verificar melhor e pior sessão
    assert data["melhor_sessao"]["nivel_foco"] == 5
    assert data["pior_sessao"]["nivel_foco"] == 2

    # Verificar distribuição e feedback
    assert data["distribuicao_categorias"] == {"coding": 1, "reuniao": 1, "estudo": 1}
    assert data["feedback"] == "Maratona produtiva de alto nível! 🚀"
