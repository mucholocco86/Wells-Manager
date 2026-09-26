# Wells Extractor

**Wells Extractor** é uma ferramenta gráfica para Windows voltada ao trabalho com arquivos de jogos feitos em **Ren'Py**.

O programa reúne quatro funções principais:

- **Decompilar RPYC único** — converte um arquivo `.rpyc` em `.rpy`.
- **Decompilar RPYC por pasta** — procura e decompila os arquivos `.rpyc` encontrados em uma pasta.
- **Extrair RPA único** — extrai o conteúdo de um arquivo `.rpa`.
- **Extrair RPA por pasta** — procura e extrai arquivos `.rpa` encontrados em uma pasta.

## Versão executável

A versão compilada pode ser distribuída como um único arquivo `.exe` usando o PyInstaller. O motor **unrpyc** é incorporado ao executável durante a compilação, portanto o usuário final não precisa manter uma pasta `unrpyc` ao lado do `.exe`.

## Estrutura do código-fonte

A versão para desenvolvimento contém:

```text
Wells Extractor/
├── main.py
├── wells.ico
└── unrpyc/
    ├── unrpyc.py
    ├── deobfuscate.py
    └── decompiler/
        └── ...
```

O `main.py` funciona como a interface e o orquestrador do Wells Extractor, enquanto o diretório `unrpyc` contém o motor de decompilação utilizado pelo programa.

## Como executar pelo Python

Com Python instalado, execute:

```cmd
python main.py
```

Para uso do motor de decompilação, a pasta `unrpyc` deve permanecer junto do `main.py` quando o programa for executado diretamente pelo Python.

## Como criar o executável `.exe`

### 1. Abra o CMD na pasta do projeto

Entre na pasta onde estão `main.py`, `wells.ico` e a pasta `unrpyc`.

### 2. Execute o comando do PyInstaller

```cmd
pyinstaller --clean --onefile --windowed --name "Wells Extractor GUI" --collect-all chardet --collect-all unrpyc --add-data "unrpyc;unrpyc" --icon=wells.ico main.py
```

O comando acima foi usado para gerar a versão executável testada do Wells Extractor.

O `.exe` será criado dentro da pasta:

```text
dist\
```

Normalmente o arquivo terá o nome:

```text
Wells Extractor GUI.exe
```

### 3. Teste o executável

Para confirmar que o `unrpyc` foi realmente incorporado, teste o `.exe` sem colocar uma pasta `unrpyc` ao lado dele.

O executável deve continuar funcionando normalmente, pois no modo `--onefile` o PyInstaller extrai temporariamente os arquivos incorporados para seu diretório interno de execução.

## Para quem está começando

Se você está começando a programar, uma forma simples de entender este projeto é separar as responsabilidades:

```text
                 Wells Extractor
                       │
          ┌────────────┴────────────┐
          │                         │
       main.py                  unrpyc/
          │                         │
          │                  motor de RPYC
          │                         │
          ├── interface             │
          ├── seleção de arquivos   │
          ├── processamento RPA     │
          └── chamada do motor ─────┘
```

Quando executado normalmente pelo Python, o `main.py` encontra o `unrpyc` na pasta do projeto.

Quando transformado em um executável `--onefile`, o PyInstaller coloca os arquivos necessários dentro do executável e os disponibiliza durante a execução. O Wells Extractor possui uma inicialização específica para localizar o `unrpyc` nesse ambiente.

Essa diferença entre **arquivo físico ao lado do programa** e **recurso incorporado ao executável** é uma das partes mais importantes deste projeto para quem está aprendendo a empacotar aplicações Python.

## Dependências principais

- Python 3.x para executar o código-fonte.
- PyInstaller para gerar o executável.
- `chardet` utilizado pelo projeto.
- `unrpyc`, incluído neste pacote junto com seus módulos necessários.

## Licenças e créditos

O Wells Extractor utiliza componentes de terceiros. O código do `unrpyc` incluído neste pacote mantém sua licença e seus avisos de copyright originais em `unrpyc/LICENSE`.

Consulte os arquivos de licença distribuídos com os componentes antes de redistribuir ou incorporar este código em outro projeto.

## Estado do projeto

**Versão final / estável.**

Esta versão foi testada nas quatro operações principais do programa:

- RPYC único → RPY
- RPYC por pasta → RPY
- RPA único → arquivos
- RPA por pasta → arquivos

Em um teste real de extração de um arquivo RPA contendo **2.743 arquivos**, o resultado foi:

```text
EXTRAÇÃO COMPLETA!: 2743, arquivos processados: 1, erros: 0
```

Esta versão é considerada concluída para o uso a que se destina.
