# Choices — sistema completo identificado até agora

## Estado da investigação

A análise do sistema de Choices avançou de uma simples identificação de `ChoicesClass` para um modelo arquitetural mais completo: **AST/Choice estrutural**, **estado dinâmico**, **seleção real**, **checkpoint**, **rollback** e **estrutura interna dos blocos AST** são canais relacionados, mas não são a mesma coisa.

Documentos detalhados desta etapa:

- `01_FLUXO_CHOICE_ROLLBACK.md` — fluxo da Choice desde a detecção no `renpy.ast.Menu`, passando pela seleção via `ChoiceReturn`, execução pelo Ren'Py, observação de alterações pelo `StoreMonitor` e retorno por rollback.
- `02_LIMITES_E_CASOS_ESPECIAIS.md` — limites, Choices ocultas, texto substituído versus valor real, `jumpTo`, CodeView, fixed rollback, Skip e regras de preservação para o Wells.
- `03_AST_MENU_BLOCOS_CALL_IF_JUMP.md` — nova etapa: estrutura real de `Menu.items`, blocos de Choice, `If.entries`, diferença entre `Call` e `Jump`, operações visuais separadas (`Show`, `Scene`, `With`) e limite estrutural de `URMChoice.jumpTo`.

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

## Estrutura AST confirmada no Ren'Py 7.4.11

O SDK confirma que `Menu.items` guarda blocos AST reais para as alternativas.

```text
Menu
├── Choice A → (label, condition, block A)
└── Choice B → (label, condition, block B)
```

`Menu.chain(next)` encadeia os blocos das Choices para a continuação do Menu. Depois que `renpy.exports.menu()` retorna a escolha, `Menu.execute()` faz `next_node()` do primeiro nó do bloco selecionado.

Um bloco pode conter outros nós estruturados:

```text
Choice
 ├── Python
 ├── If
 │    ├── block A
 │    └── block B
 ├── Call
 └── Jump
```

O `If` também possui blocos próprios. `Call` utiliza a infraestrutura de chamada/retorno do contexto; `Jump` apenas transfere o próximo nó para o destino encontrado no script.

Portanto `Jump` não é uma operação visual. `Show`, `Scene`, `Hide` e `With` são nós distintos responsáveis pelas respectivas operações visuais/transições.

## `jumpTo` não é um grafo completo

O URM procura o primeiro `renpy.ast.Jump` diretamente presente na lista de nós da Choice.

Isso significa:

```text
Choice → Jump A
```

é detectado pelo `jumpTo`, mas:

```text
Choice → If → Jump A
```

não é encontrado por essa propriedade, embora o Jump exista na árvore AST e possa ser alcançado em runtime.

A coluna `Next label` deve ser documentada como uma **heurística de Jump direto**, não como previsão completa do fluxo.

Isso é particularmente importante porque `CodeView.nodesToCode()` possui profundidade diferente: ele consegue percorrer `If` recursivamente, enquanto `jumpTo` deliberadamente não faz essa travessia.

## Jump e aparência de continuidade visual

A análise do SDK refinou a observação de gameplay de que um `Jump` pode parecer produzir uma mudança visual contínua.

O mecanismo real é:

```text
Jump cena_02
  ↓
lookup do label
  ↓
label cena_02
  ↓
Show / Scene / diálogo / outros nós
  ↓
novo estado visual
```

Assim, um Jump pode ser usado como ponte de controle para uma mudança visual imediata, mas a mudança pertence aos nós alcançados, não ao Jump.

Classificação:

- 🟡 **OBSERVAÇÃO SUA:** Jump pode aparecer associado a continuidade/mudança visual em gameplay.
- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** Jump transfere controle para o nó do destino.
- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** Show/Scene/Hide/With são operações AST separadas.
- 🟠 **HIPÓTESE refinada:** a aparência de continuidade pode vir do primeiro nó ou sequência do label alvo.
- 🔴 **NÃO CONFIRMADO:** Jump possui significado narrativo universal de continuidade, mudança de cena ou neutralidade.

## Choices ocultas

O URM mantém Choices cuja condição atual é falsa e apresenta sua visibilidade separadamente.

Isso permite inspeção de alternativas que a interface normal do jogo pode não mostrar.

A própria ação de seleção não faz uma segunda checagem de `isVisible`, o que é coerente com a funcionalidade histórica do URM de permitir selecionar Choices ocultas.

Isso deve ser tratado como intervenção avançada, não como mera reprodução visual do Menu normal.

## Código da Choice ≠ mudança de variável

Esta distinção está formalmente registrada.

O código mostrado na tela de Choices vem dos **nós AST pertencentes à alternativa**. Em particular, para `renpy.ast.Python`, `CodeView.nodesToCode()` utiliza `node.code.source`.

Exemplo:

```renpy
"A":
    RPjosy += 5
```

