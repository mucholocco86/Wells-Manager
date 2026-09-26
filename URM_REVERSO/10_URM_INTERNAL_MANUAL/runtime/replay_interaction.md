# Replay do URM — interação com labels sem executar a Choice atual

## Fonte

`classes/main.rpy` e `screens/labels.rpy`.

## Responsabilidade

O `URMReplay` é uma ferramenta de exploração do URM usada quando o usuário quer reproduzir um label sem transformar essa reprodução em continuação normal do gameplay atual.

Isso é diferente de `URMChoice.Action`.

```text
URMChoice.Action
    ↓
ChoiceReturn
    ↓
continuação nativa da Choice
```

Enquanto:

```text
URMReplay
    ↓
call_replay(label, replayScope)
    ↓
reprodução isolada
    ↓
retorno ao URM
```

## `URMReplay`

A classe recebe:

```text
label
finishAction
screenErrorVariable
```

Antes do replay, verifica:

```python
renpy.has_label(self.label)
```

Se o label não existir, abre uma confirmação/erro do URM.

## `replayScope`

Antes de chamar o replay, o URM constrói um dicionário com os valores públicos do `renpy.store`:

```python
replayScope = {}
for k, v in renpy.store.__dict__.items():
    if not k.startswith('_') and k != 'suppress_overlay':
        replayScope[k] = v
```

Isso demonstra que o replay não é simplesmente um `Jump(label)` comum.

O URM prepara um escopo derivado do estado público atual antes de entregar esse escopo ao mecanismo de replay do Ren'Py.

## Tratamento de erros

Durante a reprodução, o URM substitui temporariamente:

```python
renpy.display.error.report_exception
```

por um handler próprio.

O handler captura a mensagem curta do erro e retorna `True`.

Depois da tentativa de replay, o handler original é restaurado.

Se ocorreu erro e a tela que abriu o replay ainda está disponível, o URM coloca uma mensagem no `errorMessage` da tela.

Caso contrário, executa `finishAction` quando fornecida.

Finalmente:

```python
renpy.restart_interaction()
```

## Interface `URM_replay_jump`

A tela apresenta explicitamente a ideia de reprodução sem afetar o gameplay corrente e informa que o usuário retorna ao painel ao encerrar o replay.

Ela oferece:

```text
Play
Remember
Cancel
```

Portanto o clique em um label no CodeView não é uma execução direta do texto mostrado.

O caminho é:

```text
texto reconstruído
      ↓
label interativo
      ↓
URMLabelDialog
      ↓
URM_replay_jump
      ↓
URMReplay
      ↓
replay controlado
```

## Relação com `jumpTo` de `URMChoice`

`URMChoice.jumpTo` procura apenas o primeiro `renpy.ast.Jump` direto no bloco da Choice.

Quando encontra:

```text
Choice
 ↓
Jump target
```

o URM pode oferecer o label através da interface de Choices.

A tela então usa `URMReplay` para oferecer reprodução do label.

Isso cria uma distinção importante:

```text
jumpTo
    = detecção estrutural de um Jump direto

URMReplay
    = ferramenta de reprodução do label detectado
```

Um não é o outro.

## CodeView e replay

O CodeView também pode reconhecer texto como:

```text
jump alguma_label
call alguma_label
```

e transformar a parte correspondente em hyperlink.

Nesse caso, o caminho para replay é independente da propriedade `jumpTo` da Choice:

```text
CodeView
  ↓
URMLabelDialog
  ↓
URM_replay_jump
  ↓
URMReplay
```

Assim, existem pelo menos dois pontos de entrada para a mesma família de ferramenta de replay:

1. a informação estrutural `URMChoice.jumpTo`;
2. a informação textual interativa produzida pelo `CodeView`.

## Diferença para `URM_jump`

O URM também possui uma tela `URM_jump`.

Essa tela oferece um **Jump real** e avisa explicitamente que ele afetará o jogo:

```text
Jump
 ↓
continuação do jogo a partir do label
```

Já `URM_replay_jump` oferece:

```text
Replay
 ↓
execução em replay
 ↓
retorno ao URM
```

Essa diferença é arquiteturalmente importante.

O URM possui, portanto, duas ferramentas conceitualmente distintas:

```text
JUMP
  = intervenção no fluxo atual

REPLAY
  = exploração isolada de um label
```

## Relação com Choices

A árvore fica:

```text
Choice
  │
  ├── Action
  │     ↓
  │   ChoiceReturn
  │     ↓
  │   gameplay normal
  │
  ├── jumpTo
  │     ↓
  │   URM_replay_jump
  │     ↓
  │   URMReplay
  │
  └── code
        ↓
      CodeView
        ↓
      label hyperlink
        ↓
      URM_replay_jump
        ↓
      URMReplay
```

Isso mostra novamente que a árvore de Choices alcança ferramentas que não estão fisicamente no arquivo `choices.rpy`.

## Classificação

- 🟢 **CONFIRMADO — URM:** `URMReplay` constrói `replayScope` com variáveis públicas do store.
- 🟢 **CONFIRMADO — URM:** o replay usa `renpy.call_replay()`.
- 🟢 **CONFIRMADO — URM:** erros do replay recebem tratamento temporário e são devolvidos à interface quando apropriado.
- 🟢 **CONFIRMADO — URM:** `URM_jump` e `URM_replay_jump` são ferramentas diferentes.
- 🔵 **CONFIRMADO — Ren'Py 7.4.11:** `renpy.has_label()` e os mecanismos de interação/replay pertencem ao runtime do motor.
- 🟠 **PONTO A FECHAR:** ainda devemos rastrear no SDK 7.4.11 a implementação interna de `call_replay()` para documentar exatamente como o Ren'Py constrói e encerra o contexto de replay.

## Regra para Wells

Não substituir replay por `Jump()` durante a primeira reconstrução.

O comportamento observado exige preservar a distinção:

```text
Jump atual ≠ Replay isolado
```

Essa diferença faz parte da funcionalidade do URM e da experiência de exploração que o sistema oferece.
