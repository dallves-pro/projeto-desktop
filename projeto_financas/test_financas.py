from typing import Optional

from financas_pkg import (
    Carteira,
    Categoria,
    Despesa,
    GeradorRelatorio,
    Receita,
    RepositorioFinancas,
)

ARQUIVO_BANCO = "financas.db"  # arquivo criado automaticamente na pasta projeto_financas


# ----- Leitura de dados -----

def ler_float(mensagem: str) -> Optional[float]:
    try:
        return float(input(mensagem))
    except ValueError:
        print("\n[ERRO] Digite um valor numerico valido.")
        return None


def ler_float_opcional(mensagem: str, atual: float) -> Optional[float]:
    # Enter mantém o valor atual
    texto = input(mensagem).strip()
    if not texto:
        return atual
    try:
        return float(texto)
    except ValueError:
        print("\n[ERRO] Digite um valor numerico valido.")
        return None


def ler_codigo(mensagem: str) -> Optional[int]:
    try:
        return int(input(mensagem))
    except ValueError:
        print("\n[ERRO] Digite um codigo numerico valido.")
        return None


# ----- Categorias -----

def cadastrar_categoria(carteira: Carteira) -> None:
    nome = input("Nome da nova categoria: ")
    limite = ler_float("Limite de orcamento: R$ ")
    if limite is not None:
        carteira.criar_categoria(nome, limite)


def visualizar_categorias(carteira: Carteira) -> None:
    categorias = carteira.categorias
    if not categorias:
        print("\nNenhuma categoria cadastrada ainda.")
        return

    print("\n--- CATEGORIAS CADASTRADAS ---")
    for i, c in enumerate(categorias, 1):
        gasto = carteira.total_gasto_na_categoria(c)
        print(f"{i}. {c.nome} | gasto R$ {gasto:.2f} de R$ {c.limite_orcamento:.2f}")

    escolha = input("Numero da categoria para acessar (Enter para voltar): ").strip()
    if not escolha:
        return
    if escolha.isdigit() and 1 <= int(escolha) <= len(categorias):
        menu_categoria(carteira, categorias[int(escolha) - 1])
    else:
        print("\n[ERRO] Opcao invalida.")


def menu_categoria(carteira: Carteira, categoria: Categoria) -> None:
     while True:
        print(f"\n--- CATEGORIA: {categoria.nome} (limite R$ {categoria.limite_orcamento:.2f}) ---")
        print("1. Adicionar despesa nesta categoria")
        print("2. Ver despesas desta categoria")
        print("3. Editar esta categoria (nome e limite)")
        print("4. Excluir esta categoria (com todas as suas despesas)")
        print("5. Voltar")
        opcao = input("Escolha uma opcao: ")
 
        if opcao == '1':
            adicionar_despesa(carteira, categoria)
        elif opcao == '2':
            listar_despesas(carteira, categoria)
        elif opcao == '3':
            editar_categoria(carteira, categoria)
        elif opcao == '4':
            if excluir_categoria(carteira, categoria):
                return  # a categoria não existe mais: volta ao menu principal
        elif opcao == '5':
            return
        else:
            print("\n[ERRO] Opcao invalida. Tente novamente.")


def adicionar_despesa(carteira: Carteira, categoria: Categoria) -> None:
    desc = input(f"Descricao da Despesa ({categoria.nome}): ")
    data = input("Data (DD/MM/AAAA): ")
    valor = ler_float("Valor: R$ ")
    if valor is not None:
        carteira.adicionar_transacao(Despesa(valor, desc, data, categoria))


def listar_despesas(carteira: Carteira, categoria: Categoria) -> None:
    despesas = carteira.despesas_da_categoria(categoria)
    if not despesas:
        print("\nNenhuma despesa nesta categoria.")
        return
    for d in despesas:
        print(f"  #{d.id} | {d.descricao} | R$ {d.valor:.2f} | {d.data}")
    print(f"  Total gasto: R$ {carteira.total_gasto_na_categoria(categoria):.2f}")


def editar_categoria(carteira: Carteira, categoria: Categoria) -> None:
    novo_nome = input(f"Novo nome (atual: {categoria.nome}; Enter mantem): ").strip() or categoria.nome
    novo_limite = ler_float_opcional(
        f"Novo limite (atual: R$ {categoria.limite_orcamento:.2f}; Enter mantem): R$ ",
        categoria.limite_orcamento,
    )
    if novo_limite is not None:
        carteira.editar_categoria(categoria, novo_nome, novo_limite)


