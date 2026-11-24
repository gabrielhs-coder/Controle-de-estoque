import tkinter as tk
from tkinter import messagebox, ttk
from banco.movimentacoes import listar_movimentacoes, registrar_movimentacao
from banco.produtos import listar_produtos
from utilitarios.validacoes import validar_quantidade_inteira


class RegistroMovimentacaoFrame(ttk.Frame):
    def __init__(self, parent, on_dados_alterados=None):
        super().__init__(parent, padding=20)
        self.on_dados_alterados = on_dados_alterados
        self.mapa_produtos = {}
        self._construir_interface()
        self.atualizar_dados()

    def _construir_interface(self):
        ttk.Label(
            self,
            text="Registro de Entradas e Saídas",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        painel = ttk.LabelFrame(self, text="Nova Movimentação", padding=15)
        painel.pack(fill="x")

        # Seleção de produto
        ttk.Label(painel, text="Produto:").grid(row=0, column=0, sticky="w", padx=5, pady=6)
        self.cmb_produto = ttk.Combobox(painel, width=48, state="readonly")
        self.cmb_produto.grid(row=0, column=1, sticky="w", padx=5, pady=6)
        self.cmb_produto.bind("<<ComboboxSelected>>", self._ao_selecionar_produto)

        self.lbl_saldo_atual = ttk.Label(painel, text="Saldo atual: -")
        self.lbl_saldo_atual.grid(row=0, column=2, sticky="w", padx=10, pady=6)

        # Tipo de movimentação
        ttk.Label(painel, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5, pady=6)
        self.cmb_tipo = ttk.Combobox(painel, values=["entrada", "saida"], width=20, state="readonly")
        self.cmb_tipo.set("entrada")
        self.cmb_tipo.grid(row=1, column=1, sticky="w", padx=5, pady=6)

        # Quantidade
        ttk.Label(painel, text="Quantidade:").grid(row=2, column=0, sticky="w", padx=5, pady=6)
        self.ent_quantidade = ttk.Entry(painel, width=20)
        self.ent_quantidade.grid(row=2, column=1, sticky="w", padx=5, pady=6)

        ttk.Button(painel, text="Registrar Movimentação", command=self._registrar).grid(
            row=3, column=1, sticky="w", padx=5, pady=12
        )

        # Histórico recente
        ttk.Label(
            self,
            text="Histórico de Movimentações",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(18, 6))

        colunas = ("id", "codigo", "produto", "tipo", "quantidade", "data")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings", height=10)
        cabecalhos = {
            "id": "ID",
            "codigo": "Código",
            "produto": "Produto",
            "tipo": "Tipo",
            "quantidade": "Qtd",
            "data": "Data/Hora",
        }
        larguras = {"id": 50, "codigo": 100, "produto": 220, "tipo": 90, "quantidade": 70, "data": 160}

        for col in colunas:
            self.tree.heading(col, text=cabecalhos[col])
            self.tree.column(col, width=larguras[col], anchor="center" if col != "produto" else "w")

        self.tree.pack(fill="both", expand=True)

    def atualizar_dados(self):
        produtos = listar_produtos()
        self.mapa_produtos.clear()
        opcoes = []

        for codigo, nome, _, _, qtd, _ in produtos:
            rotulo = f"{codigo} - {nome}"
            self.mapa_produtos[rotulo] = qtd
            opcoes.append(rotulo)

        self.cmb_produto["values"] = opcoes
        if opcoes and self.cmb_produto.get() not in self.mapa_produtos:
            self.cmb_produto.set(opcoes[0])
        elif not opcoes:
            self.cmb_produto.set("")
            self.lbl_saldo_atual.config(text="Saldo atual: -")

        self._ao_selecionar_produto()
        self._carregar_historico()

    def _ao_selecionar_produto(self, event=None):
        selecionado = self.cmb_produto.get()
        if selecionado in self.mapa_produtos:
            self.lbl_saldo_atual.config(text=f"Saldo atual: {self.mapa_produtos[selecionado]} un.")

    def _carregar_historico(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for mov in listar_movimentacoes():
            mov_id, codigo, nome_prod, tipo, qtd, data = mov
            tipo_fmt = "Entrada (+)" if tipo == "entrada" else "Saída (-)"
            self.tree.insert(
                "",
                "end",
                values=(mov_id, codigo, nome_prod or "Produto removido", tipo_fmt, qtd, data),
            )

    def _registrar(self):
        selecionado = self.cmb_produto.get().strip()
        if not selecionado or " - " not in selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto válido.")
            return

        codigo = selecionado.split(" - ", 1)[0].strip()
        tipo = self.cmb_tipo.get().strip()

        ok_qtd, qtd = validar_quantidade_inteira(self.ent_quantidade.get(), permitir_zero=False)
        if not ok_qtd:
            messagebox.showwarning("Validação", qtd)
            return

        sucesso, mensagem = registrar_movimentacao(codigo, tipo, qtd)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.ent_quantidade.delete(0, tk.END)
            self.atualizar_dados()
            if self.on_dados_alterados:
                self.on_dados_alterados()
        else:
            messagebox.showerror("Erro", mensagem)