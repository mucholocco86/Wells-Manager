# Mapa cruzado URM

| Área | Arquivo/classe | Função | Dependências críticas |
|---|---|---|---|
| Choices | `classes/choices.rpy` | observar Menu atual | AST, Context, CodeView |
| Choice | `URMChoice` | representar item | Store, AST, ChoiceReturn |
| CodeView | `classes/codeview.rpy` | reconstruir AST | AST, VarsStore |
| Path | `classes/PathDetection.rpy` | caminhos/condições | AST, Store, Choices |
| Vars | `classes/vars.rpy` | memória/controles | URMFiles, Store |
| Monitor | `StoreMonitorClass` | mudanças/checkpoints | callbacks, get_changes, SetField |
| TextBox | `classes/textbox.rpy` | Say/presentação | say_arguments_callback, show_screen |
| TextRepl | `classes/textrepl.rpy` | substituição/filtro | say_menu_text_filter, say_arguments_callback |
| Files | `classes/URMFiles.rpy` | persistência URM | ZIP/JSON, Settings |
| Settings | `classes/settings.rpy` | configuração | persistent, arquivos URM |
| Loader | `framework/bootstrap.rpy` | módulos | loader/load_string |
| API | `framework/modules/API.rpy` | atualização | archive, RPA, reload_script |

Ren'Py executa o jogo; o URM observa/manipula pontos específicos do runtime e fornece ferramentas de inspeção e controle.
