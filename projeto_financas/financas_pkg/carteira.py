from .transacao import Transacao
from .receita import Receita
from .despesa import Despesa
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
        if isinstance(t, Despesa):
            if not t.categoria.verificar_limite(t.valor):
                print(f"[BLOQUEADO] A despesa '{t.descricao}' excede o limite.")
                return
            if self.saldo < t.valor:
                print(f"[BLOQUEADO] Saldo insuficiente.")
                return
            
            self.__transacoes.append(t)
            print(f"[SUCESSO] Despesa '{t.descricao}' cadastrada.")
            
        elif isinstance(t, Receita):
            self.__transacoes.append(t)
            print(f"[SUCESSO] Receita '{t.descricao}' cadastrada.")

    def criar_meta(self, objetivo: float, saldo_inicial: float) -> None:
        nova_meta = MetaFinanceira(objetivo, saldo_inicial)
        self.__metas.append(nova_meta)

    @property
    def transacoes(self) -> list:
        return self.__transacoes

    @property
    def metas(self) -> list:
        return self.__metas