from banco.conexao import inicializar_banco
from interface.menu_principal import MenuPrincipalApp


def main():
    inicializar_banco()
    app = MenuPrincipalApp()
    app.mainloop()


if __name__ == "__main__":
    main()