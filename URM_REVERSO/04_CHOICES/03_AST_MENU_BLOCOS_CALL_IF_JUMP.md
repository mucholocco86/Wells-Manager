# Choices — AST real: Menu, blocos, If, Call, Jump e continuidade

## Objetivo

Esta etapa fecha uma parte importante que estava aberta: o que o Ren'Py 7.4.11 realmente faz com os blocos pertencentes a uma Choice e por que `jumpTo` do URM não pode ser tratado como um analisador completo de fluxo.

Fonte de referência:

- `renpy-7.4.11-sdk/renpy/ast.py`

A análise abaixo é baseada no SDK 7.4.11 presente neste repositório.

---

## 1. O AST é estruturado em nós e blocos

O próprio `ast.py` define as classes correspondentes às statements da linguagem. `Node.chain(next)` recebe o nó que deverá ser seguido depois da execução do nó/bloco. `Node.execute()` é o contrato que cada nó usa para definir sua execução e chamar `next_node(...)` quando apropriado.

O mecanismo `next_node(n)` não executa `n` imediatamente: ele registra no contexto qual será o próximo nó a executar.

Portanto existe uma distinção fundamental:

```text
Node atual
   ↓ execute()
next_node(destino)
   ↓
contexto Ren'Py registra o próximo nó
   ↓
executor continua
```

Isso é mais preciso do que imaginar cada statement como uma função Python que chama diretamente a próxima função.

---

## 2. Menu: cada Choice possui um bloco próprio

Em Ren'Py 7.4.11, `Menu.items` contém estruturas do tipo:

```text
(label, condition, block)
```

O `block` é a lista de nós AST associados àquela alternativa.

O método `Menu.chain(next)` faz:

```text
Menu.next = next

para cada Choice:
    chain_block(block, next)
```

Isso é extremamente importante.

A alternativa não é apenas um texto ou um callback. Ela possui uma sequência real de nós AST.

Exemplo conceitual:

```text
Menu
├── Choice A
│   └── block
│       ├── Python
│       ├── If
│       └── Jump
│
└── Choice B
    └── block
        ├── Python
        └── Call
```

O Ren'Py prepara essas estruturas para que cada bloco tenha continuidade própria.

---

## 3. O Menu não executa o bloco antes da escolha

Durante `Menu.execute()`, o Ren'Py constrói a lista de escolhas e, para cada item que possui bloco, associa o valor `i` como identificador interno da alternativa.

O Menu chama:

```python
renpy.exports.menu(...)
```

e aguarda o valor retornado.

Depois:

```python
if choice is not None:
    next_node(self.items[choice][2][0])
else:
    next_node(self.next)
```

Logo:

```text
Menu
 ↓
interação
 ↓
índice escolhido
 ↓
primeiro nó do bloco escolhido
 ↓
execução real do bloco
```

Essa é a razão pela qual o URM consegue inspecionar `item[2]` antes da execução: o bloco já existe como AST, mas seus nós ainda não precisam ter sido executados.

---

## 4. `If` possui blocos próprios e todos são encadeados para a continuação

O `renpy.ast.If` contém:

```text
entries = [(condition, block), ...]
```

Seu `chain(next)` registra `self.next = next` e encadeia cada bloco para `next`.

Durante `execute()`:

```text
If
 ↓
avalia condition 1
 ├── True → primeiro nó do block 1
 └── False
      ↓
   condition 2
      ├── True → primeiro nó do block 2
      └── nenhuma verdadeira → self.next
```

Portanto um `If` dentro de uma Choice cria um segundo nível de decisão dentro do bloco da alternativa.

Isso demonstra diretamente por que:

```text
Choice → If → Jump A
```

não é equivalente, para fins de inspeção, a:

```text
Choice → Jump A
```

No primeiro caso, o `Jump` está dentro de um bloco filho do `If`; ele não está diretamente na lista `choice[2]` examinada por `URMChoice.jumpTo`.

---

## 5. `Call` e `Jump` não são a mesma operação

### Jump

O `Jump.execute()`:

