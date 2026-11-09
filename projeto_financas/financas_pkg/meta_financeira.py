from .calculadora_mixin import CalculadoraMixin

class MetaFinanceira(CalculadoraMixin):
    def __init__(self, objetivo: float, saldo_atual: float):
        self.__objetivo = objetivo
        self.__saldo_atual = saldo_atual

    def calcular_progresso(self) -> float:
        return self.calcular_progresso(self.__saldo_atual, self.__objetivo)
