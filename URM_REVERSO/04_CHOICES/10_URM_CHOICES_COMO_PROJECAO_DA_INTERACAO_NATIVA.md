# 10 — URM Choices como projeção da interação nativa

**Status:** 🟢 confirmado — arquitetura principal; detalhes de interação confirmados no Ren'Py 7.4.11.  
**Finalidade:** registrar a ponte entre a leitura estrutural feita pelo URM e a interação real do Menu, e preparar a transferência para o primeiro Walkthrough experimental do Wells.

---

## 1. A descoberta central

A tela `URM_choices` não constitui um segundo executor de Choices.

O URM lê o `Menu` atual diretamente pelo contexto/script:

```text
renpy.game.context()
        ↓
current
        ↓
renpy.game.script.lookup(current)
        ↓
renpy.ast.Menu
        ↓
Menu.items
        ↓
URMChoice
```

A tela transforma essa leitura em uma superfície alternativa de inspeção e seleção.

Isso deve ser separado do executor nativo:

```text
                 REN'PY
                   │
                   ▼
                 Menu
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   interação nativa       leitura URM
        │                     │
        ▼                     ▼
   ChoiceReturn          URMChoice
        │                     │
        └──────────┬──────────┘
                   ▼
              apresentação
```

---

## 2. O URM lê uma fonte diferente daquela que a Choice Screen recebe

Existe uma distinção importante entre:

### Fonte estrutural do URM

`ChoicesClass.currentChoices` consulta o `renpy.ast.Menu` e seus `Menu.items`. Cada item contém conceitualmente:

```text
item[0] → texto
item[1] → condição
item[2] → bloco AST
```

`URMChoice` mantém essa estrutura para inspeção.

### Dados preparados pelo Ren'Py para a Choice Screen

`renpy.exports.display_menu()` constrói objetos `MenuEntry` para a tela de Choice. Cada entrada recebe, entre outros dados, `label`, `action`, `chosen`, `args` e `kwargs`.

Portanto:

```text
Menu.items
   │
   ├──────────────→ URMChoice
   │                 (estrutura AST)
   │
   └→ display_menu()
          ↓
       MenuEntry
          ↓
       Choice Screen
```

Esta é uma informação importante para o futuro Wells: **a interface nativa de Choice não precisa carregar o bloco AST completo para que o Wells o descubra**. O Wells pode consultar a fonte estrutural do Menu separadamente e correlacioná-la com a interação pelo índice/valor apropriado.

---

## 3. `URM_choices` é uma superfície modal sobre a interação

A tela do URM declara:

```renpy
screen URM_choices():
    layer 'x52Overlay'
    style_prefix 'x52URM'
    modal True
```

Ela mostra uma tabela contendo, entre outras informações:

```text
#
Choice
Visible
Code
Next label
Select
```

A tela não chama `Jump.execute()`, `Call.execute()`, `If.execute()` ou executores equivalentes para realizar a escolha.

Sua ação de seleção é `choice.Action`.

---

## 4. `URMChoice.Action` usa `ChoiceReturn`

No URM 2.6.2:

```python
@property
def Action(self):
    def choose():
        renpy.game.log.rollback_is_fixed = False
        return renpy.ui.ChoiceReturn(
            self._m1_choices__choice[0],
            self._m1_choices__index
        )()
    return choose
```

O ponto essencial é a chamada:

```python
ChoiceReturn(... )()
```

No Ren'Py 7.4.11, `ChoiceReturn` herda de `ChoiceActionBase`, e sua chamada retorna `self.value`. A infraestrutura de Action define `__call__()` como o ponto de execução da ação de interface.

Portanto a função do `ChoiceReturn` é devolver o valor da alternativa à interação, e não executar o bloco AST da alternativa.

---

## 5. O circuito completo da seleção

O circuito confirmado pode ser representado assim:

```text
Menu.execute()
      ↓
renpy.exports.menu()
      ↓
display_menu()
      ↓
Choice Screen
      ↓
usuário seleciona
      ↓
ChoiceReturn.__call__()
      ↓
valor da Choice
      ↓
ui.interact()
      ↓
resultado da interação
      ↓
checkpoint(rv)
      ↓
Menu.execute()
      ↓
primeiro nó do bloco escolhido
      ↓
execução AST real
```

A ordem microscópica entre todos os estados internos continua sendo uma área que pode exigir trace adicional, mas a divisão de responsabilidades está confirmada.

