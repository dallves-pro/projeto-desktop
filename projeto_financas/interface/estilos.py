"""Estilos ttk (abas, tabelas, botões, barras e campos) sobre o tema 'clam'."""
from tkinter import font as tkfont
from tkinter import ttk

from .tema import CORES

# Preenchido por aplicar_estilos(). Os outros módulos leem daqui, ex.: FONTES["texto"]
FONTES: dict = {}


def _primeira_disponivel(root, familias, padrao):
    """Escolhe a primeira família de fonte instalada no computador do usuário."""
    disponiveis = set(tkfont.families(root))
    return next((familia for familia in familias if familia in disponiveis), padrao)


def aplicar_estilos(root):
    """Chame uma vez, logo depois de criar a janela principal e antes de criar os widgets."""
    texto = _primeira_disponivel(root, ("Segoe UI", "Helvetica", "Arial"), "Helvetica")
    mono = _primeira_disponivel(root, ("Consolas", "Courier New", "Courier"), "Courier")
    FONTES.update({
        "texto": (texto, 11),
        "negrito": (texto, 11, "bold"),
        "rotulo": (texto, 10),
        "selo": (texto, 9, "bold"),
        "subtitulo": (texto, 15, "bold"),
        "cabecalho_titulo": (texto, 26, "bold"),
        "cabecalho_texto": (texto, 12),
        "cabecalho_rotulo": (texto, 10),
        "cabecalho_valor": (texto, 16, "bold"),
        "mono": (mono, 10),
    })

    root.configure(bg=CORES["fundo"])
    estilo = ttk.Style(root)
    estilo.theme_use("clam")  # só o 'clam' aceita cores personalizadas em abas, barras e botões

    # Abas: equivalem a .navegacao a e .navegacao a.ativo
    estilo.configure("TNotebook", background=CORES["fundo"], borderwidth=0)
    estilo.configure("TNotebook.Tab", padding=(16, 8), font=FONTES["negrito"],
                     background=CORES["card"], foreground=CORES["suave"], borderwidth=0)
    estilo.map("TNotebook.Tab",
               background=[("selected", CORES["primaria"])],
               foreground=[("selected", "#ffffff")])

    # Tabelas: equivalem a .tabela th e .tabela td
    estilo.configure("Treeview", background=CORES["card"], fieldbackground=CORES["card"],
                     foreground=CORES["texto"], bordercolor=CORES["borda"],
                     rowheight=30, font=FONTES["texto"])
    estilo.configure("Treeview.Heading", background=CORES["tabela_cabecalho"],
                     foreground=CORES["primaria_escura"], font=FONTES["negrito"],
                     relief="flat", padding=(8, 6))
    estilo.map("Treeview",
               background=[("selected", CORES["selecao"])],
               foreground=[("selected", CORES["primaria_escura"])])
    estilo.map("Treeview.Heading", background=[("active", CORES["destaque"])])

    # Barras de progresso: equivalem a .barra-preenchimento (uma cor por estilo)
    for nome, cor in (("Principal", CORES["primaria"]),
                      ("Receita", CORES["receita"]),
                      ("Meta", CORES["meta"])):
        estilo.configure(f"{nome}.Horizontal.TProgressbar",
                         background=cor, troughcolor=CORES["barra"],
                         bordercolor=CORES["barra"], lightcolor=cor, darkcolor=cor,
                         thickness=12)

    # Botões: equivalem a .botao, .filtro e .filtro[aria-pressed="true"]
    # nome: (cor de fundo, cor do texto, cor ao passar o mouse)
    variantes = {
        "Primario": (CORES["primaria"], "#ffffff", CORES["primaria_escura"]),
        "Secundario": (CORES["card"], CORES["primaria"], CORES["destaque"]),
        "Perigo": (CORES["despesa"], "#ffffff", "#8f241c"),
    }
    for nome, (fundo, letra, ao_passar) in variantes.items():
        borda = CORES["primaria"] if nome == "Secundario" else fundo
        estilo.configure(f"{nome}.TButton", background=fundo, foreground=letra,
                         bordercolor=borda, lightcolor=fundo, darkcolor=fundo,
                         font=FONTES["negrito"], padding=(14, 7), relief="flat",
                         focusthickness=0)
        estilo.map(f"{nome}.TButton",
                   background=[("active", ao_passar), ("disabled", CORES["barra"])],
                   foreground=[("disabled", CORES["suave"])])

    # Campos: equivalem a .campo input e .campo select
    estilo.configure("TEntry", fieldbackground=CORES["card"], foreground=CORES["texto"],
                     bordercolor=CORES["entrada"], lightcolor=CORES["entrada"],
                     darkcolor=CORES["entrada"], padding=6, font=FONTES["texto"])
    estilo.configure("TCombobox", fieldbackground=CORES["card"], foreground=CORES["texto"],
                     bordercolor=CORES["entrada"], padding=6, font=FONTES["texto"])