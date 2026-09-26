# Choices — seleção, fixed rollback e fronteira com o Ren'Py

## Objetivo

Registrar o comportamento do URM na seleção de uma Choice sem confundir responsabilidades do mod com responsabilidades do motor.

## Fluxo interno do URM

```text
ChoicesClass
    ↓
URMChoice
    ↓
Action
    ↓
rollback_is_fixed = False
    ↓
renpy.ui.ChoiceReturn(original_text, index)()
```

Até aqui, a sequência é código do URM.

## O que acontece depois

A partir de `ChoiceReturn`, a continuação pertence ao Ren'Py:

```text
URMChoice.Action
    ↓
Ren'Py ChoiceReturn
    ↓
interação/menu
    ↓
valor da Choice
    ↓
Menu.execute()
    ↓
primeiro nó do bloco selecionado
```

O URM não precisa reproduzir a execução do bloco para fazer a seleção.

## Relação com rollback

No Ren'Py 7.4.11, a interação informa ao `RollbackLog` que ocorreu uma interação; checkpoints são usados para registrar pontos de rollback/roll-forward. `ChoiceReturn` também possui consultas relacionadas a fixed rollback e roll-forward.

No URM, a linha:

```python
renpy.game.log.rollback_is_fixed = False
```

é executada imediatamente antes de `ChoiceReturn`.

### Classificação atual

- 🟢 **CONFIRMADO — URM:** o URM força `rollback_is_fixed` para `False` antes da seleção programática.
- 🔵 **CONFIRMADO — Ren'Py 7.4.11:** `ChoiceReturn.get_sensitive()` e `get_selected()` consultam `in_fixed_rollback()`/`roll_forward_info()`.
- 🟠 **HIPÓTESE FORTE:** a linha do URM permite que sua seleção programática passe pela mesma infraestrutura de Choice sem ficar limitada pelo estado de fixed rollback.
- 🔴 **NÃO CONFIRMADO:** a intenção original do autor além desse efeito mecânico.

## `did_interaction` não é o checkpoint

O SDK 7.4.11 mostra uma distinção importante:

```text
interação termina
    ↓
did_interaction = True
    ↓
próxima execução de nó
    ↓
RollbackLog.begin()
    ↓
novo período de rollback
```

O `did_interaction` é um sinal de que uma interação ocorreu. O checkpoint é uma operação separada.

Isso evita a interpretação incorreta:

```text
Choice → did_interaction → checkpoint
```

como se `did_interaction` fosse o próprio checkpoint.

## StoreMonitor e o circuito de `force_checkpoint`

Esta análise fechou o outro braço do circuito de estado.

### 🟢 URM — StoreMonitor

O callback Python do `StoreMonitor` faz, entre outras operações de monitoramento:

```python
renpy.game.context().force_checkpoint = True
```

Isso **não** chama `checkpoint()` diretamente e não cria por si só um objeto `Rollback`.

O StoreMonitor é, portanto, um **solicitante/observador de checkpoint** no caminho de alterações Python do Store.

### 🔵 Ren'Py 7.4.11 — Context → RollbackLog

O executor de `Context.run()` transfere essa solicitação para o `RollbackLog` quando o ciclo de execução decide atualizar o rollback:

```python
if self.rollback and self.force_checkpoint:
    renpy.game.log.force_checkpoint = True
    self.force_checkpoint = False
```

A sequência é:

```text
Python do jogo
    ↓
python_callbacks
    ↓
StoreMonitor
    ↓
Context.force_checkpoint = True
    ↓
Context.run()
    ↓
RollbackLog.force_checkpoint = True
```

### 🔵 Ren'Py 7.4.11 — `complete()` → `checkpoint()`

Ao completar o período atual, `RollbackLog.complete()` verifica a flag:

```python
if self.force_checkpoint:
    self.checkpoint(hard=False)
    self.force_checkpoint = False
```

Logo, o caminho completo é:

```text
StoreMonitor
    ↓
Context.force_checkpoint
    ↓
executor Ren'Py
    ↓
RollbackLog.force_checkpoint
    ↓
RollbackLog.complete()
    ↓
checkpoint(hard=False)
```

