# Guia para o avaliador — teste simples e interativo (Streamlit)

Este documento explica **como rodar o projeto**, **como testar pela interface Streamlit** (forma mais rápida e visual) e **como cada parte do sistema se encaixa**. Para detalhes de JSON e regras campo a campo, use também [`CONTRATO.md`](CONTRATO.md).

---

## 1. O que é o sistema

- **API (FastAPI)** que registra sessões de foco já encerradas e devolve **pontuação**, **peso** (só Pomodoro), **penalidades** e **diagnóstico agregado**.
- **Dois métodos de registro:**
  - **Pomodoro:** vários **blocos** no mesmo dia; cada POST é um bloco; exige **plano do dia** (quantos blocos) antes de registrar.
  - **Sessão única:** um **único** registro por **dia de referência**; bloco longo com meta e quantidade de pausas.
- **Persistência:** SQLite em `data/produtividade.db` (criado na subida da API).
- **Streamlit:** cliente de testes que chama a API em `http://localhost:8000` — ideal para validar fluxos sem Postman.

---

## 2. Como rodar (dois processos)

### Terminal 1 — API

```bash
cd teste-tecnico-python-backend-SouJunior
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Saúde: abrir `/docs` já confirma que subiu.

### Terminal 2 — Streamlit

Com o **mesmo** venv ativo (ou outro com `streamlit` e `requests`):

```bash
cd teste-tecnico-python-backend-SouJunior
streamlit run streamlit_app.py
```

O navegador abre o app; ele **depende** da API no endereço configurado no código (`API_URL = "http://localhost:8000"`). Se a API não estiver no ar, as abas mostram erro de conexão.

---

## 3. Teste interativo no Streamlit — roteiro sugerido

### 3.1 Topo da página: **Dia de referência**

- É um **calendário** que define o dia usado nos registros e no plano Pomodoro (query `dia_referencia` na API).
- Serve para **testar em qualquer data** sem mudar o relógio do computador.
- **Dica:** use uma data fixa (ex.: hoje) durante um fluxo; troque o dia para simular “outro dia” e novos planos/registros.

### 3.2 Aba **“Registrar Sessão”**

| Passo | O que fazer | O que validar |
|--------|-------------|----------------|
| 1 | Escolher **Pomodoro**. | Mensagem pedindo para **definir quantas sessões** antes dos blocos. |
| 2 | Informar número de blocos e clicar **Salvar plano de hoje**. | Plano gravado; contador “X/Y blocos” e “Nª sessão”. |
| 3 | Preencher formulário (foco, tempo, comentário, pausa se houver) e **Registrar**. | Status 201 na prática: métricas de pontuação; Pomodoro faz **rerun** e atualiza progresso. |
| 4 | Repetir até completar o plano. | Ao atingir o limite, próximo envio deve falhar com mensagem clara (API 400). |
| 5 | Trocar para **Sessão única**. | Expander com **recomendações de tempo e pausas**; só **uma** sessão única por dia de referência — segunda tentativa bloqueada (UI + API). |
| 6 | Registrar uma sessão única válida (meta/tempo 30–720 min). | Pontuação e possíveis penalidades na resposta. |

**Regras importantes refletidas na UI:**

- **Pomodoro:** formulário de bloco **só aparece** com plano salvo e ainda com vagas (`GET /registro-foco/status-dia`).
- **Sessão única:** formulário some se já existir registro `sessao_unica` naquele dia.

### 3.3 Aba **“Diagnóstico”**

| Ação | Efeito |
|--------|--------|
| **Período:** “Todos” ou “Filtrar por mês/ano” + **Buscar** | Carrega agregados: tempo total, médias, Pomodoro (incl. **média ponderada** `Σ(nota×peso)/Σ(pesos)`), Sessão única, lista de sessões. |
| **Gerenciar registros** | Apagar por ID ou apagar todos — após sucesso a lista **atualiza** (estado em `session_state` + novo GET). |

Use para conferir se **média ponderada do Pomodoro** bate com blocos de exemplo (notas × pesos / soma dos pesos).

### 3.4 Aba **“Comparar Sessões”**

- Escolhe duas sessões do período e mostra comparação percentual (depende dos dados já registrados).

### 3.5 Aba **“Como funciona”**

- Texto estático explicando foco 1–5, Pomodoro (nota, peso na média, pausas), Sessão única (meta, pausas, penalidades em linguagem simples).

---

## 4. Como cada parte do sistema funciona (visão de arquitetura)

```text
[Streamlit] --HTTP--> [FastAPI app.main]
                            |
                     [routers/registros.py]
                     - valida body (Pydantic)
                     - aplica regras de “pode registrar?”
                            |
              +-----------+-----------+
              |                       |
    [pomodoro_service]      [sessao_unica_service]
    [diagnostico_service]            |
              |                       |
         [storage/database.py]  <-- SQLite
              data/produtividade.db
