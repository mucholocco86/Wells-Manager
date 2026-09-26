# Choices — microciclo de interação, checkpoint e roll-forward no Ren'Py 7.4.11

## Objetivo

Fechar a ordem operacional da Choice sem confundir três coisas diferentes:

1. retorno do valor escolhido;
2. registro/checkpoint de rollback;
3. continuação da execução da AST.

A análise é baseada exclusivamente no SDK `renpy-7.4.11-sdk/` do repositório e no código do URM 2.6.2 já extraído em `MOD_ANALISE.zip`.

---

## 1. A ordem real do Menu

No `Menu.execute()` do Ren'Py 7.4.11, o Menu prepara primeiro sua continuação normal (`self.next`) e então chama o mecanismo de menu.

O caminho relevante é:

```text
Menu.execute()
   │
   ├─ prepara next_node(self.next)
   │
   └─ renpy.exports.menu(...)
             │
             ▼
        display_menu(...)
             │
             ▼
        ChoiceReturn
             │
             ▼
        ui.interact()
             │
             ▼
        ChoiceReturn.__call__()
             │
             ▼
        rv = valor da Choice
             │
             ▼
        checkpoint(rv)
             │
             ▼
        display_menu retorna rv
             │
             ▼
        Menu.execute continua
             │
             ▼
        next_node(primeiro nó do bloco escolhido)
```

O ponto mais importante é que `checkpoint(rv)` está no processamento do resultado da interação, enquanto a execução do bloco escolhido acontece depois, no `Menu.execute()`.

---

## 2. O que `ChoiceReturn` realmente produz

`ChoiceReturn.__call__()` faz duas coisas no SDK 7.4.11:

```python
if self.chosen is not None:
    self.chosen[(self.location, self.label)] = True

return self.value
```

Portanto ele:

- registra a escolha como escolhida quando existe mecanismo de marcação;
- devolve o `value` associado à alternativa.

Ele não executa o bloco AST.

### 🟢 CONFIRMADO — Ren'Py 7.4.11

`ChoiceReturn` é uma `Action` e seu `__call__()` retorna o valor da escolha.

### 🟢 CONFIRMADO — Ren'Py 7.4.11

O bloco escolhido é resolvido posteriormente pelo `Menu.execute()`.

---

## 3. `checkpoint(rv)` não é a criação imediata de uma nova entrada

Este é um ponto que pode causar confusão.

`display_menu()` chama:

```python
checkpoint(rv)
```

Mas `RollbackLog.checkpoint()` não significa simplesmente:

```text
criar uma nova Rollback agora
```

Ele marca o `current` rollback como checkpoint e, dependendo do estado, registra dados de forward ou manipula a pilha `forward`.

A criação da próxima entrada ocorre no ciclo de `RollbackLog.begin()`.

### 🟢 CONFIRMADO — Ren'Py 7.4.11

`checkpoint()` e `begin()` são operações diferentes.

`checkpoint()` marca/fecha informação de checkpoint no objeto rollback corrente.

`begin()` pode posteriormente criar um novo objeto `Rollback` e anexá-lo ao log.

---

## 4. Onde entra a execução do bloco escolhido

Depois que `display_menu()` devolve `rv`, o `Menu.execute()` recebe a escolha.

Para uma Choice normal, o valor corresponde ao índice da alternativa. O Menu então direciona o contexto para o primeiro nó do bloco correspondente:

```text
rv
 │
 ▼
items[rv][2][0]
 │
 ▼
next_node(...)
```

Esse primeiro nó pode ser qualquer AST válida, por exemplo:

```text
Python
Show
Say
If
Jump
Call
...
```

Portanto o valor retornado pela Choice não descreve necessariamente a consequência narrativa. Ele seleciona qual bloco AST será executado.

---

## 5. A próxima entrada de rollback aparece no ciclo seguinte

`RollbackLog.begin()` é chamado antes da execução de um novo nó.

Ele decide se precisa iniciar uma nova entrada. Entre as condições consideradas estão:

- interação desde o último reset;
- checkpoint do rollback atual;
- `retain_after_load`;
- `force=True`.

Quando decide iniciar:

```text
begin()
  ↓
complete(True) do current anterior, quando aplicável
  ↓
cria Rollback()
  ↓
self.log.append(self.current)
  ↓
executa o novo nó
```

Assim, a sequência conceitual mais precisa é:

```text
INTERAÇÃO DA CHOICE
      ↓
ChoiceReturn.__call__()
      ↓
valor rv
      ↓
checkpoint(rv)
      ↓
Menu.execute()
      ↓
seleciona primeiro nó do bloco
      ↓
begin() do ciclo seguinte
      ↓
nova entrada/current rollback
      ↓
execução do nó do bloco
```

