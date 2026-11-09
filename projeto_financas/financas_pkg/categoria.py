class Categoria:
    def __init__(self, nome: str, limite_orcamento: float):
        self.__nome = nome
        self.__limite_orcamento = limite_orcamento

@property
def nome(self) -> str:
    return self.__nome

def verificador_limite(self, valor: float) -> bool:
    return valor <= self.__limite_orcamento
