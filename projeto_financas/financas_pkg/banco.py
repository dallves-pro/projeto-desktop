import sqlite3
from typing import Dict, List, Optional

from .categoria import Categoria
from .meta_financeira import MetaFinanceira
from .transacao import Transacao


class RepositorioFinancas:
    """Salva configurações, metas, categorias e movimentações em um banco SQLite.

    Use um caminho de arquivo (ex.: 'financas.db') para persistir entre execuções,
    ou ':memory:' para um banco temporário (usado nos testes).
    """

    def __init__(self, caminho: str):
        self.__conexao = sqlite3.connect(caminho)
        self.__conexao.row_factory = sqlite3.Row  # permite acessar as colunas pelo nome
        self.__criar_tabelas()

    def __criar_tabelas(self) -> None:
        self.__conexao.execute(
            """CREATE TABLE IF NOT EXISTS configuracoes (
                   chave TEXT PRIMARY KEY,
                   valor REAL NOT NULL)"""
        )
        self.__conexao.execute(
            """CREATE TABLE IF NOT EXISTS metas (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   objetivo REAL NOT NULL,
                   saldo_inicial REAL NOT NULL)"""
        )
        self.__conexao.execute(
            """CREATE TABLE IF NOT EXISTS categorias (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nome TEXT NOT NULL UNIQUE,
                   limite_orcamento REAL NOT NULL)"""
        )
        self.__conexao.execute(
            """CREATE TABLE IF NOT EXISTS transacoes (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   tipo TEXT NOT NULL,
                   valor REAL NOT NULL,
                   descricao TEXT NOT NULL,
                   data TEXT NOT NULL,
                   fonte TEXT,
                   categoria_id INTEGER REFERENCES categorias(id))"""
        )
        self.__conexao.commit()

    # ----- Configurações (ex.: saldo inicial da carteira) -----

    def obter_configuracao(self, chave: str) -> Optional[float]:
        linha = self.__conexao.execute(
            "SELECT valor FROM configuracoes WHERE chave = ?", (chave,)
        ).fetchone()
        return linha["valor"] if linha is not None else None

    def definir_configuracao(self, chave: str, valor: float) -> None:
        with self.__conexao:
            self.__conexao.execute(
                "INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)",
                (chave, valor),
            )

    # ----- Metas -----

    def inserir_meta(self, objetivo: float, saldo_inicial: float) -> int:
        with self.__conexao:
            cursor = self.__conexao.execute(
                "INSERT INTO metas (objetivo, saldo_inicial) VALUES (?, ?)",
                (objetivo, saldo_inicial),
            )
        return cursor.lastrowid

    def carregar_metas(self) -> List[MetaFinanceira]:
        linhas = self.__conexao.execute(
            "SELECT id, objetivo, saldo_inicial FROM metas ORDER BY id"
        ).fetchall()
        metas = []
        for linha in linhas:
            meta = MetaFinanceira(linha["objetivo"], linha["saldo_inicial"])
            meta.definir_id(linha["id"])
            metas.append(meta)
        return metas

    def atualizar_meta(self, meta_id: int, objetivo: float, saldo_inicial: float) -> None:
        with self.__conexao:
            self.__conexao.execute(
                "UPDATE metas SET objetivo = ?, saldo_inicial = ? WHERE id = ?",
                (objetivo, saldo_inicial, meta_id),
            )

    def remover_meta(self, meta_id: int) -> None:
        with self.__conexao:
            self.__conexao.execute("DELETE FROM metas WHERE id = ?", (meta_id,))

    # ----- Categorias -----

    def inserir_categoria(self, nome: str, limite_orcamento: float) -> int:
        with self.__conexao:  # 'with' confirma (commit) a operação ao final
            cursor = self.__conexao.execute(
                "INSERT INTO categorias (nome, limite_orcamento) VALUES (?, ?)",
                (nome, limite_orcamento),
            )
        return cursor.lastrowid

    def carregar_categorias(self) -> List[Categoria]:
        linhas = self.__conexao.execute(
            "SELECT id, nome, limite_orcamento FROM categorias ORDER BY id"
        ).fetchall()
        categorias = []
        for linha in linhas:
            categoria = Categoria(linha["nome"], linha["limite_orcamento"])
            categoria.definir_id(linha["id"])
            categorias.append(categoria)
        return categorias

    def atualizar_categoria(self, categoria_id: int, nome: str, limite_orcamento: float) -> None:
        with self.__conexao:
            self.__conexao.execute(
                "UPDATE categorias SET nome = ?, limite_orcamento = ? WHERE id = ?",
                (nome, limite_orcamento, categoria_id),
            )

    def remover_categoria(self, categoria_id: int) -> None:
        # Apaga antes as despesas da categoria, para não sobrar registro órfão no banco
        with self.__conexao:
            self.__conexao.execute("DELETE FROM transacoes WHERE categoria_id = ?", (categoria_id,))
            self.__conexao.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))

    # ----- Movimentações -----

    def inserir_transacao(self, registro: dict) -> int:
        with self.__conexao:
            cursor = self.__conexao.execute(
                """INSERT INTO transacoes (tipo, valor, descricao, data, fonte, categoria_id)
                   VALUES (:tipo, :valor, :descricao, :data, :fonte, :categoria_id)""",
                registro,
            )
        return cursor.lastrowid

    def carregar_transacoes(self, categorias_por_id: Dict[int, Categoria]) -> List[Transacao]:
        linhas = self.__conexao.execute("SELECT * FROM transacoes ORDER BY id").fetchall()
        # A própria Transacao decide qual subclasse cria cada linha (polimorfismo)
        return [Transacao.reconstruir(dict(linha), categorias_por_id) for linha in linhas]

    def atualizar_transacao(self, transacao_id: int, registro: dict) -> None:
        with self.__conexao:
            self.__conexao.execute(
                """UPDATE transacoes
                   SET valor = :valor, descricao = :descricao, data = :data,
                       fonte = :fonte, categoria_id = :categoria_id
                   WHERE id = :id""",
                {**registro, "id": transacao_id},
            )

    def remover_transacao(self, transacao_id: int) -> None:
        with self.__conexao:
            self.__conexao.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))

    def fechar(self) -> None:
        self.__conexao.close()