1. obtém `target`;
2. se for expressão, avalia o destino;
3. procura o nó com `renpy.game.script.lookup(target)`;
4. marca o contexto como `abnormal = True`;
5. faz `next_node(rv)`.

Ele não cria uma pilha de retorno própria.

Modelo:

```text
Jump A
  ↓
lookup(A)
  ↓
next_node(nó de A)
  ↓
continuação em A
```

### Call

O `Call.execute()` usa:

```python
renpy.game.context().call(label, return_site=self.next.name)
```

e depois `next_node(rv)`.

Isso cria a semântica de chamada com retorno do contexto.

Modelo:

```text
Call A
  ↓
context.call(A, return_site=...)
  ↓
Label A
  ↓
Return
  ↓
retorno ao local registrado
```

Logo, para o Wells, não é correto agrupar `Call` e `Jump` como se ambos fossem apenas "próximo label".

---

## 6. O que isso explica sobre a hipótese do `Jump` "neutro"

A observação de gameplay continua sendo válida como observação, mas agora podemos separar o mecanismo real da aparência visual.

O `Jump` não executa `show`, `scene`, `with`, mudança de pose ou passagem de tempo.

Porém ele pode apontar para um label cujo primeiro nó seja, por exemplo:

```text
Jump cena_02
    ↓
label cena_02:
    ↓
Show personagem olhando para a porta
```

Nesse caso, para o jogador, a mudança visual pode parecer uma continuidade instantânea.

O que ocorreu tecnicamente foi:

```text
Jump
  ↓
transferência de controle
  ↓
Label alvo
  ↓
Show
  ↓
novo estado visual
```

Portanto a hipótese anterior fica refinada:

- 🟡 Observação: em gameplay, Jump pode aparecer associado a uma mudança visual contínua.
- 🟢 Confirmado Ren'Py: Jump é transferência de controle para o nó do label alvo.
- 🟢 Confirmado Ren'Py: `Show`, `Scene`, `Hide`, `With` etc. são nós separados que realizam operações visuais/temporais específicas.
- 🟠 Hipótese explicativa: a aparência de continuidade vem frequentemente do que existe no label alvo, não do Jump em si.
- 🔴 Não confirmado: Jump possui significado narrativo universal de "continuidade" ou "mudança de cena".

---

## 7. `Show`, `Scene` e `With` confirmam a separação entre controle e apresentação

No mesmo `ast.py`:

- `Show.execute()` chama `show_imspec(...)`;
- `Scene.execute()` chama `renpy.config.scene(...)` e pode mostrar uma imagem;
- `Hide.execute()` chama `renpy.config.hide(...)`;
- `With.execute()` avalia uma transição e chama `renpy.exports.with_statement(...)`.

Portanto o SDK fornece evidência direta para a separação:

```text
Jump = controle de fluxo
Show = alteração/apresentação de imagem
Scene = alteração de cena
With = transição
```

Uma cadeia pode combinar todos eles, mas um não deve ser atribuído semanticamente ao outro.

---

## 8. Por que `URMChoice.jumpTo` é deliberadamente limitado

O URM faz:

```python
for content in self._m1_choices__choice[2]:
    if isinstance(content, renpy.ast.Jump):
        self._m1_choices__jumpTo = content.target
        break
```

Esse código olha apenas para os elementos diretamente presentes no bloco da Choice.

Ele não chama `get_children()`.
Ele não percorre recursivamente `If.entries`.
Ele não segue `Call`.
Ele não executa condições.
Ele não percorre o label encontrado.

Portanto a coluna `Next label` da UI deve ser entendida como:

> **primeiro `Jump` direto encontrado no bloco AST da Choice.**

Ela não é um resultado de análise de fluxo global.

---

## 9. `get_children()` mostra que o AST consegue representar a árvore completa

O SDK também fornece `get_children()` para nós que possuem blocos internos.

Por exemplo:

```text
Menu
 └── Choice block
      └── If
           ├── block A
           └── block B
```

O `If.get_children()` visita seus blocos.

O `Menu.get_children()` visita os blocos de todas as Choices.

