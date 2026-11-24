"""Janela principal: cabeçalho, abas (painel, movimentações, categorias, metas e relatório)."""
import contextlib
import io
import tkinter as tk
from tkinter import messagebox, ttk

from financas_pkg import Carteira, GeradorRelatorio, RepositorioFinancas

from .componentes import Cabecalho, Cartao, Terminal, rotulo
from .estilos import FONTES, aplicar_estilos
from .formularios import (FormularioCategoria, FormularioDespesa, FormularioEdicao,
                          FormularioMeta, FormularioReceita, JanelaDespesasCategoria)
from .tema import CORES, formatar_moeda, formatar_percentual

FILTROS = (("todas", "Todas"), ("receita", "Receitas"), ("despesa", "Despesas"))


class JanelaPrincipal(tk.Tk):
    def __init__(self, caminho_banco):
        super().__init__()
        self.title("Gerenciador de Finanças Pessoais")
        self.geometry("1120x780")
        self.minsize(960, 680)
        aplicar_estilos(self)  # precisa vir antes de criar os widgets (preenche FONTES)

        self.repositorio = RepositorioFinancas(caminho_banco)
        self.carteira = Carteira(1500.0, self.repositorio)  # 1500 só vale na 1a execução
        if self.carteira.primeira_execucao:
            self.carteira.criar_meta(10000.0, 2000.0)

        self.aceitas = 0
        self.bloqueadas = 0
        self.filtro = "todas"
        self.construir()
        self.atualizar_telas()
        self.protocol("WM_DELETE_WINDOW", self.fechar)

    # ----- Montagem da tela -----

    def construir(self):
        self.cabecalho = Cabecalho(self)
        self.cabecalho.pack(fill="x")

        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=20, pady=16)
        self.aba_painel = tk.Frame(self.abas, bg=CORES["fundo"], padx=8, pady=8)
        self.aba_movimentacoes = tk.Frame(self.abas, bg=CORES["fundo"], padx=8, pady=8)
        self.aba_categorias = tk.Frame(self.abas, bg=CORES["fundo"], padx=8, pady=8)
        self.aba_metas = tk.Frame(self.abas, bg=CORES["fundo"], padx=8, pady=8)
        self.aba_relatorio = tk.Frame(self.abas, bg=CORES["fundo"], padx=8, pady=8)
        self.abas.add(self.aba_painel, text="Painel")
        self.abas.add(self.aba_movimentacoes, text="Movimentações")
        self.abas.add(self.aba_categorias, text="Categorias")
        self.abas.add(self.aba_metas, text="Saldo e metas")
        self.abas.add(self.aba_relatorio, text="Relatório")

        self.construir_painel()
        self.construir_movimentacoes()
        self.construir_categorias()
        self.construir_metas()
        self.construir_relatorio()

    def construir_painel(self):
        quadro = self.aba_painel
        rotulo(quadro, "Orçamento por categoria", fundo=CORES["fundo"],
               cor=CORES["primaria_escura"], fonte="subtitulo").pack(anchor="w")
        self.area_categorias = tk.Frame(quadro, bg=CORES["fundo"])
        self.area_categorias.pack(fill="x")

        rotulo(quadro, "Metas financeiras", fundo=CORES["fundo"],
               cor=CORES["primaria_escura"], fonte="subtitulo").pack(anchor="w", pady=(12, 0))
        self.area_metas = tk.Frame(quadro, bg=CORES["fundo"])
        self.area_metas.pack(fill="x")

        rotulo(quadro, "Registro das operações", fundo=CORES["fundo"],
               cor=CORES["primaria_escura"], fonte="subtitulo").pack(anchor="w", pady=(12, 0))
        self.terminal = Terminal(quadro, linhas=8)
        self.terminal.pack(fill="both", expand=True, pady=(4, 0))

    def construir_movimentacoes(self):
        quadro = self.aba_movimentacoes
        barra = tk.Frame(quadro, bg=CORES["fundo"])
        barra.pack(fill="x", pady=(0, 10))

        self.botoes_filtro = {}
        for chave, texto in FILTROS:
            botao = ttk.Button(barra, text=texto,
                               command=lambda c=chave: self.definir_filtro(c))
            botao.pack(side="left", padx=(0, 6))
            self.botoes_filtro[chave] = botao
        ttk.Button(barra, text="Remover", style="Perigo.TButton",
                   command=self.remover_movimentacao).pack(side="right")
        ttk.Button(barra, text="Editar", style="Secundario.TButton",
                   command=self.editar_movimentacao).pack(side="right", padx=6)
        ttk.Button(barra, text="+ Despesa", style="Primario.TButton",
                   command=self.nova_despesa).pack(side="right", padx=6)
        ttk.Button(barra, text="+ Receita", style="Primario.TButton",
                   command=self.nova_receita).pack(side="right")

        self.tabela_movimentacoes = ttk.Treeview(
            quadro, show="headings", selectmode="browse",
            columns=("numero", "tipo", "descricao", "categoria", "data", "valor", "efeito"))
        for coluna, texto, largura, alinhamento in (
                ("numero", "#", 60, "center"), ("tipo", "Tipo", 100, "w"),
                ("descricao", "Descrição", 260, "w"), ("categoria", "Categoria", 160, "w"),
                ("data", "Data", 110, "center"), ("valor", "Valor", 130, "e"),
                ("efeito", "Efeito no saldo", 150, "e")):
            self.tabela_movimentacoes.heading(coluna, text=texto)
            self.tabela_movimentacoes.column(coluna, width=largura, anchor=alinhamento)
        # Cores das linhas: a tag vem de chave_estilo(), método polimórfico de cada movimentação
        self.tabela_movimentacoes.tag_configure("receita", foreground=CORES["receita"])
        self.tabela_movimentacoes.tag_configure("despesa", foreground=CORES["despesa"])
        self.tabela_movimentacoes.pack(fill="both", expand=True)
        self.definir_filtro("todas")

    def construir_categorias(self):
        quadro = self.aba_categorias
        barra = tk.Frame(quadro, bg=CORES["fundo"])
        barra.pack(fill="x", pady=(0, 10))
        ttk.Button(barra, text="+ Categoria", style="Primario.TButton",
                   command=lambda: FormularioCategoria(self)).pack(side="left")
        ttk.Button(barra, text="Editar", style="Secundario.TButton",
                   command=self.editar_categoria).pack(side="left", padx=6)
        ttk.Button(barra, text="Ver despesas", style="Secundario.TButton",
                   command=self.ver_despesas).pack(side="left")
        ttk.Button(barra, text="Excluir", style="Perigo.TButton",
                   command=self.excluir_categoria).pack(side="right")

        self.tabela_categorias = ttk.Treeview(
            quadro, show="headings", selectmode="browse",
            columns=("nome", "limite", "gasto", "disponivel", "uso"))
        for coluna, texto, largura, alinhamento in (
                ("nome", "Categoria", 240, "w"), ("limite", "Limite", 150, "e"),
                ("gasto", "Gasto", 150, "e"), ("disponivel", "Disponível", 150, "e"),
                ("uso", "Uso do limite", 130, "e")):
            self.tabela_categorias.heading(coluna, text=texto)
            self.tabela_categorias.column(coluna, width=largura, anchor=alinhamento)
        self.tabela_categorias.pack(fill="both", expand=True)

    def construir_metas(self):
        quadro = self.aba_metas
        topo = tk.Frame(quadro, bg=CORES["fundo"])
        topo.pack(fill="x", pady=(0, 10))
        rotulo(topo, "Saldo inicial (R$)", fundo=CORES["fundo"],
               cor=CORES["suave"], fonte="rotulo").pack(side="left")
        self.campo_saldo = ttk.Entry(topo, width=16)
        self.campo_saldo.pack(side="left", padx=8)
        ttk.Button(topo, text="Alterar saldo inicial", style="Primario.TButton",
                   command=self.alterar_saldo).pack(side="left")

        barra = tk.Frame(quadro, bg=CORES["fundo"])
        barra.pack(fill="x", pady=(0, 10))
        ttk.Button(barra, text="+ Meta", style="Primario.TButton",
                   command=lambda: FormularioMeta(self)).pack(side="left")
        ttk.Button(barra, text="Editar", style="Secundario.TButton",
                   command=self.editar_meta).pack(side="left", padx=6)
        ttk.Button(barra, text="Excluir", style="Perigo.TButton",
                   command=self.excluir_meta).pack(side="left")

        self.tabela_metas = ttk.Treeview(
            quadro, show="headings", selectmode="browse",
            columns=("numero", "objetivo", "economizado", "progresso", "inicial"))
        for coluna, texto, largura, alinhamento in (
                ("numero", "#", 60, "center"), ("objetivo", "Objetivo", 170, "e"),
                ("economizado", "Economizado", 170, "e"), ("progresso", "Progresso", 130, "e"),
                ("inicial", "Saldo inicial da meta", 220, "e")):
            self.tabela_metas.heading(coluna, text=texto)
            self.tabela_metas.column(coluna, width=largura, anchor=alinhamento)
        self.tabela_metas.pack(fill="both", expand=True)

    def construir_relatorio(self):
        quadro = self.aba_relatorio
        barra = tk.Frame(quadro, bg=CORES["fundo"])
        barra.pack(fill="x", pady=(0, 10))
        ttk.Button(barra, text="Atualizar", style="Primario.TButton",
                   command=self.atualizar_relatorio).pack(side="left")
        self.texto_relatorio = tk.Text(
            quadro, bg=CORES["relatorio"], fg=CORES["texto"], font=FONTES["mono"],
            relief="flat", bd=0, padx=16, pady=12, wrap="none",
            highlightthickness=1, highlightbackground=CORES["borda"], state="disabled")
        self.texto_relatorio.pack(fill="both", expand=True)

    # ----- Execução das operações da carteira -----

    def executar(self, operacao, *argumentos):
        """Roda uma operação da carteira e captura as mensagens que ela imprime.

        Devolve (ok, linhas). ok é False se alguma linha começar com [BLOQUEADO] ou [ERRO].
        """
        captura = io.StringIO()
        with contextlib.redirect_stdout(captura):
            operacao(*argumentos)
        linhas = [linha for linha in captura.getvalue().splitlines() if linha.strip()]
        self.terminal.registrar(linhas)
        ok = not any(linha.startswith(("[BLOQUEADO]", "[ERRO]")) for linha in linhas)
        if ok:
            self.aceitas += 1
        else:
            self.bloqueadas += 1
        return ok, linhas

    def acao(self, operacao, *argumentos, janela=None):
        """Executa, mostra aviso se a carteira bloqueou e atualiza todas as telas."""
        ok, linhas = self.executar(operacao, *argumentos)
        if not ok:
            messagebox.showwarning("Operação bloqueada", "\n".join(linhas),
                                   parent=janela or self)
        self.atualizar_telas()
        return ok

    def atualizar_telas(self):
        self.cabecalho.definir_indicadores([
            ("Saldo final", formatar_moeda(self.carteira.saldo)),
            ("Total de receitas", formatar_moeda(self.carteira.total_receitas)),
            ("Total de despesas", formatar_moeda(self.carteira.total_despesas)),
            ("Aceitas / bloqueadas", f"{self.aceitas} / {self.bloqueadas}"),
        ])
        self.atualizar_painel()
        self.atualizar_movimentacoes()
        self.atualizar_categorias()
        self.atualizar_metas()
        self.atualizar_relatorio()

    # ----- Atualização de cada aba -----

    @staticmethod
    def esvaziar(quadro):
        for widget in quadro.winfo_children():
            widget.destroy()

    def atualizar_painel(self):
        self.esvaziar(self.area_categorias)
        for coluna in range(3):
            self.area_categorias.columnconfigure(coluna, weight=1, uniform="cartao")
        for i, categoria in enumerate(self.carteira.categorias):
            gasto = self.carteira.total_gasto_na_categoria(categoria)
            percentual = gasto / categoria.limite_orcamento * 100
            cartao = Cartao(self.area_categorias, cor_faixa=CORES["receita"])
            cartao.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            corpo = cartao.corpo
            rotulo(corpo, categoria.nome, fundo=CORES["cartao"],
                   cor=CORES["primaria_escura"], fonte="negrito").pack(anchor="w")
            rotulo(corpo, f"Limite: {formatar_moeda(categoria.limite_orcamento)}",
                   fundo=CORES["cartao"]).pack(anchor="w")
            rotulo(corpo, f"Gasto: {formatar_moeda(gasto)} "
                          f"({formatar_percentual(percentual)} do limite)",
                   fundo=CORES["cartao"]).pack(anchor="w")
            rotulo(corpo, f"Disponível: {formatar_moeda(categoria.limite_orcamento - gasto)}",
                   fundo=CORES["cartao"]).pack(anchor="w")
            ttk.Progressbar(corpo, style="Receita.Horizontal.TProgressbar",
                            maximum=100, value=min(percentual, 100)).pack(fill="x", pady=(8, 0))

        self.esvaziar(self.area_metas)
        for coluna in range(3):
            self.area_metas.columnconfigure(coluna, weight=1, uniform="meta")
        for i, meta in enumerate(self.carteira.metas):
            atual = meta.saldo_atual(self.carteira.transacoes)
            progresso = meta.calcular_progresso(self.carteira.transacoes)
            cartao = Cartao(self.area_metas, cor_faixa=CORES["meta"])
            cartao.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            corpo = cartao.corpo
            rotulo(corpo, f"Meta de {formatar_moeda(meta.objetivo)}", fundo=CORES["cartao"],
                   cor=CORES["primaria_escura"], fonte="negrito").pack(anchor="w")
            rotulo(corpo, f"Economizado: {formatar_moeda(atual)}",
                   fundo=CORES["cartao"]).pack(anchor="w")
            rotulo(corpo, f"Progresso: {formatar_percentual(progresso)}",
                   fundo=CORES["cartao"]).pack(anchor="w")
            ttk.Progressbar(corpo, style="Meta.Horizontal.TProgressbar",
                            maximum=100, value=max(0, min(progresso, 100))).pack(fill="x", pady=(8, 0))

    def atualizar_movimentacoes(self):
        tabela = self.tabela_movimentacoes
        tabela.delete(*tabela.get_children())
        for t in self.carteira.transacoes:
            if self.filtro not in ("todas", t.chave_estilo()):
                continue
            categoria = t.categoria_vinculada()  # None para receitas (polimorfismo)
            efeito = t.efeito_no_saldo()
            tabela.insert("", "end", iid=str(t.id), tags=(t.chave_estilo(),), values=(
                t.id, t.tipo(), t.descricao,
                categoria.nome if categoria is not None else "—",
                t.data, formatar_moeda(t.valor),
                ("+" if efeito > 0 else "") + formatar_moeda(efeito),
            ))

    def atualizar_categorias(self):
        tabela = self.tabela_categorias
        tabela.delete(*tabela.get_children())
        for c in self.carteira.categorias:
            gasto = self.carteira.total_gasto_na_categoria(c)
            tabela.insert("", "end", iid=str(c.id), values=(
                c.nome, formatar_moeda(c.limite_orcamento), formatar_moeda(gasto),
                formatar_moeda(c.limite_orcamento - gasto),
                formatar_percentual(gasto / c.limite_orcamento * 100),
            ))

    def atualizar_metas(self):
        self.campo_saldo.delete(0, "end")
        self.campo_saldo.insert(0, f"{self.carteira.saldo_inicial:.2f}")
        tabela = self.tabela_metas
        tabela.delete(*tabela.get_children())
        for numero, m in enumerate(self.carteira.metas, 1):
            tabela.insert("", "end", iid=str(m.id), values=(
                numero, formatar_moeda(m.objetivo),
                formatar_moeda(m.saldo_atual(self.carteira.transacoes)),
                formatar_percentual(m.calcular_progresso(self.carteira.transacoes)),
                formatar_moeda(m.saldo_inicial),
            ))

    def atualizar_relatorio(self):
        texto = GeradorRelatorio().gerar_dados(self.carteira)
        self.texto_relatorio.configure(state="normal")
        self.texto_relatorio.delete("1.0", "end")
        self.texto_relatorio.insert("1.0", texto)
        self.texto_relatorio.configure(state="disabled")

    # ----- Ações dos botões -----

    def definir_filtro(self, chave):
        self.filtro = chave
        for nome, botao in self.botoes_filtro.items():
            botao.configure(style="Primario.TButton" if nome == chave else "Secundario.TButton")
        self.atualizar_movimentacoes()

    def movimentacao_selecionada(self):
        selecao = self.tabela_movimentacoes.selection()
        if not selecao:
            messagebox.showinfo("Seleção", "Selecione uma movimentação na tabela.", parent=self)
            return None
        return self.carteira.buscar_transacao(int(selecao[0]))

    def nova_receita(self):
        FormularioReceita(self)

    def nova_despesa(self):
        if not self.carteira.categorias:
            messagebox.showinfo("Categorias", "Cadastre uma categoria antes de lançar despesas.",
                                parent=self)
            return
        FormularioDespesa(self)

    def editar_movimentacao(self):
        alvo = self.movimentacao_selecionada()
        if alvo is not None:
            FormularioEdicao(self, alvo)

    def remover_movimentacao(self):
        alvo = self.movimentacao_selecionada()
        if alvo is None:
            return
        if messagebox.askyesno("Remover movimentação", f"Remover '{alvo.descricao}'?", parent=self):
            self.acao(self.carteira.remover_transacao, alvo.id)

    def categoria_selecionada(self):
        selecao = self.tabela_categorias.selection()
        if not selecao:
            messagebox.showinfo("Seleção", "Selecione uma categoria na tabela.", parent=self)
            return None
        return next(c for c in self.carteira.categorias if c.id == int(selecao[0]))

    def editar_categoria(self):
        alvo = self.categoria_selecionada()
        if alvo is not None:
            FormularioCategoria(self, alvo)

    def ver_despesas(self):
        alvo = self.categoria_selecionada()
        if alvo is not None:
            JanelaDespesasCategoria(self, alvo)

    def excluir_categoria(self):
        alvo = self.categoria_selecionada()
        if alvo is None:
            return
        if messagebox.askyesno("Excluir categoria",
                               f"Excluir '{alvo.nome}' e todas as suas despesas?", parent=self):
            self.acao(self.carteira.remover_categoria, alvo)

    def alterar_saldo(self):
        try:
            novo_saldo = float(self.campo_saldo.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Valor inválido", "Digite um número válido para o saldo.",
                                   parent=self)
            return
        self.acao(self.carteira.alterar_saldo_inicial, novo_saldo)

    def meta_selecionada(self):
        selecao = self.tabela_metas.selection()
        if not selecao:
            messagebox.showinfo("Seleção", "Selecione uma meta na tabela.", parent=self)
            return None
        return next(m for m in self.carteira.metas if m.id == int(selecao[0]))

    def editar_meta(self):
        alvo = self.meta_selecionada()
        if alvo is not None:
            FormularioMeta(self, alvo)

    def excluir_meta(self):
        alvo = self.meta_selecionada()
        if alvo is None:
            return
        if messagebox.askyesno("Excluir meta", f"Excluir a meta de {formatar_moeda(alvo.objetivo)}?",
                               parent=self):
            self.acao(self.carteira.excluir_meta, alvo)

    def fechar(self):
        self.repositorio.fechar()
        self.destroy()