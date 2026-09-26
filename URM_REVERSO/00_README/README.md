# URM_REVERSO

Arquivo de engenharia reversa do Universal Ren'Py Mod (URM), de 0x52, realizado para compreender sua arquitetura e preparar a futura aplicação seletiva no Wells Framework.

## Regra de isolamento

**ESTA ÁRVORE É ISOLADA.** Nenhum arquivo ou pasta fora de `URM_REVERSO/` deve ser alterado por este trabalho.

Especialmente protegidos e fora do escopo de escrita:
- `renpy-7.4.11-sdk/` — SDK de referência do Ren'Py 7.4.11.
- `wells/` — projeto estável e funcional do Wells Framework. NÃO TOCAR.
- `wells_beta/` — cópia de desenvolvimento usada no outro trabalho para o sistema de walkthrough.
- `__urw/` — material separado do usuário.

## Objetivo atual

Mapear o URM inteiro antes de decidir o que será transplantado para o Wells. A fase atual não é de poda: componentes aparentemente secundários, antigos ou indiretos permanecem classificados até que suas relações sejam entendidas.

## Fonte principal

O trabalho parte do arquivo `MOD_ANALISE.zip`, contendo `1_URM_ORIGINAL/` e `2_URM_X52_CONVERTIDO/`. Os `.rpy` convertidos são artefatos de análise produzidos durante o trabalho; não devem ser confundidos com o código-fonte distribuído originalmente.

## Estado consolidado

- Arquitetura geral do URM: mapa preliminar avançado.
- Sistema de Choices: núcleo identificado e relações principais mapeadas.
- Loader x52MF2: comportamento principal confirmado.
- VarsStore/StoreMonitor: mecanismos de estado e observação identificados.
- TextBox/TextRepl: camada de apresentação/interceptação identificada.
- PathDetection/CodeView: relações com fluxo e AST identificadas.
- Próxima validação crítica: cruzar o comportamento observado no URM com o SDK completo do Ren'Py 7.4.11, especialmente Menu/ChoiceReturn, rollback, checkpoints, Store.get_changes e python_callbacks.

## Princípio de evidência

- **CONFIRMADO** — diretamente observado no código, artefato ou execução/evidência.
- **INFERÊNCIA** — explicação arquitetural derivada de fatos confirmados.
- **HIPÓTESE** — ainda precisa de prova.
- **ABERTO** — pergunta ainda não resolvida.

## Estrutura

`03_ARCHITECTURE/` — arquitetura e fluxo geral.
`04_CHOICES/` — sistema completo de Choices.
`05_LOADER/` — bootstrap, x52MF2 e carregamento de módulos.
`06_RENPY_COMPATIBILITY/` — comparação planejada contra o SDK 7.4.11.
`07_EVIDENCE/` — evidências visuais e materiais de execução.
`08_CROSS_REFERENCE/` — relações entre classes, arquivos e mecanismos.
`09_WELLS_APPLICATION/` — somente critérios e preparação para futura aplicação; não contém alterações no Wells estável.
