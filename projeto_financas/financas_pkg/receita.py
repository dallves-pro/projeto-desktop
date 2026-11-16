from typing import Optional

from .categoria import Categoria
from .transacao import Transacao
from .calculadora_mixin import CalculadoraMixin


class Receita(Transacao, CalculadoraMixin):
    def __init__(self, valor: float, descricao: str, data: str, fonte: str):
        super().__init__(valor, descricao, data)
        self.__fonte = fonte

    def tipo(self) -> str:
        return "Receita"

    def efeito_no_saldo(self) -> float:
        return self.valor

    def gasto_em(self, categoria: Categoria) -> float: 
        # Receitas nunca representam gasto
        return 0.0

    def validar(self, saldo_atual: float, transacoes: list) -> Optional[str]:
        # Receitas nunca são bloqueadas
        return None