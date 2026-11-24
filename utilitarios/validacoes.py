def validar_codigo(codigo: str) -> tuple[bool, str]:
    codigo_limpo = codigo.strip()
    if not codigo_limpo:
        return False, "O código do produto é obrigatório."
    if len(codigo_limpo) < 2:
        return False, "O código deve ter pelo menos 2 caracteres."
    return True, codigo_limpo.upper()


def validar_nome(nome: str) -> tuple[bool, str]:
    nome_limpo = nome.strip()
    if not nome_limpo:
        return False, "O nome do produto é obrigatório."
    return True, nome_limpo


def validar_categoria(categoria: str) -> tuple[bool, str]:
    cat_limpa = categoria.strip()
    return True, cat_limpa if cat_limpa else "Geral"


def validar_preco(preco_str: str) -> tuple[bool, float | str]:
    try:
        valor = float(preco_str.replace(",", ".").strip())
        if valor < 0:
            return False, "O preço não pode ser negativo."
        return True, round(valor, 2)
    except ValueError:
        return False, "Preço inválido. Informe um número válido (ex.: 29.90)."


def validar_quantidade_inteira(qtd_str: str, permitir_zero: bool = False) -> tuple[bool, int | str]:
    try:
        qtd = int(qtd_str.strip())
        if permitir_zero and qtd < 0:
            return False, "A quantidade não pode ser negativa."
        if not permitir_zero and qtd <= 0:
            return False, "A quantidade deve ser maior que zero."
        return True, qtd
    except ValueError:
        return False, "Quantidade inválida. Informe um número inteiro."