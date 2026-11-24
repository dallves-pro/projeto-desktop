"""Paleta de cores e formatação de valores da interface desktop.

Os valores de CORES são as variáveis CSS (:root) da folha financas.css do projeto
gerenciador-financas-bmvc. Para trocar o visual inteiro, edite apenas este arquivo.

Este módulo não importa tkinter: por isso pode ser testado em qualquer ambiente.
"""

CORES = {
    "fundo": "#f3f6fa",              # --cor-fundo
    "texto": "#1f2937",              # --cor-texto
    "suave": "#5b6676",              # --cor-suave
    "primaria": "#0f4c81",           # --cor-primaria
    "primaria_escura": "#0a3257",    # --cor-primaria-escura
    "receita": "#17804f",            # --cor-receita
    "despesa": "#b83227",            # --cor-despesa
    "alerta": "#b7791f",             # --cor-alerta
    "meta": "#6d28d9",               # --cor-meta
    "borda": "#dde4ee",              # --cor-borda
    "card": "#ffffff",               # --cor-card
    "cartao": "#fbfcfe",             # .cartao e .regra
    "tabela_cabecalho": "#f1f5fb",   # .tabela th
    "barra": "#e5ebf3",              # .barra (trilho da barra de progresso)
    "destaque": "#e8f0fa",           # hover de .navegacao a e de .botao
    "selecao": "#cfe0f3",            # linha selecionada (extensão própria)
    "entrada": "#c3cedd",            # borda de .campo input e .campo select
    "cabecalho_suave": "#e4eef9",    # .subtitulo
    "cabecalho_rotulo": "#cfe2f5",   # .indicadores dt
    "cabecalho_selo": "#bcd6f0",     # .selo
    "terminal": "#0e1726",           # .terminal
    "terminal_texto": "#d6e3f3",     # .terminal (texto)
    "terminal_aceita": "#7ee2a8",    # .linha-terminal.aceita
    "terminal_bloqueada": "#ffb98a", # .linha-terminal.bloqueada
    "relatorio": "#f4f7fb",          # .relatorio e .codigo
}

RAIO_CANTO = 12  # --raio: 12px. Usado nos cantos arredondados desenhados em Canvas.


def misturar(cor_a: str, cor_b: str, fracao: float) -> str:
    """Mistura duas cores no formato #rrggbb.

    fracao = 0 devolve cor_a; fracao = 1 devolve cor_b.
    Imita o rgba() do CSS: misturar(CORES["primaria"], "#ffffff", 0.12)
    equivale a rgba(255, 255, 255, 0.12) sobre o azul primário.
    """
    origem = [int(cor_a[i:i + 2], 16) for i in (1, 3, 5)]
    destino = [int(cor_b[i:i + 2], 16) for i in (1, 3, 5)]
    canais = [round(o + (d - o) * fracao) for o, d in zip(origem, destino)]
    return "#{:02x}{:02x}{:02x}".format(*canais)


def formatar_moeda(valor: float) -> str:
    """Converte 1234.5 em 'R$ 1.234,50' (separador de milhar com ponto, decimal com vírgula)."""
    texto = f"{valor:,.2f}"  # padrão americano: 1,234.50
    texto = texto.replace(",", "#").replace(".", ",").replace("#", ".")
    return f"R$ {texto}"


def formatar_percentual(valor: float) -> str:
    """Converte 37.5 em '37,5%'."""
    return f"{valor:.1f}%".replace(".", ",")