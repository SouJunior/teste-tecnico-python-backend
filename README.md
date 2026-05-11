# API de Foco e Produtividade

Backend em **FastAPI** com **SQLite** para registrar sessões de foco (**Pomodoro** e **Sessão única**), calcular pontuações e expor **diagnóstico agregado**. Inclui app **Streamlit** para testes interativos.

---

## Documentação

| Documento | Conteúdo |
|-----------|-----------|
| **[`docs/GUIA_AVALIADOR.md`](docs/GUIA_AVALIADOR.md)** | **Principal para avaliação:** como rodar, testar no Streamlit passo a passo, arquitetura e endpoints resumidos. |
| [`docs/CONTRATO.md`](docs/CONTRATO.md) | Contrato da API: campos, exemplos JSON, erros e regras de negócio detalhadas. |

---

## Como rodar

### Pré-requisitos

- Python 3.11+ (3.12 testado)

### Ambiente e dependências

```bash
git clone <url-do-repo>
cd teste-tecnico-python-backend-SouJunior
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
```

### API (FastAPI)

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- O banco `data/produtividade.db` é criado/atualizado na inicialização (`lifespan`).

### Interface de testes (Streamlit)

Em **outro terminal**, com o venv ativo e a API **já rodando**:

```bash
streamlit run streamlit_app.py
```

O app usa `http://localhost:8000` por padrão. Fluxo completo e explicação de cada aba: **[`docs/GUIA_AVALIADOR.md`](docs/GUIA_AVALIADOR.md)**.

### Testes automatizados (pytest)

Na raiz do projeto (com venv ativo e dependências instaladas):

```bash
pytest
```

Os testes usam um **SQLite temporário** por função (não alteram `data/produtividade.db`).

---

## Endpoints (visão geral)

| Método | Rota | Descrição |
|--------|------|-------------|
| `GET` | `/registro-foco/status-dia` | Estado do dia: plano Pomodoro, vagas, se já existe sessão única. |
| `POST` | `/pomodoro/plano` | Define quantos blocos Pomodoro no dia (`dia_referencia` opcional). |
| `GET` | `/pomodoro/plano` | Consulta plano do dia. |
| `POST` | `/registro-foco` | Registra bloco Pomodoro ou sessão única (`dia_referencia` opcional). |
| `GET` | `/diagnostico-produtividade` | Diagnóstico; query `mes=YYYY-MM` opcional. |
| `DELETE` | `/registros/{id}` | Remove um registro. |
| `DELETE` | `/registros` | Remove todos os registros e planos. |

Detalhes e payloads: [`docs/CONTRATO.md`](docs/CONTRATO.md).

---

## Arquitetura

```
app/
├── main.py                    # FastAPI + lifespan (init SQLite)
├── routers/
│   └── registros.py           # Rotas HTTP
├── services/
│   ├── pomodoro_service.py    # Nota por bloco, penalidades, peso para média
│   ├── sessao_unica_service.py
│   └── diagnostico_service.py # Agregações e feedback
├── schemas/
│   └── registro.py            # Pydantic (requests/responses)
└── storage/
    └── database.py            # SQLite → data/produtividade.db
streamlit_app.py               # UI de testes (requests → API)
```

**Princípios:** rotas finas; regras de pontuação nos serviços; validação com Pydantic; persistência isolada em `storage/database.py`.

---

## Regras de pontuação (resumo)

- **Pomodoro:** nota do bloco a partir de `foco × 2` + penalidades (tempo de sessão, pausa entre blocos). **Peso** por faixa de duração entra só na **média ponderada** do diagnóstico: `Σ(nota×peso) / Σ(pesos)`.
- **Sessão única:** `foco × 2 × min(1, tempo/meta)` + penalidade por **quantidade** de pausas vs ~1 por hora.

Mais detalhe: serviços em `app/services/` e [`docs/CONTRATO.md`](docs/CONTRATO.md).

---

## Próximos passos (ideias de produto)

- Autenticação / multiusuário
- Relatórios exportáveis (PDF/CSV)
- Testes automatizados (pytest + client HTTP)
