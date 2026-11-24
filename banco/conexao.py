import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "estoque.db"
SQL_SCRIPT_PATH = BASE_DIR / "banco.sql"


def obter_conexao() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_banco() -> None:
    conn = obter_conexao()
    try:
        if SQL_SCRIPT_PATH.exists():
            script_sql = SQL_SCRIPT_PATH.read_text(encoding="utf-8")
            conn.executescript(script_sql)
        else:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS produtos (
                    codigo TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    categoria TEXT,
                    preco REAL NOT NULL CHECK(preco >= 0),
                    quantidade INTEGER DEFAULT 0 CHECK(quantidade >= 0),
                    estoque_minimo INTEGER DEFAULT 5 CHECK(estoque_minimo >= 0)
                );

                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_codigo TEXT NOT NULL,
                    tipo TEXT CHECK(tipo IN ('entrada', 'saida')) NOT NULL,
                    quantidade INTEGER NOT NULL CHECK(quantidade > 0),
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (produto_codigo) REFERENCES produtos(codigo) ON DELETE RESTRICT
                );
                """
            )
        conn.commit()
    finally:
        conn.close()