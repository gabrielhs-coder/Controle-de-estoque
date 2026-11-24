import tkinter as tk
from tkinter import ttk
from banco.produtos import listar_produtos_estoque_baixo
from interface.cadastro_produtos import CadastroProdutosFrame
from interface.consulta_estoque import ConsultaEstoqueFrame
from interface.registro_movimentacao import RegistroMovimentacaoFrame
from interface.relatorios import RelatoriosFrame


class MenuPrincipalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Controle de Estoque - INE5201")
        self.geometry("980x640")
        self.minsize(820, 540)

        self._configurar_estilos()
        self._construir_layout()
        self.notificar_atualizacao()

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Nav.TButton", font=("Segoe UI", 10, "bold"), padding=10)

    def _construir_layout(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Menu lateral de navegação
        menu_lateral = ttk.Frame(container, padding=12, width=210)
        menu_lateral.pack(side="left", fill="y")
        menu_lateral.pack_propagate(False)

        ttk.Label(
            menu_lateral,
            text="MENU PRINCIPAL",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        self.lbl_alerta_menu = ttk.Label(
            menu_lateral,
            text="",
            font=("Segoe UI", 9, "bold"),
            foreground="#b42318",
            wraplength=180,
        )
        self.lbl_alerta_menu.pack(anchor="w", pady=(0, 12))

        self.area_conteudo = ttk.Frame(container)
        self.area_conteudo.pack(side="right", fill="both", expand=True)

        self.frames = {
            "consulta": ConsultaEstoqueFrame(
                self.area_conteudo, on_dados_alterados=self.notificar_atualizacao
            ),
            "cadastro": CadastroProdutosFrame(
                self.area_conteudo, on_dados_alterados=self.notificar_atualizacao
            ),
            "movimentacao": RegistroMovimentacaoFrame(
                self.area_conteudo, on_dados_alterados=self.notificar_atualizacao
            ),
            "relatorios": RelatoriosFrame(self.area_conteudo),
        }

        for frame in self.frames.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        navegacao = [
            ("Consulta de Estoque", "consulta"),
            ("Cadastrar Produto", "cadastro"),
            ("Entrada / Saída", "movimentacao"),
            ("Relatórios e Alertas", "relatorios"),
        ]

        for texto, chave in navegacao:
            ttk.Button(
                menu_lateral,
                text=texto,
                style="Nav.TButton",
                command=lambda c=chave: self.mostrar_tela(c),
            ).pack(fill="x", pady=4)

        self.mostrar_tela("consulta")

    def mostrar_tela(self, chave: str):
        frame = self.frames[chave]
        if hasattr(frame, "atualizar_dados"):
            frame.atualizar_dados()
        frame.tkraise()

    def notificar_atualizacao(self):
        baixos = listar_produtos_estoque_baixo()
        if baixos:
            self.lbl_alerta_menu.config(
                text=f"⚠ Alerta: {len(baixos)} produto(s) com estoque baixo."
            )
        else:
            self.lbl_alerta_menu.config(text="✓ Estoque dentro do limite.")