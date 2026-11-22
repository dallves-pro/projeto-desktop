# Modelagem UML — "Gerenciador de Finanças Pessoais"

## 1. Diagrama de classes

```mermaid
classDiagram
    direction TB

    class Transacao {
        <<abstract>>
        -str descricao
        -float valor
        -str data
        +id() int
        +definir_id(int id_) void
        +tipo()* str
        +efeito_no_saldo()* float
        +gasto_em(Categoria categoria)* float
        +validar(float saldo_atual, list transacoes)* Optional~str~
        +validar_remocao(float saldo_atual, list transacoes)* Optional~str~
        +categoria_vinculada()* Optional~Categoria~
        +campos_editaveis() dict
        +campos_especificos_editaveis()* dict
        +to_registro()* dict
        +pertence_ao_registro(dict registro)* bool
        +de_registro(dict registro, dict categorias_por_id)* Transacao
        +reconstruir(dict registro, dict categorias_por_id) Transacao
    }

    class Receita {
        +efeito_no_saldo() float
        +gasto_em(Categoria categoria) float
        +validar(float saldo_atual, list transacoes) Optional~str~
        +validar_remocao(float saldo_atual, list transacoes) Optional~str~
        +to_registro() dict
        +pertence_ao_registro(dict registro) bool
        +categoria_vinculada() Optional~Categoria~
        +campos_especificos_editaveis() dict
        +de_registro(dict registro, dict categorias_por_id) Receita
    }

    class Despesa {
        +efeito_no_saldo() float
        +gasto_em(Categoria categoria) float
        +validar(float saldo_atual, list transacoes) Optional~str~
        +validar_remocao(float saldo_atual, list transacoes) Optional~str~
        +to_registro() dict
        +pertence_ao_registro(dict registro) bool
        +categoria_vinculada() Optional~Categoria~
        +campos_especificos_editaveis() dict
        +de_registro(dict registro, dict categorias_por_id) Despesa
    }

    class Categoria {
        -int id
        -str nome
        -float limite_orcamento
        +definir_id(int id_) void
        +alterar(str nome, float limite_orcamento) void
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
        +alterar(float objetivo, float saldo_inicial) void
        +saldo_atual(list transacoes) float
        +calcular_progresso(list transacoes) float
    }

    class RepositorioFinancas {
        -Connection conexao
        +obter_configuracao(str chave) float
        +definir_configuracao(str chave, float valor) void
        +inserir_meta(float objetivo, float saldo_inicial) int
        +carregar_metas() list
        +inserir_categoria(str nome, float limite_orcamento) int
        +atualizar_categoria(int categoria_id, str nome, float limite_orcamento) void
        +carregar_categorias() list
        +remover_categoria(int categoria_id) void
        +inserir_transacao(dict registro) int
        +carregar_transacoes(dict categorias_por_id) list
        +remover_meta(int meta_id) void
        +atualizar_meta(int meta_id, float objetivo, float saldo_inicial) void
        +atualizar_transacao(int transacao_id, dict registro) void
        +remover_transacao(int transacao_id) void
        +fechar() void
    }

    class Carteira {
        -float saldo_inicial
        -list categorias
        -list transacoes
        -list metas
        +saldo() float
        +criar_categoria(str nome, float limite_orcamento) Categoria
        +remover_categoria(Categoria categoria) int
        +total_gasto_na_categoria(Categoria categoria) float
        +despesas_da_categoria(Categoria categoria) list
        +adicionar_transacao(Transacao t) void
        +remover_transacao(int transacao_id) bool
        +buscar_transacao(int transacao_id) Transacao
        +editar_categoria(Categoria categoria, str novo_nome, float novo_limite) bool
        +editar_transacao(int transacao_id, dict alteracoes) bool
        +saldo_inicial() float
        +alterar_saldo_inicial(float novo_saldo) bool
        +editar_meta(MetaFinanceira meta, float novo_objetivo, float novo_saldo_inicial) bool
        +criar_meta(float objetivo, float saldo_inicial) Optional~MetaFinanceira~
        +excluir_meta(MetaFinanceira meta) bool
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

    %% Agregação: a carteira referencia as categorias e as transações cadastradas
    Carteira "1" o-- "0..*" Categoria : cadastra
    Carteira "1" o-- "0..*" Transacao : registra

    %% Associação: a carteira grava e lê seus dados pelo repositório
    Carteira "1" --> "1" RepositorioFinancas : salva em

    %% Dependências
    MetaFinanceira ..> Transacao : acompanha
    RepositorioFinancas ..> Transacao : reconstrói via reconstruir
    GeradorRelatorio ..> Carteira : lê
```