Isso prova que existe uma árvore estrutural completa disponível no AST. O fato de `URMChoice.jumpTo` não percorrê-la é uma decisão do URM, não uma limitação do AST do Ren'Py.

Essa distinção é importante para o futuro Wells:

```text
capacidade estrutural do Ren'Py
        ≠
profundidade da heurística escolhida pelo URM
```

---

## 10. `CodeView` e AST complexo

O `CodeView.nodesToCode()` também demonstra essa diferença de profundidade.

Ele trata `If` recursivamente, enquanto `jumpTo` não.

Portanto o mesmo bloco pode ser visto pelo URM em duas profundidades diferentes:

```text
CodeView
  ↓
recupera/reconstrói estruturas internas

jumpTo
  ↓
procura somente Jump direto
```

Isso é uma evidência importante contra a ideia de que todas as propriedades do `URMChoice` constituem um único analisador de fluxo.

São ferramentas diferentes, com objetivos diferentes.

---

## 11. Consequência para o Walkthrough

Se o Wells quiser responder:

> "O que existe dentro desta Choice?"

é legítimo percorrer a estrutura AST inteira da alternativa, desde que isso seja feito como **inspeção estrutural**, sem executar os nós.

Se quiser responder:

> "Para qual label esta Choice vai?"

não basta olhar o primeiro `Jump` direto. É necessário definir uma política de análise e deixar explícito que ela é uma previsão/descrição estrutural, não a execução real.

Se quiser responder:

> "O que esta Choice causará?"

não pode concluir isso apenas do `jumpTo`.

É necessário seguir o fluxo estrutural, considerar condições e chamadas e, dependendo da pergunta, separar aquilo que é código potencial daquilo que efetivamente foi executado.

Essa última distinção ainda não autoriza o Wells a virar um segundo interpretador.

---

## 12. Modelo consolidado da Choice

```text
REN'PY AST

Menu
 │
 ├── Choice A ── block A
 │               │
 │               ├── Python
 │               ├── If
 │               │    ├── block A1
 │               │    └── block A2
 │               ├── Call
 │               └── Jump
 │
 └── Choice B ── block B
                 ├── Python
                 └── Jump

              │
              ▼
       URM ChoicesClass
              │
       ┌──────┼──────────┐
       ▼      ▼          ▼
     text  condition   code
                         │
                         ▼
                      CodeView

       jumpTo
          │
          ▼
  primeiro Jump DIRETO

Seleção real
     │
     ▼
ChoiceReturn
     │
     ▼
Ren'Py Menu.execute()
     │
     ▼
primeiro nó do bloco escolhido
     │
     ▼
execução real dos nós
```

---

## 13. Regras novas confirmadas

1. **Choice possui bloco AST real.**
2. **Menu encadeia cada bloco de Choice para a continuação do Menu.**
3. **Após seleção, Menu aponta para o primeiro nó do bloco escolhido.**
4. **If possui blocos próprios e encadeia cada um deles.**
5. **Call usa contexto de chamada/retorno; Jump não é equivalente a Call.**
6. **Jump transfere controle; não é uma operação visual.**
7. **Show/Scene/Hide/With são operações AST distintas de Jump.**
8. **URM `jumpTo` não percorre a árvore interna; é uma heurística de Jump direto.**
9. **A AST do Ren'Py oferece estrutura suficiente para inspeção recursiva sem executar os nós.**
10. **A profundidade de cada ferramenta URM deve ser analisada separadamente; não existe um único "analisador de Choice" fazendo tudo.**

---

## 14. Estado da hipótese sobre `Jump`

A hipótese do usuário sobre o uso de Jump em mudanças de apresentação fica tecnicamente plausível, mas agora sem atribuir ao Jump uma função que ele não possui.

Formulação segura:

> **Um Jump pode ser usado como ponte de controle para um label cuja execução produz uma mudança visual imediata ou uma continuidade de cena. A mudança visual pertence aos nós alcançados, não ao Jump.**

Essa formulação deve substituir qualquer explicação anterior que tratasse Jump como uma espécie de transição visual ou como um elemento narrativamente neutro por definição.
