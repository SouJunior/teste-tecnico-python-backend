from datetime import date

import pandas as pd
import requests
import streamlit as st

API_URL = "http://localhost:8000"
_ERRO_CONEXAO = (
    "API não encontrada. Certifique-se de que o servidor está rodando em localhost:8000"
)


def chamar_api(metodo: str, rota: str, **kwargs):
    """
    Faz uma requisição à API tratando falhas de rede/timeout de forma central.
    Em caso de erro de requisição, mostra mensagem no Streamlit e retorna None.
    """
    try:
        return requests.request(metodo, f"{API_URL}{rota}", timeout=5, **kwargs)
    except requests.exceptions.RequestException as e:
        st.error(f"{_ERRO_CONEXAO} ({type(e).__name__}: {e})")
        return None


def _recarregar_diagnostico() -> None:
    """Refaz o GET do diagnóstico com o último filtro usado e atualiza o estado."""
    params = st.session_state.get("diag_query", {}) or None
    resp = chamar_api("GET", "/diagnostico-produtividade", params=params)
    if resp is not None and resp.status_code == 200:
        st.session_state["diag_dados"] = resp.json()


_MSG_PLANO_POMODORO_ANTES_BLOCOS = (
    "Defina quantas sessões de pomodoro fará hoje antes de poder registrar os blocos."
)

_MESES_PT = (
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
)

COMO_FUNCIONA = """
### O que é este sistema?

Você registra **sessões de trabalho/estudo** já encerradas. Em cada uma informa **quanto tempo durou**, uma **autoavaliação de foco** (1 a 5) e **um comentário**.  
Há **dois modos**: **Pomodoro** (vários blocos com pausa entre eles) e **Sessão única** (um bloco longo com várias pausas no meio). O backend calcula uma **pontuação** por sessão e o diagnóstico mostra **médias e extremos** no período que você escolher.

---

### Nível de foco (todos os métodos)

| Faixa | Significado |
|-------|-------------|
| **1** | Muito distraído |
| **5** | Estado de flow |

**Possíveis valores:** só inteiros **de 1 a 5** (mínimo absoluto **1**, máximo absoluto **5**).  
No diagnóstico, **média de foco** = média aritmética desses valores em **todas** as sessões do período (Pomodoro + Sessão única).

---

### Método Pomodoro

**O que você informa por sessão:** tempo real da sessão; opcionalmente a **pausa após** essa sessão (minutos). Cada post = uma sessão; a pausa é *entre* uma sessão e a próxima.

**Peso da sessão** (pelo tempo de foco, em minutos):

| Duração | Peso | Observação |
|---------|------|------------|
| **&lt; 20** | 1 | Sessão **inválida**: não gera pontos (`0`), mas entra na **média ponderada** do Pomodoro (penaliza o índice). |
| **20–25** | 1 | Válida |
| **26–39** | 2 | Válida |
| **40–45** | 3 | Faixa “ideal” |
| **&gt; 45** | 1 | Válida, mas aparece **aviso** de fadiga |

**Pontuação de cada bloco:** `nível de foco × 2`; em seguida aplicam-se as penalidades (pausa fora da faixa, sessão muito longa).  
**Peso da duração** não entra na nota do bloco — só na **média ponderada** do Pomodoro no diagnóstico (`Σ(nota×peso) / Σ(pesos)`).  
**Penalidades** (sobre a nota após `foco × 2`):

- Pausa **&lt; 5 min** → −**25%**
- Pausa **5 a 15 min** → sem desconto
- Pausa **&gt; 15 min** → −**40%**

**Média do Pomodoro no diagnóstico** = soma das pontuações ÷ soma dos **pesos** (média **ponderada**).

**Pontuação no Pomodoro (por bloco, até 10):**
- Base: `nota = nível_de_foco × 2`.
- Depois: penalidades de duração da sessão e de intervalo de pausa (mesmas regras acima).
- **Nota máxima por bloco: 10** (foco 5, sem penalidades).
- **Resultado agregado do dia:** média ponderada das notas dos blocos, usando o **peso** só nessa etapa.

---

### Método Sessão única

**O que você informa:** tempo **real** da sessão, **meta** planejada (30 min a **12 h** = 720 min), e **quantas pausas** fez no meio do bloco.

**Tempo — o que acontece se não cumprir a meta**
- A **meta** é o tempo que você tinha combinado comigo mesmo para aquele bloco; o **tempo real** é o que de fato rolou.
- Se estudou **menos** que a meta, a nota **cai na mesma proporção**: meta 2 h e só 1 h de foco → essa parte vale metade; meta 1 h e 30 min → vale metade também. É como um “quanto cumpri do que prometi”.
- Se estudou **mais** que a meta, **não ganha bônus** extra por isso: acima da meta conta como 100% nessa parte (o teto é cumprir o combinado).

**Pausas — o que o sistema considera “certo”**
- Para você organizar o descanso: pense em **~5 min por pausa**.
- O sistema imagina **cerca de 1 pausa a cada 1 hora** de estudo contínuo (ex.: 2 h focadas → em torno de **2 pausas** “no alvo”).
- Se o **número de pausas** ficar **bem diferente** desse ritmo (muito mais ou muito menos), ele **tira um pedaço** da nota **depois** de contar tempo e foco:
  - **quase no ideal** → não tira nada por pausa;
  - **um pouco fora** → tira **10%**;
  - **bem fora** → tira **40%**;
  - **muito fora** → tira **70%**.

**Pontuação (0 a 10):** junta foco, quanto cumpriu da meta de tempo e esse ajuste de pausas. **Nota máxima por sessão: 10**.

**Média “Sessão única” no diagnóstico** = média **aritmética** só das sessões desse método.

---

### Métricas que unem os dois métodos (diagnóstico)

- **Média de foco geral:** média dos níveis 1–5 de **todas** as sessões (Pomodoro e Sessão única).
- **Média de pontuação geral:** média das **pontuações finais** de cada sessão, **sem distinguir método**.  
  Como as fórmulas do Pomodoro e da Sessão única são diferentes, use essa média como **visão geral**, não para comparar número com número entre métodos.
- **Mínimo / máximo de foco:** menor e maior **nível de foco** visto no período (sempre entre **1** e **5** se houver dados).
- **Mínimo / máximo de pontuação:** menor e maior **pontuação de sessão** no período (o valor depende do método e dos parâmetros).

---

### Mensagem de feedback

O texto automático usa só a **média de foco geral** e faixas fixas (ex.: abaixo de 2, entre 2 e 3, … até “flow” acima de 4,5).
"""

