from .transacao import Transacao
from .meta_financeira import MetaFinanceira
from .calculadora_mixin import CalculadoraMixin


class Carteira:
    def __init__(self, saldo_inicial: float):
        self.__saldo = saldo_inicial
        self.__transacoes = []
        self.__metas = []

    @property
    def saldo(self) -> float:
        return self.__saldo + CalculadoraMixin.calcular_transacoes(self.__transacoes)

    def adicionar_transacao(self, t: Transacao) -> None:
        # Cada tipo decide se aceita a movimentação (polimorfismo)
        motivo_bloqueio = t.validar(self.saldo, self.__transacoes)
        if motivo_bloqueio is not None:
            print(f"[BLOQUEADO] {motivo_bloqueio}")
            return

        self.__transacoes.append(t)
        print(f"[SUCESSO] {t.tipo()} '{t.descricao}' cadastrada.")

    def criar_meta(self, objetivo: float, saldo_inicial: float) -> None:
        nova_meta = MetaFinanceira(objetivo, saldo_inicial)
        self.__metas.append(nova_meta)

    @property
    def transacoes(self) -> list:
        return self.__transacoes

    @property
    def metas(self) -> list:
        return self.__metas