### 🟢 CONFIRMADO — Ren'Py 7.4.11

A entrada de rollback não deve ser confundida com a simples chamada de `ChoiceReturn` nem com `checkpoint(rv)`.

---

## 6. O papel de `did_interaction`

O `RollbackLog` mantém um indicador `did_interaction`.

No início de um novo jogo ele começa como verdadeiro. O `begin()` usa esse estado para decidir se deve criar uma nova entrada.

A arquitetura deixa claro que uma interação é uma das razões pelas quais o próximo ciclo de execução deve ser registrado.

### 🟠 PONTO AINDA A SER RASTREADO MICROSCOPICAMENTE

Nesta etapa não devemos afirmar, sem seguir o caminho completo do `interface.interact()` até a alteração do campo, qual linha exata marca `did_interaction` como verdadeiro em todos os tipos de interação.

A existência do mecanismo está confirmada; a localização completa de cada escrita ainda precisa ser fechada.

---

## 7. Por que isso importa para uma Choice do URM

O URM faz:

```python
renpy.game.log.rollback_is_fixed = False
return renpy.ui.ChoiceReturn(choice_value, choice_index)()
```

O segundo comando devolve o valor da Choice ao mecanismo nativo.

O primeiro comando altera o estado de fixed rollback antes desse retorno.

Depois disso, o restante do pipeline continua sendo do Ren'Py:

```text
URM
 │
 ├─ limpa rollback_is_fixed
 │
 └─ chama ChoiceReturn
        │
        ▼
Ren'Py
 │
 ├─ recebe rv
 ├─ checkpoint(rv)
 ├─ resolve a Choice
 ├─ aponta para o bloco
 ├─ inicia o ciclo seguinte de rollback
 └─ executa AST
```

Isso confirma que o URM não substitui o executor do Menu.

---

## 8. Roll-forward: o que a Choice realmente enxerga

O SDK mantém `RollbackLog.forward`.

`forward_info()` verifica a primeira entrada da pilha e só fornece seu dado quando o contexto atual corresponde ao contexto armazenado.

`ChoiceActionBase.get_selected()` usa exatamente essa informação:

```python
roll_forward = renpy.exports.roll_forward_info()
return renpy.exports.in_fixed_rollback() and roll_forward == self.value
```

Assim, durante fixed rollback, uma Choice pode ser reconhecida como a escolha que corresponde ao dado de roll-forward.

Isso não significa que o jogador esteja fazendo uma nova escolha narrativa naquele instante. Significa que o mecanismo está reproduzindo/atravessando uma decisão já registrada no histórico forward.

---

## 9. Sensibilidade das Choices durante fixed rollback

`ChoiceActionBase.get_sensitive()` é:

```python
return (self.sensitive and
        not renpy.exports.in_fixed_rollback()
        or (not self.block_all and self.get_selected()))
```

Isso produz duas situações importantes:

```text
não está em fixed rollback
    → Choice normalmente sensível

está em fixed rollback
    → normalmente não sensível
    → pode continuar selecionável se a configuração permitir
      e esta for a Choice correspondente ao roll-forward
```

O comportamento não é apenas visual: ele está ligado ao estado de rollback do engine.

---

## 10. `fix_rollback()` e o boundary

`fix_rollback()` não liga imediatamente `rollback_is_fixed`.

Ele estabelece:

```python
self.fixed_rollback_boundary = self.log[-2].context.current
```

quando as condições permitem.

A flag `rollback_is_fixed` pode ser ligada posteriormente durante o rollback quando uma entrada correspondente ao boundary é restaurada.

Portanto:

```text
fix_rollback()
    ↓
cria boundary
    ↓
rollback
    ↓
restauração alcança boundary
    ↓
rollback_is_fixed = True
```

---

## 11. Como o forward é produzido pelo rollback

Durante `RollbackLog.rollback()`, cada `Rollback` restaurado pode possuir `rb.forward`.

Quando possui:

```python
self.forward.insert(0, (rb.context.current, rb.forward))
```

Assim, o sistema não apenas restaura o estado: ele conserva informação suficiente para atravessar novamente determinadas decisões/estados no sentido forward.

Isso é essencial para entender por que uma Choice em fixed rollback pode ficar associada a uma seleção já conhecida.

---

## 12. O caso especial de `checkpoint()` em fixed rollback

Quando:

```python
self.in_fixed_rollback() and self.forward
```