st.set_page_config(page_title="Log de Foco e Produtividade", page_icon="🎯", layout="wide")
st.title("🎯 Log de Foco e Produtividade")
st.caption("Regras de pontuação, mínimos/máximos e médias: aba **Como funciona**.")
if "flash_msg" not in st.session_state:
    st.session_state["flash_msg"] = ""
if st.session_state["flash_msg"]:
    st.success(st.session_state["flash_msg"])
    st.session_state["flash_msg"] = ""
dia_ref = st.date_input("Dia de referência para testes", value=date.today())
dia_ref_str = dia_ref.strftime("%Y-%m-%d")
st.info(
    "Escolha de produto para facilitar testes: você pode definir manualmente o dia de referência "
    "e registrar sessões em datas passadas/futuras."
)

aba_registro, aba_diagnostico, aba_comparar, aba_ajuda = st.tabs(
    ["📝 Registrar Sessão", "📊 Diagnóstico", "⚖️ Comparar Sessões", "📖 Como funciona"]
)


# ── ABA 1: REGISTRAR SESSÃO ──────────────────────────────────────────────────

with aba_registro:
    st.subheader("Nova sessão de foco")

    status_dia = None
    resp_status = chamar_api(
        "GET",
        "/registro-foco/status-dia",
        params={"dia_referencia": dia_ref_str},
    )
    if resp_status is not None and resp_status.status_code == 200:
        status_dia = resp_status.json()

    metodo = st.radio(
        "Método",
        options=["pomodoro", "sessao_unica"],
        format_func=lambda m: "🍅 Pomodoro" if m == "pomodoro" else "🧱 Sessão Única",
        horizontal=True,
    )

    if metodo == "pomodoro":
        st.markdown("#### Plano Pomodoro do dia")
        colp1, colp2 = st.columns([2, 1])
        with colp1:
            total_sessoes_dia = st.number_input(
                "Quantas sessões Pomodoro você fará hoje?",
                min_value=1,
                max_value=20,
                value=3,
                step=1,
            )
        with colp2:
            st.write("")
            if st.button("💾 Salvar plano de hoje", use_container_width=True):
                resp_plano = chamar_api(
                    "POST",
                    "/pomodoro/plano",
                    json={"total_sessoes": int(total_sessoes_dia)},
                    params={"dia_referencia": dia_ref_str},
                )
                if resp_plano is not None:
                    if resp_plano.status_code == 200:
                        plano = resp_plano.json()
                        st.success(
                            f"Plano salvo: {plano['total_sessoes']} sessões para hoje "
                            f"({plano['sessoes_registradas']} registradas, {plano['sessoes_restantes']} restantes)."
                        )
                        st.rerun()
                    else:
                        st.error(f"Erro {resp_plano.status_code} ao salvar plano do dia.")

        if status_dia is None:
            st.caption("Não foi possível carregar o estado do dia (API).")
        elif status_dia.get("pomodoro"):
            p = status_dia["pomodoro"]
            st.info(
                f"Dia {status_dia['dia']}: {p['sessoes_registradas']}/{p['total_sessoes']} blocos "
                f"({p['sessoes_restantes']} restantes)."
            )
            if p["sessoes_restantes"] > 0:
                ord_atual = p["sessoes_registradas"] + 1
                st.success(f"Você está registrando a **{ord_atual}ª sessão do Pomodoro**.")
            else:
                st.warning(
                    "Plano Pomodoro do dia completo. Apague um registro no diagnóstico ou aumente o plano (Salvar)."
                )
        else:
            st.info(_MSG_PLANO_POMODORO_ANTES_BLOCOS)

    elif metodo == "sessao_unica":
        st.caption("No dia de referência só pode haver **uma** Sessão única (um bloco que representa o dia inteiro).")
        if status_dia and status_dia.get("sessao_unica_ja_registrada"):
            st.warning(
                "Já existe uma Sessão única neste dia. Apague-a no diagnóstico ou mude o **dia de referência**."
            )

    mostrar_formulario = False
    if status_dia is not None:
        if metodo == "sessao_unica":
            mostrar_formulario = not status_dia.get("sessao_unica_ja_registrada", False)
        else:
            pom = status_dia.get("pomodoro")
            if pom and pom.get("sessoes_restantes", 0) > 0:
                mostrar_formulario = True

    enviado = False
    if mostrar_formulario:
        with st.form("form_registro"):
            col1, col2 = st.columns(2)

            with col1:
                nivel_foco = st.slider(
                    "Nível de foco",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="1 = muito distraído · 5 = estado de flow",
                )
                tempo_minutos = st.number_input("Tempo real (minutos)", min_value=1, value=35)

            with col2:
                categoria = st.selectbox(
                    "Categoria",
                    ["", "coding", "estudo", "reuniao", "outro"],
                    format_func=lambda c: "— sem categoria —" if c == "" else c,
                )
                comentario = st.text_area(
                    "Comentário",
                    placeholder="O que foi feito ou causou distração?",
                    height=100,
                )

            st.divider()

            if metodo == "pomodoro":
                st.markdown("**Pausa após esta sessão**")
                tem_pausa = st.checkbox("Houve pausa após esta sessão?", value=True)
                tempo_pausa = st.number_input(
                    "Duração da pausa (minutos)",
                    min_value=0,
                    value=8,
                    disabled=not tem_pausa,
                )
            else:
                st.markdown("**Detalhes da Sessão Única**")
                with st.expander("Recomendações de tempo de sessão e de pausas", expanded=True):
                    st.markdown(
                        """
**Tempo — meta x tempo real (acima e ao lado)**  
Aceitos entre **30 min** e **12 h (720 min)**.

- **Não cumprir a meta:** se você planejou **mais** tempo do que de fato estudou, a nota **abaixa na mesma proporção** (ex.: meta 120 min e real 60 min → metade do “ganho” de tempo; é o “cumpri tanto % do combinado”).
- **Passar da meta:** estudar **além** do combinado **não aumenta** a nota por esse motivo — o máximo considerado aqui é ter cumprido **100%** da meta.

**Pausas — como a punição funciona (bem resumido)**  
Use **~5 min por pausa** só para se orientar no descanso.

- O app imagina **~1 pausa a cada 1 h** de foco (ex.: 2 h seguidas → por volta de **2 pausas** no ritmo “esperado”).
- Conta só o **número** de pausas, não os minutos de cada uma.
- Se você **pausou muito mais ou muito menos** que esse ritmo, ele **desconta** um % da nota **já** calculada com foco + tempo:
  - **quase no ritmo certo** → **0%** de desconto por pausa;
  - **um pouco fora** → **−10%**;
  - **bem fora** → **−40%**;
  - **muito fora** → **−70%**.
"""
                    )
                col3, col4 = st.columns(2)
                with col3:
                    meta_minutos = st.number_input("Meta planejada (minutos)", min_value=30, max_value=720, value=120)
                with col4:
                    qtd_pausas = st.number_input(
                        "Quantidade de pausas realizadas",
                        min_value=0,
                        value=2,
                        help="~5 min por pausa para você planejar. O sistema compara quantas pausas fez vs ~1 por hora de estudo.",
                    )

            enviado = st.form_submit_button("✅ Registrar sessão", use_container_width=True)
    elif metodo == "sessao_unica" and status_dia is not None and status_dia.get("sessao_unica_ja_registrada"):
        pass
    elif status_dia is None:
        st.warning("Sem estado do dia: corrija a API e recarregue para registrar.")

    if enviado:
        if not comentario.strip():
            st.error("O comentário não pode estar vazio.")
        else:
            payload = {
                "metodo": metodo,
                "nivel_foco": nivel_foco,
                "tempo_minutos": int(tempo_minutos),
                "comentario": comentario,
            }
            if categoria:
                payload["categoria"] = categoria

            if metodo == "pomodoro":
                payload["tempo_pausa_minutos"] = int(tempo_pausa) if tem_pausa else None
            else:
                payload["meta_minutos"] = int(meta_minutos)
                payload["qtd_pausas"] = int(qtd_pausas)

            resp = chamar_api(
                "POST",
                "/registro-foco",
                json=payload,
                params={"dia_referencia": dia_ref_str},
            )
            if resp is None:
                pass  # erro de conexão já foi mostrado
            elif resp.status_code == 201:
                dados = resp.json()
                st.success("Sessão registrada com sucesso!")

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Pontuação", f"{dados['pontuacao']:.2f}")
                col_b.metric("Nível de foco", dados["nivel_foco"])
                if dados.get("peso"):
                    col_c.metric("Peso da sessão", dados["peso"])

                if dados.get("penalidades_aplicadas"):
                    st.warning("Penalidades aplicadas: " + ", ".join(dados["penalidades_aplicadas"]))
                if dados.get("aviso"):
                    st.info(f"⚠️ {dados['aviso']}")
                if metodo == "pomodoro":
                    st.session_state["flash_msg"] = (
                        "Sessão registrada com sucesso! Progresso do plano atualizado."
                    )
                else:
                    st.session_state["flash_msg"] = "Sessão única registrada para este dia."
                st.rerun()
            else:
                try:
                    detalhe = resp.json()
                    erros = detalhe.get("detail", resp.text) if isinstance(detalhe, dict) else str(detalhe)
                except ValueError:
                    erros = resp.text or f"Erro HTTP {resp.status_code}"
                st.error(f"Erro {resp.status_code}: {erros}")


