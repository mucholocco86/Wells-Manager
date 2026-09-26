# 08 — Fluxo de execução do bloco de uma Choice: If, Call, Jump e caminhos possíveis

**Status:** 🟢 confirmado — Ren'Py 7.4.11 para os mecanismos descritos abaixo.

## 1. Objetivo

Este documento fecha uma lacuna importante da árvore de Choices: uma Choice não é necessariamente equivalente a um único `Jump`.

`Menu.items` fornece, para cada Choice, um bloco de nós AST. O bloco pode conter Python, diálogo e estruturas de controle como `If`, `Call` e `Jump`. Portanto, para responder o que uma Choice pode fazer, é necessário distinguir **estrutura**, **execução atual** e **destino eventual**.

## 2. O bloco da Choice é uma sequência de nós AST

Em Ren'Py 7.4.11, `Menu.items` armazena entradas no formato conceitual:

```text
(label, condition, block)
```

onde `block` é uma lista de nós AST.

A infraestrutura de AST possui `Node.next`. O encadeamento é construído por `chain_block()`: cada nó é encadeado ao seguinte e o último ao nó que continua depois do bloco. `Node.execute()` deve escolher o próximo nó chamando `next_node(...)`.

Isso produz duas ideias diferentes:

```text
estrutura física do bloco
    ↓
lista de nós AST

fluxo de execução
    ↓
Node.execute()
    ↓
next_node(...)
```

O segundo não é necessariamente igual a simplesmente caminhar pela lista.

## 3. Caso simples: Choice → Jump

```text
Choice
└── Jump A
```

Aqui existe uma relação estrutural direta: o bloco contém um `Jump`.

`Jump.execute()` resolve o alvo (`target`, inclusive expressão dinâmica quando aplicável), procura o nó pelo script e usa `next_node(rv)` para transferir a execução para esse alvo. O `Jump` também é anormal para o encadeamento normal: ele não depende do `Node.next` como destino narrativo final.

Portanto:

```text
Choice
 ↓
primeiro nó do bloco
 ↓
Jump A
 ↓
label A
```

É correto dizer que existe um **destino direto explícito**.

## 4. Caso ramificado: Choice → If → A/B

```text
Choice
└── If
    ├── condição 1 → bloco A
    └── else/condição 2 → bloco B
```

A existência de A e B no AST não significa que ambos serão executados nesta passagem.

`If.execute()` avalia as entradas na ordem e seleciona o primeiro bloco cuja condição seja verdadeira. O fluxo real depende do estado atual do jogo no momento da execução.

Assim temos três níveis diferentes:

```text
AST
 ├── caminho A existe
 └── caminho B existe

estado atual
 └── condição determina qual caminho é executável agora

execução
 └── apenas o bloco selecionado é seguido nesta passagem
```

Isso é fundamental para uma leitura Walkthrough: **possibilidade estrutural não é o mesmo que caminho atualmente executado**.

## 5. Caso intermediário: Choice → Call → retorno

```text
Choice
└── Call X
    ↓
label X
    ↓
retorno
    ↓
continuação do fluxo
```

`Call` não deve ser tratado como `Jump`.

O `Call` estabelece uma chamada de label e mantém a informação necessária para retornar ao ponto apropriado quando o label termina. Portanto, uma análise que apenas procura `Jump` perde uma parte relevante do comportamento de uma Choice.

Consequentemente, `URMChoice.jumpTo` é deliberadamente uma projeção limitada: ele procura o primeiro `Jump` direto no bloco da Choice e não representa um grafo completo de execução.

## 6. Caso misto: Python + If + Call/Jump

Uma Choice pode ter uma estrutura como:

```text
Choice
├── Python
├── If
│   ├── condição verdadeira → Call A
│   └── condição falsa → Jump B
└── continuação possível
```

Aqui não existe uma resposta única obtida somente olhando para o texto da Choice ou somente procurando `jumpTo`.

É necessário correlacionar:

