from .calculadora_mixin import CalculadoraMixin


class MetaFinanceira(CalculadoraMixin):
    def __init__(self, objetivo: float, saldo_inicial: float):
        self.__objetivo = objetivo
        self.__saldo_inicial = saldo_inicial

    @property
    def objetivo(self) -> float:
        return self.__objetivo

    def saldo_atual(self, transacoes: list) -> float:
        """O valor ja economizado eh o saldo inicial da meta mais o efeito líquido das transacoes"""
        return self.__saldo_inicial + self.calcular_transacoes(transacoes)

    def calcular_progresso(self, transacoes: list) -> float:
        # Usa o cálculo genérico da mixin sobre o valor atual acompanhado pelas transações
        return super().calcular_progresso(self.saldo_atual(transacoes), self.__objetivo)
