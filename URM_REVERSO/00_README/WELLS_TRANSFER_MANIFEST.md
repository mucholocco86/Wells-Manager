# MANIFESTO DE TRANSFERÊNCIA — WELLS / URM / LABORATÓRIO

## 0. Propósito

Este documento é um contrato de continuidade para outra conversa/conta do ChatGPT. O objetivo é continuar o projeto sem reiniciar a arqueologia.

Regra central:

> **Primeiro entender → depois inspecionar → depois planejar → só então modificar.**

O GitHub é a memória persistente do projeto. O histórico da conversa é contexto adicional, não a única fonte de conhecimento.

---

## 1. Organização do trabalho

Há dois papéis:

- **R&D/pesquisa:** engenharia reversa do URM, validação contra Ren'Py e documentação em `URM_REVERSO/`.
- **Laboratório:** desenvolvimento experimental do novo Walkthrough em `wells_beta/`.

A nova conversa deve agir como continuidade do mesmo parceiro técnico: preservar decisões, restrições, metodologia e distinções já estabelecidas.

---

## 2. Repositório e proteções

Repositório: `mucholocco86/modulos`

Commit histórico de referência: `81397ad93ae4a038f6b28a0668338aab5db6834d`

### Não modificar

- `wells/` — Wells estável.
- `renpy-7.4.11-sdk/` — referência técnica do Ren'Py 7.4.11.
- `__urw/` — referência funcional/visual do URW.

### Laboratório

- `wells_beta/` — novo MOD experimental.
- `URM_REVERSO/` — memória persistente da arqueologia e documentação.

---

## 3. Objetivo

Criar um **novo MOD Walkthrough próprio**, funcionalmente inspirado na ideia de inspeção de Choices, mas tecnicamente baseado no URM + Ren'Py + experiência experimental.

**Não reconstruir URW.** URW não é fonte de verdade arquitetural.

---

## 4. Fontes e classificação

### 🟢 CONFIRMADO — URM
Diretamente demonstrado pelo código/material do URM.

### 🔵 CONFIRMADO — REN'PY 7.4.11
Diretamente demonstrado pelo SDK.

### 🟡 OBSERVAÇÃO / EXPERIMENTO
Observado em execução/teste.

### 🟠 HIPÓTESE
Interpretação ainda não comprovada.

### 🔴 INCORRETO / DESCARTADO
Demonstrado como errado.

Nunca transformar hipótese em fato sem prova.

---

## 5. Descoberta arquitetural central

O Walkthrough deve ser uma **camada de projeção/observação sobre a interação nativa do Ren'Py**, não um segundo executor.

```text
Ren'Py Runtime
      |
      +--> execução nativa
      |
      +--> Walkthrough
             +--> leitura estrutural
             +--> análise
             +--> apresentação
```

**Walkthrough observa/projeta. Ren'Py executa.**

---

## 6. Descoberta central sobre Choices

Caminho confirmado:

```text
renpy.game.context()
  ↓
context.current
  ↓
renpy.game.script.lookup(current)
  ↓
renpy.ast.Menu
  ↓
Menu.items
```

A estrutura relevante de cada Choice é:

```text
(texto, condição, bloco)
```

O terceiro elemento é um bloco AST completo. Pode conter Python, If, Call, Jump, diálogo, Translate e outros nós.

Não reduzir uma Choice ao primeiro Jump/Call/Python.

---

## 7. URMChoice e CodeView

O URM possui `URMChoice`, que projeta dados da Choice, incluindo:

- `text`
- `condition`
- `isVisible`
- `code`
- `jumpTo`
- `Action`

`jumpTo` procura apenas o primeiro Jump e portanto **não representa o fluxo completo**.

`CodeView.nodesToCode(...)` é uma projeção AST → representação humana. Não é executor nem necessariamente reconstrução literal do fonte original.

`URMChoice.text` usa substituição para apresentação, enquanto a interação nativa usa o texto original armazenado no `Menu.items`. Não confundir texto visual com valor de interação.

---

## 8. Menu.items versus MenuEntry

`Menu.items` é a estrutura completa que pode ser analisada pelo Walkthrough.

O caminho da tela nativa utiliza `MenuEntry`.

```text
Menu.items
   ├──> Walkthrough / análise estrutural
   └──> display_menu() → MenuEntry → Choice Screen
```

Isso permite uma camada Walkthrough sem substituir a interface nativa.

---

## 9. Circuito nativo da Choice

```text
Menu.execute()
  ↓
renpy.exports.menu()
  ↓
display_menu()
  ↓
ui.interact()
  ↓
ChoiceReturn
  ↓
resultado
  ↓
checkpoint(rv)
  ↓
Menu.execute continua
  ↓
bloco escolhido
  ↓
AST
```

A Action do Walkthrough, se usada para seleção, deve retornar pelo mecanismo nativo (`ChoiceReturn`) e não executar o bloco manualmente.

---

## 10. Rollback

Rollback é responsabilidade do Ren'Py. Não criar segundo rollback, segundo executor ou segundo histórico.

Já foi demonstrado experimentalmente que o protótipo pode:

```text
Choice → seleção → avanço → rollback → Choice novamente → nova seleção
```

