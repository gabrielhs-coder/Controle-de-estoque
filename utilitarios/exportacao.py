import csv
from pathlib import Path


def exportar_estoque_csv(caminho_arquivo: str, produtos: list[tuple]) -> tuple[bool, str]:
    try:
        destino = Path(caminho_arquivo)
        if destino.suffix.lower() != ".csv":
            destino = destino.with_suffix(".csv")

        with open(destino, mode="w", newline="", encoding="utf-8-sig") as arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow([
                "Código",
                "Nome",
                "Categoria",
                "Preço Unitário (R$)",
                "Quantidade",
                "Estoque Mínimo",
                "Valor Total (R$)",
                "Status",
            ])

            valor_total_geral = 0.0
            for prod in produtos:
                codigo, nome, categoria, preco, qtd, est_min = prod
                subtotal = float(preco) * int(qtd)
                valor_total_geral += subtotal
                status = "ESTOQUE BAIXO" if int(qtd) <= int(est_min) else "OK"
                writer.writerow([
                    codigo,
                    nome,
                    categoria or "Geral",
                    f"{float(preco):.2f}",
                    qtd,
                    est_min,
                    f"{subtotal:.2f}",
                    status,
                ])

            writer.writerow([])
            writer.writerow(["Valor Total Geral do Estoque (R$)", f"{valor_total_geral:.2f}"])

        return True, f"Relatório exportado com sucesso para:\n{destino}"
    except Exception as exc:
        return False, f"Erro ao exportar CSV: {exc}"