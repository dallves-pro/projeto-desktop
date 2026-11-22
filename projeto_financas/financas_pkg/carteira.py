from typing import List, Optional

from .calculadora_mixin import CalculadoraMixin
from .categoria import Categoria
from .meta_financeira import MetaFinanceira
from .banco import RepositorioFinancas
from .transacao import Transacao

CHAVE_SALDO_INICIAL = "saldo_inicial"

class Carteira:
    def __init__(self, saldo_inicial: float, repositorio: RepositorioFinancas):
        self.__repositorio = repositorio
        self.__primeira_execucao = False
        self.__saldo = self.__carregar_saldo_inicial(saldo_inicial)
        self.__categorias: List[Categoria] = []
        self.__transacoes: List[Transacao] = []
        self.__metas: List[MetaFinanceira] = []
        self.__carregar_dados()

    def __carregar_saldo_inicial(self, saldo_padrao: float) -> float:
        # O saldo_padrao só é usado na primeira execução; depois vale o que foi salvo
        salvo = self.__repositorio.obter_configuracao(CHAVE_SALDO_INICIAL)
        if salvo is None:
            self.__repositorio.definir_configuracao(CHAVE_SALDO_INICIAL, saldo_padrao)
            self.__primeira_execucao = True
            return saldo_padrao
        return salvo

    def __carregar_dados(self) -> None:
        # Categorias primeiro: as despesas precisam apontar para os MESMOS objetos Categoria
        self.__categorias = self.__repositorio.carregar_categorias()
        categorias_por_id = {c.id: c for c in self.__categorias}
        self.__transacoes = self.__repositorio.carregar_transacoes(categorias_por_id)
        self.__metas = self.__repositorio.carregar_metas()

    @property
    def primeira_execucao(self) -> bool:
        # True só quando o banco acabou de ser criado (usado para criar a meta inicial)
        return self.__primeira_execucao
 
    @property
    def saldo(self) -> float:
         return self.__saldo + CalculadoraMixin.calcular_transacoes(self.__transacoes)
 
    @property
    def saldo_inicial(self) -> float:
        return self.__saldo

    def alterar_saldo_inicial(self, novo_saldo: float) -> bool:
        # O saldo final (novo saldo inicial + movimentações) não pode ficar negativo
        saldo_final = novo_saldo + CalculadoraMixin.calcular_transacoes(self.__transacoes)
        if round(saldo_final, 2) < 0:
            print("[BLOQUEADO] Esse saldo inicial deixaria o saldo da carteira negativo.")
            return False

        self.__repositorio.definir_configuracao(CHAVE_SALDO_INICIAL, novo_saldo)
        self.__saldo = novo_saldo
        print(f"[SUCESSO] Saldo inicial alterado para R$ {novo_saldo:.2f}.")
        return True

    # ----- Categorias -----

    @property
    def categorias(self) -> List[Categoria]:
        return self.__categorias

    def criar_categoria(self, nome: str, limite_orcamento: float) -> Optional[Categoria]:
        nome = nome.strip()
        motivo = self.__validar_dados_categoria(nome, limite_orcamento)
        if motivo is not None:
            print(f"[BLOQUEADO] {motivo}")
            return None
        categoria = Categoria(nome, limite_orcamento)
        self.__salvar_categoria_nova(categoria)
        print(f"[SUCESSO] Categoria '{nome}' cadastrada.")
        return categoria

    def editar_categoria(self, categoria: Categoria, novo_nome: str, novo_limite: float) -> bool:
        novo_nome = novo_nome.strip()
        motivo = self.__validar_dados_categoria(novo_nome, novo_limite, ignorar=categoria)
        if motivo is None:
            gasto = self.total_gasto_na_categoria(categoria)
            if round(gasto, 2) > novo_limite:
                motivo = (f"O total ja gasto (R$ {gasto:.2f}) ultrapassa o novo limite "
                          f"de R$ {novo_limite:.2f}.")
        if motivo is not None:
            print(f"[BLOQUEADO] {motivo}")
            return False

        self.__repositorio.atualizar_categoria(categoria.id, novo_nome, novo_limite)
        categoria.alterar(novo_nome, novo_limite)
        print(f"[SUCESSO] Categoria '{novo_nome}' atualizada.")
        return True

    def remover_categoria(self, categoria: Categoria) -> int:
        """Remove a categoria e todas as suas despesas. Retorna quantas despesas foram apagadas."""
        quantidade = len(self.despesas_da_categoria(categoria))
        self.__repositorio.remover_categoria(categoria.id)
        # Mantém só o que NÃO é gasto nesta categoria (receitas e despesas de outras categorias)
        self.__transacoes = [t for t in self.__transacoes if t.gasto_em(categoria) == 0.0]
        self.__categorias.remove(categoria)
        print(f"[SUCESSO] Categoria '{categoria.nome}' removida ({quantidade} despesa(s) excluída(s)).")
        return quantidade

    def total_gasto_na_categoria(self, categoria: Categoria) -> float:
        return sum((t.gasto_em(categoria) for t in self.__transacoes), 0.0)

    def despesas_da_categoria(self, categoria: Categoria) -> List[Transacao]:
        # gasto_em é 0 para receitas e para despesas de outras categorias, então filtra só as desta
        return [t for t in self.__transacoes if t.gasto_em(categoria) > 0]

    def __validar_dados_categoria(self, nome: str, limite: float,
                                  ignorar: Optional[Categoria] = None) -> Optional[str]:
        if not nome:
            return "O nome da categoria nao pode ser vazio."
        if limite <= 0:
            return "O limite de orcamento deve ser maior que zero."
        # 'ignorar' permite que a própria categoria mantenha o seu nome ao ser editada
        if any(c.nome.casefold() == nome.casefold() and c is not ignorar for c in self.__categorias):
            return f"Ja existe uma categoria chamada '{nome}'."
        return None

    def __salvar_categoria_nova(self, categoria: Categoria) -> None:
        novo_id = self.__repositorio.inserir_categoria(categoria.nome, categoria.limite_orcamento)
        categoria.definir_id(novo_id)
        self.__categorias.append(categoria)

    def __pertence(self, categoria: Categoria) -> bool:
        return any(c is categoria for c in self.__categorias)

    # ----- Movimentações -----

    @property
    def transacoes(self) -> List[Transacao]:
        return self.__transacoes

    def buscar_transacao(self, transacao_id: int) -> Optional[Transacao]:
        return next((t for t in self.__transacoes if t.id == transacao_id), None)

    def adicionar_transacao(self, t: Transacao) -> None:
        if t.valor <= 0:
            print("[BLOQUEADO] O valor deve ser maior que zero.")
            return

         # Cada tipo decide se aceita a movimentação (polimorfismo)
        motivo_bloqueio = t.validar(self.saldo, self.__transacoes)
        if motivo_bloqueio is not None:
             print(f"[BLOQUEADO] {motivo_bloqueio}")
             return
 
        # Categoria criada fora da carteira: só é cadastrada depois que a despesa passou nas validações
        categoria = t.categoria_vinculada()  # None para receitas
        if categoria is not None and not self.__pertence(categoria):
            motivo_bloqueio = self.__validar_dados_categoria(categoria.nome, categoria.limite_orcamento)
            if motivo_bloqueio is not None:
                print(f"[BLOQUEADO] {motivo_bloqueio} Selecione a categoria ja cadastrada.")
                return
            self.__salvar_categoria_nova(categoria)
            print(f"[SUCESSO] Categoria '{categoria.nome}' cadastrada automaticamente.")

        t.definir_id(self.__repositorio.inserir_transacao(t.to_registro()))
        self.__transacoes.append(t)
        print(f"[SUCESSO] {t.tipo()} '{t.descricao}' cadastrada.")
 
    def editar_transacao(self, transacao_id: int, alteracoes: dict) -> bool:
        alvo = self.buscar_transacao(transacao_id)
        if alvo is None:
            print("[ERRO] Nenhuma movimentacao com esse codigo.")
            return False

        categorias_por_id = {c.id: c for c in self.__categorias}
        if "categoria_id" in alteracoes and alteracoes["categoria_id"] not in categorias_por_id:
            print("[BLOQUEADO] Categoria inexistente.")
            return False

        # Monta a versão nova do MESMO tipo: o próprio alvo sabe criar objetos do seu tipo
        registro = alvo.to_registro()
        registro.update(alteracoes)
        novo = alvo.de_registro(registro, categorias_por_id)
        novo.definir_id(transacao_id)

        if novo.valor <= 0:
            print("[BLOQUEADO] O valor deve ser maior que zero.")
            return False
        if not novo.descricao.strip():
            print("[BLOQUEADO] A descricao nao pode ser vazia.")
            return False

        # Valida a versão nova contra as OUTRAS movimentações: a antiga não deve contar
        outras = [t for t in self.__transacoes if t is not alvo]
        saldo_sem_alvo = self.__saldo + CalculadoraMixin.calcular_transacoes(outras)
        motivo_bloqueio = novo.validar(saldo_sem_alvo, outras)
        if motivo_bloqueio is None and round(saldo_sem_alvo + novo.efeito_no_saldo(), 2) < 0:
            motivo_bloqueio = "A alteracao deixaria o saldo negativo."
        if motivo_bloqueio is not None:
            print(f"[BLOQUEADO] {motivo_bloqueio}")
            return False

        self.__repositorio.atualizar_transacao(transacao_id, novo.to_registro())
        self.__transacoes[self.__transacoes.index(alvo)] = novo
        print(f"[SUCESSO] {novo.tipo()} '{novo.descricao}' atualizada.")
        return True

    def remover_transacao(self, transacao_id: int) -> bool:
        alvo = self.buscar_transacao(transacao_id)
        if alvo is None:
            print("[ERRO] Nenhuma movimentacao com esse codigo.")
            return False

        # Cada tipo decide se pode ser removido (polimorfismo)
        motivo_bloqueio = alvo.validar_remocao(self.saldo, self.__transacoes)
        if motivo_bloqueio is not None:
            print(f"[BLOQUEADO] {motivo_bloqueio}")
            return False

        self.__repositorio.remover_transacao(transacao_id)
        self.__transacoes.remove(alvo)
        print(f"[SUCESSO] {alvo.tipo()} '{alvo.descricao}' removida.")
        return True

    # ----- Metas -----

    def __validar_dados_meta(self, objetivo: float, saldo_inicial: float) -> Optional[str]:
        if objetivo <= 0:
            return "O objetivo da meta deve ser maior que zero."
        if saldo_inicial < 0:
            return "O valor ja economizado na meta nao pode ser negativo."
        return None

    def criar_meta(self, objetivo: float, saldo_inicial: float) -> Optional[MetaFinanceira]:
        motivo = self.__validar_dados_meta(objetivo, saldo_inicial)
        if motivo is not None:
            print(f"[BLOQUEADO] {motivo}")
            return None

        nova_meta = MetaFinanceira(objetivo, saldo_inicial)
        nova_meta.definir_id(self.__repositorio.inserir_meta(objetivo, saldo_inicial))
        self.__metas.append(nova_meta)
        print(f"[SUCESSO] Meta de R$ {objetivo:.2f} criada.")
        return nova_meta
 
    def editar_meta(self, meta: MetaFinanceira, novo_objetivo: float, novo_saldo_inicial: float) -> bool:
        motivo = self.__validar_dados_meta(novo_objetivo, novo_saldo_inicial)
        if motivo is not None:
            print(f"[BLOQUEADO] {motivo}")
            return False

        self.__repositorio.atualizar_meta(meta.id, novo_objetivo, novo_saldo_inicial)
        meta.alterar(novo_objetivo, novo_saldo_inicial)
        print(f"[SUCESSO] Meta atualizada (objetivo R$ {novo_objetivo:.2f}).")
        return True

    def excluir_meta(self, meta: MetaFinanceira) -> bool:
        self.__repositorio.remover_meta(meta.id)
        self.__metas.remove(meta)
        print(f"[SUCESSO] Meta de R$ {meta.objetivo:.2f} excluida.")
        return True

    @property
    def metas(self) -> list:
        return self.__metas