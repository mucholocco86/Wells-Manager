# `did_interaction` — circuito interno de interação → rollback no Ren'Py 7.4.11

> **Status:** análise confirmada no código-fonte do Ren'Py 7.4.11.
>
> **Classificação:** 🟢 CONFIRMADO — Ren'Py 7.4.11.
>
> Este documento registra uma descoberta de infraestrutura do motor. Ela não deve ser confundida com comportamento específico do URM.

---

## 1. Por que esta descoberta é importante

Durante a análise do sistema de Choices do URM surgiu uma peça interna do Ren'Py que conecta dois momentos diferentes do runtime:

1. a conclusão de uma interação com o usuário;
2. o início/gerenciamento do próximo ciclo relevante do histórico de rollback.

A peça é o estado:

```python
renpy.game.log.did_interaction
```

O nome pode parecer simples, mas seu papel só fica claro quando seguimos **quem escreve**, **quem consome**, **quando o valor é limpo** e **como isso se encaixa no `RollbackLog`**.

A conclusão documentada desta etapa é:

> `did_interaction` é um marcador interno de que uma interação ocorreu. A conclusão da interação o coloca em `True`; posteriormente `RollbackLog.begin()` consulta esse estado como uma das condições para iniciar um novo período de rollback e então o limpa.

Portanto, ele funciona como uma **peça de ligação entre o ciclo de interação e o ciclo de rollback**.

Ele não é o checkpoint em si, não é o rollback em si e não é uma “chave mestre” do motor.

---

## 2. A cadeia confirmada

O caminho encontrado no SDK 7.4.11 é:

```text
INTERAÇÃO DO USUÁRIO
        │
        ▼
conclusão do ciclo de interação
        │
        ▼
renpy.game.log.did_interaction = True
        │
        ▼
próxima execução relevante do AST
        │
        ▼
RollbackLog.begin()
        │
        ├── verifica estado anterior
        ├── considera did_interaction
        ├── inicia novo Rollback quando apropriado
        └── did_interaction = False
```

Esta cadeia é uma descoberta arquitetural do **Ren'Py**, não uma invenção do URM.

---

## 3. Onde o marcador nasce

No `renpy/display/core.py` do SDK 7.4.11, no caminho de conclusão de uma interação, o código executa:

```python
renpy.context().mark_seen()
renpy.game.context().scene_lists.shown_window = False

if renpy.game.log is not None:
    renpy.game.log.did_interaction = True
```

O contexto é importante: a atribuição acontece junto do encerramento do ciclo de interação, depois de operações como `mark_seen()` e atualização do estado da janela.

### Classificação

- 🟢 **Confirmado — Ren'Py 7.4.11:** a conclusão da interação escreve `did_interaction = True`.
- 🟢 **Confirmado — Ren'Py 7.4.11:** o marcador pertence ao `RollbackLog` (`renpy.game.log`).

---

## 4. Onde o marcador é consumido

O `RollbackLog` mantém o estado:

```python
self.did_interaction = True
```

durante sua inicialização.

No método `begin()`, o Ren'Py verifica, entre outras condições, se houve interação desde o ciclo anterior. Depois de iniciar o novo período de rollback, o método limpa o marcador:

```python
self.did_interaction = False
```

A importância disso é que o valor não representa um estado permanente do jogo. Ele funciona como um **sinal de ciclo**:

```text
False
  │
  │ interação termina
  ▼
True
  │
  │ RollbackLog.begin()
  ▼
False
```

Isso explica por que é mais correto descrevê-lo como **marcador/sinal interno** do que como uma configuração ou estado narrativo.

---

## 5. O que `did_interaction` NÃO é

É importante registrar explicitamente as interpretações que seriam perigosas.

### Não é o checkpoint

O checkpoint possui seu próprio mecanismo (`checkpoint()`). `did_interaction` apenas informa que uma interação aconteceu e participa da decisão de iniciar um novo período no `RollbackLog`.

### Não é o rollback

Rollback é o mecanismo que restaura entradas e estado. `did_interaction` não restaura nada.

### Não é `ChoiceReturn`

`ChoiceReturn` representa uma ação/retorno de escolha. Ele participa da seleção e devolve o valor escolhido. `did_interaction` é um estado do log relacionado à conclusão do ciclo de interação.

### Não é `ui.interact()`

`ui.interact()` executa uma interação. O marcador aparece no caminho de conclusão do ciclo de interação; não deve ser tratado como sinônimo da função.

