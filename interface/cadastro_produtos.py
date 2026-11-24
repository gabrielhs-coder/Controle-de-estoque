import tkinter as tk
from tkinter import messagebox, ttk
from banco.produtos import atualizar_produto, buscar_produto_por_codigo, cadastrar_produto
from utilitarios.validacoes import (
    validar_categoria,
    validar_codigo,
    validar_nome,
    validar_preco,
    validar_quantidade_inteira,
)


class CadastroProdutosFrame(ttk.Frame):
    def __init__(self, parent, on_dados_alterados=None):
        super().__init__(parent, padding=20)
        self.on_dados_alterados = on_dados_alterados
        self._construir_interface()

    def _construir_interface(self):
        ttk.Label(
            self,
            text="Cadastro e Edição de Produtos",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        form = ttk.LabelFrame(self, text="Dados do Produto", padding=15)
        form.pack(fill="x", anchor="n")

        # Código
        ttk.Label(form, text="Código:").grid(row=0, column=0, sticky="w", padx=5, pady=6)
        self.ent_codigo = ttk.Entry(form, width=25)
        self.ent_codigo.grid(row=0, column=1, sticky="w", padx=5, pady=6)
        ttk.Button(form, text="Buscar", command=self._buscar_produto).grid(
            row=0, column=2, sticky="w", padx=5, pady=6
        )

        # Nome
        ttk.Label(form, text="Nome:").grid(row=1, column=0, sticky="w", padx=5, pady=6)
        self.ent_nome = ttk.Entry(form, width=40)
        self.ent_nome.grid(row=1, column=1, columnspan=2, sticky="we", padx=5, pady=6)

        # Categoria
        ttk.Label(form, text="Categoria:").grid(row=2, column=0, sticky="w", padx=5, pady=6)
        self.ent_categoria = ttk.Entry(form, width=30)
        self.ent_categoria.grid(row=2, column=1, sticky="w", padx=5, pady=6)

        # Preço
        ttk.Label(form, text="Preço (R$):").grid(row=3, column=0, sticky="w", padx=5, pady=6)
        self.ent_preco = ttk.Entry(form, width=20)
        self.ent_preco.grid(row=3, column=1, sticky="w", padx=5, pady=6)

        # Quantidade inicial
        ttk.Label(form, text="Quantidade Inicial:").grid(row=4, column=0, sticky="w", padx=5, pady=6)
        self.ent_quantidade = ttk.Entry(form, width=20)
        self.ent_quantidade.insert(0, "0")
        self.ent_quantidade.grid(row=4, column=1, sticky="w", padx=5, pady=6)

        # Estoque mínimo
        ttk.Label(form, text="Estoque Mínimo:").grid(row=5, column=0, sticky="w", padx=5, pady=6)
        self.ent_estoque_min = ttk.Entry(form, width=20)
        self.ent_estoque_min.insert(0, "5")
        self.ent_estoque_min.grid(row=5, column=1, sticky="w", padx=5, pady=6)

        # Botões
        botoes = ttk.Frame(self, padding=(0, 15))
        botoes.pack(fill="x")

        ttk.Button(botoes, text="Salvar Novo Produto", command=self._salvar_novo).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(botoes, text="Atualizar Existente", command=self._atualizar_existente).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(botoes, text="Limpar Campos", command=self._limpar_campos).pack(side="left")

    def _buscar_produto(self):
        ok_cod, res_cod = validar_codigo(self.ent_codigo.get())
        if not ok_cod:
            messagebox.showwarning("Atenção", res_cod)
            return

        produto = buscar_produto_por_codigo(res_cod)
        if not produto:
            messagebox.showinfo("Não encontrado", f"Nenhum produto encontrado com o código '{res_cod}'.")
            return

        codigo, nome, categoria, preco, quantidade, est_min = produto
        self.ent_codigo.delete(0, tk.END)
        self.ent_codigo.insert(0, codigo)

        self.ent_nome.delete(0, tk.END)
        self.ent_nome.insert(0, nome)

        self.ent_categoria.delete(0, tk.END)
        self.ent_categoria.insert(0, categoria or "")

        self.ent_preco.delete(0, tk.END)
        self.ent_preco.insert(0, f"{preco:.2f}")

        self.ent_quantidade.delete(0, tk.END)
        self.ent_quantidade.insert(0, str(quantidade))
        self.ent_quantidade.config(state="disabled")

        self.ent_estoque_min.delete(0, tk.END)
        self.ent_estoque_min.insert(0, str(est_min))

    def _salvar_novo(self):
        ok_cod, codigo = validar_codigo(self.ent_codigo.get())
        if not ok_cod:
            messagebox.showwarning("Validação", codigo)
            return

        ok_nome, nome = validar_nome(self.ent_nome.get())
        if not ok_nome:
            messagebox.showwarning("Validação", nome)
            return

        _, categoria = validar_categoria(self.ent_categoria.get())

        ok_preco, preco = validar_preco(self.ent_preco.get())
        if not ok_preco:
            messagebox.showwarning("Validação", preco)
            return

        ok_qtd, quantidade = validar_quantidade_inteira(self.ent_quantidade.get(), permitir_zero=True)
        if not ok_qtd:
            messagebox.showwarning("Validação", quantidade)
            return

        ok_min, est_min = validar_quantidade_inteira(self.ent_estoque_min.get(), permitir_zero=True)
        if not ok_min:
            messagebox.showwarning("Validação", est_min)
            return

        sucesso, mensagem = cadastrar_produto(
            codigo=codigo,
            nome=nome,
            categoria=categoria,
            preco=preco,
            quantidade=quantidade,
            estoque_minimo=est_min,
        )
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_campos()
            if self.on_dados_alterados:
                self.on_dados_alterados()
        else:
            messagebox.showerror("Erro", mensagem)

    def _atualizar_existente(self):
        ok_cod, codigo = validar_codigo(self.ent_codigo.get())
        if not ok_cod:
            messagebox.showwarning("Validação", codigo)
            return

        ok_nome, nome = validar_nome(self.ent_nome.get())
        if not ok_nome:
            messagebox.showwarning("Validação", nome)
            return

        _, categoria = validar_categoria(self.ent_categoria.get())

        ok_preco, preco = validar_preco(self.ent_preco.get())
        if not ok_preco:
            messagebox.showwarning("Validação", preco)
            return

        ok_min, est_min = validar_quantidade_inteira(self.ent_estoque_min.get(), permitir_zero=True)
        if not ok_min:
            messagebox.showwarning("Validação", est_min)
            return

        sucesso, mensagem = atualizar_produto(
            codigo=codigo,
            nome=nome,
            categoria=categoria,
            preco=preco,
            estoque_minimo=est_min,
        )
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._limpar_campos()
            if self.on_dados_alterados:
                self.on_dados_alterados()
        else:
            messagebox.showerror("Erro", mensagem)

    def _limpar_campos(self):
        self.ent_quantidade.config(state="normal")
        for campo in (self.ent_codigo, self.ent_nome, self.ent_categoria, self.ent_preco):
            campo.delete(0, tk.END)
        self.ent_quantidade.delete(0, tk.END)
        self.ent_quantidade.insert(0, "0")
        self.ent_estoque_min.delete(0, tk.END)
        self.ent_estoque_min.insert(0, "5")