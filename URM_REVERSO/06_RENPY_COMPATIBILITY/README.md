# Compatibilidade com Ren'Py 7.4.11

Esta área registra a futura validação direta contra o SDK completo existente em `renpy-7.4.11-sdk/`. O SDK é somente referência e permanece intocado.

## Prioridade

1. `renpy.ast.Menu` e `Menu.items`.
2. `renpy.ui.ChoiceReturn` e interação.
3. `rollback_is_fixed`, checkpoints e rollback log.
4. `renpy.config.python_callbacks`.
5. `renpy.store.__dict__.get_changes`.
6. `context.force_checkpoint`.
7. patches de compatibilidade do URM (`StoreDict.get_changes`, `RollbackLog.complete`, SetField e callbacks de Say).

Cada diferença deverá ser confrontada com o código real do SDK e registrada com evidência.
