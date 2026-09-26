# `URMChoice`

## Fonte

`classes/choices.rpy`

## Responsabilidade

`URMChoice` é o objeto do URM que representa uma alternativa individual encontrada em `ChoicesClass.currentChoices`.

Ele não substitui o objeto `Menu` do Ren'Py. É uma camada de inspeção e controle criada pelo URM sobre os dados estruturais da Choice.

## Dados internos

O objeto preserva o item original recebido do `Menu` e seu índice.

```text
choice[0] -> texto original
choice[1] -> condição
choice[2] -> lista de nós AST da alternativa
```

## Propriedades

### `isVisible`

Avalia a condição da Choice usando o namespace do store:

```python
 eval(self.condition, renpy.store.__dict__)
```

É uma avaliação dinâmica no estado atual; não é uma previsão histórica do que aconteceria em outro momento.

### `text`

Usa `renpy.exports.substitute(...)` para produzir o texto apresentado ao usuário, com fallback para o texto original.

Importante:

```text
texto original
   ├── substitute -> texto exibido
   └── ChoiceReturn -> valor usado na seleção
```

A camada visual não substitui o valor estrutural usado pelo mecanismo de Choice.

### `condition`

Expõe a condição original da alternativa.

### `code`

Pede a `CodeView.nodesToCode(...)` uma representação textual dos nós da alternativa e pode manter o resultado em cache.

Isso é **reconstrução de apresentação**, não uma garantia de reprodução literal do `.rpy` original.

A representação também pode participar da camada de interação do CodeView: variáveis e labels reconhecidos pelo `colorize()` podem tornar-se elementos clicáveis e encaminhar o usuário para outras ferramentas do URM.

### `jumpTo`

Percorre diretamente `choice[2]` e retorna o `target` do primeiro `renpy.ast.Jump` encontrado. Se não houver Jump direto, retorna string vazia.

Portanto:

```text
Choice -> Jump A       => detectado
Choice -> If -> Jump A => não detectado por jumpTo
```

O `jumpTo` é uma heurística de Jump direto usada pelo URM para oferecer replay. Não é um analisador completo do fluxo da alternativa.

## `Action`

A ação de seleção do URM faz, em essência:

```python
renpy.game.log.rollback_is_fixed = False
return renpy.ui.ChoiceReturn(choice_text, index)()
```

O URM, portanto, **não executa manualmente o bloco AST da Choice**. Ele devolve a seleção para o mecanismo de Choice do Ren'Py.

### Fixed rollback

- 🟢 URM: limpa `rollback_is_fixed` imediatamente antes da chamada de `ChoiceReturn`.
- 🔵 Ren'Py 7.4.11: `ChoiceReturn` possui comportamento sensível ao estado de fixed rollback/roll-forward.
- 🟠 A função mecânica dessa intervenção foi parcialmente fechada: o SDK mostra que `rollback_is_fixed` é um estado efetivo consultado durante fixed rollback e que o URM o limpa antes da seleção programática. A intenção original do autor ainda não deve ser afirmada como fato.

## `OpenCodeView` / `OpenConditionView`

Essas ações abrem a apresentação do `URM_CodeView` para inspeção do código ou da condição. São ferramentas de observação do URM, mas a representação aberta pode conter elementos interativos que levam a ferramentas de modificação ou replay.

## Relações

```text
ChoicesClass
      |
      +--> URMChoice
               |
               +--> text
               +--> isVisible
               +--> condition
               +--> code --> CodeView
               |               |
               |               +--> variable -> Modify Value
               |               `--> label    -> Replay
               +--> jumpTo --> URM replay
               `--> Action --> Ren'Py ChoiceReturn
```

## Ponto crítico para Wells

A implementação futura deve preservar a separação entre:

1. representação da Choice;
2. apresentação do texto;
3. reconstrução do código;
4. camada de interação da representação;
5. detecção de Jump para replay;
6. seleção real através do mecanismo nativo do Ren'Py.

A interação deve ser tratada como parte da arquitetura, não como simples detalhe cosmético da interface. Misturar representação, interação e execução, porém, criaria um sistema diferente do URM.
