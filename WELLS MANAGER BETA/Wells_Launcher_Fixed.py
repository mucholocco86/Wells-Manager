# -*- coding: utf-8 -*-
"""Physical Wells launcher entry point.

Keeps exactly the folder chosen by the user and points the command bridge to
the physical Wells_Runtime directory shipped beside the launcher.
"""
from __future__ import annotations

from pathlib import Path

import Wells_Launcher as base

# Wells_Launcher keeps compatibility with older packages.  The physical build
# overrides that legacy path with the neutral Wells runtime directory name.
base.os.environ['WELLS_RENPY_SDK'] = str(base.APP_DIR / 'Wells_Runtime')


def validate_selected_project(directory):
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

    self.project = selected
    self.project_text.set("Projeto Ren'Py: " + selected.name)
    self._log('Pasta selecionada: ' + str(selected))
    return True


base.WellsManager.select_project = select_project_exact


if __name__ == '__main__':
    app = base.WellsManager()
    # Correct the legacy informational line without changing the approved UI.
    app._log('Wells Runtime físico: ' + str(base.APP_DIR / 'Wells_Runtime' / 'renpy.exe'))
    app.mainloop()
