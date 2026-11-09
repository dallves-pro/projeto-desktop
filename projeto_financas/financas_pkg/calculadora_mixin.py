class CalculadoraMixin:
    @classmethod
    def calcular_transacoes(cls, transacoes: list) -> float:
        saldo_liquido = 0.0
        for t in transacoes:
            if type(t).__name__ == "Receita":
                saldo_liquido += t.valor
            elif type(t).__name__ == "Despesa":
                saldo_liquido -= t.valor
        return saldo_liquido

    @classmethod
    def calcular_progresso(cls, saldo_atual: float, objetivo: float) -> float:
        if objetivo <= 0:
            return 0.0
        return (saldo_atual/objetivo) * 100
        