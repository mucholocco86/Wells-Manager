# Loader x52MF2 — comportamento confirmado

`framework/bootstrap.rpy` declara módulos e implementa o carregamento. `.x52rpy` e `.x52` são carregados explicitamente. Quando um `.x52rpy` não está disponível como fonte carregável, o loader pode mapear o nome lógico para o `.rpyc` correspondente, por exemplo `modules/01utils.x52rpy` -> `modules/01utils.rpyc`.

O `load()` procura `bootstrap.rpyc`, registra `archivePath` e trata um `.update` pendente. `API.rpy` baixa atualizações para `.tmp`, extrai o primeiro `.rpa` para `.update`, e `applyUpdate` substitui o archive e chama `renpy.reload_script()`.

Questões abertas: trigger da aplicação, estado seguro, UI e reconciliação entre reload, contexto, AST e estado.
