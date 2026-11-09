from abc import ABC

class Trasacao(ABC):
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
    