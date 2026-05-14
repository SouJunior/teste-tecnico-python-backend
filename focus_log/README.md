# Focus Log API - v2.0

Uma API robusta e inteligente para registrar, analisar e gamificar suas sessões de foco, construída com FastAPI e SQLite. Este projeto vai além de um simples CRUD, incorporando uma arquitetura profissional e funcionalidades criativas para se destacar.

## Filosofia do Projeto

O objetivo não é apenas armazenar dados, mas transformá-los em **insights acionáveis** e **motivação**. A API foi desenhada para ajudar o usuário a entender seus próprios padrões de produtividade e a construir o hábito da consistência através de mecânicas de gamificação.

## Funcionalidades Principais

-   **Registro de Foco**: Endpoint para registrar sessões de trabalho ou estudo.
-   **Diagnóstico de Produtividade**: Uma análise completa com métricas como média de foco, tempo total e as melhores/piores sessões.
-   **Feedback Inteligente**: Mensagens didáticas que explicam *por que* o feedback está sendo dado e sugerem ações.
-   **Gamificação (Streaks)**: Sistema de "sequências" que incentiva o registro diário, recompensando a consistência.
-   **Análise de Tags**: Correlaciona as tags usadas nos registros com o nível de foco, revelando o que te ajuda ou atrapalha a ser produtivo.

---

## Decisões de Arquitetura e Design

A estrutura do projeto foi escolhida para garantir **clareza, manutenibilidade e escalabilidade**.

-   **FastAPI**: Escolhido pela sua alta performance, sintaxe moderna com type hints (que reduz bugs) e a geração automática de documentação interativa (Swagger UI), que é excelente para desenvolvimento e testes.

-   **Arquitetura em Camadas**:
    -   `main.py`: Ponto de entrada. Mínimo de lógica, apenas configurações globais e inclusão dos roteadores.
    -   `routers/`: Responsáveis por definir os endpoints HTTP. Sua única função é receber requisições, chamar a camada de serviço e retornar respostas. Não contêm lógica de negócio.
    -   `service.py`: O "cérebro" da aplicação. Contém toda a lógica de negócio (como gerar feedbacks, calcular streaks, analisar tags). Não tem conhecimento sobre HTTP ou o banco de dados diretamente, o que a torna reutilizável e fácil de testar.
    -   `repository.py`: A única camada que interage com o banco de dados. Abstrai as queries do SQLAlchemy, centralizando o acesso aos dados.
    -   `models.py` e `schemas.py`: Separação clara entre o modelo do banco de dados (SQLAlchemy) e o modelo da API (Pydantic). Isso permite que a API evolua de forma independente do banco.

-   **SQLite**: Selecionado pela simplicidade. É um banco de dados baseado em arquivo, que não exige instalação ou configuração de um servidor, tornando o projeto extremamente fácil de rodar localmente. Para um ambiente de produção, a troca para um banco como PostgreSQL seria simples, bastando alterar a `DATABASE_URL` e instalar o driver `psycopg2`.

-   **Pydantic para Validação**: Usado extensivamente para validar os dados de entrada (`RegistroFocoCreate`) e garantir a estrutura dos dados de saída (`*Out` schemas). As mensagens de erro customizadas e o handler de exceção global em `main.py` melhoram a experiência de quem consome a API.

-   **Tarefas em Background (`BackgroundTasks`)**: A atualização da gamificação é feita em segundo plano. Isso proporciona uma resposta mais rápida ao usuário no momento do registro, pois ele não precisa esperar o cálculo da sequência ser finalizado.

---

## Como Usar

### Pré-requisitos

-   Python 3.11 ou superior

### Instalação e Execução

1.  **Clone o repositório e entre na pasta:**
    ```bash
    git clone https://github.com/seu-usuario/focus_log.git
    cd focus_log
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie o arquivo de ambiente local:**
    Este passo é crucial para definir a conexão com o banco de dados.
    ```bash
    # Windows
    copy .env.example .env
    # macOS/Linux
    cp .env.example .env
    ```

5.  **Execute a aplicação:**
    ```bash
    uvicorn app.main:app --reload
    ```
    A API estará disponível em `http://127.0.0.1:8000`.

### Testando a API

A forma mais fácil de interagir com a API é através da **documentação interativa (Swagger UI)**, disponível em:

[**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

Lá você pode testar todos os endpoints diretamente do seu navegador.

---

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

2.  **Verificar o status da sua sequência (gamificação):**
    ```bash
    curl -X 'GET' 'http://127.0.0.1:8000/analise/status' -H 'accept: application/json'
    ```

3.  **Obter a análise de tags:**
    ```bash
    curl -X 'GET' 'http://127.0.0.1:8000/analise/tags' -H 'accept: application/json'
    ```

4.  **Obter o diagnóstico de produtividade:**
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/diagnostico-produtividade' \
      -H 'accept: application/json'
    ```

---

## Como Rodar os Testes

Para garantir a qualidade e o funcionamento correto da API, execute os testes automatizados com `pytest`.

```bash
pytest
```