Isso é evidência experimental, não autorização para duplicar a arquitetura de rollback.

### Distinção crítica

Não confundir:

- `rollback_is_fixed`
- `force_checkpoint`

O primeiro participa do comportamento da interação/rollback em torno da seleção. O segundo pertence a outro circuito, incluindo StoreMonitor, e não deve ser colocado arbitrariamente na Action da Choice.

---

## 11. Protótipo da IA do Google

O protótipo experimental é material de bancada, não fonte de verdade.

Ele já demonstrou:

- comunicação visual Walkthrough ↔ Choice;
- integração com a tela de Choice;
- seleção;
- continuidade;
- rollback;
- retorno à Choice;
- nova seleção após rollback.

Mas possui simplificações conhecidas: primeiro Jump/Call/Python, `isVisible=True`, condição incompleta, consequências reduzidas e uso inadequado de `force_checkpoint` na Action.

Use-o como ponto de partida experimental, preservando o que já funcionou, mas reconstruindo a lógica sobre a arquitetura confirmada.

---

## 12. IA do Google e compatibilidade

A experiência não demonstra que a IA seja ruim. Ela pode produzir protótipos funcionais e respeita fortemente a documentação oficial do Ren'Py.

A limitação observada é principalmente de **memória contextual de curto prazo em conversas longas**: com muito contexto pode simplificar arquitetura, esquecer restrições ou perder relações previamente estabelecidas.

Por isso este manifesto e `URM_REVERSO/` existem como memória externa.

---

## 13. Ren'Py 8.5.3

Houve um experimento em que o protótipo inicial funcionava nas versões anteriores testadas, inclusive 7.4.11, mas encontrou traceback no Ren'Py 8.5.3 envolvendo a organização da `screen say` e propriedades como `xanchor`/`xalign`/posicionamento.

A IA do Google utilizou esse conhecimento para adaptar o protótipo ao 8.5.3.

Lição: arquitetura geral e detalhes específicos de SDK devem ser separados. Não assumir compatibilidade automática entre versões e não criar uma grande camada de compatibilidade antes de haver necessidade comprovada.

---

## 14. Primeiro MVP recomendado

Implementar apenas:

1. detectar `Menu` atual;
2. ler `Menu.items`;
3. representar Choices;
4. mostrar índice, texto, condição e visibilidade;
5. preservar o bloco AST;
6. produzir projeção legível do bloco;
7. integrar visualmente ao Wells Choices;
8. selecionar pelo circuito nativo;
9. testar rollback.

Não implementar ainda editor, edição de Store, replay, execução paralela, simulação, grafo avançado ou rollback próprio.

Arquitetura:

```text
Context / AST
      ↓
    Menu
      ↓
 Menu.items
   ↙       ↘
Walkthrough  Choice
   ↘       ↙
  ChoiceReturn
      ↓
 Ren'Py native
      ↓
   execução
```

---

## 15. Procedimento obrigatório

Antes de modificar:

1. Ler este manifesto.
2. Ler a documentação relevante de `URM_REVERSO/04_CHOICES/`.
3. Inspecionar `wells_beta`, especialmente o sistema atual de Choices e suas screens.
4. Identificar pontos de integração.
5. Apresentar arquitetura encontrada, arquivos que serão modificados, arquivos protegidos, plano e testes.
6. Só então modificar.

Se faltar informação: **pesquisar primeiro, nunca inventar**.

---

## 16. Como colaborar com o usuário

O usuário prefere português, explicações diretas, rigor técnico sem condescendência, exemplos concretos e distinção explícita entre fato, observação e hipótese.

Ele está aprendendo programação e arquitetura através do próprio processo de engenharia reversa. Não acelerar o processo sacrificando compreensão.

Quando algo estiver confirmado no código, dizer que está confirmado. Quando for hipótese, dizer que é hipótese. Quando houver dúvida, pesquisar.

O usuário trabalha com um modelo de pequena organização:

```text
DIREÇÃO
 ↓
PESQUISA / R&D
 ↓
ESPECIFICAÇÃO
 ↓
DESENVOLVIMENTO — WELLS BETA
 ↓
QA / TESTES
 ↓
DOCUMENTAÇÃO
 ↓
NOVO CONHECIMENTO
 ↓
PESQUISA
```

---

## 17. Regra de sobrevivência do projeto

Decisões arquiteturais importantes não devem depender da memória de uma conversa.

Registrar descobertas importantes no GitHub. O projeto deve sobreviver à troca de conta, conversa, modelo ou sessão.

> **O conhecimento do projeto deve sobreviver à conversa.**

---

## 18. Estado atual

A arqueologia não terminou, mas já existe conhecimento suficiente para iniciar o primeiro MVP estrutural do Walkthrough.

Objetivo imediato:

```text
MENU REAL
 ↓
MENU.ITEMS
 ↓
WALKTHROUGH
 ↓
WELLS UI
 ↓
CHOICE REAL
 ↓
CHOICERETURN
 ↓
REN'PY
 ↓
ROLLBACK
 ↓
CHOICE NOVAMENTE
```

Não reconstruir URW. Não criar segundo Ren'Py. Não criar segundo executor. Não criar segundo rollback. Não modificar `wells/`, SDK ou `__urw`.
