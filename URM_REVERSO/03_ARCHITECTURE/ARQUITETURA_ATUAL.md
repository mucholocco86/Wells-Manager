# Arquitetura atual — mapa consolidado

Ren'Py é o executor/interpreter do fluxo. O URM observa, apresenta, registra e manipula partes do runtime.

A análise das Choices refinou esse modelo: **estrutura da Choice, estado dinâmico, seleção, fluxo AST e rollback são fluxos relacionados, porém distintos**.

```text
                         REN'PY
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
       AST                STORE            ROLLBACK
        │                  │                  │
        ▼                  ▼                  ▼
     Choices          StoreMonitor         Ren'Py
        │                  │                  │
     CodeView           VarsStore           │
        │                  │                 │
        └──────────┬───────┘                 │
                   ▼                         │
                 URM UI ◄───────────────────┘
```

## Fluxo típico

```text
Say -> TextBox/URM_say (se habilitado) -> avanço
    -> Python (se houver) -> StoreMonitor callback
    -> If (se houver) -> Menu -> Choices.currentChoices
    -> URMChoice -> ChoiceReturn -> continuação pelo Ren'Py
```

Este é um fluxo típico, não uma regra universal: Menu pode aparecer sem Say imediatamente antes.

## Choices: modelo refinado

Quando o contexto atual aponta para um `renpy.ast.Menu`, o URM pode construir `URMChoice` diretamente a partir dos itens do Menu.

No Ren'Py 7.4.11, cada item possui a forma estrutural:

```text
(label, condition, block)
```

onde `block` é uma lista de nós AST da alternativa.

```text
Ren'Py Script/AST
      ↓
renpy.ast.Menu
      ↓
Menu.items
      ↓
ChoicesClass.currentChoices
      ↓
URMChoice
      ├── text
      ├── condition
      ├── visibility
      ├── AST nodes / block
      └── jumpTo
```

O `Menu.chain()` do SDK encadeia os blocos das alternativas para a continuação do Menu. Após a seleção, `Menu.execute()` aponta o contexto para o primeiro nó do bloco escolhido.

## AST interno de uma Choice

Uma Choice não precisa ser uma sequência plana de Python/Jumps. O bloco pode conter estruturas aninhadas:

```text
Choice block
 ├── Python
 ├── If
 │    ├── block A
 │    └── block B
 ├── Call
 └── Jump
```

O `If` possui seus próprios blocos e o SDK os encadeia para a continuação apropriada. `Call` utiliza `context.call(..., return_site=...)`, enquanto `Jump` faz `lookup(target)` e registra o nó alvo como próximo nó.

Isso é uma descoberta importante para o mapa arquitetural: **fluxo AST e destino direto de Choice não são sinônimos**.

## Jump ≠ operação visual

O SDK 7.4.11 confirma que `Jump.execute()` realiza transferência de controle:

```text
Jump
 ↓
lookup(target)
 ↓
next_node(target_node)
```

Já `Show`, `Scene`, `Hide` e `With` são nós diferentes e realizam as operações visuais/transições correspondentes.

Assim uma sequência como:

```text
Jump cena_02
 ↓
label cena_02
 ↓
Show personagem olhando para a porta
```

pode produzir uma mudança visual aparentemente contínua, mas a mudança pertence ao nó alcançado, não ao `Jump`.

Classificação preservada:

- 🟡 Observação de gameplay: Jump pode aparecer associado a continuidade visual.
- 🟢 Confirmado Ren'Py 7.4.11: Jump é transferência de controle.
- 🟢 Confirmado Ren'Py 7.4.11: Show/Scene/Hide/With são mecanismos separados.
- 🟠 Hipótese: a aparência de continuidade pode resultar do conteúdo do label alvo.
- 🔴 Não confirmado: Jump possui significado narrativo universal de continuidade, mudança de cena ou neutralidade.

## `jumpTo` do URM

`URMChoice.jumpTo` é propositalmente mais limitado que a árvore AST disponível no Ren'Py.

