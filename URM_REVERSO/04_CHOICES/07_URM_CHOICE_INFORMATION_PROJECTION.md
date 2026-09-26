# Choices — projeção de informação, fidelidade estrutural e limites de interpretação

## Objetivo

Registrar a análise da segunda dimensão do sistema de Choices: não apenas como o URM seleciona uma Choice, mas como ele **lê, interpreta e apresenta** a informação encontrada no AST.

A distinção central é:

```text
REALIDADE DO REN'PY
    Menu.items
        ↓
    bloco AST
        ├── execução real
        └── leitura do URM
              ↓
        projeção interpretada
```

O URM pode ler corretamente a estrutura do engine e, ainda assim, apresentar uma representação que não seja uma reprodução completa da execução possível.

---

## 1. `Menu.items` é a fonte estrutural

No Ren'Py 7.4.11, um item de Menu é estruturado como:

```text
(label, condition, block)
```

onde `block` é a lista de nós AST associada à alternativa.

Portanto uma Choice pode ser vista como:

```text
Choice
├── texto original
├── condição
└── bloco de execução
    ├── AST node
    ├── AST node
    └── ...
```

Essa estrutura pertence ao Ren'Py, não ao URM.

---

## 2. `URMChoice` cria uma representação própria

O URM transforma o item em um objeto `URMChoice` com propriedades como:

```text
text
condition
isVisible
code
jumpTo
Action
```

Isso significa que o objeto não é uma cópia passiva do item do Ren'Py. Ele é uma **camada de adaptação/interpretação**.

A separação é:

```text
Menu.items
    ↓
URMChoice
    ├── representação visual
    ├── avaliação de estado
    ├── projeção de código
    └── heurística de destino
```

---

## 3. Texto visual versus valor usado na seleção

`URMChoice.text` usa substituição de texto do Ren'Py.

Assim, uma fonte como:

```text
"Olá [player_name]"
```

pode ser apresentada como:

```text
"Olá Davi"
```

Porém a ação do URM passa para `ChoiceReturn` o valor original de `choice[0]`, e não a propriedade visual `URMChoice.text`.

Portanto:

```text
choice[0]
   ├──→ substitute → interface
   │
   └──→ ChoiceReturn → mecanismo de seleção
```

A apresentação não substitui a estrutura real usada pelo motor.

---

## 4. Choices ocultas são mantidas para inspeção

`ChoicesClass.currentChoices` percorre os itens do Menu e cria `URMChoice` para alternativas que possuem conteúdo, independentemente de sua condição atual ser verdadeira ou falsa.

A visibilidade é calculada separadamente.

Isso produz uma diferença importante:

```text
Menu normal
    ↓
opções atualmente selecionáveis

URM
    ↓
estrutura de alternativas do Menu
    + estado de visibilidade
```

Essa é uma capacidade de inspeção/intervenção, não simplesmente uma réplica da interface nativa.

---

## 5. `isVisible` é uma reavaliação independente

O URM calcula a visibilidade avaliando a condição no store:

```python
eval(self.condition, renpy.store.__dict__)
```

Isso é uma segunda avaliação da expressão, separada da avaliação que o Menu normal realiza durante sua execução.

Para condições simples isso tende a coincidir com o estado esperado. Entretanto, conceitualmente não se deve transformar essa operação em uma garantia universal de equivalência temporal, especialmente para expressões que possam depender de chamadas ou efeitos de avaliação.

Regra para Wells:

> observar/reavaliar uma condição não deve ser tratado automaticamente como recuperar o resultado histórico que o engine utilizou em uma interação anterior.

---

## 6. `code` é uma projeção AST → texto

`URMChoice.code` usa:

```python
CodeView.nodesToCode(choice[2])
```

O processo é:

```text
AST real
   ↓
nodesToCode()
   ↓
texto legível
```

Não é:

```text
arquivo .rpy original
   ↓
cópia literal
```

Para `renpy.ast.Python`, o URM consegue usar `node.code.source`, mantendo uma relação forte com o código-fonte associado ao nó.

Para `If`, `Jump`, `Call`, `UserStatement`, `Translate` e outros nós, o CodeView reconstrói uma representação textual.

Portanto o texto exibido pode ser estruturalmente fiel sem ser literalmente idêntico ao código escrito pelo desenvolvedor.

---

## 7. `jumpTo` é uma heurística estrutural

O URM procura o primeiro `renpy.ast.Jump` diretamente presente na lista de nós do bloco da Choice.

Isso deve ser entendido como:

> primeiro `Jump` direto encontrado no conteúdo da alternativa, quando existente.

