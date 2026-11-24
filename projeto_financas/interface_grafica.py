"""Ponto de entrada da interface gráfica.

Execute a partir da pasta projeto_financas:
    python interface_grafica.py

O banco financas.db é criado automaticamente nesta mesma pasta, como no menu de texto.
"""
import os

from interface.janela_principal import JanelaPrincipal

CAMINHO_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "financas.db")

JanelaPrincipal(CAMINHO_BANCO).mainloop()