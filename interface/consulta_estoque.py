import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from banco.produtos import (
    calcular_valor_total_estoque,
    excluir_produto,
    listar_categorias,
    listar_produtos,
)
from utilitarios.exportacao import exportar_estoque_csv


class ConsultaEstoqueFrame(ttk.Frame):
    def __init__(self, parent, on_dados_alterados=None):
        super().__init__(parent, padding=20)
        self.on_dados_alterados = on_dados_alterados
        self._construir_interface()
        self.atualizar_dados()

    def _construir_interface(self):
        ttk.Label(
            self,
            text="Consulta de Estoque Atual",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        barra_filtro = ttk.Frame(self)
        barra_filtro.pack(fill="x", pady=(0, 10))

        ttk.Label(barra_filtro, text="Filtrar por Categoria:").pack(side="left", padx=(0, 6))
        self.cmb_categoria = ttk.Combobox(barra_filtro, state="readonly", width=25)
        self.cmb_categoria.pack(side="left", padx=(0, 10))
        self.cmb_categoria.bind("<<ComboboxSelected>>", lambda _e: self._carregar_tabela())

        ttk.Button(barra_filtro, text="Atualizar", command=self.atualizar_dados).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(barra_filtro, text="Exportar CSV", command=self._exportar_csv).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(barra_filtro, text="Excluir Selecionado", command=self._excluir_selecionado).pack(
            side="right"
        )

        colunas = ("codigo", "nome", "categoria", "preco", "quantidade", "minimo", "subtotal", "status")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings", height=14)
        titulos = {
            "codigo": "Código",
            "nome": "Nome",
            "categoria": "Categoria",
            "preco": "Preço (R$)",
            "quantidade": "Qtd",
            "minimo": "Mínimo",
            "subtotal": "Valor Total (R$)",
            "status": "Status",
        }
        larguras = {
            "codigo": 90,
            "nome": 210,
            "categoria": 120,
            "preco": 100,
            "quantidade": 70,
            "minimo": 75,
            "subtotal": 120,
            "status": 120,
        }

        for col in colunas:
            self.tree.heading(col, text=titulos[col])
            self.tree.column(col, width=larguras[col], anchor="center" if col != "nome" else "w")

        self.tree.tag_configure("baixo", background="#fde8e8", foreground="#9b1c1c")
        self.tree.pack(fill="both", expand=True)

        rodape = ttk.Frame(self, padding=(0, 10))
        rodape.pack(fill="x")

        self.lbl_total_itens = ttk.Label(rodape, text="Produtos exibidos: 0", font=("Segoe UI", 11))
        self.lbl_total_itens.pack(side="left")

        self.lbl_valor_total = ttk.Label(
            rodape,
            text="Valor Total em Estoque: R$ 0,00",
            font=("Segoe UI", 12, "bold"),
        )
        self.lbl_valor_total.pack(side="right")

    def atualizar_dados(self):
        categorias = ["Todas"] + listar_categorias()
        selecionada = self.cmb_categoria.get()
        self.cmb_categoria["values"] = categorias
        if selecionada in categorias:
            self.cmb_categoria.set(selecionada)
        else:
            self.cmb_categoria.set("Todas")
        self._carregar_tabela()

    def _carregar_tabela(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        categoria = self.cmb_categoria.get() or "Todas"
        produtos = listar_produtos(categoria=categoria)

        for codigo, nome, cat, preco, qtd, est_min in produtos:
            subtotal = float(preco) * int(qtd)
            baixo = int(qtd) <= int(est_min)
            status = "ESTOQUE BAIXO" if baixo else "OK"
            tags = ("baixo",) if baixo else ()
            self.tree.insert(
                "",
                "end",
                values=(
                    codigo,
                    nome,
                    cat or "Geral",
                    f"R$ {float(preco):.2f}",
                    qtd,
                    est_min,
                    f"R$ {subtotal:.2f}",
                    status,
                ),
                tags=tags,
            )

        valor_total = calcular_valor_total_estoque(categoria=categoria)
        self.lbl_total_itens.config(text=f"Produtos exibidos: {len(produtos)}")
        self.lbl_valor_total.config(text=f"Valor Total em Estoque: R$ {valor_total:.2f}")

    def _exportar_csv(self):
        categoria = self.cmb_categoria.get() or "Todas"
        produtos = listar_produtos(categoria=categoria)
        if not produtos:
            messagebox.showwarning("Aviso", "Não há produtos para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório CSV",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")],
            initialfile="relatorio_estoque.csv",
        )
        if caminho:
            sucesso, msg = exportar_estoque_csv(caminho, produtos)
            if sucesso:
                messagebox.showinfo("Exportação concluída", msg)
            else:
                messagebox.showerror("Erro", msg)

    def _excluir_selecionado(self):
        selecionados = self.tree.selection()
        if not selecionados:
            messagebox.showwarning("Atenção", "Selecione um produto na tabela para excluir.")
            return

        valores = self.tree.item(selecionados[0], "values")
        codigo, nome = valores[0], valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja realmente excluir o produto '{nome}' ({codigo})?",
        )
        if confirmar:
            sucesso, msg = excluir_produto(codigo)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.atualizar_dados()
                if self.on_dados_alterados:
                    self.on_dados_alterados()
            else:
                messagebox.showerror("Erro", msg)