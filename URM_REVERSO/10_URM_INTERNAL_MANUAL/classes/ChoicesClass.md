# `ChoicesClass`

## Fonte

`classes/choices.rpy`

## Responsabilidade

`ChoicesClass` é a porta de entrada do URM para detectar e representar o `Menu` atualmente ativo do Ren'Py.

## `isDisplayingChoice`

O URM obtém o nó corrente pelo contexto e resolve o script correspondente. Se o nó for uma instância de `renpy.ast.Menu`, o valor é `True`; em caso de erro, retorna `False`.

```text
context.current
    -> script.lookup(current)
    -> isinstance(..., renpy.ast.Menu)
```

### Classificação

- 🟢 URM: a classe executa essa consulta.
- 🔵 Ren'Py 7.4.11: `Menu` é um nó AST do script.

## `currentChoices`

Quando existe um `Menu`, o URM percorre `script.items`. Para cada item com estrutura suficiente e bloco associado, cria um `URMChoice(index, item)`.

Estrutura tratada pelo URM:

```text
item[0] = texto
item[1] = condição
item[2] = bloco de nós AST
```

O método **não filtra** a lista apenas por `isVisible`. Isso é importante porque o URM historicamente permite inspecionar e selecionar Choices ocultas.

## `hiddenCount`

Conta as Choices retornadas por `currentChoices` cuja propriedade `isVisible` é falsa.

## Relações internas

```text
ChoicesClass
 ├── currentChoices
 │     └── URMChoice
 ├── hiddenCount
 └── isDisplayingChoice
```

## Dependências externas

```text
URM ChoicesClass
    ├── renpy.game.context()
    ├── renpy.game.script.lookup()
    └── renpy.ast.Menu
```

Essas APIs pertencem ao Ren'Py; o URM apenas as consulta.

## Não confundir

`ChoicesClass` detecta e representa Choices. Ela não executa manualmente os nós do bloco da alternativa. A seleção é devolvida ao mecanismo nativo por `URMChoice.Action`.
