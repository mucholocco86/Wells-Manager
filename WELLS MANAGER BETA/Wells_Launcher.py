# -*- coding: utf-8 -*-
from __future__ import annotations
import json, os, sys, threading, queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP = 'Wells Manager'
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
ROOT = APP_DIR if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
EXTRACTOR_DIR = ROOT / 'Wells_Extractor'
REVISOR_DIR = ROOT / 'Wells_Revisor'
SDK_MODULE_DIR = ROOT / 'Wells_SDK'
for directory in (EXTRACTOR_DIR, EXTRACTOR_DIR / 'unrpyc', REVISOR_DIR, SDK_MODULE_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

# The reduced Ren'Py 7.4.11 runtime is deliberately physical beside the launcher.
# sdk_core already honors this override, so no runtime is unpacked to a _MEI folder.
os.environ['WELLS_RENPY_SDK'] = str(APP_DIR / 'renpy-7.4.11-sdk')

import extractor_core
from wells_revisor_core import review_file
import sdk_core
import dialogue_manager


class WellsManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry('940x650')
        self.minsize(820, 600)
        self.configure(bg='#222222')
        try:
            self.iconbitmap(str(ROOT / 'wells.ico'))
        except Exception:
            pass
        self.events = queue.Queue()
        self.busy = False
        self.project = None
        self.last_browse_dir = APP_DIR
        self.settings_path = APP_DIR / 'Wells_Settings.json'
        self.last_translation = 'english'
        try:
            saved = json.loads(self.settings_path.read_text(encoding='utf-8'))
            value = saved.get('last_translation')
            if isinstance(value, str) and value.strip():
                self.last_translation = value.strip()
        except Exception:
            pass
        self.log_path = APP_DIR / 'Wells_Log.txt'
        try:
            self.log_path.write_text('', encoding='utf-8')
        except Exception:
            pass
        self.status = tk.StringVar(value='Status: Nenhuma operação iniciada.')
        self.project_text = tk.StringVar(value="Projeto Ren'Py: nenhum selecionado")
        self._style()
        self._build()
        self.after(60, self._poll)
        self._log('Wells Manager iniciado.')
        self._log("Ferramentas Wells e núcleo Ren'Py físico carregados.")
        self._log('Pasta de trabalho: ' + str(APP_DIR))
        self._log("Runtime Ren'Py: " + str(APP_DIR / 'renpy-7.4.11-sdk' / 'renpy.exe'))

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Wells.Horizontal.TProgressbar', troughcolor='#303030', background='#1595d3',
                        bordercolor='#555555', lightcolor='#1595d3', darkcolor='#1595d3')

    def _build(self):
        tk.Label(self, text='WELLS MANAGER', bg='#222222', fg='#ff1010',
                 font=('Segoe UI', 20, 'bold')).pack(pady=(10, 1))
        tk.Label(self, text="Ferramentas para jogos Ren'Py", bg='#222222', fg='#d0d0d0',
                 font=('Segoe UI', 8)).pack(pady=(0, 6))
        top = tk.Frame(self, bg='#222222')
        top.pack(fill='x', padx=18, pady=(0, 6))
        tk.Button(top, text='Selecionar projeto', command=self.select_project, bg='#a6a6a6', fg='#101010',
                  font=('Segoe UI', 8, 'bold')).pack(side='left')
        tk.Label(top, textvariable=self.project_text, bg='#222222', fg='#e0e0e0',
                 font=('Segoe UI', 9), anchor='w').pack(side='left', padx=10, fill='x', expand=True)

        body = tk.Frame(self, bg='#222222')
        body.pack(fill='x', padx=12)
        self.buttons = []
        # Layout approved by the user: REN'PY | GERENCIADOR | REVISOR | FERRAMENTAS.
        self._column(body, "REN'PY", [
            ('Gerar traduções', self.sdk_generate),
            ('Eliminar persistentes', self.sdk_persistent),
            ('Checar script (Lint)', self.sdk_lint),
            ('Forçar recompilação', self.sdk_compile),
        ], 0)
        self._column(body, 'GERENCIADOR', [
            ('TXT completo', lambda: self.manager_action('txt', False)),
            ('TXT em blocos', lambda: self.manager_action('txt', True)),
            ('DOCX completo', lambda: self.manager_action('docx', False)),
            ('DOCX em blocos', lambda: self.manager_action('docx', True)),
        ], 1)
        self._column(body, 'REVISOR', [
            ('Revisar TXT', lambda: self.revise('txt')),
            ('Revisar DOCX', lambda: self.revise('docx')),
        ], 2)
        self._column(body, 'FERRAMENTAS', [
            ('RPYC → RPY', self.rpyc_file),
            ('Pasta RPYC → RPY', self.rpyc_folder),
            ('Extrair RPA', self.rpa_file),
            ('Pasta RPA', self.rpa_folder),
            ('Compactar RPA', self.rpa_pack),
        ], 3)

        tk.Label(self, textvariable=self.status, bg='#222222', fg='#f0f0f0',
                 font=('Segoe UI', 10)).pack(fill='x', padx=30, pady=(10, 4))
        self.bar = ttk.Progressbar(self, style='Wells.Horizontal.TProgressbar', maximum=100, length=560)
        self.bar.pack()
        log_area = tk.Frame(self, bg='#222222', height=205)
        log_area.pack(fill='both', expand=True, padx=50, pady=(8, 12))
        log_area.pack_propagate(False)
        tk.Label(log_area, text='Log de atividade', bg='#222222', fg='#f0f0f0',
                 font=('Segoe UI', 10), anchor='w').pack(fill='x', pady=(0, 3))
        self.log = tk.Text(log_area, bg='#2b2b2b', fg='#eee', insertbackground='white', relief='solid', bd=1,
                           font=('Consolas', 9), state='disabled', wrap='word', padx=5, pady=4)
        self.log.pack(fill='both', expand=True)

    def _column(self, parent, title, items, col):
        frame = tk.Frame(parent, bg='#2b2b2b', bd=1, relief='solid')
        frame.grid(row=0, column=col, sticky='nsew', padx=4)
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(frame, text=title, bg='#2b2b2b', fg='#ff1010',
                 font=('Segoe UI', 11, 'bold')).pack(pady=(9, 7))
        for text, command in items:
            button = tk.Button(frame, text=text, command=command, height=1, bg='#a6a6a6', fg='#101010',
                               activebackground='#c5c5c5', relief='raised', bd=2,
                               font=('Segoe UI', 8, 'bold'))
            button.pack(padx=8, pady=2, fill='x')
            self.buttons.append(button)
        tk.Frame(frame, bg='#2b2b2b', height=6).pack()

    def _log(self, text):
        text = str(text)
        self.log.configure(state='normal')
        self.log.insert('end', text + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')
        try:
            with self.log_path.open('a', encoding='utf-8', newline='\n') as handle:
                handle.write(text + '\n')
        except Exception:
            pass

    def _save_settings(self):
        try:
            self.settings_path.write_text(
                json.dumps({'last_translation': self.last_translation}, ensure_ascii=False, indent=2) + '\n',
                encoding='utf-8')
        except Exception:
            pass

    def _set_busy(self, value):
        self.busy = value
        for button in self.buttons:
            button.configure(state='disabled' if value else 'normal')

    def _progress(self, value, text=None, log=None):
        self.events.put(('progress', value, text, log))

    def _status_cb(self, text):
        self.events.put(('status', text))

    def _log_cb(self, text):
        self.events.put(('log', text))

    def _run(self, label, worker, done=None):
        if self.busy:
            return
        self._set_busy(True)
        self.bar['value'] = 0
        self.status.set('Status: ' + label)
        def go():
            try:
                self.events.put(('done', worker(), done))
            except Exception as exc:
                self.events.put(('error', exc))
        threading.Thread(target=go, daemon=True).start()

    def _poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == 'progress':
                    _, value, text, log = event
                    self.bar['value'] = value
                    if text:
                        self.status.set('Status: ' + text)
                    if log:
                        self._log(log)
                elif kind == 'status':
                    self.status.set('Status: ' + event[1])
                elif kind == 'log':
                    self._log(event[1])
                elif kind == 'done':
                    _, result, callback = event
                    self._set_busy(False)
                    self.bar['value'] = 100
                    if callback:
                        callback(result)
                elif kind == 'error':
                    self._set_busy(False)
                    self.status.set('Status: Erro.')
                    self._log('[ERRO] ' + str(event[1]))
                    messagebox.showerror(APP, str(event[1]))
        except queue.Empty:
            pass
        self.after(60, self._poll)

    def _browse_initialdir(self):
        path = Path(self.last_browse_dir)
        while not path.is_dir() and path.parent != path:
            path = path.parent
        return str(path if path.is_dir() else APP_DIR)

    def _askdirectory(self, **kwargs):
        kwargs.setdefault('initialdir', self._browse_initialdir())
        value = filedialog.askdirectory(**kwargs)
        if value:
            self.last_browse_dir = Path(value).resolve()
        return value

    def _askopenfilenames(self, **kwargs):
        kwargs.setdefault('initialdir', self._browse_initialdir())
        values = filedialog.askopenfilenames(**kwargs)
        if values:
            self.last_browse_dir = Path(values[0]).resolve().parent
        return values

    def _askopenfilename(self, **kwargs):
        kwargs.setdefault('initialdir', self._browse_initialdir())
        value = filedialog.askopenfilename(**kwargs)
        if value:
            self.last_browse_dir = Path(value).resolve().parent
        return value

    def _asksaveasfilename(self, **kwargs):
        kwargs.setdefault('initialdir', self._browse_initialdir())
        value = filedialog.asksaveasfilename(**kwargs)
        if value:
            self.last_browse_dir = Path(value).resolve().parent
        return value

    def select_project(self):
        directory = self._askdirectory(title="Selecione a pasta principal do jogo Ren'Py")
        if not directory:
            return False
        project = Path(directory).resolve()
        if project.name.lower() == 'game':
            project = project.parent
        if not (project / 'game').is_dir():
            messagebox.showerror(APP, "A pasta selecionada não contém a pasta 'game'.")
            return False
        self.project = project
        self.project_text.set("Projeto Ren'Py: " + project.name)
        self._log('Projeto: ' + project.name)
        return True

    def _need_project(self):
        return bool(self.project or self.select_project())

    def _sdk(self, title, function, done='Operação concluída.'):
        if not self._need_project():
            return
        self._log('=== ' + title.upper() + ' ===')
        self._log('Projeto: ' + self.project.name)
        def worker():
            return function(self.project, log=self._log_cb)
        def finish(result):
            self.status.set('Status: ' + done)
            self._log('[OK] ' + done)
        self._run(title + '...', worker, finish)

    def sdk_generate(self):
        if not self._need_project():
            return
        win = tk.Toplevel(self)
        win.title('Gerar Traduções')
        win.resizable(False, False)
        win.configure(bg='#222222')
        win.transient(self)
        win.grab_set()
        language = tk.StringVar(value=self.last_translation)
        empty = tk.BooleanVar(value=True)
        tk.Label(win, text='Idioma', bg='#222', fg='white').grid(row=0, column=0, padx=12, pady=(12, 5), sticky='w')
        tk.Entry(win, textvariable=language, width=25).grid(row=0, column=1, padx=12, pady=(12, 5))
        tk.Checkbutton(win, text='Gerar strings vazias', variable=empty, bg='#222', fg='white',
                       selectcolor='#333', activebackground='#222', activeforeground='white').grid(
                           row=1, column=0, columnspan=2, padx=12, sticky='w')
        def go(kind):
            lang = language.get().strip()
            if not lang:
                return messagebox.showerror(APP, 'Informe o idioma.', parent=win)
            self.last_translation = lang
            self._save_settings()
            win.destroy()
            functions = {
                'generate': lambda p, log: sdk_core.generate_translations(p, lang, empty.get(), log),
                'extract': lambda p, log: sdk_core.extract_string_translations(p, lang, log),
                'merge': lambda p, log: sdk_core.merge_string_translations(p, lang, False, log),
                'replace': lambda p, log: sdk_core.merge_string_translations(p, lang, True, log),
                'reverse': lambda p, log: sdk_core.reverse_language(p, lang, log),
            }
            names = {'generate': 'Gerar traduções', 'extract': 'Extrair strings', 'merge': 'Mesclar strings',
                     'replace': 'Mesclar/substituir strings', 'reverse': 'Inverter idioma'}
            self._sdk(names[kind], functions[kind])
        frame = tk.Frame(win, bg='#222')
        frame.grid(row=2, column=0, columnspan=2, padx=10, pady=12)
        for index, (text, kind) in enumerate([
            ('Gerar', 'generate'), ('Extrair strings', 'extract'), ('Mesclar', 'merge'),
            ('Substituir', 'replace'), ('Inverter', 'reverse')]):
            tk.Button(frame, text=text, command=lambda value=kind: go(value), width=14).grid(
                row=index // 2, column=index % 2, padx=3, pady=3)

    def sdk_persistent(self):
        if self._need_project() and messagebox.askyesno(APP, 'Eliminar os dados persistentes deste projeto?'):
            self._sdk('Eliminar dados persistentes', sdk_core.delete_persistent, 'Dados persistentes eliminados.')

    def sdk_lint(self):
        if self._need_project():
            self._sdk('Checar script (Lint)', sdk_core.lint, 'Checagem concluída.')

    def sdk_compile(self):
        if self._need_project():
            self._sdk('Forçar recompilação', sdk_core.force_recompile, 'Recompilação concluída.')

    # GERENCIADOR: TAB is internal. TXT/DOCX + physical JSON are the user workflow.
    def manager_action(self, fmt, blocks):
        if not self._need_project():
            return
        try:
            info = dialogue_manager.pending(APP_DIR)
        except Exception as exc:
            return messagebox.showerror(APP, str(exc))
        if info:
            mode = info.get('wells_manager_mode', 'full')
            expected = 'blocks' if blocks else 'full'
            if info.get('format') != fmt or mode != expected:
                return messagebox.showinfo(
                    APP,
                    'Existe uma extração {} {} aguardando retorno. Use o mesmo botão que iniciou essa extração.'.format(
                        str(info.get('format', '')).upper(), 'em blocos' if mode == 'blocks' else 'completa'))
            return self.manager_inject(fmt, blocks)
        return self.manager_export_dialog(fmt, blocks)

    def manager_export_dialog(self, fmt, blocks):
        win = tk.Toplevel(self)
        win.title('{} {}'.format(fmt.upper(), 'em blocos' if blocks else 'completo'))
        win.resizable(False, False)
        win.configure(bg='#222222')
        win.transient(self)
        win.grab_set()
        language = tk.StringVar(value=self.last_translation)
        strings = tk.BooleanVar(value=True)
        tk.Label(win, text='Idioma da tradução', bg='#222', fg='white').grid(
            row=0, column=0, padx=12, pady=(12, 5), sticky='w')
        tk.Entry(win, textvariable=language, width=25).grid(row=0, column=1, padx=12, pady=(12, 5))
        tk.Checkbutton(win, text='Incluir menus, botões e outras strings', variable=strings,
                       bg='#222', fg='white', selectcolor='#333', activebackground='#222',
                       activeforeground='white').grid(row=1, column=0, columnspan=2, padx=12, pady=4, sticky='w')
        tk.Label(win, text='O TAB será usado internamente como âncora e o JSON físico guardará o mapa de retorno.',
                 bg='#222', fg='#d0d0d0', wraplength=420, justify='left').grid(
                     row=2, column=0, columnspan=2, padx=12, pady=(4, 8), sticky='w')
        def start():
            lang = language.get().strip()
            if not lang:
                return messagebox.showerror(APP, 'Informe o idioma da tradução.', parent=win)
            self.last_translation = lang
            self._save_settings()
            include = strings.get()
            win.destroy()
            self._log('=== GERENCIADOR {} {} ==='.format(fmt.upper(), 'BLOCOS' if blocks else 'COMPLETO'))
            self._log('Projeto: ' + self.project.name)
            def worker():
                return dialogue_manager.prepare(
                    self.project, lang, fmt=fmt, blocks=blocks, output_dir=APP_DIR,
                    include_strings=include, log=self._log_cb,
                    progress=lambda value, text=None: self._progress(value, text))
            def finish(result):
                self.status.set('Status: Extração concluída; traduza o documento e clique no mesmo botão para importar.')
                self._log('[OK] {} registros; {} documento(s) {}.'.format(
                    result['entries'], result.get('blocks', 1), fmt.upper()))
                self._log('[OK] Mapa físico temporário: ' + result['map'])
                self._log('[OK] TAB usado somente como âncora interna.')
            self._run('Preparando documentos {}...'.format(fmt.upper()), worker, finish)
        tk.Button(win, text='Extrair', command=start, width=18).grid(
            row=3, column=0, columnspan=2, padx=12, pady=(2, 12))

    def manager_inject(self, fmt, blocks):
        label = '{} {}'.format(fmt.upper(), 'em blocos' if blocks else 'completo')
        if not messagebox.askyesno(APP, 'Importar a tradução do {} de volta para game/tl?'.format(label)):
            return
        self._log('=== IMPORTAR TRADUÇÃO {} ==='.format(label))
        def worker():
            return dialogue_manager.inject(
                self.project, APP_DIR, fmt, blocks=blocks, log=self._log_cb,
                progress=lambda value, text=None: self._progress(value, text))
        def finish(result):
            self.status.set('Status: Tradução importada com sucesso.')
            self._log('[OK] {} registros reinjetados em {} arquivos TL.'.format(result['entries'], result['files']))
            self._log('[OK] JSON/TAB temporários removidos após confirmação da escrita.')
        self._run('Validando e importando tradução...', worker, finish)

    # FERRAMENTAS
    def rpyc_file(self):
        files = self._askopenfilenames(title='Selecionar RPYC/RPYMC',
                                       filetypes=[("Ren'Py compilado", '*.rpyc *.rpymc'), ('Todos', '*.*')])
        if files:
            paths = [Path(value) for value in files]
            base = Path(os.path.commonpath([str(path.parent) for path in paths])).resolve()
            self._extract_rpyc(paths, base, base.name)

    def rpyc_folder(self):
        directory = self._askdirectory(title='Selecionar pasta contendo RPYC/RPYMC')
        if directory:
            folder = Path(directory).resolve()
            files = [path for path in folder.rglob('*') if path.suffix.lower() in ('.rpyc', '.rpymc')]
            self._extract_rpyc(files, folder, folder.name)

    def _extract_rpyc(self, files, display_root=None, root_name=None):
        self._log('=== RPYC → RPY ===')
        self._log('Raiz: ' + str(root_name))
        self._log('Arquivos: ' + str(len(files)))
        def worker():
            return extractor_core.decompile_rpyc_files(
                files, lambda value: self._progress(value), self._log_cb, self._status_cb,
                display_root=display_root)
        def finish(result):
            self.status.set('Status: Decompilação concluída.')
            self._log('[OK] {}, ignorados: {}, erros: {}'.format(result['ok'], result['skipped'], result['errors']))
        self._run('Preparando descompilação...', worker, finish)

    def rpa_file(self):
        files = self._askopenfilenames(title='Selecionar arquivos RPA', filetypes=[("Ren'Py Archive", '*.rpa')])
        if files:
            paths = [Path(value).resolve() for value in files]
            base = Path(os.path.commonpath([str(path.parent) for path in paths])).resolve()
            self._extract_rpa(paths, base, base.name)

    def rpa_folder(self):
        directory = self._askdirectory(title='Selecionar pasta contendo RPA')
        if directory:
            folder = Path(directory).resolve()
            self._extract_rpa([path for path in folder.rglob('*.rpa') if path.is_file()], folder, folder.name)

    def _extract_rpa(self, files, display_root=None, root_name=None):
        self._log('=== EXTRAIR RPA ===')
        self._log('Raiz: ' + str(root_name))
        self._log('Arquivos RPA: ' + str(len(files)))
        def worker():
            return extractor_core.extract_rpa_archives(
                files, lambda value: self._progress(value), self._log_cb, self._status_cb,
                display_root=display_root)
        def finish(result):
            self.status.set('Status: Extração RPA concluída.')
            self._log('[OK] Extraídos: {}; RPA: {}; erros: {}'.format(
                result['extracted'], result['archives'], result['errors']))
        self._run('Preparando extração RPA...', worker, finish)

    def rpa_pack(self):
        selected = [Path(value).resolve() for value in self._askopenfilenames(
            title='Selecionar arquivos para compactar em RPA', filetypes=[('Todos', '*.*')])]
        if selected:
            base = Path(os.path.commonpath([str(path.parent) for path in selected])).resolve()
        else:
            folder = self._askdirectory(title='Selecionar pasta para compactar em RPA')
            if not folder:
                return
            selected = [Path(folder).resolve()]
            base = selected[0].parent
        output = self._asksaveasfilename(title='Salvar RPA', defaultextension='.rpa',
                                         filetypes=[("Ren'Py Archive", '*.rpa')])
        if not output:
            return
        output_path = Path(output).resolve()
        entries = {}
        self._log('=== COMPACTAR RPA ===')
        for selected_path in selected:
            candidates = [path for path in selected_path.rglob('*') if path.is_file()] if selected_path.is_dir() else [selected_path]
            for path in candidates:
                if path != output_path:
                    entries[path.relative_to(base).as_posix()] = path
        file_entries = sorted(entries.items(), key=lambda item: item[0].lower())
        if not file_entries:
            return messagebox.showinfo(APP, 'A seleção não contém arquivos.')
        def worker():
            return extractor_core.pack_rpa(
                file_entries, output_path, lambda value: self._progress(value), self._log_cb, self._status_cb)
        def finish(result):
            self.status.set('Status: Compactação RPA concluída.')
            self._log('[OK] {} arquivos → {}'.format(result['compacted'], Path(result['output']).name))
        self._run('Preparando compactação RPA...', worker, finish)

    # REVISOR
    def revise(self, fmt):
        types = [('Documento TXT', '*.txt')] if fmt == 'txt' else [('Documento Word', '*.docx')]
        path = self._askopenfilename(title='Selecione o documento para revisar', filetypes=types + [('Todos', '*.*')])
        if not path:
            return
        self._log('=== REVISOR {} ==='.format(fmt.upper()))
        self._log('Documento: ' + Path(path).name)
        def progress(value, text=None, log=None):
            self._progress(value, text, log)
        def worker():
            return review_file(Path(path), REVISOR_DIR, progress=progress)
        def finish(result):
            self.status.set('Status: {} linhas revisadas.'.format(result['records']))
            self._log('[OK] Linhas alteradas: {}.'.format(result['changed']))
            self._log('[OK] Tokens preservados: {}.'.format(result['tokens']))
            self._log('[OK] Saída: {}'.format(Path(result['output']).name))
        self._run('Preparando revisão...', worker, finish)


if __name__ == '__main__':
    WellsManager().mainloop()