O checkpoint solicitado pelo `force_checkpoint` é um checkpoint **não-hard** (`hard=False`). Isso não deve ser confundido com a criação de um hard checkpoint ou com a criação direta de um novo período de rollback.

## Dois circuitos diferentes que podem se encontrar

A árvore de Choices deve preservar dois caminhos distintos:

### Circuito A — seleção da Choice

```text
Menu
  ↓
display_menu()
  ↓
ui.interact()
  ↓
ChoiceReturn
  ↓
valor da escolha
  ↓
checkpoint(rv)
  ↓
bloco escolhido
```

### Circuito B — alteração de estado Python

```text
Python node
  ↓
python_callbacks
  ↓
StoreMonitor
  ↓
Context.force_checkpoint
  ↓
RollbackLog.force_checkpoint
  ↓
complete()
  ↓
checkpoint(hard=False)
```

### Consequência arquitetural

O StoreMonitor **não é o sistema de rollback das Choices**.

Ele observa/intercepta alterações de estado no caminho Python. A seleção da Choice continua pertencendo à infraestrutura nativa de Menu/ChoiceReturn/checkpoint do Ren'Py.

Uma Choice pode, entretanto, levar à execução de Python que altera o Store; nesse caso os dois circuitos aparecem em sequência:

```text
CHOICE
  ↓
ChoiceReturn
  ↓
checkpoint da interação
  ↓
bloco escolhido
  ↓
Python
  ↓
StoreMonitor
  ↓
force_checkpoint
  ↓
checkpoint adicional do caminho de estado
```

Não devemos colapsar esses dois caminhos em um único mecanismo chamado genericamente de "rollback da Choice".

## Fixed rollback

`fix_rollback()` e `rollback_is_fixed` também não são a mesma operação.

No SDK 7.4.11, `fix_rollback()` estabelece uma fronteira; durante a operação de rollback, quando o contexto restaurado alcança a fronteira apropriada, o estado `rollback_is_fixed` pode ser ativado.

Consequentemente:

```text
fix_rollback()
    ≠
rollback_is_fixed = True
```

A primeira cria/define a condição de fronteira; a segunda representa o estado efetivo consultado pelo runtime.

## Correção de uma hipótese anterior

### 🔴 INCORRETO

> "O StoreMonitor cria o rollback da Choice."

A evidência do SDK 7.4.11 mostra que essa formulação mistura dois caminhos diferentes.

### Formulação correta

> **O URM intervém na seleção programática de uma Choice e, separadamente, o StoreMonitor observa alterações Python e solicita ao mecanismo de rollback do Ren'Py que marque um checkpoint não-hard.**

O dono do mecanismo de rollback continua sendo o Ren'Py.

## Por que isso importa para o URM

A linha do URM não deve ser traduzida para:

> "URM controla o rollback do Ren'Py."

A formulação mais precisa é:

> **O URM intervém em um estado de fixed rollback do Ren'Py imediatamente antes de devolver uma seleção ao mecanismo nativo de Choice.**

E, no caminho de alterações Python:

> **O URM usa o callback do Ren'Py para observar mudanças e solicitar um checkpoint por meio de `Context.force_checkpoint`, deixando a materialização do checkpoint para o `RollbackLog`.**

Isso preserva a fronteira arquitetural:

```text
Ren'Py = dono do rollback
URM    = observador/interventor pontual
```

## Regra para Wells

Na primeira reconstrução fiel:

1. preservar a chamada a `ChoiceReturn`;
2. preservar a alteração de `rollback_is_fixed` enquanto sua função mecânica não estiver totalmente fechada;
3. não criar um segundo sistema de rollback;
4. não substituir `did_interaction` por um suposto checkpoint;
5. não substituir `Context.force_checkpoint` por uma chamada direta a `checkpoint()`;
6. preservar a cadeia `StoreMonitor → Context.force_checkpoint → RollbackLog.force_checkpoint → complete() → checkpoint(hard=False)` enquanto a árvore completa não for encerrada;
7. não remover configurações do Ren'Py apenas por parecerem antigas ou indiretas.

A poda ou alteração dessas peças fica para uma etapa experimental posterior, depois que a árvore completa estiver documentada.