pode ser apresentado como código da alternativa. Isso não significa que `RPjosy` já tenha mudado.

A mudança efetiva de estado pertence ao caminho separado:

```text
execução Ren'Py
    ↓
StoreMonitor
    ↓
oldVal / newVal
```

## CodeView e fidelidade

O CodeView é uma reconstrução de apresentação da AST. Para nós Python, `node.code.source` fornece uma ligação forte com a fonte associada ao nó. Para outros nós, o URM reconstrói uma representação legível.

O próprio URM avisa que o código mostrado é gerado por ele e provavelmente não é exatamente igual ao que o desenvolvedor escreveu.

Portanto, para o Wells, é necessário distinguir:

```text
fonte associada ao nó Python
≠
reconstrução CodeView
≠
arquivo .rpy original
```

## Texto exibido versus valor usado na seleção

`URMChoice.text` usa `renpy.exports.substitute()` para apresentação.

`URMChoice.Action`, porém, passa `self._m1_choices__choice[0]` para `ChoiceReturn`, e não `self.text`.

Assim existe uma separação importante:

```text
item original
 ├──→ substitute → texto apresentado
 └──→ ChoiceReturn → seleção real
```

Isso reforça a regra de que a camada visual não deve substituir a estrutura real usada pelo Ren'Py.

## Seleção

A ação de `URMChoice` faz:

```python
renpy.game.log.rollback_is_fixed = False
return renpy.ui.ChoiceReturn(choice_text, index)()
```

O URM não executa manualmente o código da alternativa. A decisão é devolvida ao mecanismo de interação do Ren'Py, que continua a execução real dos nós associados à escolha.

## Estado dinâmico

`StoreMonitor` é um componente separado do sistema de Choices. Ele observa/intercepta determinadas alterações do store e usa `get_changes()` no callback Python para obter deltas de estado.

Quando uma variável está sendo monitorada, `handleVarChange()` pode criar a notificação `Variable changed`, com valor anterior e valor novo.

Isso não deve ser confundido com a notificação dedicada `Choices detected`.

## Notificação de Choice

A tela `URM_notifications` possui uma seção específica para Choices baseada em `Choices.isDisplayingChoice` e nas configurações correspondentes.

A mensagem observada nos screenshots `0018`/`0019` é:

```text
Choices detected
```

Ela indica presença de Choice/Menu no fluxo atual; não é uma notificação de mudança de variável.

## Path Detection

`PathDetection` é separado de `Choices`.

```text
Choice:
renpy.ast.Menu
    ↓
Choices.currentChoices

Path Detection:
nó atual
    ↓
look-ahead
    ↓
If futuro
    ↓
Paths
```

Não devemos fundir os dois sistemas na futura implementação do Wells.

## Rollback

A investigação atual sustenta o seguinte modelo:

```text
Choice
  ↓
ChoiceReturn
  ↓
Ren'Py executa a alternativa
  ↓
Store pode mudar
  ↓
StoreMonitor observa
  ↓
Ren'Py mantém seu estado de rollback
  ↓
usuário faz rollback
  ↓
Ren'Py restaura estado/contexto
  ↓
Choice pode reaparecer
  ↓
URM observa novamente
```

O URM não deve ser modelado como dono de um segundo estado ou de um segundo mecanismo de rollback.

## Fixed rollback e Skip

O changelog do URM registra:

- 2.1: Choices dialog capaz de bypass de fixed choices / fixed rollback;
- 2.2.1: Skip capaz de avançar rapidamente até a próxima Choice;
- 2.3: CodeView inteligente para Choices e paths;
- 2.6.1: prevenção de dados estáticos do URM no save.

A presença de:

```python
renpy.game.log.rollback_is_fixed = False
```

antes de `ChoiceReturn` reforça que o bypass de fixed rollback faz parte do mecanismo de seleção do URM.

A semântica exata desse campo e o circuito completo de checkpoint/rollback continuam sendo investigados diretamente no SDK 7.4.11.

## Perguntas abertas atualizadas

1. Semântica exata de `rollback_is_fixed` e sua relação com `ChoiceReturn`.
2. Sequência precisa de `force_checkpoint` → `RollbackLog.complete()`.
3. Ordem exata entre interação, checkpoint, execução da Choice e registro no rollback.
4. Sequência interna de restauração de contexto/store durante rollback.
5. Como o Skip do URM encontra/interrompe a próxima Choice.
6. Comportamento de Choices com estruturas AST muito complexas.
7. Compatibilidade exata entre versões Ren'Py suportadas pelo URM.
8. Limites entre fonte Python associada à AST e fonte textual original do script.
9. Segurança/consistência ao permitir Choices ocultas/fixed rollback.

**Regra de preservação:** ainda não implementar nem simplificar o sistema. Primeiro completar a árvore inteira; somente depois decidir o que será transplantado para o Wells Framework.
