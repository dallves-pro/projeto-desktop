class Categoria:
    def __init__(self, nome: str, limite_orcamento: float):
        self.__nome = nome
        self.__limite_orcamento = limite_orcamento

    @property
    def nome(self) -> str:
        return self.__nome

    def verificar_limite(self, total_gasto: float) -> bool: # Indica se o total gasto na categoria esta dentro do limite.
        return round(total_gasto, 2) <= self.__limite_orcamento
    # O valor eh arredondado para centavos para que erros de ponto flutuante nao bloqueiem um gasto que chega exatamente ao limite.
