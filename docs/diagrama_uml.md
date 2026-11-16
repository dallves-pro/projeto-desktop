# Modelagem UML — "Gerenciador de Finanças Pessoais"

## 1. Diagrama de classes

```mermaid
classDiagram
    direction TB

    class Transacao {
        <<abstract>>
        -float valor
        -str descricao
        -str data
        +tipo()* str
        +efeito_no_saldo()* float
        +gasto_em(Categoria categoria)* float
        +validar(float saldo_atual, list transacoes)* Optional~str~
    }

    class Receita {
        -str fonte
        +tipo() str
        +efeito_no_saldo() float
        +gasto_em(Categoria categoria) float
        +validar(float saldo_atual, list transacoes) Optional~str~
    }

    class Despesa {
        -Categoria categoria
        +tipo() str
        +efeito_no_saldo() float
        +gasto_em(Categoria categoria) float
        +validar(float saldo_atual, list transacoes) Optional~str~
    }

    class Categoria {
        -str nome
        -float limite_orcamento
        +verificar_limite(float total_gasto) bool
    }

    class CalculadoraMixin {
        <<mixin>>
        +calcular_transacoes(list transacoes)$ float
        +calcular_progresso(float saldo_atual, float objetivo)$ float
    }

    class MetaFinanceira {
        -float objetivo
        -float saldo_inicial
        +saldo_atual(list transacoes) float
        +calcular_progresso(list transacoes) float
    }

    class Carteira {
        -float saldo_inicial
        -list transacoes
        -list metas
        +saldo() float
        +adicionar_transacao(Transacao t) void
        +criar_meta(float objetivo, float saldo_inicial) void
    }

    class GeradorRelatorio {
        +gerar_dados(Carteira carteira) str
    }

    %% Generalização (herança)
    Transacao <|-- Receita
    Transacao <|-- Despesa
    CalculadoraMixin <|-- Receita
    CalculadoraMixin <|-- Despesa
    CalculadoraMixin <|-- MetaFinanceira

    %% Associação: cada despesa pertence a uma categoria
    Despesa "0..*" --> "1" Categoria : pertence a

    %% Composição: metas nascem e morrem com a carteira
    Carteira "1" *-- "0..*" MetaFinanceira : possui

    %% Agregação: a carteira referencia as transações cadastradas
    Carteira "1" o-- "0..*" Transacao : registra

    %% Dependências
    MetaFinanceira ..> Transacao : acompanha
    GeradorRelatorio ..> Carteira : lê
```

### Pontos de polimorfismo

| Método (declarado em `Transacao`) | `Receita` | `Despesa` |
|---|---|---|
| `tipo()` | retorna `"Receita"` | retorna `"Despesa"` |
| `efeito_no_saldo()` | `+valor` | `-valor` |
| `gasto_em(categoria)` | `0` (receita nunca é gasto) | `valor`, se a categoria for a mesma; senão `0` |
| `validar(saldo_atual, transacoes)` | sempre aceita (`None`) | recusa se o total gasto na categoria, com esta despesa, exceder o limite; recusa se o saldo for insuficiente |

Os métodos marcados com `*` são **abstratos**: `Transacao` não pode ser instanciada diretamente, e cada subclasse é obrigada a implementá-los. Com isso, `CalculadoraMixin`, `Carteira`, `MetaFinanceira` e `GeradorRelatorio` tratam todas as movimentações pela mesma interface, exclusivamente por polimorfismo.

### Regras de funcionamento

- **Limite de categoria acumulado:** o limite de uma `Categoria` vale para o total gasto nela (soma das despesas já aceitas mais a nova), não para cada despesa isolada.
- **Progresso da meta:** `MetaFinanceira.saldo_atual(transacoes)` é o saldo inicial da meta mais o efeito líquido de todas as transações da carteira. O progresso é esse valor dividido pelo objetivo.

## 2. Diagrama de sequência — adição de uma transação

```mermaid
sequenceDiagram
    actor Usuario
    participant Menu as test_financas.py
    participant C as Carteira
    participant T as Transacao (Receita ou Despesa)

    Usuario->>Menu: informa os dados da movimentação
    Menu->>C: adicionar_transacao(t)
    C->>T: validar(saldo, transacoes)
    alt movimentação recusada
        T-->>C: motivo do bloqueio
        C-->>Menu: [BLOQUEADO] motivo
    else movimentação aceita
        T-->>C: None
        C->>C: transacoes.append(t)
        C->>T: tipo()
        C-->>Menu: [SUCESSO] tipo cadastrada
    end
```