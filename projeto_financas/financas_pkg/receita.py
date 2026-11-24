from typing import Optional

from .categoria import Categoria
from .transacao import Transacao
from .calculadora_mixin import CalculadoraMixin


class Receita(Transacao, CalculadoraMixin):
    TIPO_REGISTRO = "Receita"

    def __init__(self, valor: float, descricao: str, data: str, fonte: str):
        super().__init__(valor, descricao, data)
        self.__fonte = fonte

    def tipo(self) -> str:
        return self.TIPO_REGISTRO

    def efeito_no_saldo(self) -> float:
        return self.valor

    def gasto_em(self, categoria: Categoria) -> float: 
        # Receitas nunca representam gasto
        return 0.0

    def validar(self, saldo_atual: float, transacoes: list) -> Optional[str]:
        # Receitas nunca são bloqueadas
        return None

    def validar_remocao(self, saldo_atual: float, transacoes: list) -> Optional[str]:
        # Remover uma receita diminui o saldo: ele não pode ficar negativo
        if round(saldo_atual - self.valor, 2) < 0:
            return (f"A receita '{self.descricao}' não pode ser removida: "
                    f"o saldo ficaria negativo.")
        return None

    def categoria_vinculada(self) -> Optional[Categoria]:
        # Receitas não pertencem a nenhuma categoria de despesa
        return None

    def chave_estilo(self) -> str:
        return "receita"

    def entrada_no_saldo(self) -> float:
        # Receita é toda entrada de dinheiro
        return self.valor

    def saida_do_saldo(self) -> float:
        # Receita nunca é saída de dinheiro
        return 0.0

    def campos_especificos_editaveis(self) -> dict:
        return {"fonte": "Fonte pagadora"}

    def to_registro(self) -> dict:
        return {
            "tipo": self.TIPO_REGISTRO,
            "valor": self.valor,
            "descricao": self.descricao,
            "data": self.data,
            "fonte": self.__fonte,
            "categoria_id": None,
        }

    @classmethod
    def pertence_ao_registro(cls, registro: dict) -> bool:
        return registro["tipo"] == cls.TIPO_REGISTRO

    @classmethod
    def de_registro(cls, registro: dict, categorias_por_id: dict) -> "Receita":
        return cls(registro["valor"], registro["descricao"], registro["data"], registro["fonte"])