Não deve ser entendido como:

> próximo destino que necessariamente será executado em todos os cenários.

Por exemplo:

```text
Choice
└── If
    ├── condição A → Jump A
    └── condição B → Jump B
```

possui múltiplos destinos possíveis, mas uma busca estrutural simples pelo primeiro `Jump` não produz um grafo completo de execução.

Outro exemplo:

```text
Choice
└── Call A
    └── If
        └── Jump B
```

também não é representado adequadamente por uma propriedade que procura apenas `Jump` direto no primeiro nível do bloco.

Conclusão:

```text
jumpTo ≠ grafo de fluxo
jumpTo = heurística de destino estrutural
```

---

## 8. Estrutura e execução devem permanecer separadas

Uma Choice pode conter uma árvore de execução complexa:

```text
Choice
└── If
    ├── Python
    ├── Call
    │    └── Jump
    └── Jump
```

A existência desses nós informa o que **pode** acontecer, mas não determina sozinho o que acontecerá no estado atual.

Para saber o caminho real é necessário considerar a execução do AST, condições e estado do Store.

Assim existem três níveis:

```text
ESTRUTURA
    Menu.items / AST

ESTADO
    variáveis / condições atuais

EXECUÇÃO
    nós realmente percorridos
```

O URM Choice dialog é predominantemente uma ferramenta de inspeção estrutural com algumas avaliações de estado e heurísticas de fluxo.

---

## 9. Consequência para a futura análise de Paths

`URMChoice.jumpTo` e `PathDetection` não devem ser fundidos.

`jumpTo` responde aproximadamente:

> existe um `Jump` direto identificável neste bloco?

Path Detection responde outra pergunta:

> existem caminhos condicionais que o URM consegue detectar adiante no fluxo?

Uma análise completa de consequências futuras exigiria uma travessia mais profunda do AST e uma modelagem de controle que não está contida em `URMChoice.jumpTo`.

---

## 10. A “lâmpada do farol”

A metáfora do usuário é útil como ferramenta de diagnóstico:

```text
CARRO / SISTEMA
├── transmissão
│   └── rollback + nova decisão
│
└── farol
    └── leitura/apresentação das informações
```

A segunda investigação não deve partir da premissa de que o URM está errado. O ponto técnico é identificar **em que momento uma representação resumida deixa de corresponder ao comportamento completo do AST/runtime**.

A mesma distinção deverá ser aplicada ao URW, que é apenas referência visual/funcional e não fonte de engenharia.

---

## 11. Regras de preservação para o Wells

1. Preferir a estrutura AST/runtime fornecida pelo Ren'Py a parsing textual do script.
2. Separar texto original, texto substituído e valor usado na seleção.
3. Separar estrutura da Choice de seu estado de visibilidade.
4. Não tratar `CodeView` como cópia literal garantida do `.rpy`.
5. Não tratar `jumpTo` como previsão completa de fluxo.
6. Não executar os nós da Choice apenas para obter informação estrutural.
7. Não criar um Store paralelo para simular o runtime.
8. Se for necessário mostrar consequências, distinguir claramente:
   - consequência estrutural possível;
   - consequência condicionada;
   - consequência observada durante execução real.

---

## 12. Estado da investigação

### 🟢 Confirmado — URM

- `currentChoices` parte de `Menu.items`;
- `URMChoice` representa o item do Menu;
- `text` usa substituição;
- `isVisible` reavalia a condição;
- `code` usa `CodeView.nodesToCode`;
- `jumpTo` procura `Jump` direto;
- Choices ocultas permanecem na representação.

### 🔵 Confirmado — Ren'Py 7.4.11

- `Menu.items` contém texto/condição/bloco;
- o bloco é formado por nós AST;
- `Menu.execute()` utiliza o bloco escolhido para continuar a execução;
- `If`, `Call` e `Jump` possuem semânticas de controle distintas.

### 🟡 Observação sua

A interface inspirada em URW pode apresentar informações de Choice que parecem não corresponder completamente ao comportamento esperado durante o jogo.

### 🟠 Hipótese

A divergência pode surgir quando uma representação estrutural/heurística é apresentada como se fosse uma descrição completa do fluxo de execução.

A causa exata no URW ainda precisa ser demonstrada por código/traceback/runtime e não deve ser atribuída ao sistema sem evidência.

---

## Princípio

> **O farol deve mostrar a estrada que foi identificada; não devemos confundir o feixe de luz com a estrada inteira.**

E, para o Wells:

> **estrutura → estado → execução → apresentação** devem continuar sendo camadas distintas.
