# Contrato da API — Foco e Produtividade

Documentação dos endpoints, campos, regras de negócio e respostas.

**Avaliador:** para um roteiro de teste interativo com Streamlit e visão de arquitetura, veja **[`GUIA_AVALIADOR.md`](GUIA_AVALIADOR.md)**.

---

## Convenções

### `dia_referencia` (query opcional na maioria dos endpoints)

Quase todas as rotas aceitam `?dia_referencia=YYYY-MM-DD`. Quando omitido, o valor é **hoje** (data local da máquina onde a API roda). Permite registrar e consultar dados em datas passadas ou futuras sem mudar o relógio do sistema — útil para testes.

Validação: regex `^\d{4}-\d{2}-\d{2}$`. Formato inválido → `422 Unprocessable Entity`.

### `criado_em` no response

Guardado e retornado como **string `YYYY-MM-DD`** (data, não datetime). Corresponde ao `dia_referencia` usado no momento do POST.

---

## Endpoints

| Método | Rota | Resumo |
|--------|------|--------|
| `GET` | `/registro-foco/status-dia` | Estado do dia: plano Pomodoro, vagas, se já há sessão única |
| `POST` | `/registro-foco` | Cria um registro (Pomodoro ou Sessão única) |
| `POST` | `/pomodoro/plano` | Define quantos blocos Pomodoro no dia |
| `GET` | `/pomodoro/plano` | Consulta plano do dia |
| `GET` | `/diagnostico-produtividade` | Diagnóstico agregado (mês opcional) |
| `DELETE` | `/registros/{id}` | Remove um registro |
| `DELETE` | `/registros` | Remove todos os registros e planos |

---

## `GET /registro-foco/status-dia`

Diz se o formulário pode liberar registros de Pomodoro (e quantos faltam) e se a sessão única já foi feita no dia.

### Query

| Nome | Tipo | Default |
|---|---|---|
| `dia_referencia` | `YYYY-MM-DD` | hoje |

### Response `200 OK`

```json
{
  "dia": "2026-05-11",
  "pomodoro": {
    "total_sessoes": 4,
    "sessoes_registradas": 2,
    "sessoes_restantes": 2
  },
  "sessao_unica_ja_registrada": false
}
```

- `pomodoro` é `null` quando ainda não existe plano para o dia.

---

## `POST /pomodoro/plano`

Cria/atualiza o plano Pomodoro do dia. **Pré-requisito** para registrar blocos Pomodoro.

### Query

| Nome | Tipo | Default |
|---|---|---|
| `dia_referencia` | `YYYY-MM-DD` | hoje |

### Body

```json
{ "total_sessoes": 4 }
```

Regras: `total_sessoes` entre 1 e 20.

### Response `200 OK`

```json
{
  "dia": "2026-05-11",
  "total_sessoes": 4,
  "sessoes_registradas": 0,
  "sessoes_restantes": 4
}
```

---

## `GET /pomodoro/plano`

Consulta o plano do dia.

### Query

| Nome | Tipo | Default |
|---|---|---|
| `dia_referencia` | `YYYY-MM-DD` | hoje |

### Respostas

- `200 OK`: mesmo formato do POST.
- `404 Not Found`: `{"detail": "Plano Pomodoro para YYYY-MM-DD ainda não definido."}` (a data corresponde a `dia_referencia`).

---

## `POST /registro-foco`

Registra um bloco de trabalho encerrado. O contrato do body é **discriminado** pelo campo `metodo` (`pomodoro` ou `sessao_unica`).

### Query

| Nome | Tipo | Default |
|---|---|---|
| `dia_referencia` | `YYYY-MM-DD` | hoje |

### Campos comuns (todos os métodos)

| Campo | Tipo | Regras |
|---|---|---|
| `metodo` | `"pomodoro"` ou `"sessao_unica"` | Literal exato |
| `nivel_foco` | int | 1 a 5 |
| `tempo_minutos` | int | ≥ 1 (Pomodoro). Sessão única: 30–720 |
| `comentario` | string | não vazio |
| `categoria` | enum opcional | `"coding"`, `"reuniao"`, `"estudo"`, `"outro"` |