`checkpoint()` tenta consumir a informação correspondente do topo de `forward` se o contexto coincidir.

Se não coincidir, pode substituir/limpar a informação de forward conforme a lógica do SDK.

Isso significa que `checkpoint(rv)` durante fixed rollback participa de uma reconciliação entre:

```text
estado atual
     +
contexto
     +
valor rv
     +
forward stack
```

Não é simplesmente um marcador de "o jogador escolheu".

---

## 13. Consequência para a leitura do URM

A linha:

```python
renpy.game.log.rollback_is_fixed = False
```

antes de:

```python
ChoiceReturn(... )()
```

fica ainda mais significativa depois deste rastreamento.

### 🟢 CONFIRMADO — URM

O URM força o estado `rollback_is_fixed` para falso antes de entregar a seleção ao Ren'Py.

### 🟢 CONFIRMADO — Ren'Py 7.4.11

O estado fixed rollback influencia a sensibilidade das `ChoiceAction` e o uso da pilha `forward`.

### 🟠 INTERPRETAÇÃO CONTROLADA

A intenção funcional provável é permitir que a ação de seleção do URM atravesse a barreira de fixed rollback em vez de ficar presa ao comportamento normal de uma Choice durante roll-forward/fixed rollback.

A palavra "provável" permanece necessária porque a intenção do autor não está escrita de forma explícita nessa linha; o comportamento mecânico está confirmado.

---

## 14. O que não devemos fazer no Wells

Não devemos implementar:

```text
Wells → copia RollbackLog
Wells → cria seu próprio forward
Wells → executa AST da Choice
Wells → decide consequências
```

O modelo correto continua sendo:

```text
Wells
  ↓
observa/apresenta
  ↓
usa uma Action compatível
  ↓
Ren'Py ChoiceReturn
  ↓
Ren'Py Menu
  ↓
Ren'Py AST
  ↓
Ren'Py rollback
```

---

## 15. Estado atual da investigação

### 🟢 CONFIRMADO

- `ChoiceReturn.__call__()` retorna o valor da Choice.
- `display_menu()` chama `checkpoint(rv)` depois da interação.
- `checkpoint()` não é sinônimo de criação imediata de uma nova entrada `Rollback`.
- `Menu.execute()` usa o retorno para selecionar o primeiro nó do bloco da Choice.
- `RollbackLog.begin()` é responsável pela criação da próxima entrada quando suas condições são satisfeitas.
- `forward` é utilizado para roll-forward/fixed rollback.
- `ChoiceActionBase` usa `roll_forward_info()` para determinar seleção durante fixed rollback.
- fixed rollback depende de `rollback_is_fixed` e `fixed_rollback_boundary`.
- o URM limpa `rollback_is_fixed` antes de sua `ChoiceReturn`.

### 🟠 AINDA EM INVESTIGAÇÃO

- a localização exata de todas as escritas em `did_interaction` no ciclo da interface;
- a sequência completa de `interface.interact()` → marcação de interação → `begin()` em todos os tipos de interação;
- todos os caminhos de Choice durante rollback, incluindo casos com `fix_rollback_without_choice`;
- diferença operacional entre uma Choice comum, uma Choice em fixed rollback e uma Choice atravessada por roll-forward.

### 🔴 NÃO CONCLUIR

- que `checkpoint(rv)` sozinho cria a nova entrada de rollback;
- que `ChoiceReturn` executa o bloco;
- que fixed rollback é apenas um bloqueio visual;
- que o valor `rv` contém a consequência narrativa;
- que a linha do URM que limpa `rollback_is_fixed` "desfaz rollback" por si só.

---

## 16. Diagrama final desta etapa

```text
                    MENU AST
                       │
                       ▼
                 Menu.execute
                       │
                       ▼
               renpy.exports.menu
                       │
                       ▼
                 display_menu
                       │
                       ▼
                  ui.interact
                       │
                       ▼
              ChoiceReturn.__call__
                       │
                       ▼
                       rv
                       │
                       ▼
                 checkpoint(rv)
                       │
                       ▼
                 Menu.execute
                       │
                       ▼
            primeiro nó do bloco escolhido
                       │
                       ▼
                  begin() seguinte
                       │
                       ▼
              nova entrada Rollback
                       │
                       ▼
                 execução AST
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          Store              Contexto
             │                   │
             └─────────┬─────────┘
                       ▼
                  RollbackLog
                       │
              ┌────────┼─────────┐
              ▼        ▼         ▼
         checkpoint  forward   fixed boundary
                           │
                           ▼
                    roll-forward
```
