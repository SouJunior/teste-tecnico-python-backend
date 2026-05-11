# Uso de inteligência artificial neste desafio

Este documento descreve, de forma transparente, como a **inteligência artificial (IA)** foi utilizada no desenvolvimento deste projeto — com **dois perfis de agente** complementares — e deixa claro o papel da **auditoria humana** (autoria) sobre o código e o comportamento entregue.

---

## Objetivo do documento

- Registrar que o trabalho contou com **assistentes de IA** (ambiente Cursor, modelos conversacionais).
- Explicar a **separação de papéis** entre o agente focado em **mentoria/construção** e o agente focado em **revisão/qualidade**.
- Esclarecer o que a IA **pode** fazer e o que **não substitui**: decisão final, entendimento do domínio e garantia de qualidade continuam sob **responsabilidade humana**.
- Servir de referência para **avaliadores** ou **equipes** com política explícita de uso de IA em testes técnicos.

---

## Dois agentes de IA

Foram utilizados **dois agentes**, com prioridades distintas:

### Agente mentor

**Papel:** apoiar a **maturação das ideias** (produto, regras de negócio, fluxos no Streamlit) e a **construção do boilerplate** e do código inicial.

**Exemplos de contribuição:**

- Discussão de requisitos e tradução em estrutura de projeto (FastAPI, camadas, SQLite).
- Rascunho de endpoints, schemas Pydantic, serviços de pontuação e integração com a UI de testes.
- Iteração a partir de feedback (“assim não”, “ajuste a média ponderada”, etc.).

### Agente revisor

**Papel:** priorizar um projeto **enxuto**, **legível**, de **fácil manutenção**, **eficiente** e **seguro** (no nível adequado a uma demo técnica).

**Exemplos de contribuição:**

- Evitar escopo desnecessário, duplicação e “ruído” no diff.
- Sugerir simplificações, nomes e organização alinhados a leitura humana.
- Apontar riscos básicos (ex.: consistência de dados, SQL parametrizado, ausência de segredos no repositório) e boas práticas de teste.

Os dois agentes **não substituem um ao outro**: o mentor acelera **ideia + esqueleto**; o revisor puxa para **qualidade e sustentabilidade**. O que entra no repositório passou, no fim, pela **minha** filtragem e decisão.

---

## Resumo por área (o que a IA cobriu)

| Área | Mentor (ideias + construção) | Revisor (enxuto + claro + sustentável) |
|------|------------------------------|----------------------------------------|
| **Código** | Estrutura inicial, fluxos, correções após bugs reportados | Cortar excesso, manter legível e coerente com o restante do projeto |
| **Regras de negócio** | Modelagem a partir da conversa | Checar se implementação reflete a regra sem encosto desnecessário |
| **Testes** | Proposta de pytest, `TestClient`, fixtures | Garantir que testes sejam objetivos e não frágeis demais |
| **Documentação** | Rascunhos (README, guia, contrato) | Textos alinhados ao que o código realmente faz |

---

## O que foi feito por mim (auditoria e autoria)

**Todo o resultado final foi auditado, ajustado e validado por mim**, incluindo:

- **Leitura e compreensão** do código sugerido por qualquer um dos agentes — linha a linha quando necessário.
- **Reescrita** do que não atendia ao desafio, às regras combinadas ou ao padrão que defini com o agente revisor (clareza, manutenção, segurança básica de demo).
- **Decisões de produto** (ex.: dia de referência, plano Pomodoro antes dos blocos, uma sessão única por dia, textos de interface e documentação).
- **Execução dos testes** (`pytest`) e **testes manuais** (API + Streamlit) no meu ambiente.
- **Commits e histórico** no Git organizados conforme minha preferência de granularidade e mensagens em português.

A IA **não** substitui:

- Garantir que o desafio foi **interpretado corretamente**.
- Confirmar que não há **efeitos colaterais** indesejados (dados, UX, limitações conscientes de segurança em ambiente de teste).
- Assumir **responsabilidade** pelo envio: o repositório reflete o que **eu** aceitei após revisão.

---

## Como interpreto o uso de IA neste contexto

- São **ferramentas** — úteis como documentação viva ou discussão com colegas — com a diferença de serem rápidas e sujeitas a **erros ou alucinações**.
- O valor entregue depende de **instruções claras**, **dois focos** (construir vs. revisar) e, sobretudo, de **revisão humana** antes de considerar pronto.

---

## Referência para avaliadores

- O código-fonte, os testes em `tests/` e a documentação em `docs/` podem ser inspecionados normalmente.
- Este arquivo declara o uso de IA de forma **explícita**, incluindo a distinção **mentor × revisor**; dúvidas sobre decisões específicas podem ser esclarecidas na entrevista ou no PR, apontando para commits ou arquivos concretos.

---

*Documento elaborado pelo autor do repositório para fins de transparência no desafio SouJunior / teste técnico.*