def excluir_categoria(carteira: Carteira, categoria: Categoria) -> bool:
    quantidade = len(carteira.despesas_da_categoria(categoria))
    confirmacao = input(f"Excluir '{categoria.nome}' e {quantidade} despesa(s)? (s/n): ")
    if confirmacao.strip().lower() != 's':
        print("Exclusao cancelada.")
        return False
    carteira.remover_categoria(categoria)
    return True


def escolher_categoria(carteira: Carteira, atual_id: int) -> Optional[int]:
    categorias = carteira.categorias
    for i, c in enumerate(categorias, 1):
        marcador = "  (atual)" if c.id == atual_id else ""
        print(f"  {i}. {c.nome}{marcador}")
    escolha = input("Numero da nova categoria (Enter mantem a atual): ").strip()
    if not escolha:
        return atual_id
    if escolha.isdigit() and 1 <= int(escolha) <= len(categorias):
        return categorias[int(escolha) - 1].id
    print("\n[ERRO] Opcao invalida.")
    return None


# ----- Movimentações -----

def adicionar_receita(carteira: Carteira) -> None:
    desc = input("Descricao da Receita: ")
    data = input("Data (DD/MM/AAAA): ")
    fonte = input("Fonte pagadora: ")
    valor = ler_float("Valor: R$ ")
    if valor is not None:
        carteira.adicionar_transacao(Receita(valor, desc, data, fonte))


def listar_movimentacoes(carteira: Carteira) -> None:
    print("\n--- MOVIMENTACOES ---")
    for t in carteira.transacoes:
        print(f"  #{t.id} [{t.tipo()}] {t.descricao} | R$ {t.valor:.2f} | {t.data}")


def editar_movimentacao(carteira: Carteira) -> None:
    if not carteira.transacoes:
        print("\nNenhuma movimentacao cadastrada.")
        return
    listar_movimentacoes(carteira)

    codigo = ler_codigo("Codigo (#) da movimentacao a editar: ")
    if codigo is None:
        return
    alvo = carteira.buscar_transacao(codigo)
    if alvo is None:
        print("\n[ERRO] Nenhuma movimentacao com esse codigo.")
        return
 
    atual = alvo.to_registro()
    alteracoes = {}
    # O próprio objeto diz quais campos podem ser editados (polimorfismo)
    for chave, rotulo in alvo.campos_editaveis().items():
        if chave == "categoria_id":
            nova_categoria = escolher_categoria(carteira, atual["categoria_id"])
            if nova_categoria is None:
                return
            alteracoes[chave] = nova_categoria
        elif chave == "valor":
            novo_valor = ler_float_opcional(
                f"{rotulo} (atual: {atual[chave]:.2f}; Enter mantem): R$ ", atual[chave])
            if novo_valor is None:
                return
            alteracoes[chave] = novo_valor
        else:
            texto = input(f"{rotulo} (atual: {atual[chave]}; Enter mantem): ").strip()
            if texto:
                alteracoes[chave] = texto

    carteira.editar_transacao(codigo, alteracoes)


def remover_movimentacao(carteira: Carteira) -> None:
    if not carteira.transacoes:
        print("\nNenhuma movimentacao cadastrada.")
        return
    listar_movimentacoes(carteira)
    codigo = ler_codigo("Codigo (#) da movimentacao a remover: ")
    if codigo is not None:
        carteira.remover_transacao(codigo)


# ----- Saldo inicial e metas -----

def alterar_saldo_inicial(carteira: Carteira) -> None:
    novo_saldo = ler_float_opcional(
        f"Novo saldo inicial (atual: R$ {carteira.saldo_inicial:.2f}; Enter mantem): R$ ",
        carteira.saldo_inicial,
    )
    if novo_saldo is not None:
        carteira.alterar_saldo_inicial(novo_saldo)


def listar_metas(carteira: Carteira) -> None:
    if not carteira.metas:
        print("\nNenhuma meta cadastrada.")
        return
    print("\n--- METAS ---")
    for i, m in enumerate(carteira.metas, 1):
        atual = m.saldo_atual(carteira.transacoes)
        progresso = m.calcular_progresso(carteira.transacoes)
        print(f"{i}. Objetivo R$ {m.objetivo:.2f} | economizado R$ {atual:.2f} "
              f"| progresso {progresso:.2f}% | saldo inicial da meta R$ {m.saldo_inicial:.2f}")