> Campos não listados são rejeitados (`extra="forbid"` no Pydantic).

### Campos exclusivos — Pomodoro

| Campo | Tipo | Observação |
|---|---|---|
| `tempo_pausa_minutos` | int ou `null` | Pausa após esta sessão. `null` = última sessão do dia |

### Campos exclusivos — Sessão única

| Campo | Tipo | Observação |
|---|---|---|
| `meta_minutos` | int | **Obrigatório**. 30 a 720 (12 h) |
| `qtd_pausas` | int | **Obrigatório**. ≥ 0 |

### Exemplos de request

**Pomodoro:**
```json
{
  "metodo": "pomodoro",
  "nivel_foco": 4,
  "tempo_minutos": 38,
  "comentario": "Estudei algoritmos de grafos sem distração",
  "tempo_pausa_minutos": 8,
  "categoria": "estudo"
}
```

**Sessão única:**
```json
{
  "metodo": "sessao_unica",
  "nivel_foco": 5,
  "tempo_minutos": 480,
  "meta_minutos": 540,
  "qtd_pausas": 7,
  "comentario": "Sprint de desenvolvimento — foco alto, reuniões interromperam",
  "categoria": "coding"
}
```

### Response `201 Created`

```json
{
  "id": 1,
  "metodo": "pomodoro",
  "nivel_foco": 4,
  "tempo_minutos": 38,
  "comentario": "Estudei algoritmos de grafos sem distração",
  "categoria": "estudo",
  "tempo_pausa_minutos": 8,
  "meta_minutos": null,
  "qtd_pausas": null,
  "pontuacao": 8.0,
  "peso": 2,
  "penalidades_aplicadas": [],
  "aviso": null,
  "criado_em": "2026-05-11"
}
```

### Erros de regra de negócio (`400 Bad Request`)

Retornados como `{"detail": "<mensagem>"}`:

| Situação | Mensagem |
|---|---|
| Pomodoro sem plano do dia | "Defina primeiro o plano Pomodoro do dia (quantidade de sessões)." |
| Pomodoro com plano completo | "Plano Pomodoro completo: X/Y blocos registrados. Para registrar mais, apague um registro ou aumente o plano Pomodoro do dia." |
| Segunda sessão única no mesmo dia | "Só é permitida uma Sessão única por dia de referência. Apague o registro existente ou escolha outro dia." |

### Validações de schema (`422 Unprocessable Entity`)

As mensagens vêm do Pydantic v2 (em inglês). Exemplos de campos que devolvem 422 quando inválidos:

- `nivel_foco` fora de 1–5
- `metodo` diferente de `"pomodoro"` / `"sessao_unica"`
- `tempo_minutos` < 1 (Pomodoro) ou fora de 30–720 (Sessão única)
- `meta_minutos` ausente, fora de 30–720, em Sessão única
- `qtd_pausas` ausente ou negativo em Sessão única
- `comentario` vazio
- Qualquer campo extra não previsto

---

## `GET /diagnostico-produtividade`

Resumo agregado das sessões registradas.

### Query

| Parâmetro | Formato | Efeito |
|---|---|---|
| `mes` | `YYYY-MM` | Restringe ao mês civil (ex.: `2026-05`) |
| _(omitido)_ | — | Todos os registros |

### Response `200 OK`

```json
{
  "tempo_total_minutos": 280,
  "total_sessoes": 5,
  "media_foco_geral": 3.8,
  "media_pontuacao_geral": 6.12,
  "foco_min": 2,
  "foco_max": 5,
  "pontuacao_min": 0.0,
  "pontuacao_max": 10.0,
  "pomodoro": {
    "total_sessoes": 1,
    "blocos_registrados": 4,
    "sessoes_validas": 3,
    "sessoes_invalidas": 1,
    "media_ponderada": 7.5
  },
  "sessao_unica": {
    "total_sessoes": 1,
    "media_pontuacao": 3.24
  },
  "mensagem_feedback": "Bom ritmo! Ajuste suas pausas para chegar ao próximo nível de desempenho.",
  "sessoes_no_periodo": [
    {
      "id": 1,
      "dia": "2026-05-10",
      "metodo": "pomodoro",
      "nivel_foco": 4,
      "tempo_minutos": 35,
      "pontuacao": 8.0,
      "comentario": "Estudei algoritmos"
    }
  ]
}
```

