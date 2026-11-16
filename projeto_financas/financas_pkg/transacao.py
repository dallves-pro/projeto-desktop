from abc import ABC, abstractmethod
from typing import Optional

from .categoria import Categoria


class Transacao(ABC):
    """Classe base abstrata de todas as movimentações financeiras."""

    def __init__(self, valor: float, descricao: str, data: str):
        self.__valor = valor
        self.__descricao = descricao
        self.__data = data

    @property
    def valor(self) -> float:
        return self.__valor

    @property
    def descricao(self) -> str:
        return self.__descricao

    @property
    def data(self) -> str:
        return self.__data

    @abstractmethod
    def tipo(self) -> str:
        """Nome do tipo da movimentacao"""

    @abstractmethod
    def efeito_no_saldo(self) -> float:
        """Variação que a movimentacao provoca no saldo (positiva ou negativa)"""

    @abstractmethod
    def gasto_em(self, categoria: Categoria) -> float:
        """Valor que a movimentacao representa de gasto na categoria informada"""

    @abstractmethod
    def validar(self, saldo_atual: float, transacoes: list) -> Optional[str]:
        """Retorna o motivo do bloqueio, ou 'None' se a movimentacao for aceita"""

        """`transacoes` sao as movimentacoes ja aceitas pela carteira, necessarias
        para calcular o total gasto em uma categoria"""