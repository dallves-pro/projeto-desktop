from abc import ABC, abstractmethod
from typing import Optional

from .categoria import Categoria


class Transacao(ABC):
    """Classe base abstrata de todas as movimentações financeiras."""

    def __init__(self, valor: float, descricao: str, data: str):
        self.__id: Optional[int] = None  # preenchido quando a movimentação é salva no banco
        self.__valor = valor
        self.__descricao = descricao
        self.__data = data

    @property
    def id(self) -> Optional[int]:
        return self.__id

    def definir_id(self, id_: int) -> None:
        self.__id = id_

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

    @abstractmethod
    def validar_remocao(self, saldo_atual: float, transacoes: list) -> Optional[str]:
        """Retorna o motivo que impede remover a movimentacao, ou 'None' se a remoção for permitida"""

    @abstractmethod
    def categoria_vinculada(self) -> Optional[Categoria]:
        """Categoria de despesa à qual a movimentacao pertence (None para receitas)"""

    @abstractmethod
    def campos_especificos_editaveis(self) -> dict:
        """Campos que só este tipo de movimentacao tem: nome do campo -> rótulo do menu"""

    def campos_editaveis(self) -> dict:
        campos = {"descricao": "Descricao", "valor": "Valor", "data": "Data"}
        campos.update(self.campos_especificos_editaveis())
        return campos

    @abstractmethod
    def to_registro(self) -> dict:
        """Converte a movimentacao em um dicionario pronto para ser salvo no banco"""

    @classmethod
    @abstractmethod
    def pertence_ao_registro(cls, registro: dict) -> bool:
        """Diz se esta subclasse sabe reconstruir o registro lido do banco"""

    @classmethod
    @abstractmethod
    def de_registro(cls, registro: dict, categorias_por_id: dict) -> "Transacao":
        """Cria a movimentacao a partir do registro lido do banco"""

    @classmethod
    def reconstruir(cls, registro: dict, categorias_por_id: dict) -> "Transacao":
        # Cada subclasse responde por si mesma se o registro é dela (polimorfismo)
        for subclasse in cls.__subclasses__():
            if subclasse.pertence_ao_registro(registro):
                transacao = subclasse.de_registro(registro, categorias_por_id)
                transacao.definir_id(registro["id"])
                return transacao
        raise ValueError(f"Tipo de movimentacao desconhecido no banco: {registro['tipo']}")