---

## 6. Por que o bloco AST não deve ser executado pelo Walkthrough

O bloco de uma Choice pode conter:

```text
Python
Dialogue
If
Call
Jump
ou outras statements
```

E pode possuir ramificações:

```text
Choice
└── If
    ├── caminho A
    └── caminho B
```

Executar esse bloco apenas para descobrir o que ele contém criaria um segundo caminho de execução e poderia produzir efeitos no Store, Context, rollback ou outros sistemas.

O Walkthrough deve fazer:

```text
ler AST
   ↓
interpretar estrutura
   ↓
apresentar informação
```

em vez de:

```text
ler AST
   ↓
executar AST para descobrir resultado
   ↓
tentar desfazer resultado
```

---

## 7. `rollback_is_fixed` e `force_checkpoint` não devem ser misturados

O URM limpa:

```python
renpy.game.log.rollback_is_fixed = False
```

antes de retornar o `ChoiceReturn`.

Já `force_checkpoint` aparece em outro circuito do URM, especialmente associado ao `StoreMonitor`, que sinaliza `Context.force_checkpoint` para o processamento nativo do rollback.

Portanto o seguinte não foi demonstrado e não deve ser adotado como regra:

```text
ChoiceReturn
   ↓
force_checkpoint
```

A distinção correta é:

```text
rollback_is_fixed
    → estado de fixed rollback

force_checkpoint
    → solicitação de checkpoint forçado
```

---

## 8. Texto visual e valor de seleção

O URM possui duas perspectivas sobre o texto:

```text
choice[0]
   │
   ├──→ renpy.exports.substitute()
   │       ↓
   │     URMChoice.text
   │       ↓
   │     apresentação
   │
   └──→ ChoiceReturn
           ↓
        valor usado no circuito
```

Isso evita confundir:

- texto original da estrutura;
- texto substituído para apresentação;
- valor retornado pela interação.

O futuro Wells deve preservar essa separação.

---

## 9. Condição e visibilidade

O URM não elimina as alternativas ocultas da representação estrutural.

`currentChoices` percorre os itens válidos de `Menu.items` e depois `URMChoice.isVisible` reavalia a condição.

Assim:

```text
estrutura
   ↓
Choice A
Choice B
Choice C

estado atual
   ↓
True / False / True

apresentação URM
   ↓
A visível
B oculta
C visível
```

A visibilidade é uma propriedade derivada do estado atual. Não deve ser tratada automaticamente como um registro histórico do que o Menu avaliou em uma interação anterior.

---

## 10. `CodeView` é projeção, não executor

`URMChoice.code` chama:

```python
CodeView.nodesToCode(self._m1_choices__choice[2])
```

Portanto:

```text
bloco AST
   ↓
nodesToCode()
   ↓
texto legível
```

O `CodeView` não executa os nós para gerar o texto.

Isso fornece um modelo útil para o Wells:

```text
AST
 ↓
projeção estrutural
 ↓
interface Walkthrough
```

---

## 11. A descoberta do protótipo experimental do Wells

**🟡 OBSERVAÇÃO SUA — Wells Beta / protótipo externo:**

Um protótipo experimental criado a partir desta biblioteca conseguiu estabelecer comunicação visual entre uma camada Walkthrough e a interface de Choices.

Foi observado que:

```text
Walkthrough
    ↓
mensagem/informação
    ↓
interface Choice
```

funcionou.

Também foi observado que, após uma Choice ser selecionada, o rollback permitiu retornar à Choice e realizar uma nova seleção corretamente.

Isso constitui evidência experimental de que a camada adicional pode coexistir com o circuito nativo de interação/rollback sem exigir um segundo sistema de rollback.

### Limite da evidência

Esse experimento não demonstra que a implementação estrutural do Walkthrough esteja completa. Ele demonstra principalmente a viabilidade da integração e da seleção.

---

## 12. O que o protótipo externo simplificou em excesso

A análise do protótipo revelou uma diferença importante entre uma ponte funcional e o Walkthrough que estamos projetando.

Uma implementação resumida tende a fazer algo como:

```text
Choice
 ↓
procura primeiro Python/Call/Jump
 ↓
mostra resultado
```

Isso não é suficiente.

O modelo que já foi comprovado em nossa engenharia exige:

