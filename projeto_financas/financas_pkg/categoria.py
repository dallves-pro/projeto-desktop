from typing import Optional

class Categoria:
    def __init__(self, nome: str, limite_orcamento: float):
        self.__id: Optional[int] = None  # preenchido quando a categoria é salva no banco
        self.__nome = nome
        self.__limite_orcamento = limite_orcamento

    @property
    def id(self) -> Optional[int]:
        return self.__id

    def definir_id(self, id_: int) -> None:
        self.__id = id_

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def limite_orcamento(self) -> float:
        return self.__limite_orcamento

    def alterar(self, nome: str, limite_orcamento: float) -> None:
        # Altera o MESMO objeto: as despesas continuam apontando para ele
        self.__nome = nome
        self.__limite_orcamento = limite_orcamento

    def verificar_limite(self, total_gasto: float) -> bool: # Indica se o total gasto na categoria esta dentro do limite.
        return round(total_gasto, 2) <= self.__limite_orcamento
    # O valor eh arredondado para centavos para que erros de ponto flutuante nao bloqueiem um gasto que chega exatamente ao limite.