# ── ABA 2: DIAGNÓSTICO ───────────────────────────────────────────────────────

with aba_diagnostico:
    st.subheader("Diagnóstico de produtividade")

    hoje = date.today()
    anos = list(range(hoje.year - 6, hoje.year + 2))
    default_ano_idx = anos.index(hoje.year) if hoje.year in anos else len(anos) - 1

    periodo = st.radio(
        "Período do diagnóstico",
        options=["todos", "mes"],
        format_func=lambda x: "Todos os registros" if x == "todos" else "Filtrar por mês e ano",
        horizontal=True,
        help="Para filtrar, escolha apenas o mês civil e o ano — sem dia.",
    )

    col_m, col_y, col_btn = st.columns([1, 1, 1])
    with col_m:
        mes_num = st.selectbox(
            "Mês",
            options=list(range(1, 13)),
            format_func=lambda m: _MESES_PT[m - 1],
            index=hoje.month - 1,
            disabled=(periodo == "todos"),
        )
    with col_y:
        ano_num = st.selectbox(
            "Ano",
            options=anos,
            index=default_ano_idx,
            disabled=(periodo == "todos"),
        )
    with col_btn:
        st.write("")
        buscar = st.button("🔍 Buscar", use_container_width=True)

    params = {}
    if periodo == "mes":
        params["mes"] = f"{ano_num:04d}-{mes_num:02d}"

    if buscar:
        resp = chamar_api("GET", "/diagnostico-produtividade", params=params or None)
        if resp is not None:
            if resp.status_code == 200:
                st.session_state["diag_dados"] = resp.json()
                st.session_state["diag_query"] = dict(params)
            else:
                try:
                    det = resp.json()
                    msg = det.get("detail", resp.text) if isinstance(det, dict) else str(det)
                except ValueError:
                    msg = resp.text or ""
                st.error(f"Diagnóstico indisponível (HTTP {resp.status_code}): {msg}")

    dados = st.session_state.get("diag_dados")
    if dados is None:
        st.caption("Clique em **Buscar** para carregar o diagnóstico e poder apagar registros.")
    else:
        feedback = dados["mensagem_feedback"]
        media = dados["media_foco_geral"]
        total = dados.get("total_sessoes", 0)

        if total == 0:
            st.info(feedback)
        elif media < 3.0:
            st.error(f"😔 {feedback}")
        elif media < 4.0:
            st.warning(f"🙂 {feedback}")
        else:
            st.success(f"🚀 {feedback}")

        st.divider()

        if total > 0:
            st.markdown("#### Visão geral (todos os métodos)")
            g1, g2, g3 = st.columns(3)
            g1.metric("Sessões no período", total)
            g2.metric("Tempo total estudado", f"{dados['tempo_total_minutos']} min")
            g3.metric(
                "Média de pontuação (todas as sessões)",
                f"{dados.get('media_pontuacao_geral', 0):.2f}",
                help="Média aritmética da pontuação final de cada sessão; mistura Pomodoro e Sessão única.",
            )
            st.caption(
                "A média de pontuação geral junta métodos com fórmulas diferentes — use para ver o “ritmo” geral, "
                "não para comparar diretamente com a média ponderada só do Pomodoro."
            )

            st.markdown("##### Foco (autoavaliação 1–5)")
            f1, f2, f3 = st.columns(3)
            f1.metric("Média", f"{media:.2f} / 5")
            f2.metric("Mínimo", dados.get("foco_min", 0))
            f3.metric("Máximo", dados.get("foco_max", 0))

            st.markdown("##### Pontuação por sessão (valores observados no período)")
            p1, p2 = st.columns(2)
            p1.metric("Menor pontuação", f"{dados.get('pontuacao_min', 0):.2f}")
            p2.metric("Maior pontuação", f"{dados.get('pontuacao_max', 0):.2f}")

        else:
            st.metric("Tempo total", f"{dados['tempo_total_minutos']} min")

        pom = dados["pomodoro"]
        su = dados["sessao_unica"]

        if pom["total_sessoes"] > 0:
            st.markdown("#### 🍅 Pomodoro")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Sessões de Pomodoro", pom["total_sessoes"])
            c2.metric("Blocos registrados", pom.get("blocos_registrados", pom["total_sessoes"]))
            c3.metric("Blocos válidos", pom["sessoes_validas"])
            c4.metric("Média ponderada", f"{pom['media_ponderada']:.2f}")

        if su["total_sessoes"] > 0:
            st.markdown("#### 🧱 Sessão Única")
            c1, c2 = st.columns(2)
            c1.metric("Sessões", su["total_sessoes"])
            c2.metric("Média de pontuação", f"{su['media_pontuacao']:.2f}")

        linhas = dados.get("sessoes_no_periodo") or []
        if linhas:
            st.markdown("#### 📋 Sessões neste período")
            df = pd.DataFrame(linhas)
            df = df.rename(
                columns={
                    "id": "ID",
                    "dia": "Dia",
                    "metodo": "Método",
                    "nivel_foco": "Foco",
                    "tempo_minutos": "Min",
                    "pontuacao": "Pontuação",
                    "comentario": "Comentário",
                }
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

        if pom["total_sessoes"] == 0 and su["total_sessoes"] == 0:
            st.caption("Nenhuma sessão encontrada para o período selecionado.")

        st.divider()
        st.markdown("#### 🗑️ Gerenciar registros")
        if linhas:
            ids = [int(r["id"]) for r in linhas]
            id_apagar = st.selectbox("Apagar registro por ID", ids, key="diag_delete_id")
            if st.button("Apagar registro selecionado", key="diag_delete_btn"):
                rid = int(id_apagar)
                resp_del = chamar_api("DELETE", f"/registros/{rid}")
                if resp_del is not None:
                    if resp_del.status_code == 200:
                        _recarregar_diagnostico()
                        st.success(f"Registro {rid} apagado.")
                        st.rerun()
                    else:
                        st.error(f"Erro {resp_del.status_code} ao apagar registro.")
        if st.button("Apagar TODOS os registros", key="diag_delete_all_btn"):
            resp_del_all = chamar_api("DELETE", "/registros")
            if resp_del_all is not None:
                if resp_del_all.status_code == 200:
                    _recarregar_diagnostico()
                    st.success("Todos os registros foram apagados.")
                    st.rerun()
                else:
                    st.error(f"Erro {resp_del_all.status_code} ao apagar todos os registros.")


# ── ABA 3: COMPARAR SESSÕES ──────────────────────────────────────────────────

with aba_comparar:
    st.subheader("Comparar duas sessões")
    st.caption(
        "Selecione duas sessões e veja, em percentual, se a primeira foi melhor ou pior que a segunda."
    )

    hoje = date.today()
    anos = list(range(hoje.year - 6, hoje.year + 2))
    default_ano_idx = anos.index(hoje.year) if hoje.year in anos else len(anos) - 1

    periodo_cmp = st.radio(
        "Período para buscar sessões",
        options=["todos", "mes"],
        format_func=lambda x: "Todos os registros" if x == "todos" else "Filtrar por mês e ano",
        horizontal=True,
        key="cmp_periodo",
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        mes_cmp = st.selectbox(
            "Mês",
            options=list(range(1, 13)),
            format_func=lambda m: _MESES_PT[m - 1],
            index=hoje.month - 1,
            disabled=(periodo_cmp == "todos"),
            key="cmp_mes",
        )
    with c2:
        ano_cmp = st.selectbox(
            "Ano",
            options=anos,
            index=default_ano_idx,
            disabled=(periodo_cmp == "todos"),
            key="cmp_ano",
        )
    with c3:
        st.write("")
        buscar_cmp = st.button("🔍 Carregar sessões", use_container_width=True, key="cmp_buscar")

    if buscar_cmp:
        params_cmp = {}
        if periodo_cmp == "mes":
            params_cmp["mes"] = f"{ano_cmp:04d}-{mes_cmp:02d}"
        st.session_state["cmp_params"] = params_cmp

    params_cmp = st.session_state.get("cmp_params", {})

    resp_cmp = chamar_api("GET", "/diagnostico-produtividade", params=params_cmp)
    if resp_cmp is None:
        linhas = []
    elif resp_cmp.status_code != 200:
        st.error(f"Erro {resp_cmp.status_code} ao buscar sessões para comparação.")
        linhas = []
    else:
        linhas = resp_cmp.json().get("sessoes_no_periodo") or []

    if linhas and len(linhas) < 2:
        st.info("É preciso ter pelo menos 2 sessões no período selecionado para comparar.")
    elif linhas:
        opcoes = {
            f"ID {s['id']} • {s['dia']} • {s['metodo']} • nota {s['pontuacao']:.2f}": s
            for s in linhas
        }
        labels = list(opcoes.keys())

        col_a, col_b = st.columns(2)
        with col_a:
            escolha_a = st.selectbox("Primeira sessão", labels, key="cmp_sessao_a")
        with col_b:
            idx_b = 1 if len(labels) > 1 else 0
            escolha_b = st.selectbox("Segunda sessão", labels, index=idx_b, key="cmp_sessao_b")

        sessao_a = opcoes[escolha_a]
        sessao_b = opcoes[escolha_b]

        if sessao_a["id"] == sessao_b["id"]:
            st.warning("Escolha duas sessões diferentes para comparar.")
        else:
            nota_a = float(sessao_a["pontuacao"])
            nota_b = float(sessao_b["pontuacao"])
            delta = nota_a - nota_b

            m1, m2, m3 = st.columns(3)
            m1.metric("Nota sessão A", f"{nota_a:.2f}")
            m2.metric("Nota sessão B", f"{nota_b:.2f}")
            m3.metric("Diferença absoluta", f"{delta:+.2f}")

            if nota_b == 0:
                if nota_a == 0:
                    st.info("As duas sessões ficaram com nota 0. Não há variação percentual.")
                else:
                    st.info(
                        "A sessão B tem nota 0, então não dá para calcular percentual relativo com segurança."
                    )
            else:
                variacao_pct = (delta / nota_b) * 100
                if variacao_pct > 0:
                    st.success(f"A primeira sessão foi **{variacao_pct:.1f}% melhor** que a segunda.")
                elif variacao_pct < 0:
                    st.error(f"A primeira sessão foi **{abs(variacao_pct):.1f}% pior** que a segunda.")
                else:
                    st.info("As duas sessões tiveram a mesma pontuação final.")


# ── ABA 4: COMO FUNCIONA ─────────────────────────────────────────────────────

with aba_ajuda:
    st.markdown(COMO_FUNCIONA)
