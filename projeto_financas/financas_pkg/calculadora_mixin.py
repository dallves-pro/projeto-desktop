class CalculadoraMixin:
    @classmethod
    def calcular_transacoes(cls, transacoes: list) -> float:
        # Cada transação informa o próprio efeito no saldo (polimorfismo)
        return sum((t.efeito_no_saldo() for t in transacoes), 0.0)

    @classmethod
    def calcular_progresso(cls, saldo_atual: float, objetivo: float) -> float:
        if objetivo <= 0:
            return 0.0
        return (saldo_atual / objetivo) * 100
        