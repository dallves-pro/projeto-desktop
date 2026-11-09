from financas_pkg import Categoria, Receita, Despesa, Carteira, GeradorRelatorio

def workspace():
    cat_essencial = Categoria("Essencial", 2000.0)
    cat_lazer = Categoria("Lazer", 500.0)
    
    minha_carteira = Carteira(1500.0)
    minha_carteira.criar_meta(10000.0, 2000.0)

    while True:
        print("\n--- MENU DE FINANCAS PESSOAIS ---")
        print("1. Adicionar Receita")
        print("2. Adicionar Despesa (Essencial)")
        print("3. Adicionar Despesa (Lazer)")
        print("4. Gerar Relatório")
        print("5. Sair")
        
        opcao = input("Escolha uma opcao: ")

        if opcao == '1':
            desc = input("Descricao da Receita: ")
            data = input("Data (DD/MM/AAAA): ")
            fonte = input("Fonte pagadora: ")
            try:
                valor = float(input("Valor: R$ "))
                nova_receita = Receita(valor, desc, data, fonte)
                minha_carteira.adicionar_transacao(nova_receita)
            except ValueError:
                print("\n[ERRO] Digite um valor numerico valido.")

        elif opcao in ['2', '3']:
            categoria_selecionada = cat_essencial if opcao == '2' else cat_lazer
            desc = input(f"Descricao da Despesa ({categoria_selecionada.nome}): ")
            data = input("Data (DD/MM/AAAA): ")
            try:
                valor = float(input("Valor: R$ "))
                nova_despesa = Despesa(valor, desc, data, categoria_selecionada)
                minha_carteira.adicionar_transacao(nova_despesa)
            except ValueError:
                print("\n[ERRO] Digite um valor numerico valido.")

        elif opcao == '4':
            relatorio = GeradorRelatorio()
            print(relatorio.gerar_dados(minha_carteira))

        elif opcao == '5':
            print("\nEncerrando o Gerenciador de Financas. Ate logo!")
            break
            
        else:
            print("\n[ERRO] Opcao invalida. Tente novamente.")

if __name__ == "__main__":
    workspace()