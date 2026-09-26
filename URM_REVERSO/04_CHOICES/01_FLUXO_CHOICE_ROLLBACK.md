# Choices — fluxo completo observado, execução e rollback

## Objetivo deste documento

Este documento registra a interpretação consolidada da arquitetura de Choices do URM até esta etapa da arqueologia. O foco é separar rigorosamente três coisas que, visualmente, parecem uma única funcionalidade:

1. **informação estrutural da Choice**, obtida diretamente da AST real do Ren'Py;
2. **mudanças efetivas de estado**, observadas pelo StoreMonitor;
3. **execução, checkpoint e rollback**, que continuam pertencendo ao Ren'Py.

A regra de ouro para a aplicação posterior no Wells Framework é: **Ren'Py continua sendo o dono da execução e do estado; o Walkthrough deve observar e apresentar a realidade que o Ren'Py já possui.**

---

## 1. A descoberta central

O URM não parece reconstruir uma Choice a partir do texto do arquivo `.rpy`. Em `classes/choices.rpy`, `ChoicesClass.isDisplayingChoice` obtém o nó atual do contexto e faz a verificação:

```python
script = renpy.game.script.lookup(current)
if isinstance(script, renpy.ast.Menu):
```

Quando encontra um `renpy.ast.Menu`, `currentChoices` percorre `script.items` e cria objetos `URMChoice` para os itens válidos.

Isso coloca a origem da informação nesta cadeia:

```text
Jogo
  ↓
Ren'Py parser/compiler
  ↓
AST real em memória
  ↓
renpy.ast.Menu
  ↓
ChoicesClass
  ↓
URMChoice
  ↓
interface do URM
```

Isso é muito diferente de uma solução baseada em regex, leitura de arquivo ou tentativa de inferir o significado da escolha.

---

## 2. O que existe dentro de uma URMChoice

O `URMChoice` recebe o item da AST e trabalha com três partes principais:

```text
item[0] → texto da Choice
item[1] → condição
item[2] → lista de nós AST executados pela Choice
```

A representação observada no URM inclui:

- texto da escolha;
- visibilidade;
- condição;
- código reconstruído a partir dos nós;
- primeiro destino encontrado por `renpy.ast.Jump`;
- ação legítima de seleção usando a infraestrutura do Ren'Py.

### Texto

A propriedade `text` passa pelo mecanismo de substituição do Ren'Py (`renpy.exports.substitute`). Portanto, o URM não precisa inventar seu próprio mecanismo para substituir texto dinâmico.

### Condição

A propriedade `isVisible` avalia a condição usando `renpy.store.__dict__`. Isso significa que a visibilidade apresentada pelo URM é derivada do estado atual do store.

### Código

A propriedade `code` chama:

```python
CodeView.nodesToCode(tuple[2])
```

Ou seja, o URM pega os nós AST pertencentes à alternativa e os transforma em uma representação de código para exibição.

---

## 3. A informação exibida no CodeView não é a mesma coisa que uma mudança de variável

Esta distinção precisa permanecer explícita na documentação e na futura implementação do Wells.

Exemplo:

```renpy
menu:
    "Agradeça à árvore.":
        tree_thank = True

    "Seja cruel com a árvore.":
        tree_thank = False
```

O URM pode mostrar, antes da execução da escolha:

```text
Agradeça à árvore.
Code:
tree_thank = True
```

e:

```text
Seja cruel com a árvore.
Code:
tree_thank = False
```

A evidência visual dos screenshots `0018` e `0019` demonstra exatamente esse comportamento.

Isso não significa que `tree_thank` tenha acabado de mudar para `True` ou `False`. O código exibido é uma representação dos nós AST contidos naquela alternativa.

Portanto:

```text
CHOICE CODE
    ↓
AST da alternativa
    ↓
CodeView.nodesToCode()
```

é um canal de informação.

Enquanto:

```text
EXECUÇÃO
    ↓
StoreMonitor
    ↓
oldVal / newVal
```

é outro canal.

Misturar os dois criaria uma fonte de informação ambígua e não reproduziria corretamente a arquitetura do URM.

---

## 4. CodeView é um reconstrutor de apresentação, não um segundo interpretador

`CodeView.nodesToCode()` conhece determinados tipos de nós AST, entre eles:

- `renpy.ast.Python` → usa `node.code.source`;
- `renpy.ast.If` → percorre recursivamente as entradas;
- `renpy.ast.Jump` → mostra o destino;
- `renpy.ast.Call` → mostra label/argumentos;
- `renpy.ast.UserStatement` → trata determinadas operações como `call/show/hide screen`;
- `renpy.ast.Translate` → representa como comentário de diálogo.

O ponto especialmente forte é o tratamento de `renpy.ast.Python`: o URM utiliza `node.code.source`. Assim, quando o desenvolvedor escreveu uma operação como:

```python
RPjosy += 5
```

é possível preservar a própria fonte associada ao nó Python para exibição, em vez de tentar deduzir semanticamente que a variável “ganhou 5 pontos”.

