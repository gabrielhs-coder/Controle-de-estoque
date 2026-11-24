import sqlite3
from banco.conexao import obter_conexao


def cadastrar_produto(
    codigo: str,
    nome: str,
    categoria: str,
    preco: float,
    quantidade: int = 0,
    estoque_minimo: int = 5,
) -> tuple[bool, str]:
    conn = obter_conexao()
    try:
        conn.execute(
            """
            INSERT INTO produtos (codigo, nome, categoria, preco, quantidade, estoque_minimo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (codigo, nome, categoria, preco, quantidade, estoque_minimo),
        )
        conn.commit()
        return True, f"Produto '{nome}' ({codigo}) cadastrado com sucesso!"
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc) or "PRIMARY KEY" in str(exc):
            return False, f"Já existe um produto cadastrado com o código '{codigo}'."
        return False, f"Erro de integridade no banco: {exc}"
    except sqlite3.Error as exc:
        return False, f"Erro ao cadastrar produto: {exc}"
    finally:
        conn.close()


def buscar_produto_por_codigo(codigo: str) -> tuple | None:
    conn = obter_conexao()
    try:
        cursor = conn.execute(
            """
            SELECT codigo, nome, categoria, preco, quantidade, estoque_minimo
            FROM produtos
            WHERE codigo = ?
            """,
            (codigo.strip().upper(),),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def listar_produtos(categoria: str | None = None) -> list[tuple]:
    conn = obter_conexao()
    try:
        if categoria and categoria != "Todas":
            cursor = conn.execute(
                """
                SELECT codigo, nome, categoria, preco, quantidade, estoque_minimo
                FROM produtos
                WHERE categoria = ?
                ORDER BY nome ASC
                """,
                (categoria,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT codigo, nome, categoria, preco, quantidade, estoque_minimo
                FROM produtos
                ORDER BY nome ASC
                """
            )
        return cursor.fetchall()
    finally:
        conn.close()


def listar_categorias() -> list[str]:
    conn = obter_conexao()
    try:
        cursor = conn.execute(
            """
            SELECT DISTINCT categoria
            FROM produtos
            WHERE categoria IS NOT NULL AND TRIM(categoria) != ''
            ORDER BY categoria ASC
            """
        )
        return [linha[0] for linha in cursor.fetchall()]
    finally:
        conn.close()


def listar_produtos_estoque_baixo() -> list[tuple]:
    conn = obter_conexao()
    try:
        cursor = conn.execute(
            """
            SELECT codigo, nome, categoria, preco, quantidade, estoque_minimo
            FROM produtos
            WHERE quantidade <= estoque_minimo
            ORDER BY quantidade ASC, nome ASC
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


def calcular_valor_total_estoque(categoria: str | None = None) -> float:
    produtos = listar_produtos(categoria=categoria)
    return sum(float(prod[3]) * int(prod[4]) for prod in produtos)


def atualizar_produto(
    codigo: str,
    nome: str,
    categoria: str,
    preco: float,
    estoque_minimo: int,
) -> tuple[bool, str]:
    conn = obter_conexao()
    try:
        cursor = conn.execute(
            """
            UPDATE produtos
            SET nome = ?, categoria = ?, preco = ?, estoque_minimo = ?
            WHERE codigo = ?
            """,
            (nome, categoria, preco, estoque_minimo, codigo),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, f"Produto '{codigo}' não encontrado."
        return True, f"Produto '{codigo}' atualizado com sucesso!"
    except sqlite3.Error as exc:
        return False, f"Erro ao atualizar produto: {exc}"
    finally:
        conn.close()


def excluir_produto(codigo: str) -> tuple[bool, str]:
    conn = obter_conexao()
    try:
        cursor = conn.execute("DELETE FROM produtos WHERE codigo = ?", (codigo,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, f"Produto '{codigo}' não encontrado."
        return True, f"Produto '{codigo}' removido com sucesso."
    except sqlite3.IntegrityError:
        return (
            False,
            "Não é possível excluir um produto que já possui movimentações registradas.",
        )
    except sqlite3.Error as exc:
        return False, f"Erro ao excluir produto: {exc}"
    finally:
        conn.close()