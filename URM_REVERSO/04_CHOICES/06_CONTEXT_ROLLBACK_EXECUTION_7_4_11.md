# 06 — Context, Rollback e reinício da execução — Ren’Py 7.4.11

## Status

- 🔵 **CONFIRMADO — Ren’Py 7.4.11**: conteúdo deste documento baseado diretamente no SDK `renpy-7.4.11-sdk` preservado neste repositório, commit de referência `81397ad93ae4a038f6b28a0668338aab5db6834d`.
- 🟠 **HIPÓTESE**: qualquer generalização para outras versões do Ren’Py permanece pendente de comparação entre SDKs.

## Objetivo

Fechar a relação entre `RollbackLog.rollback()`, `Context`, a pilha de contextos e a retomada da execução do AST.

A conclusão principal é que rollback não é apenas restauração de variáveis: o registro de rollback preserva um `Context` associado ao ponto restaurado e, após restaurar o estado, o Ren’Py cria um novo registro corrente e reinicia a execução no contexto restaurado.

## 1. O que o Context representa

No Ren’Py 7.4.11, `Context` é o objeto que representa o contexto atual do interpretador. Entre seus campos estão:

- `current`: nome do nó atualmente executado;
- `return_stack`: pontos de retorno de chamadas;
- `call_location_stack`;
- `dynamic_stack`;
- `scene_lists`;
- `rollback`: indica se o contexto participa do sistema de rollback;
- `info`: objeto revertível associado ao contexto;
- `abnormal` / `last_abnormal`;
- `force_checkpoint`;
- dados de música, movie, tradução e outros estados de execução.

O método `goto_label()` simplesmente define o nome do nó que deverá ser executado quando o contexto continuar.

**Evidência:** `renpy/execution.py`, classe `Context`, SDK 7.4.11.

## 2. Context não é o RollbackLog

Os papéis são diferentes:

```text
Context
  ↓
representa onde e como a execução está ocorrendo

RollbackLog
  ↓
guarda estados anteriores que podem ser restaurados
```

O `RollbackLog` possui uma sequência de objetos `Rollback`. Cada entrada possui, entre outros dados, um `context` associado ao estado registrado.

Portanto, um rollback pode restaurar simultaneamente:

```text
estado de dados
+
estado de controle da execução
```

## 3. Descoberta central: rollback restaura o Context

Em `RollbackLog.rollback()` o motor primeiro seleciona os registros que serão revertidos e os coloca em `revlog`.

Depois executa:

```python
for rb in revlog:
    rb.rollback()
```

Durante esse processo, o código também verifica a fronteira de fixed rollback e reconstrói informações de roll-forward.

Após isso, o Ren’Py não simplesmente continua do ponto atual. Ele cria um novo `Rollback` corrente e copia para ele uma versão rollback do contexto restaurado:

```python
self.current = Rollback()
self.current.context = renpy.game.context().rollback_copy()
```

Em seguida, o mecanismo lança `RestartContext()` ou `RestartTopContext()` para reiniciar a execução.

**Consequência:** rollback restaura estado e depois força uma retomada da execução a partir do contexto restaurado.

## 4. Fluxo confirmado do rollback normal

```text
Rollback solicitado
        ↓
seleção dos checkpoints
        ↓
registros removidos do log
        ↓
revlog
        ↓
rb.rollback()
        ↓
restauração de dados + Context
        ↓
reconstrução de forward info
        ↓
execute_default_statement(False)
        ↓
novo Rollback corrente
        ↓
Context.rollback_copy()
        ↓
RestartContext()
        ↓
Context.run()
        ↓
AST continua a partir do ponto restaurado
```

## 5. `Context.run()` é a ponte para a execução novamente

`Context.run()` recebe o nó inicial ou, quando não recebe, faz lookup de `self.current` no script.

Durante o loop de execução, o Ren’Py atualiza:

```python
self.current = node.name
```

e decide, para cada nó, se deve iniciar/atualizar o rollback antes da execução.

A decisão considera, entre outros fatores:

- `_begin_rollback`;
- primeira passagem pelo loop;
- `force_checkpoint`;
- `node.rollback == "force"`;
- `node.rollback == "never"`;
- `all_nodes_rollback`;
- informações de roll-forward.

Quando apropriado:

```python
renpy.game.log.begin(force=force_rollback)
```

Se o próprio `Context` marcou `force_checkpoint`, isso é transferido para o `RollbackLog`:

```python
renpy.game.log.force_checkpoint = True
self.force_checkpoint = False
```

Isso confirma a ponte:

```text
Context
  ↓
Context.run()
  ↓
RollbackLog.begin()/force_checkpoint
```

