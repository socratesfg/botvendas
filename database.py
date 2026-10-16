import sqlite3

DB_NAME = "bot_vendas.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            produto TEXT NOT NULL,
            valor REAL NOT NULL,
            txid TEXT UNIQUE,
            status TEXT DEFAULT 'pendente',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def criar_pedido(user_id: int, produto: str, valor: float, txid: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pedidos (user_id, produto, valor, txid, status)
        VALUES (?, ?, ?, ?, 'pendente')
    """,
        (user_id, produto, valor, txid),
    )
    conn.commit()
    conn.close()


def buscar_pedido_por_txid(txid: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE txid = ?", (txid,))
    pedido = cursor.fetchone()
    conn.close()
    return pedido


def atualizar_status_pedido(txid: str, novo_status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE pedidos SET status = ? WHERE txid = ?
    """,
        (novo_status, txid),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")