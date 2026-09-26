# `Var` — representação e modificação de variáveis

## Fonte

`classes/vars.rpy`

## Responsabilidade

`Var` é a abstração do URM para representar uma variável do `renpy.store` ou um caminho de subobjeto/lista/dicionário.

Ela é importante para a camada de interação porque transforma um nome encontrado pelo sistema de busca em um objeto que pode ser **consultado, expandido, lembrado, observado ou modificado**.

## Resolução do valor

`Var` preserva:

```text
name = nome/caminho da variável
storeDict = namespace opcional
```

A propriedade `namePath` separa caminhos como:

```text
var1.var2[3].var4["var 5"]
```

em componentes navegáveis.

`value` percorre esses componentes usando acesso ao dicionário, atributos e índices.

## Tipos suportados

`getValType()` identifica, entre outros:

- string;
- boolean;
- int;
- float;
- list;
- dict;
- função;
- `StoreModule`;
- `persistent`;
- objetos/classes com `__dict__`.

`isSupportedVarType()` define quais tipos podem participar das ferramentas de variável.

## `isEditable`

A propriedade é baseada no namespace usado pelo objeto:

```python
return not bool(self._m1_vars__storeDict)
```

Os `Var` criados normalmente pela busca usam `storeDict=None`; portanto, esses objetos são considerados editáveis pelo mecanismo de modificação, desde que o tipo e a operação sejam suportados.

Isso é especialmente importante para caminhos de atributos de objetos. Uma variável como:

```text
x52URM.archivePath
```

pode ser representada por `Var` e resolvida como atributo do objeto `x52URM`.

## `setValue()`

A alteração de valor é realizada por `Var.setValue()`.

Para tipos básicos, o URM converte a entrada para uma representação Python apropriada e executa a atribuição no store:

```text
Var
 ↓
setValue()
 ↓
validação do tipo
 ↓
renpy.store.<nome> = novo valor
```

Também existem operadores para operações específicas, como `append` em listas.

Quando a variável está congelada pelo `VarsStore`, o URM a descongela temporariamente antes da alteração e a congela novamente no `finally`.

## `SetVarValue`

`SetVarValue` é um `Action`/objeto chamável que encapsula a chamada de `Var.setValue()` e administra sucesso/erro da interface.

```text
URM_modify_value
      ↓
SetVarValue
      ↓
Var.setValue
      ↓
alteração do store
```

## Tela `URM_modify_value`

A tela é usada tanto para visualizar quanto para modificar uma variável.

Para os tipos básicos suportados:

```text
boolean → alternância True/False
string  → entrada textual
int     → entrada numérica
float   → entrada numérica decimal
```

O mesmo diálogo também permite, quando autorizado, operações auxiliares como lembrar/esquecer e observar a variável.

## Busca e objetos internos

`SearchClass` percorre `renpy.store.__dict__` e, quando `Settings.searchObjects` está habilitado, pode descer para objetos que possuem `__dict__`.

O padrão documentado do URM inclui:

```python
'searchObjects': True
```

A filtragem de nomes internos usa `searchInternalVars` principalmente para nomes iniciados por `_`.

Consequentemente, atributos públicos de objetos públicos do store podem aparecer na busca mesmo quando a intenção do usuário é procurar dados do próprio URM.

Isso é uma característica arquitetural importante: o sistema de variáveis do URM não é limitado às variáveis de gameplay que um desenvolvedor criou explicitamente.

## Caso `x52URM.archivePath`

O loader coloca o caminho do archive no módulo `x52URM`:

```python
x52URM.archivePath = archivePath
```

Como `x52URM` é um objeto acessível pelo store e possui atributos, o mecanismo genérico de busca/expansão de objetos pode chegar a:

```text
x52URM.archivePath
```

E o mecanismo genérico de `Var` pode tratá-lo como um valor de string editável.

### Consequência importante

Isso significa que a capacidade observada pelo usuário de editar um caminho como:

```text
C:\...\game\0x52URM.rpa
```

não precisa de uma tela especial dedicada a “editar o caminho do archive”. Ela pode surgir da **infraestrutura genérica de busca + Var + Modify Value**.

Essa descoberta é mais significativa do que o caso isolado do `archivePath`, porque mostra que o URM possui uma arquitetura de **interação genérica com o namespace do store e seus objetos**.

## O que uma alteração de `archivePath` realmente significa

O código analisado permite concluir algo mais preciso do que “mudar o local onde o URM está carregado”.

O loader usa o caminho encontrado para localizar o archive no carregamento inicial e registra esse caminho no módulo. Posteriormente, a API de atualização consulta `archivePath` para verificar acesso, baixar um `.tmp`, criar `archivePath + '.update'` e preparar a substituição do archive.

Portanto, alterar a variável em memória:

```text
x52URM.archivePath
```

**não demonstra que o módulo atualmente carregado foi movido ou recarregado a partir do novo local.**

O efeito confirmado é que consumidores posteriores que consultem essa variável poderão receber o novo caminho.

Essa distinção é essencial e evita o teste perigoso de mover o `.rpa` apenas para descobrir o que acontece.

## Classificação

- 🟢 **CONFIRMADO — URM:** `Var` resolve caminhos de variáveis e objetos.
- 🟢 **CONFIRMADO — URM:** `Var.setValue()` pode modificar tipos básicos suportados.
- 🟢 **CONFIRMADO — URM:** a busca pode percorrer objetos públicos do store quando `searchObjects` está habilitado.
- 🟢 **CONFIRMADO — URM:** `x52URM.archivePath` é um atributo público do módulo e é usado posteriormente pela API.
- 🟢 **CONFIRMADO — URM:** a tela `URM_modify_value` é uma interface genérica para esse mecanismo.
- 🟡 **OBSERVAÇÃO SUA:** você viu o caminho do archive na interface e identificou que ele podia ser editado.
- 🔴 **INCORRETO:** concluir que editar esse valor, por si só, muda imediatamente o archive que já está carregado.

## Relação com Choices

Embora `Var` não pertença exclusivamente ao sistema de Choices, ele é uma dependência funcional do CodeView:

```text
Choice
 ↓
URMChoice.code
 ↓
CodeView.colorize()
 ↓
URMVarDialog
 ↓
Var
 ↓
URM_modify_value
 ↓
setValue()
```

Isso explica por que a árvore de Choices alcança o sistema de variáveis.

## Regra para Wells

Na primeira reconstrução fiel, não substituir `Var` por um simples campo de texto. A abstração precisa preservar:

1. resolução de nomes e caminhos;
2. leitura dinâmica do valor;
3. identificação de tipos;
4. navegação por objetos/listas/dicionários;
5. edição dos tipos suportados;
6. integração com congelamento/monitoramento;
7. integração com CodeView;
8. possibilidade de alcançar objetos do próprio framework, enquanto isso fizer parte do comportamento original.
