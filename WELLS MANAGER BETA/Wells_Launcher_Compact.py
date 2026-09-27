# -*- coding: utf-8 -*-
"""Portable provisional Wells Manager launcher.

The user receives one Wells_Manager.exe containing GERENCIADOR, REVISOR and
FERRAMENTAS plus every resource those three blocks need. The REN'PY block stays
frozen and is not exposed in this build.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import Wells_Launcher_Fixed as fixed

base = fixed.base

# In PyInstaller one-file mode resources are unpacked automatically into its
# private temporary bundle directory. Keep APP_DIR as the folder containing the
# user's EXE (settings/logs/documents), but point all read-only packaged assets
# and the internal Manager runtime at the bundle directory.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    bundle = Path(sys._MEIPASS).resolve()
    base.ROOT = bundle
    base.EXTRACTOR_DIR = bundle / 'Wells_Extractor'
    base.REVISOR_DIR = bundle / 'Wells_Revisor'
    base.SDK_MODULE_DIR = bundle / 'Wells_SDK'
    os.environ['WELLS_RENPY_SDK'] = str(bundle / 'Wells_Runtime')


def _build_compact(self):
    tk = base.tk
    ttk = base.ttk

    tk.Label(self, text='WELLS MANAGER', bg='#222222', fg='#ff1010',
             font=('Segoe UI', 20, 'bold')).pack(pady=(10, 1))
    tk.Label(self, text='Gerenciador • Revisor • Ferramentas', bg='#222222', fg='#d0d0d0',
             font=('Segoe UI', 8)).pack(pady=(0, 6))

    top = tk.Frame(self, bg='#222222')
    top.pack(fill='x', padx=18, pady=(0, 6))
    tk.Button(top, text='Selecionar projeto', command=self.select_project,
              bg='#a6a6a6', fg='#101010', font=('Segoe UI', 8, 'bold')).pack(side='left')
    tk.Label(top, textvariable=self.project_text, bg='#222222', fg='#e0e0e0',
             font=('Segoe UI', 9), anchor='w').pack(side='left', padx=10, fill='x', expand=True)

    body = tk.Frame(self, bg='#222222')
    body.pack(fill='x', padx=12)
    self.buttons = []

    self._column(body, 'GERENCIADOR', [
        ('TXT completo', lambda: self.manager_action('txt', False)),
        ('TXT em blocos', lambda: self.manager_action('txt', True)),
        ('DOCX completo', lambda: self.manager_action('docx', False)),
        ('DOCX em blocos', lambda: self.manager_action('docx', True)),
    ], 0)
    self._column(body, 'REVISOR', [
        ('Revisar TXT', lambda: self.revise('txt')),
        ('Revisar DOCX', lambda: self.revise('docx')),
    ], 1)
    self._column(body, 'FERRAMENTAS', [
        ('RPYC → RPY', self.rpyc_file),
        ('Pasta RPYC → RPY', self.rpyc_folder),
        ('Extrair RPA', self.rpa_file),
        ('Pasta RPA', self.rpa_folder),
        ('Compactar RPA', self.rpa_pack),
    ], 2)

    tk.Label(self, textvariable=self.status, bg='#222222', fg='#f0f0f0',
             font=('Segoe UI', 10)).pack(fill='x', padx=30, pady=(10, 4))
    self.bar = ttk.Progressbar(self, style='Wells.Horizontal.TProgressbar', maximum=100, length=560)
    self.bar.pack()

    log_area = tk.Frame(self, bg='#222222', height=205)
    log_area.pack(fill='both', expand=True, padx=50, pady=(8, 12))
    log_area.pack_propagate(False)
    tk.Label(log_area, text='Log de atividade', bg='#222222', fg='#f0f0f0',
             font=('Segoe UI', 10), anchor='w').pack(fill='x', pady=(0, 3))
    self.log = tk.Text(log_area, bg='#2b2b2b', fg='#eee', insertbackground='white',
                       relief='solid', bd=1, font=('Consolas', 9), state='disabled',
                       wrap='word', padx=5, pady=4)
    self.log.pack(fill='both', expand=True)


base.WellsManager._build = _build_compact

_previous_log = base.WellsManager._log


def _compact_log(self, text):
    value = str(text)
    if value == "Ferramentas Wells e núcleo Ren'Py físico carregados.":
        value = 'Gerenciador, Revisor e Ferramentas carregados.'
    if value.startswith("Runtime Ren'Py: "):
        return
    return _previous_log(self, value)


base.WellsManager._log = _compact_log


if __name__ == '__main__':
    app = base.WellsManager()
    app.mainloop()
