import sqlite3
from banco.conexao import obter_conexao


def registrar_movimentacao(
    produto_codigo: str,
    tipo: str,
    quantidade: int,
) -> tuple[bool, str]:
    tipo_normalizado = tipo.strip().lower()
    if tipo_normalizado not in ("entrada", "saida"):
        return False, "Tipo de movimentação inválido. Use 'entrada' ou 'saida'."

    if quantidade <= 0:
        return False, "A quantidade da movimentação deve ser maior que zero."

    conn = obter_conexao()
    try:
        cursor = conn.execute(
            "SELECT nome, quantidade FROM produtos WHERE codigo = ?",
            (produto_codigo,),
        )
        produto = cursor.fetchone()
        if not produto:
            return False, f"Produto com código '{produto_codigo}' não encontrado."

        nome_produto, qtd_atual = produto
        if tipo_normalizado == "saida" and quantidade > qtd_atual:
            return (
                False,
                f"Estoque insuficiente para '{nome_produto}'. Disponível: {qtd_atual} | Solicitado: {quantidade}.",
            )

        # A trigger no SQLite atualiza automaticamente a tabela produtos ao inserir
        conn.execute(
            """
            INSERT INTO movimentacoes (produto_codigo, tipo, quantidade)
            VALUES (?, ?, ?)
            """,
            (produto_codigo, tipo_normalizado, quantidade),
        )
        conn.commit()

        nova_qtd = qtd_atual + quantidade if tipo_normalizado == "entrada" else qtd_atual - quantidade
        acao = "Entrada" if tipo_normalizado == "entrada" else "Saída"
        return True, f"{acao} de {quantidade} un. registrada para '{nome_produto}'. Novo saldo: {nova_qtd}."
    except sqlite3.Error as exc:
        conn.rollback()
        return False, f"Erro ao registrar movimentação: {exc}"
    finally:
        conn.close()


def listar_movimentacoes(produto_codigo: str | None = None) -> list[tuple]:
    conn = obter_conexao()
    try:
        if produto_codigo and produto_codigo.strip():
            cursor = conn.execute(
                """
                SELECT m.id, m.produto_codigo, p.nome, m.tipo, m.quantidade, m.data
                FROM movimentacoes m
                LEFT JOIN produtos p ON p.codigo = m.produto_codigo
                WHERE m.produto_codigo = ?
                ORDER BY m.data DESC, m.id DESC
                """,
                (produto_codigo.strip().upper(),),
            )
        else:
            cursor = conn.execute(
                """
                SELECT m.id, m.produto_codigo, p.nome, m.tipo, m.quantidade, m.data
                FROM movimentacoes m
                LEFT JOIN produtos p ON p.codigo = m.produto_codigo
                ORDER BY m.data DESC, m.id DESC
                """
            )
        return cursor.fetchall()
    finally:
        conn.close()