A interpretação correta para o Wells é, portanto:

> **Mostrar o que a AST contém; não inventar o significado que aquilo supostamente possui.**

---

## 5. O momento em que a Choice aparece

A tela de notificações do URM possui uma seção específica para Choices. Ela depende de condições como:

```python
x52URM.Settings.showChoicesNotification
and x52URM.Choices.isDisplayingChoice
```

A mensagem observada no runtime é:

```text
Choices detected
```

Essa mensagem é diferente das notificações temporárias de mudança de variável.

A arquitetura fica:

```text
Ren'Py chega a um Menu
        ↓
Choices.isDisplayingChoice == True
        ↓
URM_notifications detecta
        ↓
"Choices detected"
        ↓
usuário abre a tela de Choices
```

Portanto, o banner observado nos screenshots `0018`/`0019` não é prova de que uma variável mudou. Ele é a detecção da presença de uma Choice/`renpy.ast.Menu` no fluxo atual.

---

## 6. O URM não executa manualmente o código da alternativa

Esta é outra peça crítica.

A ação de `URMChoice` faz essencialmente:

```python
renpy.game.log.rollback_is_fixed = False
return renpy.ui.ChoiceReturn(choice_text, index)()
```

O URM não pega o texto `RPjosy += 5` e chama `exec()` para executar a escolha.

Em vez disso, ele utiliza `ChoiceReturn` para devolver ao mecanismo de interação do Ren'Py a informação de qual alternativa foi selecionada.

Conceitualmente:

```text
Usuário seleciona Choice A
        ↓
URMChoice.Action
        ↓
ChoiceReturn(...)
        ↓
Ren'Py recebe a escolha
        ↓
Ren'Py continua o fluxo real
        ↓
Ren'Py executa os nós da alternativa
```

Isso evita criar um segundo interpretador de Ren'Py dentro do URM.

---

## 7. O segundo canal: StoreMonitor

Depois que o Ren'Py executa os nós da alternativa, o estado real do jogo pode mudar.

O URM possui um `StoreMonitorClass` separado para acompanhar isso.

Ele trabalha por dois caminhos principais:

### 7.1 Interceptação de SetField

Quando suportado pela versão do Ren'Py, o URM localiza determinados métodos internos do store e substitui o `__code__` pelo método injetável do próprio StoreMonitor, preservando uma cópia do método original.

O método injetado chama:

```python
StoreMonitor.handleVarChange(name, old_value, new_value)
```

e, quando permitido, chama o método original.

### 7.2 Callback Python

O URM também registra um callback em `renpy.config.python_callbacks`.

O callback usa `get_changes()` do store para obter alterações e então chama `handleVarChange()` para os nomes encontrados.

O código também faz:

```python
renpy.game.context().force_checkpoint = True
```

Isso mostra uma integração direta com o mecanismo de checkpoint/rollback do Ren'Py.

Importante: isso não deve ser resumido como “qualquer alteração de variável gera um checkpoint imediatamente”. O que foi confirmado é que o callback Python do URM força um checkpoint no contexto, e que o processamento posterior pertence ao sistema de rollback do Ren'Py.

---

## 8. Mudança real de variável

Se uma variável estiver marcada como monitorada, `handleVarChange()` pode produzir uma notificação de mudança.

O fluxo é:

```text
execução do jogo
    ↓
variável realmente muda
    ↓
StoreMonitor
    ↓
oldVal / newVal
    ↓
VarsStore.isMonitored(varName)
    ↓
Notifications.add(...)
    ↓
URM_var_changed
```

A tela `URM_var_changed` pode mostrar:

```text
Variable
Previous value
New value
```

Isso é uma fotografia do estado efetivo observado em runtime, e não uma previsão baseada no código da Choice.

---

## 9. Exemplo completo: Choice que altera variável

Considere:

```renpy
menu:
    "A":
        RPjosy += 5

    "B":
        RPjosy -= 5
```

### Antes da escolha

Ren'Py está no Menu.

O URM encontra:

```text
Menu
├── Choice A
│   └── Python: RPjosy += 5
└── Choice B
    └── Python: RPjosy -= 5
```

O Walkthrough pode apresentar os dois códigos.

Nenhum deles foi executado pelo Walkthrough.

### Usuário escolhe A

```text
Usuário
  ↓
URMChoice.Action
  ↓
ChoiceReturn
  ↓
Ren'Py
  ↓
executa RPjosy += 5
```

Se `RPjosy` era `10`, o estado real passa a ser `15`.

### Observação da mudança

Se `RPjosy` estiver sendo monitorada:

```text
10 → 15
```

pode ser capturado pelo StoreMonitor.

O URM pode então apresentar uma notificação de mudança.

### Continuação

O jogo continua executando seus próprios nós:

```text
Python
↓
If
↓
Jump/Call
↓
Dialogue
↓
Menu
↓
...
```

O URM continua observando.

---

## 10. Rollback: quem realmente desfaz a escolha?

O ponto mais importante é este:

> **O URM não deve ser tratado como o componente responsável por restaurar manualmente o estado do jogo.**

