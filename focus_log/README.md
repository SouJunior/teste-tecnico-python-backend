# Focus Log API

Uma API simples e robusta para registrar e analisar suas sessões de foco, construída com FastAPI e SQLite.

## Pré-requisitos

- Python 3.11 ou superior

## Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/focus_log.git
    cd focus_log
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie o arquivo de ambiente:**
    Copie o arquivo `.env.example` para um novo arquivo chamado `.env`.
    ```bash
    # Windows
    copy .env.example .env
    # macOS/Linux
    cp .env.example .env
    ```
    O `DATABASE_URL` padrão (`sqlite:///./focus_log.db`) já está configurado para usar SQLite.

5.  **Execute a aplicação:**
    ```bash
    uvicorn app.main:app --reload
    ```
    A API estará disponível em `http://127.0.0.1:8000`. A documentação interativa (Swagger UI) pode ser acessada em `http://127.0.0.1:8000/docs`.

## Exemplos de Uso (cURL)

1.  **Registrar uma nova sessão de foco:**
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/registro-foco' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "nivel_foco": 5,
      "tempo_minutos": 90,
      "comentario": "Desenvolvendo a funcionalidade de diagnóstico com foco total!",
      "categoria": "coding",
      "tags": "backend,python,api"
    }'
    ```

2.  **Obter o diagnóstico de produtividade:**
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/diagnostico-produtividade' \
      -H 'accept: application/json'
    ```

## Regras de Feedback

O endpoint de diagnóstico fornece um feedback motivacional com base na sua performance.

| Condição                          | Mensagem                                                               |
|-----------------------------------|------------------------------------------------------------------------|
| Média de Foco < 2                 | "Muitas distrações. Tente Pomodoro e desligue notificações. 🔕"       |
| Média de Foco < 3                 | "Foco abaixo do ideal. Pausas mais longas podem ajudar. ☕"            |
| Média < 4 e Total < 60 min        | "Sessões curtas e foco mediano. Tente blocos de 25 min contínuos. ⏱️" |
| Média de Foco < 4                 | "Progresso razoável! Identifique distrações e elimine. 🎯"            |
| Média >= 4 e Total >= 120 min     | "Maratona produtiva de alto nível! 🚀"                                 |
| Média de Foco >= 4                | "Ótimo foco! Mais blocos e você terá um dia excelente. 💪"             |

## Como Rodar os Testes

Para garantir a qualidade e o funcionamento correto da API, execute os testes automatizados com `pytest`.

```bash
pytest
```

## Estrutura de Pastas

O projeto segue uma arquitetura limpa e organizada para facilitar a manutenção e escalabilidade.

```
focus_log/
├── app/                  # Contém toda a lógica da aplicação
│   ├── main.py           # Ponto de entrada da API, handlers de erro globais
│   ├── database.py       # Configuração do banco de dados (engine, SessionLocal)
│   ├── models.py         # Modelos de dados do SQLAlchemy (tabelas)
│   ├── schemas.py        # Schemas Pydantic para validação e serialização
│   ├── repository.py     # Funções de acesso ao banco (CRUD)
│   ├── service.py        # Lógica de negócio pura (ex: gerar feedback)
│   └── routers/          # Módulos dos endpoints da API
│       ├── registro.py     # Endpoint para criar registros
│       └── diagnostico.py  # Endpoint para obter o diagnóstico
├── tests/                # Testes automatizados
│   ├── test_registro.py    # Testes para o endpoint de registro
│   └── test_diagnostico.py # Testes para o endpoint de diagnóstico
├── .env.example          # Exemplo de arquivo de variáveis de ambiente
├── requirements.txt      # Dependências do projeto
└── README.md             # Este arquivo
```
