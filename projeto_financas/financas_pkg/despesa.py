from .trasacao import Trasacao
from .calculadora_mixin import CalculadoraMixin
from .categoria import Categoria

class Despesa(Trasacao, CalculadoraMixin):
    def __init__(self, valor: float, descricao: str, data: str, categoria: Categoria):
        super().__init__(valor, descricao, data)
        self.__categoria = categoria

    @property
    def categoria(self) -> Categoria:
        return self.__categoria
    