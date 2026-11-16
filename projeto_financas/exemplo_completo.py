"""Exemplo de execução não interativo: exercita todas as funcionalidades do
pacote financas_pkg e verifica os resultados com asserts.
"""
from financas_pkg import (
    Carteira,
    Categoria,
    Despesa,
    GeradorRelatorio,
    MetaFinanceira,
    Receita,
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
    titulo("3. Carteira: limite acumulado por categoria e bloqueios")

    essencial = Categoria("Essencial", 2000.0)
    lazer = Categoria("Lazer", 500.0)

    carteira = Carteira(1500.0)
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

    carteira = Carteira(100.0)
    # Dentro do limite da categoria, mas sem saldo para pagar.
    carteira.adicionar_transacao(Despesa(150.0, "Show", "09/11/2026", Categoria("Lazer", 500.0)))

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
    acompanhada = Carteira(500.0)
    acompanhada.criar_meta(1000.0, 200.0)
    meta_acompanhada = acompanhada.metas[0]
    assert abs(meta_acompanhada.calcular_progresso(acompanhada.transacoes) - 20.0) < 1e-9

    acompanhada.adicionar_transacao(Receita(300.0, "Freelance", "11/11/2026", "Cliente Y"))
    assert abs(meta_acompanhada.calcular_progresso(acompanhada.transacoes) - 50.0) < 1e-9

    acompanhada.adicionar_transacao(Despesa(100.0, "Mercado", "12/11/2026", Categoria("Essencial", 2000.0)))
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
    print("OK - relatório contém saldo, movimentações e progresso da meta")


def main() -> None:
    demo_polimorfismo()
    demo_categoria()
    carteira = demo_carteira()
    demo_saldo_insuficiente()
    demo_metas(carteira)
    demo_relatorio(carteira)
    print("\nTodas as funcionalidades foram executadas e verificadas com sucesso.")


if __name__ == "__main__":
    main()