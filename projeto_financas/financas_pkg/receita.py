from .transacao import Trasacao
from .calculadora_mixin import CalculadoraMixin

class Receita(Trasacao, CalculadoraMixin):
    def __init__(self, valor: float, descricao: str, data: str, fonte: str):
        super().__init__(valor, descricao, data)
        self.__fonte = fonte
        