# Choices — ChoiceReturn, checkpoint e fixed rollback no Ren'Py 7.4.11

## Objetivo

Fechar o circuito entre a seleção de uma Choice pelo URM e os mecanismos nativos de interação e rollback do Ren'Py 7.4.11.

Fontes de referência:

- `renpy-7.4.11-sdk/renpy/ui.py`
- `renpy-7.4.11-sdk/renpy/python.py`
- `renpy-7.4.11-sdk/renpy/ast.py`
- código de `classes/choices.rpy` do URM 2.6.2

---

## 1. O URM não executa o bloco da Choice manualmente

A ação do URM é:

```python
renpy.game.log.rollback_is_fixed = False
return renpy.ui.ChoiceReturn(choice_value, choice_index)()
```

A consequência arquitetural é importante:

```text
URM UI
  ↓
URMChoice.Action
  ↓
ChoiceReturn
  ↓
retorno do valor da Choice
  ↓
Ren'Py resolve a interação
  ↓
Menu.execute()
  ↓
primeiro nó do bloco escolhido
  ↓
execução real
```

O URM não chama `Python.execute()`, `Jump.execute()`, `Call.execute()` etc. da alternativa para "simular" a escolha.

---

## 2. ChoiceReturn é uma Action e seu `__call__` devolve o valor

No SDK 7.4.11, `ui.Action.__call__()` é o contrato de execução de uma Action.

`ChoiceReturn.__call__()` registra a Choice como escolhida quando aplicável e retorna `self.value`.

Portanto o `ChoiceReturn` não é o executor do bloco da Choice.

Ele funciona como uma ponte entre a interface interativa e o valor que o mecanismo de Menu espera receber.

Modelo:

```text
Button / Action
      ↓
ChoiceReturn.__call__()
      ↓
value da Choice
      ↓
display_menu()
      ↓
Menu.execute()
```

---

## 3. O valor devolvido é diferente da execução do bloco

No `Menu.execute()` do Ren'Py 7.4.11, depois que a interação retorna o índice/valor da alternativa, o Menu direciona `next_node()` para o primeiro nó do bloco correspondente.

Isso produz uma separação precisa:

```text
ChoiceReturn
  = informa qual alternativa foi escolhida

Menu.execute
  = transforma essa escolha em continuação AST

AST do bloco
  = executa o comportamento da alternativa
```

Esta separação deve ser preservada no Wells.

---

## 4. `rollback_is_fixed` não é o mesmo que `force_checkpoint`

A investigação fechou uma distinção que estava pendente.

O `RollbackLog` mantém, entre outros estados:

```text
rollback_is_fixed
fixed_rollback_boundary
force_checkpoint
```

Eles possuem funções diferentes.

### `rollback_is_fixed`

É consultado por `in_fixed_rollback()` e representa o estado em que o histórico está atravessando uma região de fixed rollback.

### `force_checkpoint`

É uma solicitação para que o fechamento do processamento atual produza um checkpoint, mesmo quando o fluxo normal não produziria um naquele ponto.

Portanto:

```text
force_checkpoint ≠ rollback_is_fixed
```

Não devemos tratar os dois como duas formas do mesmo mecanismo.

---

## 5. Como `force_checkpoint` entra no ciclo

`RollbackLog.begin(force=False)` normalmente só inicia uma nova entrada de rollback quando houve interação, checkpoint anterior ou quando foi explicitamente forçado.

Quando `force=True`, o início não é ignorado.

Depois, `RollbackLog.complete()` verifica:

```python
if self.force_checkpoint:
    self.checkpoint(hard=False)
    self.force_checkpoint = False
```

Assim, o fluxo é:

```text
alguma operação define context.force_checkpoint = True
            ↓
execução continua
            ↓
complete()
            ↓
checkpoint(hard=False)
            ↓
force_checkpoint é limpo
```

O checkpoint forçado é, portanto, uma operação de fechamento/registro do estado, não uma indicação de que o rollback inteiro está "fixado".