**Notas:**

- `total_sessoes` conta **dias** com Pomodoro (não blocos) + sessões únicas. `blocos_registrados` mostra a contagem real de blocos Pomodoro.
- `media_pontuacao_geral` mistura métodos com fórmulas diferentes — útil como visão geral, não como comparação direta entre métodos.
- `sessoes_no_periodo` traz os registros considerados, em ordem cronológica, com o dia de cada um.

### Sem registros

```json
{
  "tempo_total_minutos": 0,
  "total_sessoes": 0,
  "media_foco_geral": 0.0,
  "media_pontuacao_geral": 0.0,
  "foco_min": 0,
  "foco_max": 0,
  "pontuacao_min": 0.0,
  "pontuacao_max": 0.0,
  "pomodoro": {
    "total_sessoes": 0,
    "blocos_registrados": 0,
    "sessoes_validas": 0,
    "sessoes_invalidas": 0,
    "media_ponderada": 0.0
  },
  "sessao_unica": { "total_sessoes": 0, "media_pontuacao": 0.0 },
  "mensagem_feedback": "Nenhuma sessão registrada ainda. Comece sua primeira sessão!",
  "sessoes_no_periodo": []
}
```

---

## `DELETE /registros/{registro_id}`

Remove um registro pelo `id`.

- `200 OK`: `{"ok": true}`
- `404 Not Found`: `{"detail": "Registro não encontrado."}`

## `DELETE /registros`

Remove **todos** os registros e planos Pomodoro. Sempre `200 OK`: `{"ok": true}`.

---

## Regras de negócio

### Método Pomodoro

**Peso por duração do bloco (afeta só a média ponderada do diagnóstico):**

| Duração do bloco | Peso | Válido |
|---|---|---|
| < 20 min | 1 | Não (nota = 0, conta como inválida) |
| 20–25 min | 1 | Sim |
| 26–39 min | 2 | Sim |
| 40–45 min | 3 | Sim (faixa ideal) |
| > 45 min | 1 | Sim (aviso + −20% na nota) |

**Nota de cada bloco (antes da agregação):**
```
nota = nivel_foco × 2
nota *= (1 − 0.20)   se duração > 45 min
nota *= (1 − pen_pausa)   se houver pausa fora de 5–15 min
```

**Penalidades de pausa (sobre a nota acima):**

| Situação | Penalidade |
|---|---|
| Pausa < 5 min | −25% |
| Pausa 5–15 min | sem penalidade |
| Pausa > 15 min | −40% |

**Média ponderada no diagnóstico:**
```
media_ponderada = Σ(nota_do_bloco × peso_do_bloco) / Σ(pesos)
```

### Método Sessão Única

**Pontuação:**
```
pontuacao = nivel_foco × 2 × min(1, tempo_minutos / meta_minutos) × (1 − pen_pausas)
```

**Pausas ideais:** 1 por hora trabalhada.

**Penalidades por desvio das pausas ideais:**

| Desvio das pausas ideais | Penalidade |
|---|---|
| ≤ 33% | sem penalidade |
| 33%–50% | −10% |
| 50%–86% | −40% |
| > 86% | −70% |

### Mensagens de feedback (baseadas em `media_foco_geral`)

| Faixa | Mensagem |
|---|---|
| < 2.0 | "Muita distração hoje. Tente ambientes mais silenciosos e sessões mais curtas." |
| 2.0–2.9 | "Foco abaixo do ideal. Experimente o método Pomodoro para estruturar melhor seu ritmo." |
| 3.0–3.9 | "Bom ritmo! Ajuste suas pausas para chegar ao próximo nível de desempenho." |
| 4.0–4.4 | "Ótima performance! Você está perto do estado de flow." |
| ≥ 4.5 | "Estado de flow! Maratona produtiva de alto nível. Continue assim." |
