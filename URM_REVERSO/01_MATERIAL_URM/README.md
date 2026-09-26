# 01 — Material de origem do URM

Esta pasta preserva o material-fonte utilizado na engenharia reversa do Universal Ren'Py Mod (URM).

## Organização

- `1_URM_ORIGINAL/` — material distribuído/original do pacote analisado. Preservar sem reinterpretar ou misturar com os artefatos convertidos.
- `2_URM_X52_CONVERTIDO/` — material convertido/gerado durante o processo de análise, usado para leitura e inspeção técnica.

## Regra de preservação

Os arquivos destas pastas são **material de referência**, não documentação interpretativa. Não substituir, resumir ou reorganizar o conteúdo interno sem necessidade documentada.

A documentação em `URM_REVERSO/` descreve o que foi comprovado a partir deste material e do SDK Ren'Py 7.4.11.

## Relação entre as fontes

```text
1_URM_ORIGINAL
       │
       ▼
2_URM_X52_CONVERTIDO
       │
       ▼
URM_REVERSO/*
       │
       └── conhecimento documentado
```

Não confundir os `.rpy` convertidos com o código-fonte distribuído originalmente.