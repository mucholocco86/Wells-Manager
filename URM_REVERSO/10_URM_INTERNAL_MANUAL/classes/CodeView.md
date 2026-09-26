# `CodeView`

## Fonte

`classes/codeview.rpy`

## Responsabilidade

`CodeView` é a camada do URM que transforma estruturas AST em uma **projeção textual seletiva e interativa** para a interface.

Ele não é um parser do `.rpy`, nem um serializador completo do AST.

Sua função pode ser resumida como:

```text
AST
 ↓
nodesToCode()
 ↓
representação estrutural seletiva
 ↓
colorize()
 ↓
markup visual + elementos interativos
```

## `nodesToCode()`

A função percorre os nós fornecidos e representa apenas determinados tipos de conteúdo de forma legível.

Entre os casos tratados estão:

- `Python` — fonte Python do nó quando disponível;
- `If` — condições e blocos, com recursão;
- `Jump` — destino do Jump e interrupção da representação daquela sequência;
- `Call` — label e argumentos quando representáveis;
- `UserStatement` — determinados `call/show/hide screen`;
- `Translate` — marcador `# Some dialogue`.

Também existem filtros posteriores, como `stripRenpyCode`, quando `Settings.codeViewShowAll` está desligado.

Portanto:

```text
AST completo
     ↓
projeção CodeView
     ↓
apenas parte estruturalmente relevante
```

Nada disso significa que o AST original foi removido ou alterado.

## `# Some dialogue`

Quando encontra `renpy.ast.Translate`, o CodeView pode emitir:

```text
# Some dialogue
```

Esse marcador é uma compressão de apresentação específica desse tipo de região. Não deve ser descrito como um resumo semântico geral produzido por uma compreensão do conteúdo.

Se a representação resultar somente nesse marcador, o próprio `nodesToCode()` pode suprimi-la.

## `colorize()`

Depois da reconstrução, `colorize()` transforma o texto em markup Ren'Py.

Entre outras operações, ele:

1. escapa chaves existentes;
2. pode avaliar visualmente condições textuais `if/elif`;
3. aplica padrões de tokenização e coloração;
4. pode tornar variáveis interativas;
5. pode tornar labels interativos.

Assim, `colorize()` é uma etapa diferente de `nodesToCode()`.

## Condições visuais

Quando habilitado, `evaluateConditions()` procura condições textuais de `if/elif` e acrescenta indicadores visuais como:

```text
# V - Condition is met
# X - Condition not met
# ? - Unable to evaluate condition
```

Isso é uma **avaliação de apresentação** e não substitui o `If.execute()` do Ren'Py.

## Variáveis interativas

O CodeView registra:

```python
renpy.config.hyperlink_handlers['URMVarDialog'] = self.handleVarClicked
```

Variáveis reconhecidas podem ser envolvidas em hyperlinks. Ao clicar, o URM abre:

```python
renpy.show_screen('URM_modify_value', Var(varName), allowRemember=True)
```

O fluxo é:

```text
variável reconstruída
      ↓
link URMVarDialog
      ↓
URM_modify_value
      ↓
SetVarValue / Var
      ↓
alteração ou consulta do valor
```

Isso explica por que informações como `tree_thank = True` podem ser mais que texto visual: a variável pode funcionar como ponto de entrada para a ferramenta de modificação do URM.

## Labels interativos

O CodeView também registra:

```python
renpy.config.hyperlink_handlers['URMLabelDialog'] = self.handleLabelClicked
```

Ao clicar em um label reconhecido, abre:

```python
renpy.show_screen('URM_replay_jump', label)
```

O fluxo é:

```text
label reconstruído
      ↓
link URMLabelDialog
      ↓
URM_replay_jump
      ↓
URMReplay
      ↓
replay
```

Isso não significa que `colorize()` execute diretamente o Jump ou Call do AST. Ele encaminha a interação para outra ferramenta.

## Relação com Choices

`URMChoice.code` chama `CodeView.nodesToCode(choice[2])`. O resultado pode então passar por `URM_CodeView`, que chama `CodeView.colorize()` para apresentação.

Portanto:

```text
ChoicesClass
    ↓
URMChoice
    ↓
choice.code
    ↓
CodeView.nodesToCode
    ↓
representação
    ↓
URM_CodeView
    ↓
CodeView.colorize
    ↓
interação com variáveis/labels
```

Essa é uma dependência funcional importante para a árvore de Choices.

## Relação com outras ferramentas

```text
CodeView
 ├── variável → URM_modify_value
 ├── label → URM_replay_jump
 ├── Choices → URMChoice.code
 └── PathDetection → Path.code
```

Consequentemente, `CodeView` é infraestrutura compartilhada e não deve ser tratado como componente exclusivo da tela de Choices.

## Configuração `codeViewShowAll`

A configuração controla a filtragem de conteúdo menos relevante para a apresentação. Quando desativada, `stripRenpyCode()` remove determinadas linhas relacionadas a `renpy.*` e `ui.*` conforme as regras textuais implementadas pelo URM.

Isso reforça a ideia de **projeção seletiva**:

```text
fonte/AST completo
        ↓
representação CodeView
        ↓
filtragem textual
        ↓
apresentação contextual
```

## Classificação

- 🟢 **CONFIRMADO — URM:** `nodesToCode()` e `colorize()` possuem essas responsabilidades.
- 🟢 **CONFIRMADO — URM:** variáveis e labels podem ser transformados em hyperlinks para ferramentas do URM.
- 🔵 **CONFIRMADO — Ren'Py 7.4.11:** hyperlinks/markup e screens são mecanismos de interface do motor usados como infraestrutura externa.
- 🟠 **HIPÓTESE:** a intenção de design por trás de cada regra individual de filtragem não deve ser inferida além do comportamento observado no código.

## Regra para Wells

Na primeira reconstrução fiel:

1. preservar a separação `nodesToCode()` → `colorize()`;
2. preservar a projeção seletiva antes de qualquer otimização;
3. preservar a interação com variáveis e labels;
4. preservar as ferramentas acionadas pelos links enquanto a árvore não estiver fechada;
5. não transformar o CodeView em um parser/serializador completo;
6. somente depois da reprodução funcional decidir quais elementos visuais serão reformulados para o Wells.
