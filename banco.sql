PRAGMA foreign_keys = ON;

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

-- Trigger opcional: atualiza automaticamente a quantidade na tabela produtos
CREATE TRIGGER IF NOT EXISTS trg_atualizar_estoque_apos_movimentacao
AFTER INSERT ON movimentacoes
BEGIN
    UPDATE produtos
    SET quantidade = CASE
        WHEN NEW.tipo = 'entrada' THEN quantidade + NEW.quantidade
        WHEN NEW.tipo = 'saida' THEN quantidade - NEW.quantidade
    END
    WHERE codigo = NEW.produto_codigo;
END;