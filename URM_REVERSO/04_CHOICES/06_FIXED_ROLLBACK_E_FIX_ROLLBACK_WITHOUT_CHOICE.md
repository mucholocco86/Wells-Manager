# Choices — fixed rollback e a hipótese `fix_rollback_without_choice`

## Objetivo

Investigar a hipótese levantada na etapa anterior de que existiria, no Ren'Py 7.4.11, um caminho chamado `fix_rollback_without_choice` responsável por explicar diretamente quando uma Choice fica bloqueada, liberada ou reutilizável durante fixed rollback.

Esta etapa usa somente:

- `renpy-7.4.11-sdk/` do repositório `mucholocco86/modulos`;
- o código URM 2.6.2 já extraído de `MOD_ANALISE.zip`;
- documentação de análise já registrada em `URM_REVERSO/`.

---

## 1. Resultado principal: o nome da função não foi encontrado no SDK 7.4.11

Foram procuradas as referências:

```text
fix_rollback_without_choice
fix_rollback
rollback_is_fixed
```

no repositório e na fonte do SDK disponível no projeto.

A busca por `fix_rollback_without_choice` não encontrou uma definição correspondente no Ren'Py 7.4.11 usado como referência.

### 🟢 CONFIRMADO — projeto

Não temos evidência no SDK 7.4.11 do projeto de uma função com esse nome que possa ser tratada como a peça responsável pelo comportamento de Choice durante fixed rollback.

### 🔴 DESCARTADO como premissa atual

Não devemos continuar tratando `fix_rollback_without_choice` como se fosse uma função confirmada do Ren'Py 7.4.11.

A expressão permaneceu nos documentos anteriores apenas como um caminho que ainda precisava ser investigado; esta investigação mostrou que o nome não pode ser usado como fundamento arquitetural sem uma fonte adicional que prove sua existência em outra versão/contexto.

---

## 2. A investigação muda de direção

A pergunta correta deixa de ser:

> "O que `fix_rollback_without_choice` faz?"

E passa a ser:

> "Quais mecanismos reais do Ren'Py 7.4.11 fazem uma Choice ficar sensível, insensível, selecionada por roll-forward ou novamente executável durante fixed rollback?"

Essa segunda pergunta pode ser respondida diretamente pelo código que encontramos.

---

## 3. A primeira peça real: `ChoiceActionBase.get_sensitive()`

O SDK 7.4.11 contém a lógica essencial:

```python
return (self.sensitive and not renpy.exports.in_fixed_rollback()
        or (not self.block_all and self.get_selected()))
```

Isso mostra que a sensibilidade da Choice não depende de uma função chamada `fix_rollback_without_choice`.

Ela depende de duas portas principais:

```text
                  ChoiceActionBase
                         │
                         ▼
                 get_sensitive()
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
    não está em fixed rollback    get_selected()
             │                       │
             ▼                       ▼
        sensitive normal       roll-forward correspondente
```

### 🟢 CONFIRMADO — Ren'Py 7.4.11

Em fixed rollback, a condição normal `self.sensitive` deixa de ser suficiente para habilitar a Choice.

A segunda parte da expressão pode reabilitar a ação quando a Choice é a correspondente ao estado de roll-forward e `block_all` permite isso.

---

## 4. A segunda peça real: `get_selected()`

O código encontrado é essencialmente:

```python
roll_forward = renpy.exports.roll_forward_info()
return renpy.exports.in_fixed_rollback() and roll_forward == self.value
```

Portanto a pergunta "qual Choice está sendo atravessada durante o roll-forward?" é respondida por uma comparação entre:

```text
estado fixed rollback
        +
valor de roll-forward
        +
valor da Choice
```

Não existe aqui uma procura por `Jump`, nem uma análise das consequências do bloco.

### 🟢 CONFIRMADO — Ren'Py 7.4.11

Uma Choice pode ser reconhecida como a Choice correspondente ao roll-forward porque seu `value` coincide com o valor fornecido por `roll_forward_info()` enquanto o contexto está em fixed rollback.

---

## 5. De onde vem `roll_forward_info()`

O `RollbackLog` mantém uma pilha/lista de informações de forward.

Durante rollback, quando um `Rollback` restaurado possui dados de forward, esses dados podem ser inseridos em `self.forward` junto do contexto correspondente.

Conceitualmente:

```text
ROLLBACK
   │
   ▼
restaura estado anterior
   │
   ├── restaura contexto
   │
   └── preserva dados forward
            │
            ▼
        self.forward
            │
            ▼
   roll_forward_info()
```

Isso explica por que uma Choice pode saber que existe uma seleção anterior que deve ser atravessada no caminho forward.

---

## 6. O que `fixed_rollback_boundary` realmente faz

Outra peça importante é `fix_rollback()`.

Ele não simplesmente faz:

```python
rollback_is_fixed = True
```