---

## 6. StoreMonitor e `force_checkpoint`

O URM `StoreMonitor` também faz:

```python
renpy.game.context().force_checkpoint = True
```

no caminho do callback Python que processa mudanças no Store.

Isso não significa que o URM esteja criando diretamente uma entrada completa de rollback.

Ele sinaliza ao mecanismo nativo do Ren'Py que o checkpoint deve ser forçado no ciclo apropriado.

O Ren'Py continua responsável por chamar `complete()`, coletar mudanças de Store e registrar a entrada.

Essa é uma integração muito mais segura do que o URM manter uma cópia própria do histórico.

---

## 7. `checkpoint()` e fixed rollback

O `RollbackLog.checkpoint()` tem uma lógica específica quando:

```python
self.in_fixed_rollback() and self.forward
```

Nesse caso, ele pode consumir dados da pilha `forward` e associá-los ao checkpoint atual.

Fora desse caso, dados fornecidos explicitamente podem ser registrados e a pilha `forward` pode ser mantida ou limpa conforme as condições.

Isso mostra que fixed rollback está ligado ao relacionamento entre:

```text
log de rollback
forward stack
checkpoint
boundary
```

Não é apenas uma flag de UI.

---

## 8. Como o fixed rollback é estabelecido

`fix_rollback()` faz:

```python
if not self.rollback_is_fixed and len(self.log) > 1:
    self.fixed_rollback_boundary = self.log[-2].context.current
```

A flag `rollback_is_fixed` propriamente dita é ativada durante o processo de rollback quando uma entrada cujo contexto corresponde a `fixed_rollback_boundary` é restaurada.

Portanto existe uma sequência conceitual:

```text
fix_rollback()
   ↓
estabelece boundary
   ↓
rollback posterior
   ↓
entrada alcança boundary
   ↓
rollback_is_fixed = True
```

O mecanismo é histórico/contextual, não apenas visual.

---

## 9. Como o fixed rollback termina

Durante `RollbackLog.begin()`, o Ren'Py verifica o estado do histórico.

Se o contexto atual corresponde ao boundary, `rollback_is_fixed` pode ser liberado.

Existe também um segundo encerramento: se o sistema ainda estiver em fixed rollback, mas não houver dados `forward`, o mecanismo redefine o boundary para o contexto atual e desativa o estado fixo.

Modelo resumido:

```text
fixed rollback ativo
      ↓
begin()
      ├── alcançou boundary → libera
      │
      └── fixed + sem forward → encerra fixed rollback
```

---

## 10. Por que a linha do URM em `URMChoice.Action` agora faz sentido

O URM executa antes da seleção:

```python
renpy.game.log.rollback_is_fixed = False
```

Com a análise do SDK, podemos afirmar com segurança apenas isto:

### 🟢 CONFIRMADO — URM

O URM limpa explicitamente a flag de fixed rollback imediatamente antes de devolver a seleção por `ChoiceReturn`.

### 🟢 CONFIRMADO — Ren'Py 7.4.11

`rollback_is_fixed` é usado pelo RollbackLog para identificar o estado de fixed rollback e influencia operações como `checkpoint()` e `in_fixed_rollback()`.

### 🟠 INTERPRETAÇÃO TÉCNICA

A linha do URM é deliberadamente um bypass do estado fixado antes da escolha. Isso é coerente com o changelog do URM que registra suporte a bypass de fixed choices/fixed rollback.

### 🔴 NÃO DEVEMOS afirmar sem evidência adicional

Não devemos dizer que essa linha, sozinha, "desfaz o rollback", "cria um checkpoint" ou "restaura o jogo". Ela apenas altera a flag naquele instante. O restante do comportamento vem do ciclo nativo subsequente.

---

## 11. `checkpoint()` ocorre depois da interação, não como execução da Choice

A análise do pipeline mostra que o checkpoint é uma operação do sistema de rollback associada ao processamento do estado.

A escolha não precisa executar manualmente:

```text
checkpoint()
Python
If
Jump
Call
```

O mecanismo registra estado e a execução da AST ocorre pelo fluxo normal do Ren'Py.

Portanto:

```text
seleção
 ≠
execução manual
 ≠
checkpoint manual
```

São etapas distintas.

---

## 12. Forward stack e roll-forward

O RollbackLog possui uma pilha `forward`.

`forward_info()` só retorna informação quando o primeiro elemento corresponde ao contexto atual.

`checkpoint()` também possui lógica para consumir ou limpar essa pilha conforme o estado de fixed rollback e os dados registrados.

Isso explica por que a seleção de uma Choice durante uma situação de rollback não pode ser implementada apenas como:

```python
return ChoiceReturn(...)
```

sem considerar o estado de rollback.

O URM reconheceu esse problema e explicitamente mexe em `rollback_is_fixed` antes de sua ação.

---

## 13. Modelo fechado até aqui

```text
                 REN'PY MENU
                      │
                      ▼
             renpy.exports.menu
                      │
                      ▼
              display_menu / UI
                      │
                      ▼
                ui.interact
                      │
                      ▼
             ChoiceReturn.__call__
                      │
                      ▼
              valor da Choice
                      │
                      ▼
                Menu.execute
                      │
                      ▼
          primeiro nó do Choice block
                      │
                      ▼
              execução AST real
                      │
             ┌────────┴────────┐
             ▼                 ▼
          Store              Context
             │                 │
             ▼                 ▼
       mudanças / log      fluxo / rollback
             │                 │
             └────────┬────────┘
                      ▼
               RollbackLog
                      │
             ┌────────┼────────┐
             ▼        ▼        ▼
         checkpoint  forward  fixed boundary
```

E o URM entra assim:

```text
                Menu AST
                   │
                   ▼
             URM Choices
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
      text      condition   AST/code
        │          │          │
        └──────────┼──────────┘
                   ▼
                  UI
                   │
             seleção URM
                   │
                   ▼
       rollback_is_fixed = False
                   │
                   ▼
              ChoiceReturn
                   │
                   ▼
                Ren'Py
```

---

## 14. O que esta etapa elimina como hipótese

### 🔴 Eliminado

- URM executa manualmente o conteúdo da Choice.
- `ChoiceReturn` executa o bloco da Choice.
- `force_checkpoint` significa fixed rollback.
- `rollback_is_fixed` é apenas uma flag visual.
- `checkpoint()` é equivalente à seleção da Choice.

### 🟢 Confirmado

- ChoiceReturn devolve o valor da escolha ao mecanismo do Menu.
- Menu direciona a execução ao primeiro nó do bloco escolhido.
- Ren'Py mantém o rollback e o Store como mecanismos nativos.
- `force_checkpoint` solicita checkpoint forçado no ciclo de `complete()`.
- fixed rollback possui boundary e interação com a pilha `forward`.
- URM explicitamente limpa `rollback_is_fixed` antes da seleção.

### 🟠 Ainda em investigação

- ordem microscópica entre todos os eventos de interação, `checkpoint(rv)`, execução do primeiro nó e criação da próxima entrada de rollback;
- todos os casos de roll-forward/fixed rollback envolvendo uma Choice;
- diferenças de comportamento entre as versões Ren'Py que o URM tenta suportar;
- efeitos exatos de Choices marcadas/fixas em diferentes contextos de rollback.

---

## 15. Regra para o Wells

O Wells deve seguir o mesmo princípio arquitetural:

```text
Wells observa e apresenta.
Ren'Py seleciona, executa, registra e restaura.
```

Se o Wells precisar intervir numa Choice, a intervenção deve usar o mecanismo nativo de seleção e respeitar o estado de rollback da versão-alvo.

Não devemos reproduzir internamente o `RollbackLog`.

Não devemos executar o AST da Choice por conta própria.

Não devemos considerar `jumpTo`, `CodeView` ou `StoreMonitor` como substitutos do executor Ren'Py.