```text
Choice
├── texto
├── condição
├── visibilidade
├── índice
├── bloco AST completo
│   ├── nós
│   ├── If
│   ├── Call
│   ├── Jump
│   └── outros nós
├── projeção de código
├── destinos explícitos
├── caminhos possíveis
└── relação com o estado atual
```

Em particular, não devemos adotar como regra estrutural:

```text
primeiro Jump encontrado = caminho completo
Python encontrado = consequência
isVisible = True
Choice.Action = force_checkpoint
```

Essas simplificações não são sustentadas pela engenharia realizada.

---

## 13. A menor arquitetura segura para o primeiro Walkthrough

Com o conhecimento atual, já existe uma base suficiente para um **MVP experimental somente-leitura**, desde que ele seja conscientemente limitado.

O MVP pode começar por:

```text
1. detectar Menu atual
2. enumerar Menu.items
3. criar representação WFChoice
4. mostrar texto
5. mostrar condição
6. calcular visibilidade
7. guardar bloco AST sem executá-lo
8. projetar código
9. identificar nós de controle
10. apresentar informação estrutural
11. manter seleção nativa via ChoiceReturn
12. deixar rollback exclusivamente com Ren'Py
```

Depois do primeiro teste real:

```text
MVP
 ↓
teste
 ↓
observação
 ↓
problema concreto
 ↓
R&D
 ↓
expansão
```

Isso é preferível a tentar construir todo o Walkthrough de uma vez.

---

## 14. Relação entre os módulos futuros

Uma arquitetura experimental coerente pode ser:

```text
                    REN'PY
                      │
                      ▼
                 Menu / AST
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   WF Walkthrough             WF Choices
   (análise)                  (apresentação)
          │                       │
          │                       │
          └──────────┬────────────┘
                     ▼
                ChoiceReturn
                     │
                     ▼
                Ren'Py native
                     │
                     ▼
              execução / rollback
```

O Walkthrough e a interface de Choice podem conversar, mas nenhum dos dois deve assumir a responsabilidade do executor/rollback nativo.

---

## 15. Classificação final desta descoberta

### 🟢 CONFIRMADO — URM

- `ChoicesClass.currentChoices` parte do `Menu` atual e de `Menu.items`.
- `URMChoice` funciona como camada de representação sobre o item do Menu.
- `URM_choices` é uma tela modal de inspeção/seleção.
- `URMChoice.Action` usa `ChoiceReturn`.
- `URMChoice.Action` não executa manualmente o bloco AST.
- `URMChoice.code` usa `CodeView.nodesToCode()`.
- `URMChoice.jumpTo` é uma heurística limitada.

### 🔵 CONFIRMADO — Ren'Py 7.4.11

- `Action.__call__()` é o ponto de execução da Action.
- `ChoiceReturn` retorna seu `value`.
- `ChoiceReturn` gerencia estado de seleção/chosen conforme sua infraestrutura.
- `display_menu()` prepara `MenuEntry` para a Choice Screen.
- `display_menu()` chama `ui.interact()` e processa o valor retornado.
- O `Menu` continua a execução a partir do bloco correspondente à escolha.

### 🟡 OBSERVAÇÃO SUA — experimento

- A comunicação visual Walkthrough → Choice funcionou.
- O rollback após uma seleção permitiu retornar à Choice e selecionar novamente.

### 🟠 HIPÓTESE / PRÓXIMA IMPLEMENTAÇÃO

- O primeiro Walkthrough Wells pode ser construído como uma camada estrutural somente-leitura sobre o Menu nativo, correlacionando a análise com a interface de Choice por identidade/indexação sem assumir a execução do bloco.

---

## 16. Conclusão

A informação mais importante desta etapa é que **não precisamos escolher entre um Walkthrough rico e a preservação do sistema nativo de Choices**.

Podemos ter ambos:

```text
Ren'Py continua executando.

Wells continua observando.

Walkthrough interpreta.

Choice Screen apresenta.

ChoiceReturn comunica a seleção.

Rollback continua pertencendo ao Ren'Py.
```

Essa é a ponte que o protótipo experimental começou a validar.

A próxima etapa pode, portanto, sair da pergunta:

> “É possível fazer os módulos conversarem?”

porque já existe evidência experimental de que sim.

A pergunta passa a ser:

> **“Como expandir essa comunicação para transportar a árvore estrutural completa da Choice sem transformar o Wells em um segundo executor do Ren'Py?”**

Essa é a fronteira técnica adequada para o próximo ciclo de desenvolvimento.
