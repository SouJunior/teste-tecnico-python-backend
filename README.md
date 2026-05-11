# 🧠 Log de Performance & Foco

Este é um projeto Fullstack desenvolvido para o **Desafio Técnico: API de Foco e Produtividade**. A aplicação permite que desenvolvedores e estudantes registrem suas sessões de trabalho, acompanhem o nível de estado de fluxo (*flow*) e recebam um diagnóstico inteligente sobre sua produtividade.

---

## 🚀 Tecnologias Utilizadas

### Backend
* **Python 3.12+**
* **FastAPI**: Framework web de alta performance.
* **SQLAlchemy**: ORM para mapeamento e manipulação do banco de dados.
* **SQLite**: Banco de dados relacional leve para persistência de dados.
* **Pydantic**: Validação de dados e schemas.

### Frontend
* **Angular 18**: Framework para construção da interface web.
* **Bootstrap**: Para um design responsivo e limpo.
* **HttpClient**: Para comunicação assíncrona com a API.

---

## 🛠️ Arquitetura do Projeto

O projeto segue princípios de **Clean Code** e **Separação de Responsabilidades (SOC)**:

* `app/main.py`: Ponto de entrada da API e definição das rotas.
* `app/service.py`: Camada de serviço contendo a lógica de negócio e cálculos de diagnóstico.
* `app/models.py`: Definição das tabelas do banco de dados.
* `app/schemas.py`: Validação de entrada e saída de dados com Pydantic.
* `app/database.py`: Configuração da conexão com o SQLite.

---

## 🔧 Como Rodar o Projeto

### 1. Backend (FastAPI)

Certifique-se de ter o Python instalado. Recomenda-se o uso de um ambiente virtual (`venv`).

```bash
# Entre na pasta raiz do projeto
cd teste-tecnico-python-backend

# Crie e ative o ambiente virtual
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
uvicorn app.main:app --reload