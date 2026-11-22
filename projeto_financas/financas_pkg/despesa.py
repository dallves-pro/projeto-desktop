from typing import Optional

from .transacao import Transacao
from .calculadora_mixin import CalculadoraMixin
from .categoria import Categoria


class Despesa(Transacao, CalculadoraMixin):
    TIPO_REGISTRO = "Despesa"

    def __init__(self, valor: float, descricao: str, data: str, categoria: Categoria):
        super().__init__(valor, descricao, data)
        self.__categoria = categoria

    @property
    def categoria(self) -> Categoria:
        return self.__categoria

    def tipo(self) -> str:
        return self.TIPO_REGISTRO

    def efeito_no_saldo(self) -> float:
        return -self.valor

    def gasto_em(self, categoria: Categoria) -> float:
        # Só conta se for a mesma categoria, ou seja, se for o mesmo objeto de orçamento
        return self.valor if categoria is self.__categoria else 0.0

    def validar(self, saldo_atual: float, transacoes: list) -> Optional[str]:
        # O limite vale para o total gasto na categoria, não para cada despesa isolada
        gasto_anterior = sum((t.gasto_em(self.__categoria) for t in transacoes), 0.0)
        if not self.__categoria.verificar_limite(gasto_anterior + self.valor):
            return (f"A despesa '{self.descricao}' excede o limite "
                    f"da categoria '{self.__categoria.nome}'.")
        if saldo_atual < self.valor:
            return "Saldo insuficiente."
        return None

    def validar_remocao(self, saldo_atual: float, transacoes: list) -> Optional[str]:
        # Remover uma despesa só libera saldo e limite da categoria: sempre é permitido
        return None

    def categoria_vinculada(self) -> Optional[Categoria]:
        return self.__categoria

    def campos_especificos_editaveis(self) -> dict:
        return {"categoria_id": "Categoria"}

    def to_registro(self) -> dict:
        return {
            "tipo": self.TIPO_REGISTRO,
            "valor": self.valor,
            "descricao": self.descricao,
            "data": self.data,
            "fonte": None,
            "categoria_id": self.__categoria.id,
        }

    @classmethod
    def pertence_ao_registro(cls, registro: dict) -> bool:
        return registro["tipo"] == cls.TIPO_REGISTRO

    @classmethod
    def de_registro(cls, registro: dict, categorias_por_id: dict) -> "Despesa":
        # Usa o MESMO objeto Categoria carregado pela carteira (a comparação em gasto_em usa 'is')
        categoria = categorias_por_id[registro["categoria_id"]]
        return cls(registro["valor"], registro["descricao"], registro["data"], categoria)
    