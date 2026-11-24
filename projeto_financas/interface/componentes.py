"""Componentes visuais reutilizáveis: cabeçalho, cartão, rótulo e terminal de registro."""
import tkinter as tk

from .estilos import FONTES
from .tema import CORES, RAIO_CANTO, misturar

TITULO = "Gerenciador de Finanças Pessoais"
SUBTITULO = ("Registre entradas e saídas, controle o orçamento por categoria "
             "e acompanhe metas de economia.")
SELO = "PROGRAMAÇÃO ORIENTADA A OBJETOS · TKINTER"
ALTURA_CABECALHO = 230


def rotulo(master, texto, fundo=None, cor=None, fonte="texto"):
    """Rótulo com as cores e a fonte do tema. Sem 'fundo', usa a cor de cartão."""
    return tk.Label(master, text=texto, bg=fundo or CORES["card"],
                    fg=cor or CORES["texto"], font=FONTES[fonte],
                    anchor="w", justify="left")


def retangulo_arredondado(canvas, x0, y0, x1, y1, raio, **opcoes):
    """Retângulo com cantos arredondados: um polígono suavizado (smooth=True)."""
    pontos = [
        x0 + raio, y0, x1 - raio, y0, x1, y0, x1, y0 + raio,
        x1, y1 - raio, x1, y1, x1 - raio, y1, x0 + raio, y1,
        x0, y1, x0, y1 - raio, x0, y0 + raio, x0, y0,
    ]
    return canvas.create_polygon(pontos, smooth=True, **opcoes)


class Cabecalho(tk.Canvas):
    """Equivale ao <header class="cabecalho">: gradiente, título, subtítulo e indicadores."""

    def __init__(self, master):
        super().__init__(master, height=ALTURA_CABECALHO, highlightthickness=0, bd=0)
        self.indicadores = []  # lista de tuplas (rótulo, valor)
        self.bind("<Configure>", lambda evento: self.redesenhar())

    def definir_indicadores(self, indicadores):
        self.indicadores = indicadores
        self.redesenhar()

    def redesenhar(self):
        self.delete("all")
        largura, altura = self.winfo_width(), self.winfo_height()
        if largura < 2:
            return  # a janela ainda não foi desenhada

        # Gradiente vertical: uma linha horizontal por pixel de altura.
        # O CSS usa 135deg (diagonal); aqui o gradiente é vertical.
        for y in range(altura):
            cor = misturar(CORES["primaria_escura"], CORES["primaria"], y / altura)
            self.create_line(0, y, largura, y, fill=cor)

        margem = 32
        self.create_text(margem, 30, text=SELO, anchor="nw",
                         fill=CORES["cabecalho_selo"], font=FONTES["selo"])
        self.create_text(margem, 52, text=TITULO, anchor="nw",
                         fill="#ffffff", font=FONTES["cabecalho_titulo"])
        self.create_text(margem, 112, text=SUBTITULO, anchor="nw",
                         fill=CORES["cabecalho_suave"], font=FONTES["cabecalho_texto"],
                         width=largura - 2 * margem)

        # Indicadores: rgba(255,255,255,0.12) com borda rgba(255,255,255,0.20)
        if not self.indicadores:
            return
        espaco = 12
        n = len(self.indicadores)
        caixa = (largura - 2 * margem - espaco * (n - 1)) / n
        for i, (rotulo_indicador, valor) in enumerate(self.indicadores):
            x0 = margem + i * (caixa + espaco)
            x1 = x0 + caixa
            retangulo_arredondado(
                self, x0, 160, x1, 216, RAIO_CANTO,
                fill=misturar(CORES["primaria"], "#ffffff", 0.12),
                outline=misturar(CORES["primaria"], "#ffffff", 0.20))
            self.create_text(x0 + 16, 174, text=rotulo_indicador, anchor="nw",
                             fill=CORES["cabecalho_rotulo"], font=FONTES["cabecalho_rotulo"])
            self.create_text(x0 + 16, 190, text=valor, anchor="nw",
                             fill="#ffffff", font=FONTES["cabecalho_valor"])


class Cartao(tk.Frame):
    """Equivale a .cartao e .regra: fundo claro, borda fina e faixa colorida opcional à esquerda."""

    def __init__(self, master, cor_faixa=None):
        super().__init__(master, bg=CORES["cartao"],
                         highlightthickness=1, highlightbackground=CORES["borda"])
        if cor_faixa is not None:
            tk.Frame(self, bg=cor_faixa, width=5).pack(side="left", fill="y")
        self.corpo = tk.Frame(self, bg=CORES["cartao"], padx=16, pady=14)
        self.corpo.pack(side="left", fill="both", expand=True)


class Terminal(tk.Frame):
    """Equivale a .terminal: mensagens reais da carteira, coloridas pelo resultado."""

    def __init__(self, master, linhas=8):
        super().__init__(master, bg=CORES["terminal"])
        self.texto = tk.Text(self, height=linhas, bg=CORES["terminal"],
                             fg=CORES["terminal_texto"], font=FONTES["mono"],
                             relief="flat", bd=0, padx=14, pady=10, wrap="word",
                             highlightthickness=0, cursor="arrow", state="disabled")
        self.texto.pack(fill="both", expand=True)
        self.texto.tag_configure("aceita", foreground=CORES["terminal_aceita"])
        self.texto.tag_configure("bloqueada", foreground=CORES["terminal_bloqueada"])

    def registrar(self, linhas):
        self.texto.configure(state="normal")
        for linha in linhas:
            etiqueta = "aceita" if linha.startswith("[SUCESSO]") else "bloqueada"
            self.texto.insert("end", linha + "\n", etiqueta)
        self.texto.configure(state="disabled")
        self.texto.see("end")