Ele procura o primeiro `renpy.ast.Jump` **diretamente** na lista de nós da Choice.

Portanto:

```text
Choice → Jump A
```

pode gerar `jumpTo == "A"`, mas:

```text
Choice → If → Jump A
```

não é encontrado por essa propriedade.

O `CodeView`, por outro lado, possui tratamento recursivo de `If`.

Logo:

```text
capacidade estrutural do AST
        ≠
profundidade da heurística jumpTo
```

A coluna `Next label` da UI deve ser lida como **indicação de Jump direto**, não como grafo completo ou previsão garantida do próximo destino.

## Seleção real

O `URMChoice.Action` não executa manualmente o Python da alternativa. Ele libera `rollback_is_fixed` e chama `renpy.ui.ChoiceReturn(...)`, devolvendo a seleção ao mecanismo de interação do Ren'Py.

```text
Usuário seleciona
      ↓
URMChoice.Action
      ↓
ChoiceReturn
      ↓
Ren'Py
      ↓
Menu.execute()
      ↓
primeiro nó do bloco escolhido
      ↓
execução real
```

## Estado dinâmico

O caminho de alteração de variável é separado:

```text
execução Ren'Py
      ↓
SetField / Python callback
      ↓
StoreMonitor
      ↓
oldVal / newVal
      ↓
VarsStore / Notifications
```

Uma notificação `Variable changed` só deve ser interpretada como observação de estado quando o caminho de monitoramento correspondente estiver ativo.

## Choice notification ≠ Variable changed

A tela `URM_notifications` contém uma seção dedicada à presença de Choices, baseada em `Choices.isDisplayingChoice`. A mensagem observada é `Choices detected`.

Essa notificação é distinta das notificações temporárias produzidas por `Notifications.add()` para mudanças monitoradas de variáveis.

## Rollback

O URM não é tratado como proprietário de um segundo mecanismo de rollback. O Ren'Py continua responsável pelo histórico, checkpoints e restauração de estado/contexto.

Modelo conceitual:

```text
Menu
 ↓
ChoiceReturn
 ↓
Ren'Py executa
 ↓
Store muda
 ↓
StoreMonitor observa
 ↓
Ren'Py registra estado/rollback
 ↓
Rollback
 ↓
Ren'Py restaura
 ↓
Menu pode reaparecer
 ↓
Choices observa novamente
```

A relação exata entre `rollback_is_fixed`, `ChoiceReturn`, `force_checkpoint` e `RollbackLog.complete()` continua sendo objeto de investigação no SDK 7.4.11.

## Papéis

- **Choices:** observa o `renpy.ast.Menu` atual e fornece representação/ações/UI.
- **CodeView:** reconstrói determinados nós AST em código exibível; não é o interpretador.
- **PathDetection:** analisa caminhos e condições; distinto da seleção normal de Menu.
- **VarsStore:** memória/configuração de variáveis observadas, congeladas, monitoradas e ignoradas.
- **StoreMonitor:** observa/intercepta mudanças e integra callbacks/checkpoints.
- **TextBox:** apresentação/interceptação do pipeline de Say.
- **TextRepl:** substituição/filtro de texto.

O bloqueio real de interação vem do nó Ren'Py que exige interação (`node.interact`), não do TextBox.

## Regra arquitetural para o Wells

A fonte de verdade deve continuar sendo o runtime do Ren'Py:

```text
Ren'Py = dono da execução + estado + rollback
Wells = observador + apresentador + interface de análise
```

O Wells não deve manter uma cópia independente do estado do jogo nem transformar-se em um segundo interpretador de Ren'Py.

## Fontes técnicas desta etapa

- `renpy-7.4.11-sdk/renpy/ast.py` — contrato dos nós AST, `Menu`, `If`, `Call`, `Jump`, `Show`, `Scene`, `Hide`, `With` e encadeamento.
- `URM_REVERSO/04_CHOICES/03_AST_MENU_BLOCOS_CALL_IF_JUMP.md` — análise detalhada dessa etapa.
