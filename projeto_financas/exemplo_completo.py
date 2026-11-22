"""Exemplo de execução não interativo: exercita todas as funcionalidades do
pacote financas_pkg e verifica os resultados com asserts.
"""
import os
import tempfile

from financas_pkg import (
    Carteira,
    Categoria,
    Despesa,
    GeradorRelatorio,
    MetaFinanceira,
    Receita,
    RepositorioFinancas,
    Transacao,
)


def titulo(texto: str) -> None:
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def demo_polimorfismo() -> None:
    titulo("1. Hierarquia de transações (polimorfismo)")

    # Transacao é abstrata: não pode ser instanciada diretamente.
    try:
        Transacao(100.0, "teste", "01/01/2026")
        raise AssertionError("Transacao não deveria ser instanciável")
    except TypeError as erro:
        print(f"OK - Transacao é abstrata: {erro}")

    lazer = Categoria("Lazer", 500.0)
    movimentos = [
        Receita(3000.0, "Salário", "01/11/2026", "Empresa X"),
        Despesa(200.0, "Cinema", "02/11/2026", lazer),
    ]
    # Mesma interface para tipos diferentes: cada objeto responde pelo próprio comportamento.
    for t in movimentos:
        print(f"  {t.tipo():<8} | efeito no saldo: {t.efeito_no_saldo():+.2f} "
              f"| gasto em Lazer: {t.gasto_em(lazer):.2f}")

    assert [t.efeito_no_saldo() for t in movimentos] == [3000.0, -200.0]
    assert [t.gasto_em(lazer) for t in movimentos] == [0.0, 200.0]


def demo_categoria() -> None:
    titulo("2. Categoria (limite sobre o total gasto)")

    essencial = Categoria("Essencial", 2000.0)
    assert essencial.nome == "Essencial"
    assert essencial.verificar_limite(1200.0) is True
    assert essencial.verificar_limite(2000.0) is True    # exatamente no limite
    assert essencial.verificar_limite(2000.01) is False  # ultrapassa
    print(f"OK - categoria '{essencial.nome}' aceita até R$ 2000,00 no total")


def demo_carteira() -> Carteira:
    titulo("3. Carteira: categorias com nome livre, limite acumulado e bloqueios")

    # Banco em memória: funciona como o banco de arquivo, mas some ao fim do programa.
    carteira = Carteira(1500.0, RepositorioFinancas(":memory:"))
    essencial = carteira.criar_categoria("Essencial", 2000.0)
    lazer = carteira.criar_categoria("Lazer", 500.0)
    carteira.criar_meta(10000.0, 2000.0)

    carteira.adicionar_transacao(Receita(3000.0, "Salário", "01/11/2026", "Empresa X"))
    carteira.adicionar_transacao(Despesa(1200.0, "Aluguel", "05/11/2026", essencial))      # aceita: 1200 <= 2000
    carteira.adicionar_transacao(Despesa(800.0, "Cinema", "06/11/2026", lazer))            # bloqueada: 800 > 500
    carteira.adicionar_transacao(Despesa(2500.0, "Compra grande", "07/11/2026", essencial))  # bloqueada: 1200 + 2500 > 2000
    carteira.adicionar_transacao(Despesa(300.0, "Jantar", "08/11/2026", lazer))            # aceita: 300 <= 500
    carteira.adicionar_transacao(Despesa(250.0, "Teatro", "09/11/2026", lazer))            # bloqueada: 300 + 250 > 500
    carteira.adicionar_transacao(Despesa(200.0, "Café", "10/11/2026", lazer))              # aceita: 300 + 200 = 500 (no limite)

    assert len(carteira.transacoes) == 4, "apenas 4 movimentações devem ser aceitas"
    assert carteira.saldo == 2800.0, f"saldo esperado 2800.0, obtido {carteira.saldo}"
    print(f"OK - saldo final: R$ {carteira.saldo:.2f}")
    return carteira


def demo_saldo_insuficiente() -> None:
    titulo("4. Bloqueio por saldo insuficiente")

    carteira = Carteira(100.0, RepositorioFinancas(":memory:"))
    lazer = carteira.criar_categoria("Lazer", 500.0)
    # Dentro do limite da categoria, mas sem saldo para pagar.
    carteira.adicionar_transacao(Despesa(150.0, "Show", "09/11/2026", lazer))

    assert carteira.saldo == 100.0
    assert carteira.transacoes == []
    print("OK - despesa dentro do limite foi bloqueada por falta de saldo")