## 6. Fixed rollback

No SDK 7.4.11:

```python
def fix_rollback(self):
    if not self.rollback_is_fixed and len(self.log) > 1:
        self.fixed_rollback_boundary = self.log[-2].context.current
```

`fix_rollback()` **não** ativa diretamente `rollback_is_fixed`.

Durante `rollback()`, enquanto os registros são restaurados:

```python
if (rb.context.current == self.fixed_rollback_boundary) and (rb.context.current):
    self.rollback_is_fixed = True
```

Assim, fixed rollback torna-se efetivo quando a restauração atinge a fronteira definida.

O estado também pode ser encerrado em `begin()` quando o contexto restaurado alcança a condição correspondente.

## 7. Greedy rollback e escolha do ponto restaurado

Antes da restauração, `RollbackLog.rollback()` encontra o primeiro ponto válido diminuindo o log e examinando:

- `hard_checkpoint`;
- `rollback_limit`;
- `rb.context.current`;
- existência do label correspondente no script.

Depois, se `greedy` estiver ativo, pode continuar removendo checkpoints não-hard até alcançar o ponto adequado.

Portanto, o ponto final do rollback não é escolhido simplesmente por “voltar N linhas”. Ele é determinado pelo histórico de rollback e pelas regras de checkpoint.

## 8. Por que o motor precisa reiniciar o Context

Depois de modificar o estado armazenado, continuar exatamente no fluxo de Python que estava sendo executado seria incorreto: o estado do interpretador já foi restaurado para outro momento.

O Ren’Py portanto faz:

```text
restaurar estado
      ↓
reconstruir Context corrente
      ↓
lançar RestartContext / RestartTopContext
      ↓
retomar Context.run()
```

Isso é coerente com o modelo de que o estado visual e o fluxo do jogo são consequências do estado restaurado e da execução dos nós a partir daquele ponto.

## 9. Relação com Choice

O circuito nativo já estabelecido anteriormente permanece:

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

Se posteriormente ocorrer rollback, o mecanismo de rollback não precisa de uma implementação paralela de Choice. Ele restaura o estado/contexto correspondente e reinicia a execução no ponto correto.

Isso é especialmente importante para a futura implementação do Walkthrough: a ferramenta deve respeitar o circuito nativo em vez de tentar reproduzi-lo com um sistema de rollback próprio.

## 10. Relação com Replay

`renpy.call_replay()` cria outro `Context` e outro `RollbackLog`. Portanto:

```text
Jogo principal
Context A
RollbackLog A
Store A

        ↓ call_replay()

Replay
Context B
RollbackLog B
Store isolado

        ↓ fim do replay

Context A
RollbackLog A
Store A
```

Replay é uma bolha de execução separada; não é um simples `Jump`.

## 11. StoreMonitor e checkpoint

A arquitetura já confirmada anteriormente permanece:

```text
StoreMonitor
      ↓
Context.force_checkpoint
      ↓
Context.run()
      ↓
RollbackLog.force_checkpoint
      ↓
RollbackLog.complete()
      ↓
checkpoint(hard=False)
```

O StoreMonitor não cria diretamente um objeto `Rollback` e não substitui o circuito nativo de Choice.

## 12. Invariante arquitetural vs. detalhe de versão

Este documento deve ser lido com uma separação explícita:

### Confirmado no SDK 7.4.11

- existe `Context`;
- existe pilha de contextos;
- `Context` possui `current` e estado de controle;
- `Rollback` possui referência a contexto;
- rollback restaura entradas de rollback e depois reconstrói o contexto corrente;
- a execução é reiniciada por exceções internas `RestartContext` / `RestartTopContext`;
- `Context.run()` retoma a execução do AST;
- fixed rollback é ativado durante a restauração ao atingir sua fronteira;
- `Context.force_checkpoint` é transferido para o `RollbackLog`.

### Ainda não afirmado para todas as versões

Não devemos assumir que os nomes, campos, classes ou sequência interna sejam idênticos em SDKs posteriores. A futura comparação entre SDKs deverá separar:

```text
princípio arquitetural
        ×
implementação específica da versão
```

Esta distinção será particularmente importante para investigar a fronteira de compatibilidade observada entre Ren’Py 8.5.2 e 8.5.3.

## Conclusão

A descoberta central desta etapa é:

> **Rollback no Ren’Py 7.4.11 é uma restauração coordenada de estado de dados e estado de execução, seguida pela reconstrução do contexto corrente e reinício controlado da execução.**

Isso explica por que `Context`, `RollbackLog`, `current`, `checkpoint`, `RestartContext` e `Context.run()` precisam ser analisados como partes de um único ciclo, sem serem confundidos entre si.
