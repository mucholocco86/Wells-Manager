# Choices — CodeView interativo, edição de valores e evidência de uso

## Objetivo

Este documento registra uma distinção metodológica importante obtida a partir da observação de uso do URM e que deve orientar a próxima etapa da engenharia reversa.

A observação do usuário **não é tratada como prova da implementação interna**. Ela serve como pista para localizar no código as peças responsáveis pelo comportamento observado.

---

## 1. O painel de Choices é um overlay de inspeção

Os screenshots `screenshot0018.png` e `screenshot0019.png` mostram o painel de Choices do URM **sobreposto à tela real de Choice do jogo**.

O comportamento observado é:

```text
Jogo chega a um Menu real
        ↓
URM detecta a Choice
        ↓
notificação "Choices detected"
        ↓
usuário abre o painel URM
        ↓
URM_choices aparece sobre o jogo
        ↓
Choice original continua sendo a estrutura do jogo
```

Portanto, o painel `URM_choices` não deve ser documentado como substituição do Choice screen original.

---

## 2. A lista do painel representa as alternativas do Menu atual

O usuário observa as alternativas na ordem em que aparecem no jogo.

A coluna `Visible` representa a avaliação que o URM faz da condição da alternativa.

No código já confirmado:

```python
eval(self.condition, renpy.store.__dict__)
```

e `currentChoices` não remove simplesmente os itens cuja condição seja falsa.

Assim:

```text
Choice A → Visible True
Choice B → Visible False
Choice C → Visible True
```

pode aparecer no painel mesmo que B não esteja disponível na interface normal do jogo.

---

## 3. Evidência de edição: nem todo código mostrado é editável

O usuário esclareceu que exemplos como:

```text
 tree_thank = True
```

foram fornecidos apenas para mostrar o tipo de código que o URM exibe atrás de uma Choice. Isso **não significa** que essa linha possa ser editada diretamente naquela representação.

Em contraste, em determinadas linhas/valores, por exemplo:

```text
RPjosy = 3
```

o usuário consegue clicar na representação e modificar o `value`, observando que valores como:

```text
3 → 5
3 → 15
3 → 99
3 → -5
3 → -50
```

podem ser utilizados.

### Classificação

- 🟡 **OBSERVAÇÃO SUA:** determinados valores representados no CodeView podem ser selecionados e modificados através da interface do URM.
- 🟡 **OBSERVAÇÃO SUA:** nem toda linha apresentada no código possui essa mesma capacidade de edição.
- 🟢 **CONFIRMADO — changelog URM:** o sistema possui variáveis interativas no CodeView.
- 🟢 **CONFIRMADO — changelog URM:** houve suporte/correções específicas para alteração de valores `int`/`float`.
- 🟠 **HIPÓTESE:** existe uma cadeia específica de apresentação → identificação do tipo de variável → Action de edição → alteração do Store. Essa cadeia ainda precisa ser seguida diretamente no código.

---

## 4. A pista não deve ser confundida com a implementação

A partir desta observação, quando a engenharia reversa encontrar elementos aparentemente estranhos relacionados a:

```text
value
setValue
variable
interactive
edit
modify
Var
VarsStore
CodeView
Action
```

eles não devem ser descartados apenas porque parecem não pertencer ao núcleo de Choices.

A pergunta correta será:

```text
Esse elemento participa da cadeia que transforma
um valor mostrado no CodeView em uma operação editável?
```

Somente o rastreamento de chamadas, propriedades e Actions poderá responder.

---

## 5. Relação provável com o sistema de variáveis

O URM já possui um sistema independente de representação de variáveis, incluindo `Var` e `VarsStore`.

O changelog também registra:

- suporte a listas, dicionários e objetos;
- edição de variáveis float;
- correção para alteração de valores int/float;
- variáveis interativas no CodeView;
- possibilidade de lembrar/observar variáveis a partir do CodeView;
- abertura de listas/dicionários/objetos a partir do CodeView.

Esses fatos tornam plausível investigar a conexão entre CodeView e o sistema de variáveis, **mas não autorizam assumir que toda edição do CodeView seja simplesmente uma chamada direta de `VarsStore`**.

Essa relação precisa ser demonstrada pelo código.

---

## 6. Outras áreas editáveis do URM

O usuário também identificou nos screenshots `screenshot0014.png` e `screenshot0016.png` outras áreas do URM que permitem modificar elementos do jogo.

Ele deliberadamente não utilizou algumas dessas capacidades por receio de alterar o estado do jogo e não saber restaurá-lo com segurança.

Isso é relevante para a investigação porque:

```text
capacidade observada na interface
        ↓
não implica que o usuário tenha testado todas as variantes
        ↓
mas fornece uma pista de funcionalidades que precisam ser localizadas
```

Não devemos preencher lacunas com experimentação destrutiva. A implementação deve ser localizada na fonte do URM sempre que possível.

---

## 7. Choices, edição e execução são camadas diferentes

Até o momento, a separação segura é:

```text
                 Choice real
                     │
          ┌──────────┴──────────┐
          │                     │
       inspeção              execução
          │                     │
          ▼                     ▼
     URM CodeView            Ren'Py
          │
          ├── código exibido
          ├── condição
          ├── label
          └── variáveis interativas
                         │
                         ▼
                   edição de value
                         │
                         ▼
                    Store real
```

O diagrama acima é **um mapa de investigação**, não uma descrição final da implementação. As ligações ainda precisam ser confirmadas no código.

---

## 8. Impacto na investigação de fixed rollback

A existência de edição de valores torna ainda mais importante investigar a relação entre alteração de estado e rollback.

Não devemos assumir que:

```text
editar variável
→ alterar definitivamente o jogo
```

nem que:

```text
editar variável
→ rollback automaticamente desfaz
```

A resposta depende de como a alteração chega ao Store, de como o Ren'Py registra a mutação e de quais mecanismos do URM entram em ação (`Var`, `StoreMonitor`, callbacks, checkpoint, rollback etc.).

Por isso a edição deve ser investigada como uma **cadeia própria**, depois cruzada com o circuito de rollback.

---

## 9. Evidência histórica do próprio URM

O changelog do URM registra em 6 de julho de 2024:

- CodeView inteligente para Paths e Choices;
- código com syntax highlighting;
- **interactive variables and labels in the code**;
- resultados de condições `if` exibidos no código.

Em 14 de julho de 2024 registra ainda:

- opção de lembrar e observar variáveis a partir do CodeView;
- abrir listas/dicionários/objetos a partir do CodeView;
- fechamento do diálogo ao fechar o painel pai.

O changelog anterior registra suporte/correções para edição de valores numéricos.

Esses registros são evidência independente de que a interatividade observada pelo usuário é uma funcionalidade real do URM e não deve ser tratada como uma interpretação visual equivocada.

---

## 10. Próxima escavação recomendada

A próxima análise deve localizar, no código do URM:

1. onde o CodeView constrói os elementos interativos;
2. como uma variável é reconhecida dentro da representação do código;
3. qual Action é associada ao clique;
4. qual tela/dialog é aberto para edição;
5. como o novo `value` é validado;
6. como o valor chega ao Store;
7. como `Var` participa dessa operação, se participar;
8. como `VarsStore` participa, se participar;
9. se `StoreMonitor` observa essa alteração;
10. se a alteração força checkpoint;
11. como rollback trata essa alteração;
12. quais dessas peças pertencem ao sistema de Choices e quais são infraestrutura compartilhada do URM.

### Regra

**Não remover, simplificar ou transplantar nenhuma dessas peças ainda.**

Primeiro fechar a cadeia completa.

---

## Classificação final desta etapa

### 🟢 CONFIRMADO — URM
- CodeView possui variáveis interativas;
- CodeView possui labels interativos;
- Choices possuem CodeView;
- o URM possui infraestrutura para modificar variáveis;
- existem correções específicas para edição de `int`/`float`;
- o painel de Choices é aberto como interface do URM sobre o fluxo do jogo.

### 🟢 CONFIRMADO — fonte já analisada
- `URMChoice.code` usa `CodeView.nodesToCode(choice[2])`;
- `renpy.ast.Python` é representado usando `node.code.source`;
- `URMChoice.Action` retorna um `ChoiceReturn` ao mecanismo de interação do Ren'Py.

### 🟡 OBSERVAÇÃO SUA
- determinados valores como `RPjosy = 3` podem ser clicados/editados no CodeView;
- a edição permite valores positivos e negativos;
- nem toda linha mostrada no código é editável dessa forma;
- existem outras áreas do URM com capacidades de modificação que você preferiu não utilizar.

### 🟠 HIPÓTESE
- existe uma cadeia específica de CodeView interativo até alteração do Store;
- parte dessa infraestrutura pode ser compartilhada com a área geral de variáveis do URM.

### 🔴 NÃO CONCLUIR AINDA
- que `CodeView` seja o responsável direto pela mutação;
- que toda edição passe por `VarsStore`;
- que toda edição gere checkpoint da mesma maneira;
- que rollback trate todas as edições exatamente como trata alterações produzidas pela execução normal do jogo.