def demo_metas(carteira: Carteira) -> None:
    titulo("5. Metas acompanham as transações")

    # Carteira principal: saldo inicial da meta 2000 + receitas (3000) - despesas aceitas (1200 + 300 + 200).
    meta = carteira.metas[0]
    progresso = meta.calcular_progresso(carteira.transacoes)
    assert abs(progresso - 33.0) < 1e-9, f"progresso esperado 33%, obtido {progresso}"
    assert abs(meta.saldo_atual(carteira.transacoes) - 3300.0) < 1e-9
    print(f"OK - meta da carteira principal: {progresso:.2f}% (R$ 3300,00 de R$ 10000,00)")

    # Mostra que o progresso muda a cada transação registrada.
    acompanhada = Carteira(500.0, RepositorioFinancas(":memory:"))
    essencial = acompanhada.criar_categoria("Essencial", 2000.0)
    acompanhada.criar_meta(1000.0, 200.0)
    meta_acompanhada = acompanhada.metas[0]
    assert abs(meta_acompanhada.calcular_progresso(acompanhada.transacoes) - 20.0) < 1e-9

    acompanhada.adicionar_transacao(Receita(300.0, "Freelance", "11/11/2026", "Cliente Y"))
    assert abs(meta_acompanhada.calcular_progresso(acompanhada.transacoes) - 50.0) < 1e-9

    acompanhada.adicionar_transacao(Despesa(100.0, "Mercado", "12/11/2026", essencial))
    assert abs(meta_acompanhada.calcular_progresso(acompanhada.transacoes) - 40.0) < 1e-9
    print("OK - progresso sobe com receitas e cai com despesas (20% -> 50% -> 40%)")

    meta_sem_objetivo = MetaFinanceira(0.0, 500.0)
    assert meta_sem_objetivo.calcular_progresso([]) == 0.0
    print("OK - meta com objetivo zero retorna 0% (sem divisão por zero)")


def demo_relatorio(carteira: Carteira) -> None:
    titulo("6. Relatório consolidado")

    relatorio = GeradorRelatorio().gerar_dados(carteira)
    print(relatorio)

    assert "Saldo Consolidado: R$ 2800.00" in relatorio
    assert "[Receita] Salário" in relatorio
    assert "[Despesa] Aluguel" in relatorio
    assert "Meta 1: 33.00% de progresso (R$ 3300.00 de R$ 10000.00)" in relatorio
    print("OK - relatório contém saldo, categorias, movimentações e progresso da meta")



def demo_persistencia_e_crud() -> None:
    titulo("7. Banco de dados: persistência, remoção e exclusão de categorias")

    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "teste.db")

        # 1ª "execução" do programa: cadastra os dados e encerra.
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(0.0, repositorio)
        carteira.criar_categoria("Lazer", 500.0)
        carteira.criar_categoria("Mercado", 800.0)
        lazer = carteira.categorias[0]
        carteira.adicionar_transacao(Receita(100.0, "Freelance", "10/11/2026", "Cliente Y"))
        carteira.adicionar_transacao(Despesa(60.0, "Cinema", "11/11/2026", lazer))
        repositorio.fechar()

        # 2ª "execução": tudo precisa ter sido salvo no arquivo.
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(0.0, repositorio)
        assert [c.nome for c in carteira.categorias] == ["Lazer", "Mercado"]
        assert len(carteira.transacoes) == 2
        assert carteira.saldo == 40.0
        print("OK - categorias e movimentações sobreviveram ao reinício do programa")

        # Remover a receita deixaria o saldo negativo (40 - 100 < 0): deve ser bloqueado.
        receita = carteira.transacoes[0]
        assert carteira.remover_transacao(receita.id) is False
        assert len(carteira.transacoes) == 2

        # Remover a despesa é permitido e devolve o dinheiro ao saldo.
        despesa = carteira.transacoes[1]
        assert carteira.remover_transacao(despesa.id) is True
        assert carteira.saldo == 100.0
        print("OK - remoção de receita com saldo negativo bloqueada; remoção de despesa aceita")

        # Excluir a categoria 'Mercado' com uma despesa: a despesa vai junto.
        mercado = carteira.categorias[1]
        carteira.adicionar_transacao(Despesa(30.0, "Feira", "12/11/2026", mercado))
        assert carteira.saldo == 70.0
        assert carteira.remover_categoria(mercado) == 1
        assert [c.nome for c in carteira.categorias] == ["Lazer"]
        assert len(carteira.transacoes) == 1
        assert carteira.saldo == 100.0
        print("OK - excluir categoria remove também as suas despesas e atualiza o saldo")

        # Confere no banco que a exclusão também foi salva.
        repositorio.fechar()
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(0.0, repositorio)
        assert [c.nome for c in carteira.categorias] == ["Lazer"]
        assert len(carteira.transacoes) == 1
        assert carteira.saldo == 100.0
        repositorio.fechar()
        print("OK - após novo reinício, as exclusões continuam valendo")