Em vez disso, estabelece um boundary baseado no contexto de uma entrada anterior do rollback log quando as condições permitem.

A arquitetura é aproximadamente:

```text
fix_rollback()
      │
      ▼
fixed_rollback_boundary
      │
      ▼
rollback posterior
      │
      ▼
restauração alcança o boundary
      │
      ▼
rollback_is_fixed = True
```

### 🟢 CONFIRMADO — Ren'Py 7.4.11

`fixed_rollback_boundary` e `rollback_is_fixed` são estados relacionados, mas não são a mesma coisa e não são ativados exatamente no mesmo momento.

Isso é uma distinção importante para não transformar a metáfora da "bússola" em uma explicação falsa do mecanismo.

---

## 7. O ponto que interessa ao URM

O URM executa, na sua `URMChoice.Action`, uma sequência equivalente a:

```python
renpy.game.log.rollback_is_fixed = False
return renpy.ui.ChoiceReturn(choice_value, choice_index)()
```

Temos duas operações diferentes aqui:

```text
URM
 │
 ├── altera estado fixed rollback
 │
 └── devolve ChoiceReturn ao Ren'Py
```

A segunda operação entrega a escolha ao mecanismo nativo.

A primeira remove explicitamente o estado `rollback_is_fixed` antes que a ChoiceReturn seja processada.

### 🟢 CONFIRMADO — URM

O URM modifica diretamente `rollback_is_fixed` nesse ponto.

### 🟢 CONFIRMADO — Ren'Py 7.4.11

`in_fixed_rollback()` consulta esse estado e o comportamento das ChoiceAction depende dele.

### 🟠 INTERPRETAÇÃO CONTROLADA

A leitura operacional mais forte é que o URM quer impedir que sua ação de seleção seja tratada como uma Choice presa ao estado de fixed rollback.

Mas não devemos escrever "o autor fez isso para X" como fato histórico, porque o código não contém esse comentário explicativo.

---

## 8. Isso responde a parte da teoria da `bússola`

A metáfora do usuário pode ser traduzida tecnicamente assim:

```text
Ren'Py normal
     │
     ▼
estado de rollback
     │
     ▼
fixed rollback?
     │
 ┌───┴────┐
 não      sim
 │         │
 ▼         ▼
Choice   ChoiceAction
normal   consulta estado
          + forward
```

O URM, em um ponto estratégico, faz:

```text
estado fixed rollback
        │
        ▼
URM força rollback_is_fixed = False
        │
        ▼
ChoiceReturn
        │
        ▼
Ren'Py continua o pipeline normal
```

Portanto a ideia de uma intervenção temporária está muito mais próxima do código do que parecia inicialmente.

Mas a formulação correta é:

> **O URM altera um estado interno do RollbackLog imediatamente antes de entregar uma ChoiceReturn ao mecanismo nativo.**

Não:

> "O URM desregula o motor inteiro."

A intervenção é específica e localizada.

---

## 9. Por que `ChoiceReturn` é crucial aqui

O URM poderia, em teoria, tentar executar diretamente o bloco AST da Choice.

Ele não faz isso.

Ele cria/devolve a mesma estrutura de Action que o Ren'Py usa para uma seleção:

```text
URMChoice.Action
       │
       ▼
rollback_is_fixed = False
       │
       ▼
ChoiceReturn(... )()
       │
       ▼
valor rv
       │
       ▼
Ren'Py Menu
       │
       ▼
checkpoint(rv)
       │
       ▼
resolve bloco escolhido
       │
       ▼
AST nativa
```

### 🟢 CONFIRMADO

Isso reforça a conclusão anterior: o URM interfere no estado do engine, mas deixa o engine executar a seleção e o bloco da Choice.

---

## 10. O que acontece quando a Choice está em fixed rollback

A lógica real encontrada pode ser resumida assim:

```text
                    ChoiceAction
                         │
                         ▼
                get_sensitive()
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     fixed rollback = não     fixed rollback = sim
              │                     │
              ▼                     ▼
       self.sensitive        get_selected()
                                    │
                                    ▼
                           roll_forward_info()
                                    │
                           ┌────────┴────────┐
                           ▼                 ▼
                       não coincide      coincide
                           │                 │
                           ▼                 ▼
                       bloqueada        potencialmente
                                        selecionável
```

A Choice, portanto, não é simplesmente "desligada" durante fixed rollback.

Existe uma rota especial para a Choice correspondente ao roll-forward.

---

## 11. A importância de `block_all`

A segunda parte da expressão:

```python
not self.block_all and self.get_selected()
```

mostra que mesmo uma Choice reconhecida como selecionada pelo roll-forward ainda está sujeita à configuração `block_all`.

Isso é uma pista importante para análises posteriores:

> **a reutilização de uma Choice durante fixed rollback não é uma propriedade absoluta; existem flags da própria Action que participam da decisão.**

