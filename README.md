# Gerenciador de Finanças Pessoais

## Descrição do projeto
O **Gerenciador de Finanças Pessoais** é uma aplicação desktop desenvolvida em Python para organizar a saúde financeira do usuário de forma simples e intuitiva. O projeto foi construído puramente sob o paradigma da **Programação Orientada a Objetos (POO)**.

O sistema permite registrar e monitorar entradas e saídas financeiras, categorizar despesas para evitar estouros de orçamento e estabelecer metas de economia com acompanhamento contínuo de progresso. A aplicação gera relatórios consolidados para facilitar o controle do saldo e o planejamento financeiro individual.

## Arquitetura e modelagem 
O projeto aplica conceitos fundamentais da orientação a objetos, garantindo encapsulamento, reutilização de código e separação de responsabilidades:

*   **Encapsulamento e validação:** A classe `Carteira` é a classe central. Ela utiliza atributos privados e métodos manipuladores para validar operações, impedir saldos negativos e barrar despesas que ultrapassam o limite da sua `Categoria`.
*   **Herança múltipla e generalização:** As movimentações (`Receita` e `Despesa`) herdam os atributos básicos da classe abstrata `Transacao` e as ferramentas de cálculo fornecidas pela classe `CalculadoraMixin`.
*   **Associação e composição:** A `Carteira` possui uma relação de composição com `MetaFinanceira` (as metas nascem e morrem com a carteira) e uma relação de agregação com as transações cadastradas. 

## Estrutura do projeto
O código está organizado modularmente, separando o script de interface no terminal do pacote contendo as regras da lógica do projeto:

```text
projeto_financas/
├── financas_pkg/                # Pacote com a lógica orientada a objetos
│   ├── __init__.py
│   ├── categoria.py             # Define os limites de orçamento
│   ├── calculadora_mixin.py     # Ferramenta dinâmica de cálculo
│   ├── transacao.py             # Classe base abstrata
│   ├── receita.py               # Especialização de 'Transacao'
│   ├── despesa.py               # Especialização associada a 'Categoria'
│   ├── meta_financeira.py       # Gestão de objetivos e progresso
│   ├── carteira.py              # Classe central (CRUD e validações)
│   └── gerador_relatorio.py     # Consolidação de dados 
└── test_financas.py             # Script principal de execução (Menu interativo)