def demo_saldo_e_metas_salvos() -> None:
    titulo("8. Saldo inicial e metas são salvos no banco")

    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "config.db")

        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(500.0, repositorio)
        carteira.criar_meta(1000.0, 100.0)
        repositorio.fechar()

        # Na nova execução, o valor padrão (9999) é ignorado: vale o que foi salvo.
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(9999.0, repositorio)
        assert carteira.saldo == 500.0
        assert len(carteira.metas) == 1, "a meta não pode ser duplicada"
        assert carteira.metas[0].objetivo == 1000.0
        assert carteira.metas[0].saldo_inicial == 100.0
        repositorio.fechar()
        print("OK - saldo inicial e meta foram salvos e recuperados sem duplicar")


def demo_edicoes() -> None:
    titulo("9. Edição de categorias e movimentações")

    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "edicao.db")
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(0.0, repositorio)
        mercado = carteira.criar_categoria("Mercado", 800.0)
        lazer = carteira.criar_categoria("Lazer", 500.0)
        carteira.adicionar_transacao(Receita(100.0, "Freelance", "10/11/2026", "Cliente Y"))
        carteira.adicionar_transacao(Despesa(60.0, "Cinema", "11/11/2026", lazer))
        receita, despesa = carteira.transacoes

        # Categoria: o limite não pode ficar abaixo do que já foi gasto (60).
        assert carteira.editar_categoria(lazer, "Lazer", 50.0) is False
        # Categoria: renomear e aumentar o limite mantém as despesas ligadas.
        assert carteira.editar_categoria(lazer, "Entretenimento", 600.0) is True
        assert carteira.total_gasto_na_categoria(lazer) == 60.0
        # Categoria: nome já usado por outra categoria é bloqueado.
        assert carteira.editar_categoria(lazer, "Mercado", 600.0) is False

        # Receita: reduzir o valor deixaria o saldo negativo (saldo 40 -> 50 - 60 = -10).
        assert carteira.editar_transacao(receita.id, {"valor": 50.0}) is False
        assert carteira.editar_transacao(receita.id, {"valor": 80.0, "descricao": "Freelance março"}) is True
        assert carteira.saldo == 20.0

        # Despesa: trocar de categoria move o gasto e o saldo fica certo.
        assert carteira.editar_transacao(despesa.id, {"categoria_id": mercado.id, "valor": 70.0}) is True
        assert carteira.total_gasto_na_categoria(mercado) == 70.0
        assert carteira.total_gasto_na_categoria(lazer) == 0.0
        assert carteira.saldo == 10.0
        # Despesa acima do limite da nova categoria é bloqueada.
        assert carteira.editar_transacao(despesa.id, {"valor": 900.0}) is False
        repositorio.fechar()

        # As alterações precisam ter sido gravadas no banco.
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(0.0, repositorio)
        # Categorias voltam ordenadas pelo id: Mercado (1) e Entretenimento (2)
        assert [c.nome for c in carteira.categorias] == ["Mercado", "Entretenimento"]
        assert carteira.saldo == 10.0
        assert carteira.transacoes[0].descricao == "Freelance março"
        assert carteira.total_gasto_na_categoria(carteira.categorias[0]) == 70.0
        repositorio.fechar()
        print("OK - edições de categoria e movimentação foram validadas e gravadas")

def demo_categoria_solta() -> None:
    titulo("10. Categoria criada fora da carteira é cadastrada automaticamente")

    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "solta.db")
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(1000.0, repositorio)

        # Categoria "solta" (sem id) numa despesa aceita: é cadastrada e gravada.
        solta = Categoria("Viagem", 1000.0)
        assert solta.id is None
        carteira.adicionar_transacao(Despesa(200.0, "Passagem", "12/11/2026", solta))
        assert solta.id is not None
        assert [c.nome for c in carteira.categorias] == ["Viagem"]
        assert carteira.saldo == 800.0

        # Categoria solta com nome já usado: bloqueada e nada é gravado.
        repetida = Categoria("viagem", 500.0)
        carteira.adicionar_transacao(Despesa(50.0, "Hotel", "13/11/2026", repetida))
        assert repetida.id is None
        assert len(carteira.transacoes) == 1

        # Despesa recusada (saldo insuficiente): a categoria nova NÃO pode ser gravada.
        cara = Categoria("Carro", 10000.0)
        carteira.adicionar_transacao(Despesa(5000.0, "Carro", "14/11/2026", cara))
        assert cara.id is None
        assert len(carteira.categorias) == 1
        repositorio.fechar()

        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(1000.0, repositorio)
        assert [c.nome for c in carteira.categorias] == ["Viagem"]
        assert carteira.saldo == 800.0
        repositorio.fechar()
        print("OK - categoria solta só é gravada quando a despesa é aceita")


