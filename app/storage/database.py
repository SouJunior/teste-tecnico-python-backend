import json
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "data" / "produtividade.db"

# Colunas opcionais por método: preenchidas com NULL quando o registro não as
# possui, para que o INSERT parametrizado não exploda por chave ausente.
_COLUNAS_OPCIONAIS = (
    "categoria",
    "tempo_pausa_minutos",
    "meta_minutos",
    "qtd_pausas",
    "peso",
    "aviso",
)


def inicializar() -> None:
    """Cria o banco e as tabelas se ainda não existirem."""
    DB_PATH.parent.mkdir(exist_ok=True)
    with _conectar() as conn:
        # Observação: `criado_em` guarda apenas a DATA (YYYY-MM-DD), não um timestamp.
        # É o "dia de referência" do registro, escolhido pelo cliente ou padrão = hoje.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                metodo                TEXT    NOT NULL,
                nivel_foco            INTEGER NOT NULL,
                tempo_minutos         INTEGER NOT NULL,
                comentario            TEXT    NOT NULL,
                categoria             TEXT,
                tempo_pausa_minutos   INTEGER,
                meta_minutos          INTEGER,
                qtd_pausas            INTEGER,
                pontuacao             REAL    NOT NULL,
                peso                  INTEGER,
                penalidades_aplicadas TEXT    NOT NULL,
                aviso                 TEXT,
                criado_em             TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_planos (
                dia            TEXT PRIMARY KEY,
                total_sessoes  INTEGER NOT NULL
            )
        """)


def insert(registro: dict) -> dict:
    """Persiste um registro e devolve-o com o `id` gerado."""
    payload = dict(registro)
    for col in _COLUNAS_OPCIONAIS:
        payload.setdefault(col, None)
    payload["penalidades_aplicadas"] = json.dumps(payload["penalidades_aplicadas"])

    with _conectar() as conn:
        cursor = conn.execute(
            """
            INSERT INTO registros (
                metodo, nivel_foco, tempo_minutos, comentario, categoria,
                tempo_pausa_minutos, meta_minutos, qtd_pausas,
                pontuacao, peso, penalidades_aplicadas, aviso, criado_em
            ) VALUES (
                :metodo, :nivel_foco, :tempo_minutos, :comentario, :categoria,
                :tempo_pausa_minutos, :meta_minutos, :qtd_pausas,
                :pontuacao, :peso, :penalidades_aplicadas, :aviso, :criado_em
            )
            """,
            payload,
        )
        registro["id"] = cursor.lastrowid

    return registro


def get_all(mes: Optional[str] = None) -> list[dict]:
    """Retorna todos os registros. Se `mes` for informado (YYYY-MM), filtra pelo mês civil."""
    with _conectar() as conn:
        if mes:
            rows = conn.execute(
                """
                SELECT * FROM registros
                WHERE strftime('%Y-%m', criado_em) = ?
                ORDER BY criado_em
                """,
                (mes,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM registros ORDER BY criado_em").fetchall()

    return [_row_to_dict(row) for row in rows]


def contar_registros_no_dia(metodo: str, dia: str) -> int:
    """Quantos registros existem no dia (`YYYY-MM-DD`) para o método dado."""
    with _conectar() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS qtd FROM registros WHERE metodo = ? AND DATE(criado_em) = ?",
            (metodo, dia),
        ).fetchone()
    return int(row["qtd"]) if row else 0


def definir_plano_pomodoro(dia: str, total_sessoes: int) -> dict:
    """Cria ou atualiza o plano Pomodoro de um dia (`YYYY-MM-DD`)."""
    with _conectar() as conn:
        conn.execute(
            """
            INSERT INTO pomodoro_planos (dia, total_sessoes)
            VALUES (?, ?)
            ON CONFLICT(dia) DO UPDATE SET total_sessoes = excluded.total_sessoes
            """,
            (dia, total_sessoes),
        )
    return {"dia": dia, "total_sessoes": total_sessoes}


def obter_plano_pomodoro(dia: str) -> Optional[dict]:
    with _conectar() as conn:
        row = conn.execute(
            "SELECT dia, total_sessoes FROM pomodoro_planos WHERE dia = ?",
            (dia,),
        ).fetchone()
    return dict(row) if row else None


def delete_registro(registro_id: int) -> bool:
    with _conectar() as conn:
        cur = conn.execute("DELETE FROM registros WHERE id = ?", (registro_id,))
    return cur.rowcount > 0


def clear_all() -> None:
    with _conectar() as conn:
        conn.execute("DELETE FROM registros")
        conn.execute("DELETE FROM pomodoro_planos")


def _conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["penalidades_aplicadas"] = json.loads(d["penalidades_aplicadas"])
    return d
