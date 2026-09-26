# -*- coding: utf-8 -*-
"""Physical Wells launcher entry point.

This entry point keeps the exact directory returned by the folder picker.
In particular, selecting a project's ``game`` directory no longer silently
replaces the selection with its parent.  The Ren'Py bridge already knows how
to resolve ``game`` to the project root when a Ren'Py command needs it.
"""
from __future__ import annotations

from pathlib import Path

import Wells_Launcher as base


def validate_selected_project(directory):
    """Return the exact selected directory if it identifies a Ren'Py project."""
    selected = Path(directory).expanduser().resolve()
    if selected.name.lower() == 'game' and selected.is_dir():
        return selected
    if selected.is_dir() and (selected / 'game').is_dir():
        return selected
    raise ValueError("Selecione a pasta 'game' do jogo ou a pasta principal que contém 'game'.")


def select_project_exact(self):
    directory = self._askdirectory(title="Selecione a pasta 'game' ou a pasta principal do jogo Ren'Py")
    if not directory:
        return False
    try:
        selected = validate_selected_project(directory)
    except ValueError as exc:
        base.messagebox.showerror(base.APP, str(exc))
        return False

    # Keep exactly what the native picker returned.  Do not rewrite 'game' to
    # its parent here. sdk_core._project_root() performs that conversion only
    # internally, at the moment a Ren'Py command actually requires the root.
    self.project = selected
    self.project_text.set("Projeto Ren'Py: " + selected.name)
    self._log('Pasta selecionada: ' + str(selected))
    return True


base.WellsManager.select_project = select_project_exact


if __name__ == '__main__':
    base.WellsManager().mainloop()
