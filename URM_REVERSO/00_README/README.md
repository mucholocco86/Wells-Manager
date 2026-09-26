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

## Fontes de engenharia

O trabalho parte de três fontes principais e explicitamente separadas:

1. `MOD_ANALISE.zip` — material do URM; os `.rpy` convertidos são artefatos de análise produzidos durante o trabalho e não devem ser confundidos com o código-fonte distribuído originalmente.
2. Repositório GitHub do projeto — para preservar e documentar o trabalho de engenharia reversa.
3. `renpy-7.4.11-sdk/` — referência do comportamento do motor Ren'Py 7.4.11.

O SDK é usado como **terreno mecânico e contrato de comportamento**, não como alvo de reconstrução. O objetivo não é construir o motor Ren'Py, mas entender somente as interfaces e mecanismos que o URM utiliza.

## Separação fundamental

A documentação agora distingue três camadas:

- **URM** — o que o autor do mod realmente implementou.
- **Ren'Py** — o que o motor fornece e que o URM utiliza.
- **Wells** — o que futuramente será reaproveitado ou adaptado.

Essa separação evita tratar uma descoberta do SDK como se fosse código do URM.

## Estado consolidado

- Arquitetura geral do URM: mapa preliminar avançado.
- Sistema de Choices: núcleo identificado e relações principais mapeadas.
- Loader x52MF2: comportamento principal confirmado.
- VarsStore/StoreMonitor: mecanismos de estado e observação identificados.
- TextBox/TextRepl: camada de apresentação/interceptação identificada.
- PathDetection/CodeView: relações com fluxo e AST identificadas.
- Manual interno do URM: iniciado em `10_URM_INTERNAL_MANUAL/`.
- Próxima validação crítica: continuar cruzando o comportamento observado no URM com o SDK 7.4.11 somente nos pontos em que essa dependência explica uma função real do URM.

## Princípio de evidência

- **CONFIRMADO — URM** — diretamente observado no código/material do URM.
- **CONFIRMADO — Ren'Py 7.4.11** — diretamente observado no SDK de referência.
- **OBSERVAÇÃO SUA** — comportamento observado em execução pelo usuário.
- **HIPÓTESE** — explicação ainda precisa de prova.
- **DESCARTADO/INCORRETO** — interpretação demonstrada como errada.

## Estrutura

`03_ARCHITECTURE/` — arquitetura e fluxo geral.
`04_CHOICES/` — sistema completo de Choices.
`05_LOADER/` — bootstrap, x52MF2 e carregamento de módulos.
`06_RENPY_COMPATIBILITY/` — mecanismos do Ren'Py relevantes para as dependências do URM.
`07_EVIDENCE/` — evidências visuais e materiais de execução.
`08_CROSS_REFERENCE/` — relações entre classes, arquivos e mecanismos.
`09_WELLS_APPLICATION/` — critérios e preparação para futura aplicação; não contém alterações no Wells estável.
`10_URM_INTERNAL_MANUAL/` — manual técnico consolidado do funcionamento interno do próprio URM.
