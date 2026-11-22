# Gerenciador de Finanças Pessoais

## Descrição do projeto
O **Gerenciador de Finanças Pessoais** é uma aplicação desktop desenvolvida em Python para organizar a saúde financeira do usuário de forma simples e intuitiva. O projeto foi construído puramente sob o paradigma da **Programação Orientada a Objetos (POO)**.

O sistema permite registrar e monitorar entradas e saídas financeiras, categorizar despesas com o nome que o próprio usuário escolher para evitar estouros de orçamento e estabelecer metas de economia com acompanhamento contínuo de progresso. A aplicação gera relatórios consolidados para facilitar o controle do saldo e o planejamento financeiro individual.

Categorias, movimentações, saldo inicial e metas são salvos em um banco de dados SQLite, para que continuem disponíveis mesmo depois que o programa é encerrado. Categorias e movimentações podem ser editadas, além de cadastradas e removidas. O saldo inicial pode ser alterado, e as metas podem ser criadas, editadas e excluídas, pela opção "Saldo inicial e metas" do menu.

## Arquitetura e modelagem 
O projeto aplica conceitos fundamentais da orientação a objetos, garantindo encapsulamento, reutilização de código e separação de responsabilidades:

*   **Encapsulamento e validação:** A classe `Carteira` é a classe central. Ela utiliza atributos privados e métodos manipuladores para validar operações, impedir saldos negativos e barrar despesas que façam o total gasto na sua `Categoria` ultrapassar o limite de orçamento. Além disso, ela também impede a remoção de uma receita que deixaria o saldo negativo.
*   **Herança múltipla e generalização:** As movimentações (`Receita` e `Despesa`) herdam os atributos básicos da classe abstrata `Transacao` e as ferramentas de cálculo fornecidas pela classe `CalculadoraMixin`.
*   **Associação e composição:** A `Carteira` possui uma relação de composição com `MetaFinanceira` (as metas nascem e morrem com a carteira), uma relação de agregação com as categorias e transações cadastradas e uma associação com o `RepositorioFinancas`, que faz a gravação no banco de dados. 
*   **Persistência polimórfica:** Cada subclasse de `Transacao` sabe se converter em um registro do banco de dados (to_registro) e reconstruir a si mesma a partir dele (pertence_ao_registro e de_registro).
*   **Metas financeiras:** O progresso de cada `MetaFinanceira` é calculado sobre o valor economizado: o saldo inicial da meta somado ao efeito líquido (receitas menos despesas) de todas as transações da carteira. Por isso, o progresso sobe com receitas e cai com despesas.

## Estrutura do projeto
O código está organizado modularmente, separando o script de interface no terminal do pacote contendo as regras da lógica do projeto:

```text
docs/
└── diagrama_uml.md              # Diagramas de classes e de sequência (UML)
projeto_financas/
├── financas_pkg/                # Pacote com a lógica orientada a objetos
│   ├── __init__.py
│   ├── categoria.py             # Categoria de despesa (nome e limite de orçamento)
│   ├── calculadora_mixin.py     # Ferramenta dinâmica de cálculo
│   ├── transacao.py             # Classe base abstrata
│   ├── receita.py               # Especialização de 'Transacao'
│   ├── despesa.py               # Especialização associada a 'Categoria'
│   ├── meta_financeira.py       # Gestão de objetivos e progresso
│   ├── banco.py                 # Persistência em SQLite 
│   ├── carteira.py              # Classe central (CRUD e validações)
│   └── gerador_relatorio.py     # Consolidação de dados
├── exemplo_completo.py          # Execução não interativa que testa todas as funcionalidades
└── test_financas.py             # Script principal de execução (Menu interativo)
```

## Diagrama UML
A modelagem completa (diagrama de classes e diagrama de sequência) está em [`docs/diagrama_uml.md`](docs/diagrama_uml.md). O arquivo usa "Mermaid" e é renderizado automaticamente pelo GitHub.

## Como executar
Requer Python 3 e nenhuma dependência externa.

AVISO: Na primeira execução do menu, o arquivo financas.db é criado automaticamente na pasta 'projeto_financas'. Para apagar todos os dados, basta excluir esse arquivo.

```bash
cd projeto_financas

# Menu interativo
python test_financas.py

# Exemplo que executa e verifica todas as funcionalidades
python exemplo_completo.py
```