Não devemos reduzir tudo a `rollback_is_fixed`.

---

## 12. Resultado para nossa teoria do `Jump`

Esta análise também ajuda indiretamente a separar dois conceitos que poderiam ser confundidos:

```text
Jump
 │
 └── aponta o fluxo para um target

ChoiceReturn
 │
 └── devolve o valor de uma escolha

RollbackLog
 │
 └── controla histórico, checkpoints, forward e fixed rollback
```

São mecanismos diferentes.

O URM pode tocar nos três em pontos diferentes, mas não devemos fundi-los em uma única "bússola" interna.

### 🟢 CONFIRMADO

`Jump` não é o mecanismo responsável pelo fixed rollback.

`ChoiceReturn` não é o mecanismo responsável por executar `Jump`.

`RollbackLog` não é o mecanismo responsável por descobrir `jumpTo`.

Cada peça tem seu próprio papel.

---

## 13. A teoria que foi descartada

Nossa hipótese inicial era aproximadamente:

```text
fixed rollback
      ↓
fix_rollback_without_choice()
      ↓
Choice bloqueada/liberada
```

O SDK 7.4.11 não confirmou essa arquitetura.

A arquitetura que temos evidência para afirmar é:

```text
RollbackLog
   │
   ├── rollback_is_fixed
   ├── fixed_rollback_boundary
   ├── forward
   ├── checkpoint()
   ├── begin()
   └── rollback()
             │
             ▼
      roll-forward info
             │
             ▼
ChoiceActionBase
   │
   ├── get_selected()
   └── get_sensitive()
```

Essa é a árvore que devemos seguir daqui em diante.

---

## 14. Consequência metodológica

Este caso é um exemplo perfeito da regra que adotamos para a arqueologia:

> **um nome ou uma hipótese não pode ser transformado em componente arquitetural antes de ser encontrado no código e seguido até suas utilizações.**

A expressão `fix_rollback_without_choice` parecia uma pista interessante.

Depois da busca, ela deixou de ser uma peça confirmada.

Isso não é uma perda.

É exatamente o tipo de resultado que queremos registrar no projeto:

```text
HIPÓTESE
   ↓
BUSCA NO SDK
   ↓
SEM EVIDÊNCIA
   ↓
NÃO INCORPORAR À ARQUITETURA
```

---

## 15. Estado da investigação após esta etapa

### 🟢 CONFIRMADO

- `ChoiceActionBase.get_sensitive()` trata fixed rollback de maneira especial.
- `get_selected()` usa `roll_forward_info()` e `self.value`.
- `block_all` participa da possibilidade de seleção durante fixed rollback.
- `fixed_rollback_boundary` é distinto de `rollback_is_fixed`.
- `rollback()` pode produzir dados na pilha `forward`.
- `checkpoint()` pode reconciliar estado com informações de forward durante fixed rollback.
- URM força `rollback_is_fixed = False` antes de executar sua `ChoiceReturn`.
- `ChoiceReturn` devolve o valor ao pipeline nativo do Menu.

### 🔴 DESCARTADO COMO COMPONENTE CONFIRMADO DO REN'PY 7.4.11

- `fix_rollback_without_choice` como função/mecanismo identificado no SDK.

### 🟠 AINDA ABERTO

- localização completa de todas as escritas em `did_interaction`;
- ciclo exato entre `interface.interact()`, `did_interaction`, `begin()` e criação da entrada seguinte;
- todos os caminhos específicos que chamam `fix_rollback()`;
- diferenças microscópicas entre rollback normal, fixed rollback e roll-forward em diferentes tipos de interação;
- origem exata de cada dado colocado em `Rollback.forward`.

---

## 16. Conclusão provisória

A análise **não encontrou uma função mágica responsável por liberar a Choice durante fixed rollback**.

Encontramos algo mais interessante: o Ren'Py possui uma cadeia distribuída de mecanismos em que:

```text
RollbackLog
   ↓
forward + boundary + rollback_is_fixed
   ↓
roll_forward_info()
   ↓
ChoiceActionBase.get_selected()
   ↓
ChoiceActionBase.get_sensitive()
```

E o URM entra nessa cadeia alterando `rollback_is_fixed` antes de entregar uma `ChoiceReturn` ao engine.

Portanto, por enquanto, a melhor explicação é:

> **o URM não precisa possuir uma função especial para "liberar uma Choice". Ele altera uma das condições que o próprio Ren'Py usa para decidir como uma Choice deve se comportar durante fixed rollback e então devolve a seleção ao pipeline nativo.**

Essa conclusão fortalece bastante nossa analogia da bússola: não encontramos o URM construindo uma segunda bússola; encontramos o URM alterando, em um ponto específico, uma condição que influencia para onde o mecanismo oficial deve continuar apontando.
