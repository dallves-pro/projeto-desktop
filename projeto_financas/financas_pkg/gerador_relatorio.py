from .carteira import Carteira
from .receita import Receita

class GeradorRelatorio:
    def gerar_dados(self, carteira: Carteira) -> str:
        relatorio = "\n=== RELATORIO FINANCEIRO (VISUALIZACAO) ===\n"
        relatorio += f"Saldo Consolidado: R$ {carteira.saldo:.2f}\n\n"
        relatorio += "Movimentacoes Cadastradas:\n"
        for t in carteira.transacoes:
            tipo = "Receita" if isinstance(t, Receita) else "Despesa"
            relatorio += f"  [{tipo}] {t.descricao} | Valor: R$ {t.valor:.2f} | Data: {t.data}\n"
            
        relatorio += "\nMetas Financeiras Acompanhadas:\n"
        for i, m in enumerate(carteira.metas, 1):
            relatorio += f"  Meta {i}: {m.calcular_progresso():.2f}% de progresso\n"
        relatorio += "===========================================\n"
        return relatorio