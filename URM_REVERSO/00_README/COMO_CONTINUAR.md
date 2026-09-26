# Como continuar a investigação

1. Não alterar `wells/`, `wells_beta/`, `renpy-7.4.11-sdk/` ou `__urw/`.
2. Continuar a extração panorâmica do URM antes de qualquer poda.
3. Para cada mecanismo crítico, separar fato observado de interpretação.
4. Usar `renpy-7.4.11-sdk/` apenas como referência de leitura/comparação.
5. Prioridade imediata: provar a sequência temporal e as semânticas internas de Menu, ChoiceReturn, rollback, checkpoint, Python callbacks e Store changes.
6. Só depois fechar o mapa end-to-end de Choices e iniciar a especificação de transplante para Wells.

## Ponto exato de retomada

A análise já percorreu Choices, CodeView, PathDetection, VarsStore, StoreMonitor, TextBox, TextRepl, URMFiles, Settings e o loader. A investigação seguinte deve conectar essas peças ao runtime real do Ren'Py 7.4.11.
