# Choices — sistema completo identificado até agora

## Estado da investigação

A análise do sistema de Choices avançou de uma simples identificação de `ChoicesClass` para um modelo arquitetural mais completo: **AST/Choice estrutural**, **estado dinâmico**, **seleção real**, **checkpoint**, **rollback**, **Context** e **estrutura interna dos blocos AST** são canais relacionados, mas não são a mesma coisa.

Documentos detalhados desta etapa:

- `01_FLUXO_CHOICE_ROLLBACK.md` — fluxo da Choice desde a detecção no `renpy.ast.Menu`, passando pela seleção via `ChoiceReturn`, execução pelo Ren'Py, observação de alterações pelo `StoreMonitor` e retorno por rollback.
- `02_LIMITES_E_CASOS_ESPECIAIS.md` — limites, Choices ocultas, texto substituído versus valor real, `jumpTo`, CodeView, fixed rollback, Skip e regras de preservação para o Wells.
- `03_AST_MENU_BLOCOS_CALL_IF_JUMP.md` — estrutura real de `Menu.items`, blocos de Choice, `If.entries`, diferença entre `Call` e `Jump`, operações visuais separadas e limite estrutural de `URMChoice.jumpTo`.
- `06_CONTEXT_ROLLBACK_EXECUTION_7_4_11.md` — relação entre `Context`, `RollbackLog`, restauração do contexto, `current`, `Context.run()`, `RestartContext`, fixed rollback e retomada da execução do AST no Ren'Py 7.4.11.
- `07_URM_CHOICE_INFORMATION_PROJECTION.md` — `Menu.items` como fonte estrutural, `URMChoice` como camada de interpretação/projeção e distinção entre estrutura, estado, execução e apresentação.
- `08_FLUXO_EXECUCAO_BLOCO_CHOICE_IF_CALL_JUMP.md` — distinção entre próximo nó, destino direto, caminhos possíveis, caminho atualmente executável e consequências ao analisar `If`, `Call` e `Jump` dentro de uma Choice.
- `09_MENU_ROLLBACK_FORCE_E_CONTINUIDADE_BLOCO.md` — descoberta de que `Menu` possui `rollback = "force"` por padrão e análise da relação entre política de rollback, `Menu.execute()`, `Menu.next` e a continuidade dos blocos de Choice.

## Núcleo

`classes/choices.rpy` contém `ChoicesClass`.

`isDisplayingChoice` consulta o nó atual pelo contexto/script e verifica `renpy.ast.Menu`.

`currentChoices` percorre `script.items` e cria objetos `URMChoice` para os itens válidos.

`hiddenCount` conta escolhas não visíveis.

## URMChoice

O item é tratado como tupla com:

```text
item[0] → texto da Choice
item[1] → condição
item[2] → lista de nós AST da alternativa
```

Propriedades importantes:

- `isVisible` avalia a condição em `renpy.store.__dict__`;
- `text` usa `renpy.exports.substitute`;
- `condition` preserva a condição da alternativa;
- `code` usa `CodeView.nodesToCode`;
- `jumpTo` procura o primeiro `renpy.ast.Jump` direto no conteúdo da alternativa.

## Relação Context ↔ Rollback

A análise do SDK 7.4.11 confirmou que o rollback restaura não apenas valores do store, mas também estado de controle associado ao `Context`.

O fluxo consolidado é:

```text
RollbackLog
    ↓
seleciona entradas
    ↓
revlog
    ↓
rb.rollback()
    ↓
restauração do estado/contexto
    ↓
execute_default_statement(False)
    ↓
novo Rollback corrente
    ↓
Context.rollback_copy()
    ↓
RestartContext / RestartTopContext
    ↓
Context.run()
    ↓
AST continua do ponto restaurado
```

`Context` e `RollbackLog` têm responsabilidades diferentes:

```text
Context
  → estado de controle da execução atual

RollbackLog
  → histórico de estados restauráveis
```

O `Context` contém, entre outros dados, `current`, `return_stack`, `dynamic_stack`, `scene_lists`, `rollback`, `info` e `force_checkpoint`.

`RollbackLog.rollback()` usa os contextos associados aos registros restaurados e, ao final, cria um novo registro corrente baseado em `renpy.game.context().rollback_copy()`, seguido de uma reinicialização controlada da execução.

## Fixed rollback

No SDK 7.4.11, `fix_rollback()` estabelece uma `fixed_rollback_boundary`, mas não ativa diretamente `rollback_is_fixed`.

Durante a restauração dos registros em `rollback()`, quando o `Context.current` restaurado alcança essa fronteira, `rollback_is_fixed` passa a `True`.

Portanto:

```text
fix_rollback()
    ↓
define boundary
    ↓
rollback()
    ↓
restore entries
    ↓
reach boundary
    ↓
rollback_is_fixed = True
```

A semântica exata desse estado na seleção programática do URM continua sendo tratada junto com `ChoiceReturn` e o circuito de interação.

## StoreMonitor e checkpoint

O StoreMonitor permanece separado do dono do rollback.

O fluxo confirmado é:

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

Isso não significa que toda alteração arbitrária de variável gere automaticamente um checkpoint. O caminho confirmado é o callback Python do StoreMonitor solicitando `force_checkpoint`, seguido do processamento nativo do Ren'Py.

## Choice e rollback

O circuito nativo continua sendo:

```text
Menu
 ↓
display_menu()
 ↓
ui.interact()
 ↓
ChoiceReturn
 ↓
checkpoint(rv)
 ↓
bloco escolhido
 ↓
execução AST
```

Se ocorrer rollback posteriormente, o Ren'Py restaura estado/contexto e reinicia a execução. O URM observa esse processo; ele não precisa manter um segundo mecanismo de rollback.

O próprio `Menu` possui `rollback = "force"` no AST 7.4.11. Essa propriedade participa da política de rollback consumida pelo executor e não deve ser confundida com a chamada posterior de `checkpoint(rv)` feita pelo circuito de interação.

## Execução do bloco de uma Choice

Uma alternativa de Menu possui um bloco AST próprio. Esse bloco pode conter Python, diálogo, `If`, `Call`, `Jump` e outras statements.

Portanto:

```text
Choice
 ↓
block AST
 ↓
execução dos nós
```

não equivale necessariamente a:

```text
Choice → Jump
```

Para análise completa, distinguimos:

```text
destino direto
próximo nó
caminhos possíveis
caminho atualmente executável
consequências efetivamente produzidas
```

`URMChoice.jumpTo` cobre somente uma pequena projeção dessa estrutura.

## Replay

`renpy.call_replay()` cria uma execução separada com novo `Context`, novo `RollbackLog` e stores preparados para replay. Ao terminar, o contexto de replay é removido e o log/store do jogo principal é restaurado.

Portanto:

```text
Jump
  → continua no contexto atual

Replay
  → cria uma bolha de execução separada
```

## Invariante arquitetural vs. detalhe de versão

Os mecanismos acima são **confirmados para Ren'Py 7.4.11**.

Não devemos assumir que nomes, campos, classes ou sequência interna sejam idênticos em SDKs posteriores. A futura comparação entre SDKs deverá separar:

```text
princípio arquitetural
        ×
implementação específica da versão
```

Essa separação será especialmente útil para investigar a fronteira de compatibilidade observada entre Ren'Py 8.5.2 e 8.5.3.

## Regra de preservação

Primeiro entender → depois inspecionar → depois planejar → só então modificar.

O objetivo continua sendo completar a árvore do URM antes de decidir o que será transplantado para o Wells Framework.