### Pontos de polimorfismo

| Método (declarado em `Transacao`) | `Receita` | `Despesa` |
|---|---|---|
| `tipo()` | retorna `"Receita"` | retorna `"Despesa"` |
| `efeito_no_saldo()` | `+valor` | `-valor` |
| `gasto_em(categoria)` | `0` (receita nunca é gasto) | `valor`, se a categoria for a mesma; senão `0` |
| `validar(saldo_atual, transacoes)` | sempre aceita (`None`) | recusa se o total gasto na categoria, com esta despesa, exceder o limite; recusa se o saldo for insuficiente |
| `validar_remocao(saldo_atual, transacoes)` | recusa se o saldo ficar negativo após a remoção | sempre permite (`None`) |
| `to_registro()` | dicionário com `tipo = "Receita"` e `fonte` | dicionário com `tipo = "Despesa"` e `categoria_id` |
| `pertence_ao_registro(registro)` | responde `True` se o registro for do tipo `"Receita"` | responde `True` se o registro for do tipo `"Despesa"` |
| `de_registro(registro, categorias_por_id)` | cria uma `Receita` a partir do registro | cria uma `Despesa` ligada ao objeto `Categoria` correspondente |
| `categoria_vinculada()` | retorna `None` | retorna a própria categoria |
| `campos_especificos_editaveis()` | `fonte` (campo editável só de receitas) | `categoria_id` (campo editável só de despesas) |

Os métodos marcados com `*` são **abstratos**: `Transacao` não pode ser instanciada diretamente, e cada subclasse é obrigada a implementá-los. Com isso, `CalculadoraMixin`, `Carteira`, `RepositorioFinancas`, `MetaFinanceira` e `GeradorRelatorio` tratam todas as movimentações pela mesma interface, exclusivamente por polimorfismo. O método `reconstruir` percorre as subclasses e pergunta a cada uma se o registro é dela.

### Regras de funcionamento

- **Categorias com nome livre:** o usuário cria cada categoria com o nome e o limite de orçamento que escolher. Não podem existir duas categorias com o mesmo nome.
- **Limite de categoria acumulado:** o limite de uma `Categoria` vale para o total gasto nela (soma das despesas já aceitas mais a nova), não para cada despesa isolada.
- **Exclusão de categoria:** ao excluir uma categoria, todas as suas despesas são excluídas junto, e o saldo é recalculado.
- **Remoção de movimentação:** uma receita só pode ser removida se o saldo não ficar negativo; uma despesa sempre pode ser removida.
- **Progresso da meta:** `MetaFinanceira.saldo_atual(transacoes)` é o saldo inicial da meta mais o efeito líquido de todas as transações da carteira. O progresso é esse valor dividido pelo objetivo.
- **Edição:** categorias podem ser renomeadas e ter o limite alterado, desde que o limite não fique abaixo do total já gasto. Movimentações podem ter descrição, valor, data, fonte ou categoria alterados; a versão nova é validada contra as demais movimentações antes de ser gravada.
- **Categoria criada fora da carteira:** ao lançar uma despesa com uma categoria nova, ela só é cadastrada se a despesa passar em todas as validações.
- **Metas:** podem ser criadas, editadas e excluídas pelo menu. A meta inicial só é criada na primeira execução do programa, para que uma meta excluída não volte depois.
- **Saldo inicial e metas:** o saldo inicial pode ser alterado pelo menu. O saldo final da carteira não pode ficar negativo, e o objetivo da meta deve ser maior que zero.
- **Persistência:** inclusão, edição e remoção de movimentações e categorias são gravadas no banco SQLite (`financas.db`) no momento em que acontecem. O saldo inicial e as metas também são salvos (tabelas `configuracoes` e `metas`).

## 2. Diagrama de sequência — adição de uma transação

```mermaid
sequenceDiagram
    actor Usuario
    participant Menu as test_financas.py
    participant C as Carteira
    participant T as Transacao (Receita ou Despesa)
    participant R as RepositorioFinancas

    Usuario->>Menu: informa os dados da movimentação
    Menu->>C: adicionar_transacao(t)
    C->>T: validar(saldo, transacoes)
    alt movimentação recusada
        T-->>C: motivo do bloqueio
        C-->>Menu: [BLOQUEADO] motivo
    else movimentação aceita
        T-->>C: None
        C->>T: to_registro()
        T-->>C: dicionário do registro
        C->>R: inserir_transacao(registro)
        R-->>C: id gerado pelo banco
        C->>T: definir_id(id)
        C->>C: transacoes.append(t)
        C->>T: tipo()
        C-->>Menu: [SUCESSO] tipo cadastrada
    end
```