No SDK Ren'Py 7.4.11 analisado, `StoreDict.get_changes()` participa da identificação das alterações do store, enquanto o sistema de rollback (`RollbackLog`) utiliza essas informações para manter/restaurar o estado necessário ao rollback.

Portanto, conceitualmente:

```text
Choice A
  ↓
Ren'Py executa
  ↓
RPjosy: 10 → 15
  ↓
estado é registrado pelo mecanismo de rollback
  ↓
usuário faz rollback
  ↓
Ren'Py restaura estado/contexto anterior
  ↓
RPjosy volta para 10
  ↓
fluxo anterior é reconstituído
```

O URM observa esse processo em vez de manter uma cópia independente do universo do jogo.

---

## 11. Por que isso é tão importante para o Wells

A arquitetura que queremos preservar é:

```text
                         REN'PY
                           │
              ┌────────────┼────────────┐
              │            │            │
             AST          STORE      ROLLBACK
              │            │            │
              ▼            ▼            ▼
           Choices      Monitor      Ren'Py
              │            │            │
              └──────┬─────┘            │
                     ▼                  │
                   WELLS ◄──────────────┘
                  observa
                  apresenta
```

Não queremos:

```text
Ren'Py
  +
Wells State
  +
Wells Interpreter
  +
Wells Rollback
```

porque isso criaria duas fontes de verdade e abriria espaço para divergências.

O Wells deve ser uma camada de observação/apresentação e, quando o usuário selecionar uma alternativa, utilizar a própria infraestrutura legítima de seleção do Ren'Py.

---

## 12. O papel de `rollback_is_fixed`

O `URMChoice.Action` executa explicitamente:

```python
renpy.game.log.rollback_is_fixed = False
```

antes de chamar `ChoiceReturn`.

A presença desse comando é evidência de que a seleção de uma Choice está relacionada a uma condição interna do log de rollback que o URM deliberadamente libera antes de devolver a seleção ao Ren'Py.

**A semântica exata desse campo ainda está em investigação.** Não devemos transformar sua existência em uma explicação definitiva antes de validar diretamente o código de `ChoiceReturn`, do fluxo de interação e do `RollbackLog` no SDK 7.4.11.

Esse ponto é uma peça pendente do circuito:

```text
ChoiceReturn
    ↓
rollback_is_fixed
    ↓
RollbackLog
    ↓
checkpoint/complete
    ↓
rollback
    ↓
restauração
    ↓
Menu novamente
```

---

## 13. Modelo mental consolidado

Uma representação útil do comportamento observado é:

```text
                 ┌────────────────────┐
                 │      REN'PY        │
                 │  executor real     │
                 └─────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
        MENU             STORE          ROLLBACK
          │                │                │
          ▼                ▼                ▼
      Choices          StoreMonitor       Ren'Py
          │                │
          ▼                ▼
      CodeView          VarsStore
          │                │
          └───────┬────────┘
                  ▼
             URM interface
                  │
                  ▼
             usuário decide
                  │
                  ▼
             ChoiceReturn
                  │
                  └──────────────→ REN'PY
```

Em linguagem informal: o URM fica “sentado com o balde de pipoca” enquanto o Ren'Py faz o trabalho pesado. Quando o Menu aparece, ele anuncia a Choice; quando o usuário escolhe, ele devolve a decisão ao Ren'Py; quando o estado muda, ele observa; quando o usuário faz rollback, ele deixa o Ren'Py restaurar o passado e volta a observar o fluxo reconstruído.

---

## 14. Consequências para o projeto Wells

Estas conclusões ainda são **arquitetura de referência**, não autorização para iniciar a implementação final.

### Já fortemente sustentado

- usar o `renpy.ast.Menu` real como fonte de Choices;
- extrair as alternativas diretamente dos itens do Menu;
- preservar condições e texto reais;
- inspecionar os nós AST pertencentes a cada alternativa;
- usar representação baseada em AST para o código exibido;
- separar “código da Choice” de “variável que realmente mudou”;
- deixar Ren'Py executar a escolha real;
- deixar Ren'Py administrar rollback;
- tratar StoreMonitor como observador/interceptor de estado, não como interpretador.

### Ainda não fechado

- semântica exata de `rollback_is_fixed` em 7.4.11;
- fluxo exato de `ChoiceReturn` até o registro da interação;
- momento preciso em que `force_checkpoint` produz efeito no ciclo do RollbackLog;
- comportamento em todas as formas de alteração de estado relevantes;
- compatibilidade exata entre versões do Ren'Py;
- limites e diferenças entre AST compilada e código-fonte textual original;
- comportamento de Choices com estruturas AST mais complexas;
- interação completa entre Menu, Call, Jump, If, rollback e replay.

**Conclusão de engenharia:** já existe evidência suficiente para afirmar que a arquitetura observada é extremamente promissora para o Wells, mas ainda não existe evidência suficiente para declarar o circuito inteiro fechado. A implementação de teste deve esperar a conclusão desta arqueologia.