def demo_alterar_saldo_e_metas() -> None:
    titulo("11. Alteração de saldo inicial e de metas (com persistência)")

    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "alteracoes.db")

        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(500.0, repositorio)
        carteira.criar_meta(1000.0, 100.0)
        carteira.adicionar_transacao(Receita(200.0, "Bônus", "10/11/2026", "Empresa X"))  # saldo 700
        assert carteira.saldo_inicial == 500.0

        # Saldo inicial: aceito se o saldo final continua positivo (100 + 200 = 300).
        assert carteira.alterar_saldo_inicial(100.0) is True
        assert carteira.saldo == 300.0
        # Saldo inicial que deixaria o saldo negativo (-500 + 200 = -300) é bloqueado.
        assert carteira.alterar_saldo_inicial(-500.0) is False
        assert carteira.saldo == 300.0

        # Meta: objetivo precisa ser maior que zero; valor economizado não pode ser negativo.
        meta = carteira.metas[0]
        assert carteira.editar_meta(meta, 0.0, 50.0) is False
        assert carteira.editar_meta(meta, 2000.0, -1.0) is False
        assert carteira.editar_meta(meta, 2000.0, 50.0) is True
        assert meta.objetivo == 2000.0 and meta.saldo_inicial == 50.0
        repositorio.fechar()

        # Após reiniciar, os valores alterados são os que valem (o padrão 9999 é ignorado).
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(9999.0, repositorio)
        assert carteira.saldo_inicial == 100.0
        assert carteira.saldo == 300.0
        assert len(carteira.metas) == 1
        assert carteira.metas[0].objetivo == 2000.0
        assert carteira.metas[0].saldo_inicial == 50.0
        repositorio.fechar()
        print("OK - saldo inicial e meta alterados, validados e gravados")


def demo_criar_e_excluir_metas() -> None:
    titulo("12. Criação e exclusão de metas (com persistência)")

    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "metas.db")

        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(0.0, repositorio)
        assert carteira.primeira_execucao is True

        # Dados inválidos não criam meta.
        assert carteira.criar_meta(0.0, 10.0) is None
        assert carteira.criar_meta(1000.0, -5.0) is None
        assert carteira.metas == []

        meta_a = carteira.criar_meta(1000.0, 100.0)
        meta_b = carteira.criar_meta(5000.0, 0.0)
        assert len(carteira.metas) == 2
        assert carteira.excluir_meta(meta_a) is True
        assert len(carteira.metas) == 1 and carteira.metas[0] is meta_b
        repositorio.fechar()

        # Na nova execução a meta excluída continua excluída e a meta restante é recuperada.
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(9999.0, repositorio)
        assert carteira.primeira_execucao is False
        assert [m.objetivo for m in carteira.metas] == [5000.0]
        assert carteira.excluir_meta(carteira.metas[0]) is True
        repositorio.fechar()

        # Sem metas, a execução seguinte NÃO recria a meta inicial.
        repositorio = RepositorioFinancas(caminho)
        carteira = Carteira(9999.0, repositorio)
        assert carteira.metas == []
        assert carteira.primeira_execucao is False
        repositorio.fechar()
        print("OK - metas criadas e excluídas; a meta inicial não volta após excluída")

def main() -> None:
    demo_polimorfismo()
    demo_categoria()
    carteira = demo_carteira()
    demo_saldo_insuficiente()
    demo_metas(carteira)
    demo_relatorio(carteira)
    demo_persistencia_e_crud()
    demo_saldo_e_metas_salvos()
    demo_edicoes()
    demo_categoria_solta()
    demo_alterar_saldo_e_metas()
    demo_criar_e_excluir_metas()
    print("\nTodas as funcionalidades foram executadas e verificadas com sucesso.")


if __name__ == "__main__":
    main()