### Não é exclusivo de Choices

O marcador pertence ao mecanismo geral de interação/rollback do Ren'Py. Choices podem passar por esse circuito, mas o conceito não nasceu para representar somente menus.

### Não é uma autorização para alterar o rollback

O fato de ser um estado interno observável não significa que código externo deva escrevê-lo arbitrariamente. Qualquer intervenção precisa ser analisada dentro do contexto completo do `RollbackLog`.

---

## 6. Relação com `ui.interact()` e `checkpoint()`

O circuito completo não pode ser reduzido a um único sinal.

Um modelo mais fiel é:

```text
                    REN'PY

        AST / execução normal
                 │
                 ▼
          elemento interativo
                 │
                 ▼
            ui.interact()
                 │
                 ▼
       ciclo de interação termina
                 │
                 ▼
        did_interaction = True
                 │
                 ▼
         próxima fase do log
                 │
                 ▼
       RollbackLog.begin()
                 │
                 ▼
        período de rollback
                 │
                 ├───────────────┐
                 ▼               ▼
            checkpoint       rollback
                 │               │
                 ▼               ▼
              forward      restauração
```

`checkpoint()` e `did_interaction` têm papéis diferentes.

- `did_interaction`: registra que uma interação ocorreu.
- `begin()`: usa esse sinal para organizar o próximo ciclo de rollback.
- `checkpoint()`: estabelece o ponto de checkpoint e trata dados de forward/fixed rollback.
- `rollback()`: restaura o histórico/estado.

A separação desses papéis é essencial para não transformar uma descoberta em uma explicação simplificada demais.

---

## 7. Relação com Choices

Uma Choice do Ren'Py normalmente atravessa o sistema de interação antes que seu bloco AST seja executado.

O caminho estrutural investigado nesta fase é:

```text
renpy.ast.Menu.execute()
        │
        ▼
renpy.exports.menu()
        │
        ▼
ChoiceReturn
        │
        ▼
interface / ui.interact()
        │
        ▼
ChoiceReturn.__call__()
        │
        ▼
valor da escolha
        │
        ▼
checkpoint(rv)
        │
        ▼
Menu.execute()
        │
        ▼
primeiro nó do bloco escolhido
```

Em paralelo, o ciclo de interação possui a sinalização:

```text
interação termina
        │
        ▼
did_interaction = True
        │
        ▼
RollbackLog.begin()
```

Esses dois fluxos se relacionam, mas **não são a mesma coisa**.

Isso é particularmente importante para o Wells: não devemos substituir o mecanismo de Choice do Ren'Py por uma interpretação própria baseada apenas em sinais de interação.

---

## 8. Relação com fixed rollback

A análise anterior do SDK mostrou que `RollbackLog` também mantém estados como:

```python
rollback_is_fixed
fixed_rollback_boundary
forward
```

O `did_interaction` participa de uma camada diferente: ele sinaliza a ocorrência de interação para o ciclo de criação/organização do rollback.

Portanto, o modelo correto é:

```text
                RollbackLog
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
did_interaction  checkpoint   fixed rollback
       │             │             │
       ▼             ▼             ▼
  início de       ponto de      restrição / fluxo
  ciclo de        histórico     de retorno
  rollback
```

Não se deve colapsar esses estados em uma única “variável de rollback”.

---

## 9. Por que isso apareceu durante a engenharia do URM

O URM possui código que interfere explicitamente em estados do rollback em determinados momentos. Um exemplo importante dentro de `URMChoice.Action` é:

```python
renpy.game.log.rollback_is_fixed = False
```

seguido da chamada de `ChoiceReturn`.

Essa observação levantou a necessidade de entender o mecanismo de rollback do SDK antes de modificar qualquer componente do sistema de Choices.

A descoberta de `did_interaction` mostra por que essa cautela é necessária: o ciclo de Choice não é uma função isolada. Ele está conectado a um conjunto maior de mecanismos internos do Ren'Py.

**Não devemos concluir a partir desta descoberta que `did_interaction` precisa ser alterado pelo URM.** O fato confirmado é apenas que ele ocupa esta posição no circuito do motor.

---

## 10. Regra metodológica para a engenharia do URM

Este caso estabelece uma regra geral para toda a análise futura:

> Quando uma variável, propriedade, método ou estado interno parecer “importante”, não devemos inferir sua função apenas pelo nome. Devemos seguir o ciclo completo: quem escreve → quando escreve → quem lê → o que acontece depois → quem limpa/modifica o estado.