```

| Camada | Arquivo(s) | Função |
|--------|------------|--------|
| **HTTP** | `app/routers/registros.py` | Rotas: registro, plano Pomodoro, diagnóstico, status do dia, DELETE registros. |
| **Contratos** | `app/schemas/registro.py` | Modelos Pydantic: criação discriminada (`pomodoro` vs `sessao_unica`), respostas, diagnóstico. |
| **Regras Pomodoro** | `app/services/pomodoro_service.py` | Nota ≈ `foco×2` + penalidades (duração, pausa entre blocos); **peso** por faixa de minutos para a **média ponderada** no diagnóstico (não multiplica a nota do bloco na mesma fórmula). |
| **Regras Sessão única** | `app/services/sessao_unica_service.py` | Base `foco×2×min(1, tempo/meta)` + penalidade por **quantidade** de pausas vs ~1 por hora. |
| **Agregação** | `app/services/diagnostico_service.py` | Lê todos os registros (opcionalmente filtra mês), calcula médias, Pomodoro por dia, média ponderada correta. |
| **Persistência** | `app/storage/database.py` | SQLite: tabelas `registros`, `pomodoro_planos`; inserts, contagens por dia, deletes. |
| **Bootstrap** | `app/main.py` | `lifespan` chama `database.inicializar()` ao subir. |

---

## 5. Endpoints úteis para o avaliador (resumo)

| Método | Rota | Uso |
|--------|------|-----|
| `GET` | `/registro-foco/status-dia?dia_referencia=YYYY-MM-DD` | Saber se pode registrar Pomodoro / se sessão única já existe no dia. |
| `POST` | `/pomodoro/plano?dia_referencia=...` | Definir quantidade de blocos do dia. |
| `GET` | `/pomodoro/plano?dia_referencia=...` | Consultar plano (404 se não existir). |
| `POST` | `/registro-foco?dia_referencia=...` | Criar registro (corpo JSON varia com `metodo`). |
| `GET` | `/diagnostico-produtividade?mes=YYYY-MM` | Diagnóstico (mês opcional). |
| `DELETE` | `/registros/{id}` | Apaga um registro. |
| `DELETE` | `/registros` | Limpa registros e planos (cuidado em ambiente real). |

Detalhes e exemplos: [`CONTRATO.md`](CONTRATO.md).

---

## 6. Testar sem Streamlit (opcional)

Use **Swagger** (`/docs`): os schemas discriminados aparecem nos exemplos do `POST /registro-foco`. Lembre-se de:

1. `POST /pomodoro/plano` antes dos blocos Pomodoro.
2. `dia_referencia` coerente nas queries se quiser simular datas.

### Testes automatizados (`pytest`)

Na raiz do repositório, com o venv ativo:

```bash
pytest
```

A pasta `tests/` cobre a API (FastAPI `TestClient`), serviços de pontuação e média ponderada do diagnóstico. Cada teste usa banco SQLite isolado em diretório temporário.

---

## 7. Problemas comuns

| Sintoma | Causa provável |
|---------|----------------|
| Streamlit: “API não encontrada” | `uvicorn` não está rodando ou porta diferente de 8000. |
| Pomodoro 400 “Defina primeiro o plano” | Plano não salvo para aquele `dia_referencia`. |
| Pomodoro 400 “Plano completo” | Já atingiu N blocos; apague um registro ou aumente o plano. |
| Sessão única 400 “uma por dia” | Já existe `sessao_unica` naquele dia; apague ou mude o dia de referência. |
| Banco “estranho” após testes | `DELETE /registros` no diagnóstico ou apagar `data/produtividade.db` com a API **parada** (recria na próxima subida). |

---

## 8. Checklist rápido para o avaliador

- [ ] API sobe sem erro; `/docs` abre.
- [ ] Streamlit sobe e enxerga a API.
- [ ] Pomodoro: sem plano → não registra bloco; com plano → registra até o limite.
- [ ] Sessão única: uma por dia de referência; recomendações visíveis no formulário.
- [ ] Diagnóstico: busca, métricas e média ponderada Pomodoro coerentes com dados de teste.
- [ ] Exclusão de registros reflete na lista após ação.
- [ ] (Opcional) Comparar duas sessões com dados existentes.

Boa avaliação.
