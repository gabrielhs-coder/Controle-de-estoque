import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from banco.movimentacoes import listar_movimentacoes
from banco.produtos import (
    calcular_valor_total_estoque,
    listar_produtos,
    listar_produtos_estoque_baixo,
)
from utilitarios.exportacao import exportar_estoque_csv


class RelatoriosFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self._construir_interface()
        self.atualizar_dados()

    def _construir_interface(self):
        topo = ttk.Frame(self)
        topo.pack(fill="x", pady=(0, 12))

        ttk.Label(
            topo,
            text="Relatórios e Alertas de Estoque",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")

        ttk.Button(topo, text="Atualizar Relatórios", command=self.atualizar_dados).pack(
            side="right", padx=(0, 8)
        )
        ttk.Button(topo, text="Exportar Estoque Completo (CSV)", command=self._exportar_tudo).pack(
            side="right"
        )

        # Cartões de resumo
        resumo = ttk.LabelFrame(self, text="Resumo Geral", padding=12)
        resumo.pack(fill="x", pady=(0, 12))

        self.lbl_qtd_produtos = ttk.Label(resumo, text="Total de Produtos: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_qtd_produtos.pack(side="left", padx=(0, 25))

        self.lbl_qtd_baixo = ttk.Label(
            resumo,
            text="Itens em Estoque Baixo: 0",
            font=("Segoe UI", 11, "bold"),
            foreground="#b42318",
        )
        self.lbl_qtd_baixo.pack(side="left", padx=(0, 25))

        self.lbl_valor_total = ttk.Label(
            resumo,
            text="Valor Total em Estoque: R$ 0,00",
            font=("Segoe UI", 11, "bold"),
        )
        self.lbl_valor_total.pack(side="right")

        # Alerta de estoque baixo
        ttk.Label(
            self,
            text="Alerta de Estoque Baixo (Quantidade <= Estoque Mínimo)",
            font=("Segoe UI", 12, "bold"),
            foreground="#b42318",
        ).pack(anchor="w", pady=(4, 4))

        cols_baixo = ("codigo", "nome", "categoria", "quantidade", "minimo")
        self.tree_baixo = ttk.Treeview(self, columns=cols_baixo, show="headings", height=6)
        for col, texto, larg in [
            ("codigo", "Código", 100),
            ("nome", "Produto", 260),
            ("categoria", "Categoria", 140),
            ("quantidade", "Qtd Atual", 100),
            ("minimo", "Mínimo", 100),
        ]:
            self.tree_baixo.heading(col, text=texto)
            self.tree_baixo.column(col, width=larg, anchor="center" if col != "nome" else "w")
        self.tree_baixo.pack(fill="x", pady=(0, 14))

        # Movimentações consolidadas
        ttk.Label(
            self,
            text="Relatório de Movimentações Recentes",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        cols_mov = ("id", "codigo", "produto", "tipo", "quantidade", "data")
        self.tree_mov = ttk.Treeview(self, columns=cols_mov, show="headings", height=7)
        for col, texto, larg in [
            ("id", "ID", 50),
            ("codigo", "Código", 95),
            ("produto", "Produto", 220),
            ("tipo", "Tipo", 90),
            ("quantidade", "Qtd", 70),
            ("data", "Data/Hora", 160),
        ]:
            self.tree_mov.heading(col, text=texto)
            self.tree_mov.column(col, width=larg, anchor="center" if col != "produto" else "w")
        self.tree_mov.pack(fill="both", expand=True)

    def atualizar_dados(self):
        todos_produtos = listar_produtos()
        baixos = listar_produtos_estoque_baixo()
        valor_total = calcular_valor_total_estoque()

        self.lbl_qtd_produtos.config(text=f"Total de Produtos: {len(todos_produtos)}")
        self.lbl_qtd_baixo.config(text=f"Itens em Estoque Baixo: {len(baixos)}")
        self.lbl_valor_total.config(text=f"Valor Total em Estoque: R$ {valor_total:.2f}")

        for item in self.tree_baixo.get_children():
            self.tree_baixo.delete(item)
        for codigo, nome, cat, _, qtd, est_min in baixos:
            self.tree_baixo.insert("", "end", values=(codigo, nome, cat or "Geral", qtd, est_min))

        for item in self.tree_mov.get_children():
            self.tree_mov.delete(item)
        for mov_id, codigo, nome_prod, tipo, qtd, data in listar_movimentacoes():
            tipo_fmt = "Entrada" if tipo == "entrada" else "Saída"
            self.tree_mov.insert("", "end", values=(mov_id, codigo, nome_prod or "-", tipo_fmt, qtd, data))

    def _exportar_tudo(self):
        produtos = listar_produtos()
        if not produtos:
            messagebox.showwarning("Aviso", "Não há dados de estoque para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar relatório completo",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")],
            initialfile="estoque_completo.csv",
        )
        if caminho:
            sucesso, msg = exportar_estoque_csv(caminho, produtos)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)