Aplicação prática:

```text
nome encontrado
      ↓
localizar definição
      ↓
localizar todas as escritas
      ↓
localizar todas as leituras
      ↓
seguir o contexto temporal
      ↓
seguir as chamadas subsequentes
      ↓
comparar com o AST/runtime
      ↓
classificar
```

Isso também se aplica a `jumpTo`, `rollback_is_fixed`, `force_checkpoint`, `forward`, `fixed_rollback_boundary` e qualquer outro componente que apareça durante a árvore de dependências.

---

## 11. Classificação das evidências

### 🟢 CONFIRMADO — Ren'Py 7.4.11

- `did_interaction` existe no `RollbackLog`.
- A conclusão do ciclo de interação grava `renpy.game.log.did_interaction = True`.
- `RollbackLog.begin()` consulta esse estado como parte das condições para iniciar um novo período de rollback.
- `begin()` limpa o marcador com `did_interaction = False`.
- O marcador, portanto, conecta temporalmente o fim de uma interação ao ciclo de rollback.

### 🔵 CONFIRMADO — documentação conceitual do Ren'Py

- Interações e checkpoints fazem parte do mecanismo de rollback/roll-forward.
- `ui.interact()` é um componente central do ciclo de interação.

### 🟡 OBSERVAÇÃO DE USO

A percepção de que esse estado parece uma “pequena chave” entre interação e rollback é uma interpretação intuitiva útil para lembrar a arquitetura.

### 🟠 HIPÓTESE / NÃO CONCLUIR

Não devemos concluir, somente por esta descoberta, que:

- `did_interaction` controla sozinho a criação de todos os rollbacks;
- `did_interaction` seja o único sinal necessário para qualquer checkpoint;
- URM precise escrever esse estado;
- alterar esse estado seja uma técnica segura de controle de rollback.

### 🔴 DESCARTADO

Não tratar `did_interaction` como:

- sinônimo de `checkpoint()`;
- sinônimo de `rollback()`;
- sinônimo de `ChoiceReturn`;
- mecanismo exclusivo de Choices;
- “master switch” do rollback.

---

## 12. Fontes técnicas primárias

### Ren'Py 7.4.11 SDK

- `renpy/display/core.py` — caminho de conclusão da interação que grava `renpy.game.log.did_interaction = True`.
- `renpy/python.py` — `RollbackLog`, incluindo `did_interaction`, `begin()`, `checkpoint()`, `rollback()`, `fix_rollback()`, `forward` e estados relacionados.
- `renpy/ui.py` — `ui.interact()` e `Action`.
- `renpy/exports.py` — `menu()`, `display_menu()` e integração com `ChoiceReturn`.
- `renpy/ui.py` — implementação de `ChoiceReturn`.
- `renpy/ast.py` — `Menu.execute()`, `Menu.chain()` e demais nós envolvidos no fluxo AST.

### Evidência técnica registrada na análise

- `renpy/python.py`: estado `did_interaction`, consumo em `RollbackLog.begin()` e limpeza posterior.
- `renpy/display/core.py`: atribuição `renpy.game.log.did_interaction = True` no encerramento da interação.

---

## 13. Valor para o Wells Framework

Esta descoberta deve ser preservada como **conhecimento de infraestrutura do motor**, e não apenas como detalhe do URM.

O Wells pretende observar e apresentar o comportamento do Ren'Py sem se transformar em um segundo interpretador. Para isso, conhecer os pontos internos que ligam:

```text
interação
   ↓
estado interno
   ↓
rollback
   ↓
checkpoint / forward
   ↓
continuação do AST
```

é fundamental.

A regra arquitetural permanece:

```text
Ren'Py = dono da execução + estado + rollback
URM/Wells = observador + apresentador + interface de análise
```

O conhecimento adquirido aqui deve servir para **observar corretamente o motor**, não para duplicá-lo.

---

## 14. Conclusão

A descoberta pode ser resumida em uma frase técnica segura:

> **No Ren'Py 7.4.11, `did_interaction` é um marcador interno do `RollbackLog` que é ativado quando uma interação termina e posteriormente consumido por `RollbackLog.begin()`, conectando o ciclo de interação à organização do histórico de rollback.**

Essa formulação é suficientemente precisa para ser reutilizada em outros projetos sem transformar a metáfora em uma falsa descrição do mecanismo.
