from .carteira import Carteira


class GeradorRelatorio:
    def gerar_dados(self, carteira: Carteira) -> str:
        relatorio = "\n=== RELATORIO FINANCEIRO (VISUALIZACAO) ===\n"
        relatorio += f"Saldo Consolidado: R$ {carteira.saldo:.2f}\n\n"
        relatorio += "Movimentacoes Cadastradas:\n"
        for t in carteira.transacoes:
            relatorio += f"  [{t.tipo()}] {t.descricao} | Valor: R$ {t.valor:.2f} | Data: {t.data}\n"

        relatorio += "\nMetas Financeiras Acompanhadas:\n"
        for i, m in enumerate(carteira.metas, 1):
            atual = m.saldo_atual(carteira.transacoes)
            progresso = m.calcular_progresso(carteira.transacoes)
            relatorio += (f"  Meta {i}: {progresso:.2f}% de progresso "
                          f"(R$ {atual:.2f} de R$ {m.objetivo:.2f})\n")
        relatorio += "===========================================\n"
        return relatorio