def editar_meta(carteira: Carteira) -> None:
    if not carteira.metas:
        print("\nNenhuma meta cadastrada.")
        return
    listar_metas(carteira)

    numero = ler_codigo("Numero da meta a editar: ")
    if numero is None:
        return
    if not 1 <= numero <= len(carteira.metas):
        print("\n[ERRO] Opcao invalida.")
        return
    meta = carteira.metas[numero - 1]

    novo_objetivo = ler_float_opcional(
        f"Novo objetivo (atual: R$ {meta.objetivo:.2f}; Enter mantem): R$ ", meta.objetivo)
    if novo_objetivo is None:
        return
    novo_saldo_meta = ler_float_opcional(
        f"Valor ja economizado na meta (atual: R$ {meta.saldo_inicial:.2f}; Enter mantem): R$ ",
        meta.saldo_inicial)
    if novo_saldo_meta is None:
        return
    carteira.editar_meta(meta, novo_objetivo, novo_saldo_meta)


def cadastrar_meta(carteira: Carteira) -> None:
    objetivo = ler_float("Objetivo da meta: R$ ")
    if objetivo is None:
        return
    ja_economizado = ler_float_opcional("Valor ja economizado na meta (Enter = 0): R$ ", 0.0)
    if ja_economizado is None:
        return
    carteira.criar_meta(objetivo, ja_economizado)


def excluir_meta(carteira: Carteira) -> None:
    if not carteira.metas:
        print("\nNenhuma meta cadastrada.")
        return
    listar_metas(carteira)

    numero = ler_codigo("Numero da meta a excluir: ")
    if numero is None:
        return
    if not 1 <= numero <= len(carteira.metas):
        print("\n[ERRO] Opcao invalida.")
        return
    meta = carteira.metas[numero - 1]

    confirmacao = input(f"Excluir a meta de R$ {meta.objetivo:.2f}? (s/n): ")
    if confirmacao.strip().lower() != 's':
        print("Exclusao cancelada.")
        return
    carteira.excluir_meta(meta)


def menu_saldo_e_metas(carteira: Carteira) -> None:
    while True:
        print("\n--- SALDO INICIAL E METAS ---")
        print(f"Saldo inicial atual: R$ {carteira.saldo_inicial:.2f}")
        print("1. Alterar saldo inicial")
        print("2. Ver metas")
        print("3. Criar meta")
        print("4. Editar meta")
        print("5. Excluir meta")
        print("6. Voltar")
        opcao = input("Escolha uma opcao: ")

        if opcao == '1':
            alterar_saldo_inicial(carteira)
        elif opcao == '2':
            listar_metas(carteira)
        elif opcao == '3':
            cadastrar_meta(carteira)
        elif opcao == '4':
            editar_meta(carteira)
        elif opcao == '5':
            excluir_meta(carteira)
        elif opcao == '6':
            return
        else:
            print("\n[ERRO] Opcao invalida. Tente novamente.")


# ----- Programa principal -----
 
def workspace():
    repositorio = RepositorioFinancas(ARQUIVO_BANCO)
    minha_carteira = Carteira(1500.0, repositorio)  # 1500 só é usado na 1a execução
    if minha_carteira.primeira_execucao:
        minha_carteira.criar_meta(10000.0, 2000.0)  # meta inicial: criada só na 1a execução

    while True:
        print("\n--- MENU DE FINANCAS PESSOAIS ---")
        print("1. Cadastrar nova categoria de despesa")
        print("2. Visualizar categorias de despesa")
        print("3. Adicionar Receita")
        print("4. Editar movimentacao")
        print("5. Remover movimentacao")
        print("6. Saldo inicial e metas")
        print("7. Gerar Relatorio")
        print("8. Sair")

        opcao = input("Escolha uma opcao: ")

        if opcao == '1':
            cadastrar_categoria(minha_carteira)
        elif opcao == '2':
            visualizar_categorias(minha_carteira)
        elif opcao == '3':
            adicionar_receita(minha_carteira)
        elif opcao == '4':
            editar_movimentacao(minha_carteira)
        elif opcao == '5':
            remover_movimentacao(minha_carteira)
        elif opcao == '6':
            menu_saldo_e_metas(minha_carteira)
        elif opcao == '7':
            print(GeradorRelatorio().gerar_dados(minha_carteira))
        elif opcao == '8':
            repositorio.fechar()
            print("\nEncerrando o Gerenciador de Financas. Ate logo!")
            break

        else:
             print("\n[ERRO] Opcao invalida. Tente novamente.")
 



if __name__ == "__main__":
    workspace()