1. os nós presentes no bloco;
2. as condições armazenadas no AST;
3. o estado atual usado para avaliar essas condições;
4. a semântica de `Call`/`Jump`;
5. o encadeamento `Node.next` quando o fluxo normal continua;
6. as consequências de execução dos nós intermediários.

## 7. Quatro conceitos que não devem ser confundidos

### 7.1 Destino direto

É algo explicitamente indicado por um nó, como:

```text
Jump A
```

### 7.2 Próximo nó

É o próximo nó de execução escolhido pelo mecanismo AST naquele momento. Ele pode vir de `Node.next` ou ser selecionado pelo próprio `execute()`.

### 7.3 Caminhos possíveis

É o conjunto de caminhos representados pela estrutura AST, incluindo ramos de `If` que podem ou não ser escolhidos dependendo do estado.

### 7.4 Caminho atualmente executável

É o caminho que resulta da avaliação do AST com o estado real naquele momento.

Esses quatro conceitos podem coincidir em um caso simples, mas não são sinônimos.

## 8. Consequência para a interpretação de Choices

A pergunta:

> “O que esta Choice faz?”

não possui sempre uma resposta única baseada em um único campo.

A resposta precisa ser formulada conforme a pergunta desejada:

```text
“O que ela contém?”
→ Menu.items + AST do bloco

“Onde ela aponta diretamente?”
→ Jump/Call explícitos encontrados na estrutura

“Quais caminhos existem?”
→ AST + ramos condicionais

“Qual caminho acontece agora?”
→ AST + estado atual + avaliação das condições

“O que acontece depois de escolher?”
→ execução dos nós, retornos, estado alterado e próximos nós
```

## 9. Relação com URMChoice e CodeView

Isso explica por que `URMChoice.code` é mais rico que `jumpTo`.

```text
Menu.items
    ↓
URMChoice
    ├── text
    ├── condition
    ├── isVisible
    ├── code
    └── jumpTo
```

`code` utiliza `CodeView.nodesToCode()` para projetar o bloco AST em uma representação textual mais estrutural.

`jumpTo` é apenas uma heurística de destino direto: ele não é um analisador completo do fluxo.

Portanto, não devemos interpretar `jumpTo` como “resultado final da Choice”.

## 10. Regra para o futuro Walkthrough

Uma implementação fiel ao conhecimento adquirido deve separar explicitamente:

```text
CHOICE
├── estrutura
│   └── nós AST presentes
│
├── estado
│   └── valores que influenciam condições
│
├── caminhos possíveis
│   └── ramos representados pelo AST
│
├── caminho executável agora
│   └── resultado da avaliação no estado atual
│
└── consequências observáveis
    └── mudanças produzidas pela execução real
```

A interface não deve apresentar como fato uma consequência que apenas foi deduzida de um `Jump` ou de um texto projetado.

## 11. Classificação epistemológica

- 🟢 **CONFIRMADO — Ren'Py 7.4.11:** `Menu.items` contém blocos AST; nós possuem `next`; `chain_block()` encadeia blocos; `Node.execute()` escolhe o próximo nó; `If`, `Call` e `Jump` possuem semânticas diferentes.
- 🟢 **CONFIRMADO — URM:** `URMChoice.code` usa `CodeView.nodesToCode()`; `jumpTo` procura um `Jump` direto no conteúdo da Choice.
- 🟠 **HIPÓTESE/PROJETO:** um futuro Walkthrough pode apresentar caminhos possíveis e caminho atualmente executável separadamente, usando AST + estado real, sem criar um segundo motor de execução.
- 🔴 **DESCARTADO:** tratar `jumpTo` como destino completo ou tratar qualquer Choice como “um Jump”.

## 12. Conclusão

A árvore de Choices precisa ser entendida como uma árvore de **estrutura + estado + execução**, e não como uma lista de textos com destinos.

A informação estrutural responde ao que existe. O estado responde ao que pode ser escolhido agora. A execução responde ao que realmente acontece.

Essa separação é uma das bases para que o futuro sistema de Walkthrough reflita o comportamento real do Ren'Py, em vez de fabricar consequências por inferência superficial.
