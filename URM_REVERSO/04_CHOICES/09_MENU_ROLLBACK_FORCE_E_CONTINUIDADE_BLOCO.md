# 09 — Menu, `rollback="force"` e continuidade dos blocos de Choice

**Status:** 🟢 confirmado — Ren'Py 7.4.11.

## 1. Nova peça importante da árvore

A análise direta de `renpy-7.4.11-sdk/renpy/ast.py` revelou uma característica que precisa permanecer explícita na árvore de Choices: o próprio `renpy.ast.Menu` declara, por padrão, `rollback = "force"`.

Isso significa que o Menu não é apenas um ponto de interação. Ele também participa diretamente da política de criação de rollback do Ren'Py.

Portanto a relação temporal pode ser representada como:

```text
Menu / Choice
      ↓
interação
      ↓
checkpoint / rollback boundary
```

mas a criação efetiva do registro continua pertencendo ao `Context.run()` + `RollbackLog`, não ao `Menu.execute()` como uma chamada manual de `checkpoint()`.

## 2. `Menu.rollback = "force"`

Na classe `Menu`, o construtor padrão estabelece:

```python
self.rollback = "force"
```

O `Context.run()` considera a propriedade `node.rollback` ao decidir se deve forçar o início de um novo período de rollback.

Assim, uma Choice normal não precisa que o código da Choice faça manualmente:

```python
renpy.checkpoint(...)
```

A própria natureza do nó `Menu` informa ao executor que ele deve participar da política de rollback apropriada.

Isso complementa a descoberta anterior:

```text
Menu.execute()
   ↓
renpy.exports.menu()
   ↓
ui.interact()
   ↓
valor escolhido
   ↓
checkpoint(rv)
```

O `checkpoint(rv)` é uma operação do circuito de interação após a escolha; já `rollback="force"` é uma propriedade estrutural do nó que influencia a preparação do período de rollback no executor.

Essas duas coisas não devem ser confundidas.

## 3. O bloco da Choice continua depois do Menu

`Menu.chain(next)` faz duas coisas:

```text
Menu.next = next

para cada bloco de Choice:
    chain_block(block, next)
```

Logo, o bloco associado a uma Choice recebe a continuação `next` do Menu.

Exemplo:

```text
Menu
├── Choice A
│   └── block A ─────────┐
│                       │
├── Choice B             │
│   └── block B ────────┤
│                       ↓
└── next             continuação
```

Mas isso não significa que o bloco escolhido seja executado imediatamente durante `Menu.execute()`.

`Menu.execute()` primeiro estabelece o próximo nó padrão com:

```python
next_node(self.next)
```

e, após receber a escolha, substitui esse próximo nó pelo primeiro nó do bloco selecionado:

```python
next_node(self.items[choice][2][0])
```

Portanto a sequência é:

```text
Menu.execute()
    ↓
prepara self.next
    ↓
cria escolhas
    ↓
interação
    ↓
choice = índice retornado
    ↓
next_node(primeiro nó do bloco escolhido)
    ↓
Context.run()
    ↓
executa bloco escolhido
```

## 4. Por que `next` continua sendo importante

O encadeamento não é inútil só porque uma Choice foi selecionada.

Ele define a continuação estrutural dos blocos e fornece um caminho de saída quando não há uma alternativa selecionada.

O `Menu.execute()` possui explicitamente:

```python
if choice is not None:
    next_node(self.items[choice][2][0])
else:
    next_node(self.next)
```

Assim existem dois casos:

```text
Choice retornada
    ↓
primeiro nó do bloco escolhido

sem Choice
    ↓
Menu.next
```

## 5. `If` mantém a mesma lógica estrutural

O `If.chain(next)` também registra `self.next = next` e encadeia cada bloco condicional para a continuação.

Durante `If.execute()`:

```text
If
 ↓
next_node(self.next)
 ↓
avalia entradas
 ↓
primeira condição verdadeira
 ↓
next_node(block[0])
```

Se nenhuma condição for verdadeira, permanece o `self.next` inicialmente preparado.

Isso mostra um padrão geral do AST:

```text
nó de controle
    ↓
prepara continuação padrão
    ↓
avalia condição/resultado
    ↓
substitui o próximo nó quando necessário
```

`Menu` e `If` compartilham esse princípio, embora tenham semânticas diferentes.

## 6. Consequência para a árvore de Choices

Uma Choice não deve ser modelada apenas como:

```text
Choice → destino
```

O modelo mais fiel é:

```text
Menu
├── política de rollback do nó
├── itens
│   ├── label
│   ├── condition
│   └── block AST
├── next
└── execução
    ├── interação
    ├── retorno da escolha
    └── seleção do primeiro nó do bloco
```

Depois:

```text
block AST
   ↓
Node.execute()
   ↓
next_node(...)
   ↓
próximo nó
```

Isso reforça a separação entre **estrutura**, **interação** e **execução**.

## 7. Relação com a intervenção do URM

Agora podemos posicionar melhor a ação do `URMChoice`:

```text
Menu
 ↓
URMChoice interpreta Menu.items
 ↓
usuário seleciona
 ↓
URMChoice.Action
 ↓
rollback_is_fixed = False
 ↓
ChoiceReturn(...)
 ↓
ui.interact()
 ↓
valor da escolha
 ↓
checkpoint(rv)
 ↓
Menu.execute() continua para primeiro nó do bloco
```

O URM não precisa reproduzir `Menu.rollback = "force"` em seu objeto `URMChoice`. Essa propriedade pertence ao nó nativo do Ren'Py.

Da mesma forma, o URM não precisa executar o bloco manualmente.

## 8. Novo princípio para o futuro Wells

O Walkthrough deve observar a estrutura nativa do Menu e reutilizar as semânticas do Ren'Py sempre que possível.

Isso favorece:

```text
Ren'Py AST
   ↓
semântica nativa
   ↓
camada de leitura Wells
   ↓
apresentação / análise
```

em vez de:

```text
Ren'Py AST
   ↓
segundo motor criado pelo Wells
   ↓
resultado potencialmente divergente
```

A descoberta de `Menu.rollback = "force"` é especialmente relevante para a futura transplantação porque mostra que parte do comportamento de Choices está declarada no próprio AST e consumida pelo executor.

## 9. Classificação

- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** `Menu` possui `rollback = "force"` por padrão.
- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** `Menu.chain(next)` encadeia os blocos das alternativas para `next`.
- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** `Menu.execute()` prepara `self.next`, executa a interação e, quando há escolha, aponta para o primeiro nó do bloco escolhido.
- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** sem escolha, `Menu.execute()` aponta para `self.next`.
- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** `If.chain()` e `If.execute()` seguem o padrão de continuação padrão + substituição pelo bloco selecionado.
- 🟢 **CONFIRMADO — URM:** `URMChoice.Action` utiliza o circuito nativo de `ChoiceReturn` e não executa manualmente o conteúdo do bloco.
- 🟠 **HIPÓTESE/PROJETO:** o futuro Wells deve preservar `Menu` como dono da semântica de rollback/execução e atuar como camada de observação e apresentação, recorrendo à intervenção apenas onde a funcionalidade realmente exigir.

## 10. Conclusão

Esta descoberta fecha mais uma conexão entre a árvore estrutural e a árvore temporal.

O `Menu` é simultaneamente:

1. uma estrutura que contém alternativas;
2. um nó executável;
3. um ponto de interação;
4. um participante da política de rollback;
5. um distribuidor do fluxo para o bloco escolhido.

Portanto, compreender completamente Choices exige manter essas dimensões conectadas, sem reduzi-las a um único conceito de “botão de escolha”.
