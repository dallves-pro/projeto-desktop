"""Janelas de cadastro e edição (Toplevel).

JanelaBase: moldura comum (cartão, título, campos em grade e botões).
FormularioMovimentacao: molde (Template Method) de receita e despesa. A base monta
os campos comuns e salva. Cada subclasse define os campos extras e qual objeto cria.
"""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from financas_pkg import Despesa, Receita

from .componentes import rotulo
from .tema import CORES, formatar_moeda


class JanelaBase(tk.Toplevel):
    def __init__(self, app, titulo):
        super().__init__(app)
        self.app = app
        self.title(titulo)
        self.configure(bg=CORES["fundo"])
        self.resizable(False, False)
        self.transient(app)

        # Equivale à seção .secao: cartão branco com borda e espaçamento generoso
        self.corpo = tk.Frame(self, bg=CORES["card"], padx=22, pady=20,
                              highlightthickness=1, highlightbackground=CORES["borda"])
        self.corpo.pack(fill="both", expand=True, padx=16, pady=16)
        self.corpo.columnconfigure(1, weight=1)
        rotulo(self.corpo, titulo, fonte="subtitulo", cor=CORES["primaria_escura"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.linha = 1          # próxima linha livre da grade
        self.widgets = {}       # chave -> widget do campo
        self.opcoes = {}        # chave -> lista de (texto, valor) dos campos de escolha
        self.bind("<Escape>", lambda evento: self.destroy())
        try:
            self.grab_set()     # deixa esta janela modal, como um formulário de verdade
        except tk.TclError:
            pass                # em alguns sistemas o grab só funciona depois que a janela aparece

    def campo(self, chave, texto, valor="", opcoes=None, indice=0):
        """Adiciona um rótulo e um campo. Com 'opcoes', o campo vira uma lista de escolha."""
        rotulo(self.corpo, texto, cor=CORES["suave"], fonte="rotulo").grid(
            row=self.linha, column=0, sticky="w", padx=(0, 12), pady=(8, 2))
        if opcoes is None:
            widget = ttk.Entry(self.corpo, width=34)
            widget.insert(0, valor)
        else:
            widget = ttk.Combobox(self.corpo, width=32, state="readonly",
                                  values=[nome for nome, _ in opcoes])
            widget.current(indice)
            self.opcoes[chave] = opcoes
        widget.grid(row=self.linha, column=1, sticky="ew", pady=(8, 2))
        self.widgets[chave] = widget
        self.linha += 1

    def botoes(self, texto_confirmar, comando):
        barra = tk.Frame(self.corpo, bg=CORES["card"])
        barra.grid(row=self.linha, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(barra, text="Cancelar", style="Secundario.TButton",
                   command=self.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(barra, text=texto_confirmar, style="Primario.TButton",
                   command=comando).pack(side="left")
        self.bind("<Return>", lambda evento: comando())

    def ler_texto(self, chave):
        return self.widgets[chave].get().strip()

    def ler_numero(self, chave):
        """Converte o campo em número (aceita vírgula ou ponto). Devolve None se for inválido."""
        try:
            return float(self.ler_texto(chave).replace(",", "."))
        except ValueError:
            messagebox.showwarning("Valor inválido", "Digite um valor numérico válido.", parent=self)
            return None

    def escolha(self, chave):
        """Valor associado à opção selecionada no campo de escolha."""
        return self.opcoes[chave][self.widgets[chave].current()][1]


class FormularioMovimentacao(JanelaBase):
    """Molde comum de receita e despesa. As subclasses completam os métodos marcados abaixo."""

    titulo = "Movimentação"

    def __init__(self, app):
        super().__init__(app, self.titulo)
        self.campo("descricao", "Descrição")
        self.campo("data", "Data (DD/MM/AAAA)", date.today().strftime("%d/%m/%Y"))
        self.campo("valor", "Valor (R$)")
        self.montar_campos_extras()          # polimorfismo: cada subclasse decide
        self.botoes("Salvar", self.salvar)

    def montar_campos_extras(self):
        raise NotImplementedError

    def criar_transacao(self, valor):
        raise NotImplementedError

    def salvar(self):
        valor = self.ler_numero("valor")
        if valor is None:
            return
        transacao = self.criar_transacao(valor)
        ok = self.app.acao(self.app.carteira.adicionar_transacao, transacao, janela=self)
        if ok:
            self.destroy()


class FormularioReceita(FormularioMovimentacao):
    titulo = "Nova receita"

    def montar_campos_extras(self):
        self.campo("fonte", "Fonte pagadora")

    def criar_transacao(self, valor):
        return Receita(valor, self.ler_texto("descricao"),
                       self.ler_texto("data"), self.ler_texto("fonte"))


class FormularioDespesa(FormularioMovimentacao):
    titulo = "Nova despesa"

    def montar_campos_extras(self):
        categorias = self.app.carteira.categorias
        # O valor de cada opção é o próprio objeto Categoria da carteira (a comparação usa 'is')
        self.campo("categoria", "Categoria", opcoes=[(c.nome, c) for c in categorias])

    def criar_transacao(self, valor):
        return Despesa(valor, self.ler_texto("descricao"),
                       self.ler_texto("data"), self.escolha("categoria"))


class FormularioEdicao(JanelaBase):
    """Edita uma movimentação existente. Os campos vêm de alvo.campos_editaveis(),
    método polimórfico: receita devolve 'fonte', despesa devolve 'categoria_id'."""

    def __init__(self, app, alvo):
        super().__init__(app, "Editar movimentação")
        self.alvo = alvo
        atual = alvo.to_registro()
        for chave, texto_campo in alvo.campos_editaveis().items():
            if chave == "categoria_id":
                categorias = app.carteira.categorias
                indice = next(i for i, c in enumerate(categorias) if c.id == atual[chave])
                self.campo(chave, texto_campo,
                           opcoes=[(c.nome, c.id) for c in categorias], indice=indice)
            else:
                self.campo(chave, texto_campo, str(atual[chave]))
        self.botoes("Salvar alterações", self.salvar)

    def salvar(self):
        alteracoes = {}
        for chave in self.alvo.campos_editaveis():
            if chave == "valor":
                valor = self.ler_numero(chave)
                if valor is None:
                    return
                alteracoes[chave] = valor
            elif chave == "categoria_id":
                alteracoes[chave] = self.escolha(chave)
            else:
                alteracoes[chave] = self.ler_texto(chave)
        ok = self.app.acao(self.app.carteira.editar_transacao, self.alvo.id, alteracoes, janela=self)
        if ok:
            self.destroy()


class FormularioCategoria(JanelaBase):
    def __init__(self, app, categoria=None):
        super().__init__(app, "Editar categoria" if categoria else "Nova categoria")
        self.categoria = categoria
        self.campo("nome", "Nome", categoria.nome if categoria else "")
        self.campo("limite", "Limite de orçamento (R$)",
                   f"{categoria.limite_orcamento:.2f}" if categoria else "")
        self.botoes("Salvar", self.salvar)

    def salvar(self):
        limite = self.ler_numero("limite")
        if limite is None:
            return
        nome = self.ler_texto("nome")
        if self.categoria is None:
            ok = self.app.acao(self.app.carteira.criar_categoria, nome, limite, janela=self)
        else:
            ok = self.app.acao(self.app.carteira.editar_categoria,
                               self.categoria, nome, limite, janela=self)
        if ok:
            self.destroy()


class FormularioMeta(JanelaBase):
    def __init__(self, app, meta=None):
        super().__init__(app, "Editar meta" if meta else "Nova meta")
        self.meta = meta
        self.campo("objetivo", "Objetivo (R$)", f"{meta.objetivo:.2f}" if meta else "")
        self.campo("economizado", "Já economizado (R$)",
                   f"{meta.saldo_inicial:.2f}" if meta else "0")
        self.botoes("Salvar", self.salvar)

    def salvar(self):
        objetivo = self.ler_numero("objetivo")
        if objetivo is None:
            return
        economizado = self.ler_numero("economizado")
        if economizado is None:
            return
        if self.meta is None:
            ok = self.app.acao(self.app.carteira.criar_meta, objetivo, economizado, janela=self)
        else:
            ok = self.app.acao(self.app.carteira.editar_meta,
                               self.meta, objetivo, economizado, janela=self)
        if ok:
            self.destroy()


class JanelaDespesasCategoria(JanelaBase):
    """Somente leitura: lista as despesas de uma categoria e o total gasto."""

    def __init__(self, app, categoria):
        super().__init__(app, f"Despesas de {categoria.nome}")
        tabela = ttk.Treeview(self.corpo, show="headings", height=8,
                              columns=("descricao", "data", "valor"))
        for coluna, texto, largura, alinhamento in (
                ("descricao", "Descrição", 280, "w"),
                ("data", "Data", 110, "center"),
                ("valor", "Valor", 130, "e")):
            tabela.heading(coluna, text=texto)
            tabela.column(coluna, width=largura, anchor=alinhamento)
        for despesa in app.carteira.despesas_da_categoria(categoria):
            tabela.insert("", "end", values=(despesa.descricao, despesa.data,
                                             formatar_moeda(despesa.valor)))
        tabela.grid(row=self.linha, column=0, columnspan=2, sticky="nsew")
        self.linha += 1

        total = app.carteira.total_gasto_na_categoria(categoria)
        rotulo(self.corpo, f"Total gasto: {formatar_moeda(total)} "
                           f"de {formatar_moeda(categoria.limite_orcamento)}",
               cor=CORES["despesa"], fonte="negrito").grid(
            row=self.linha, column=0, columnspan=2, sticky="w", pady=(12, 0))
        self.linha += 1

        ttk.Button(self.corpo, text="Fechar", style="Primario.TButton",
                   command=self.destroy).grid(row=self.linha, column=0, columnspan=2,
                                              sticky="e", pady=(16, 0))