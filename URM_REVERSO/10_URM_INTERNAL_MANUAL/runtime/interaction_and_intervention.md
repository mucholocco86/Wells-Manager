# Interação, representação e intervenção no URM

## Objetivo

Registrar uma propriedade arquitetural que ficou mais clara durante a análise: o URM não se limita a observar informações e exibi-las. Em vários pontos, ele transforma informações reconstruídas ou valores de estado/configuração em **elementos interativos**, e essas interações podem abrir ferramentas capazes de consultar, modificar ou redirecionar o comportamento observado.

Esta página descreve a arquitetura funcional sem confundir três coisas diferentes:

1. representação de informação;
2. interação do usuário com essa representação;
3. intervenção efetiva no estado, execução ou configuração.

## Modelo geral

```text
URM
 │
 ├── observa/reconstrói
 │
 ├── representa informação
 │
 ├── torna partes selecionadas interativas
 │
 └── encaminha a interação para uma ferramenta
            │
            ├── consultar
            ├── modificar estado
            ├── replay/jump
            └── alterar configuração/dado operacional
```

Portanto, **interação** é uma camada mais ampla que **intervenção**. Nem todo clique modifica alguma coisa; porém determinadas interações podem resultar em intervenção.

## CodeView como ponte de interação

No `CodeView`, a transformação ocorre em duas etapas principais:

```text
AST
 ↓
nodesToCode()
 ↓
representação textual seletiva
 ↓
colorize()
 ↓
markup Ren'Py + elementos interativos
```

`nodesToCode()` reconstrói uma representação humana dos nós AST. `colorize()` posteriormente identifica determinadas variáveis e labels e pode envolvê-las em hyperlinks Ren'Py.

### Variáveis

O CodeView registra o handler:

```python
renpy.config.hyperlink_handlers['URMVarDialog'] = self.handleVarClicked
```

Quando uma variável é clicada, o handler abre:

```python
renpy.show_screen('URM_modify_value', Var(varName), allowRemember=True)
renpy.restart_interaction()
```

Assim, uma informação como:

```text
tree_thank = True
```

pode deixar de ser apenas texto visual e tornar-se uma porta para a ferramenta de modificação de variável.

O fluxo funcional é:

```text
"tree_thank = True"
        ↓
CodeView reconhece tree_thank
        ↓
link URMVarDialog
        ↓
URM_modify_value
        ↓
SetVarValue / controles da Var
        ↓
novo valor
```

A tela `URM_modify_value` confirma que, para tipos suportados e quando a variável é editável, o usuário pode alterar o valor. Para booleanos, por exemplo, a interface permite alternar o valor; para `string`, `int` e `float`, fornece entrada apropriada.

## Labels e replay

O mesmo princípio é usado para labels. O CodeView registra:

```python
renpy.config.hyperlink_handlers['URMLabelDialog'] = self.handleLabelClicked
```

O handler abre:

```python
renpy.show_screen('URM_replay_jump', label)
renpy.restart_interaction()
```

O fluxo é:

```text
call/jump label
      ↓
CodeView reconhece label
      ↓
link URMLabelDialog
      ↓
URM_replay_jump
      ↓
URMReplay
      ↓
reprodução controlada pelo URM
```

A tela `URM_replay_jump` declara explicitamente que a reprodução começa em modo de replay e não deve afetar o gameplay corrente, retornando ao painel depois do término do replay.

Isso é diferente da `URMChoice.Action`: a ação de seleção de Choice devolve a escolha ao mecanismo nativo do Ren'Py; o replay é uma ferramenta separada de exploração/interação do URM.

## O caso `archivePath`

Outro tipo de interação aparece fora do CodeView: informações do próprio URM podem ser expostas através das ferramentas de variáveis/configuração.

O loader define e preenche:

```python
archivePath = None
```

E, durante o carregamento, `findArchivePath()` procura o arquivo do módulo nos arquivos carregados pelo Ren'Py e grava o caminho encontrado em:

```python
getattr(renpy.store, modName).archivePath = archivePath
```

A busca constrói o caminho a partir de `renpy.config.basedir`, da pasta `game` e do nome do arquivo de archive; se necessário, considera também a extensão `.rpa`.

O `API` posteriormente usa esse valor para operações de atualização, incluindo verificações como:

```python
if not archivePath:
```

```python
renpy.os.access(archivePath, renpy.os.W_OK)
```

E a criação de caminhos derivados:

```python
archivePath + '.tmp'
archivePath + '.update'
```

Portanto, uma informação como:

```text
C:\...\game\0x52URM.rpa
```

não deve ser tratada automaticamente como simples texto decorativo. Ela representa um **dado operacional do URM** que possui consumidores no loader/API.

### O que está confirmado

- 🟢 **URM:** `archivePath` é armazenado no módulo do URM quando o loader encontra o archive.
- 🟢 **URM:** a API usa `archivePath` para verificar acesso e preparar/aplicar atualizações.
- 🟢 **URM:** variáveis podem ser abertas pela ferramenta `URM_modify_value` quando expostas pelo sistema de variáveis/links.
- 🟡 **OBSERVAÇÃO SUA:** você observou a possibilidade de editar visualmente o caminho exibido no painel do URM.
- 🟠 **PONTO A FECHAR:** a análise ainda precisa rastrear exatamente por qual tela/objeto essa edição específica de `archivePath` é oferecida e quais efeitos ela produz se o valor for alterado antes de uma operação de atualização/carregamento.

Não devemos concluir, sem rastrear essa cadeia, que alterar o valor exibido automaticamente move o archive, recarrega o módulo ou altera permanentemente o carregamento do Ren'Py.

## Interação não significa execução direta

É importante não transformar toda interação em execução.

Por exemplo:

```text
CodeView
  ↓
click variable
  ↓
URM_modify_value
```

não significa que o CodeView executou o Python representado.

Da mesma forma:

```text
CodeView
  ↓
click label
  ↓
URM_replay_jump
```

não significa que `colorize()` executou diretamente um `Jump` AST.

O CodeView é a **ponte de apresentação/interação**; as ferramentas abertas pelo clique são responsáveis pela operação subsequente.

## Relação com Choices

Isso amplia a leitura de `URMChoice.code`:

```text
Menu
 ↓
URMChoice
 ↓
choice.code
 ↓
CodeView.nodesToCode()
 ↓
CodeView.colorize()
 ↓
┌──────────────────────┐
│ informação interativa│
└──────────┬───────────┘
           │
      ┌────┴────┐
      ▼         ▼
   variável    label
      │         │
      ▼         ▼
 Modify Value  Replay
```

Consequentemente, uma Choice não está apenas ligada a uma representação estática de seu bloco. A representação pode servir de entrada para outras ferramentas do URM.

## Arquitetura funcional consolidada

A partir desta descoberta, a descrição mais completa do comportamento observado é:

```text
                    URM
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     observação             reconstrução
          │                     │
          └──────────┬──────────┘
                     ▼
              representação
                     │
             ┌───────┴───────┐
             ▼               ▼
        informação       configuração
        interativa       / dado operacional
             │               │
       ┌─────┴─────┐         │
       ▼           ▼         ▼
   modificar     replay    editar/usar
    estado       label       dado
       │           │         │
       └─────┬─────┴─────────┘
             ▼
        intervenção
```

Essa representação ainda não afirma que todas as informações exibidas pelo URM são editáveis. A regra correta é: **quando o código demonstrar uma ponte interativa e uma ferramenta de destino, documentamos essa cadeia; quando houver apenas observação do usuário, mantemos como observação até o código fechar o caminho.**

## Regra para Wells — primeira reconstrução

Durante o transplante fiel:

1. preservar a capacidade de tornar variáveis e labels interativos;
2. preservar os handlers `URMVarDialog` e `URMLabelDialog` em sua função equivalente;
3. preservar as ferramentas de destino (`URM_modify_value`, replay e dependências) enquanto a árvore não estiver fechada;
4. não assumir que uma informação exibida é somente decorativa;
5. rastrear separadamente cada caminho de alteração de estado/configuração;
6. não testar experimentalmente alterações potencialmente destrutivas enquanto o consumidor do valor não estiver documentado;
7. deixar a reformulação visual para a camada Wells depois que a mecânica estiver fielmente reconstruída.

## Conclusão

A palavra **interação** deve fazer parte da descrição do URM.

Uma formulação operacional adequada para o manual é:

> **O URM observa e reconstrói informações do jogo e de sua própria infraestrutura, apresenta essas informações ao usuário e, em pontos selecionados, transforma a representação em uma interface interativa que pode encaminhar o usuário para ferramentas de consulta, modificação, replay ou configuração. Algumas dessas interações resultam em intervenção efetiva no estado ou no funcionamento do sistema.**
