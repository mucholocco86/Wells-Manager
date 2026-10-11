# -*- coding: utf-8 -*-
import os
import sys
import shutil
import threading
import queue
import importlib
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

APP = "Wells Manager"
SCRIPT_EXTENSIONS = {".rpy", ".rpyc", ".py", ".pyo", ".rpym", ".rpymc", ".txt", ".ttf", ".otf"}


def resource_root():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

ROOT = resource_root()
EXTRACTOR_DIR = ROOT / "Wells_Extractor"
TRANSLATOR_DIR = ROOT / "Wells_Translator"
REVISOR_DIR = ROOT / "Wells_Revisor"
for folder in (EXTRACTOR_DIR, TRANSLATOR_DIR, REVISOR_DIR):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

extractor = importlib.import_module("Wells_Extractor.main")
from Wells_Translator.wells_translator_core import (
    export_full, export_blocks, inject_translations,
    export_full_docx, export_blocks_docx, inject_docx_translations,
)
from Wells_Translator.wells_json_core import (
    export_json_full_txt, export_json_blocks_txt,
    export_json_full_docx, export_json_blocks_docx,
    inject_json_translations,
)
from Wells_Revisor.wells_revisor_core import review_file
from Wells_Revisor.wells_blindagem import (
    LISTA_BLINDADOS, LISTA_TRADUZIVEIS,
    carregar_listas, adicionar_termo, editar_termo, excluir_termo,
    conflitos,
)


def load_last_dir():
    if sys.platform != "win32":
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\WellsManager") as key:
            value, _ = winreg.QueryValueEx(key, "LastPresentedFolder")
            if value and Path(value).is_dir():
                return str(Path(value).resolve())
    except Exception:
        pass
    return None


def save_last_dir(path):
    if sys.platform != "win32":
        return
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\WellsManager") as key:
            winreg.SetValueEx(key, "LastPresentedFolder", 0, winreg.REG_SZ, str(path))
    except Exception:
        pass


class WellsManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry("702x553")
        self.resizable(True, True)
        self.minsize(702, 553)
        self.configure(bg="#222222")
        try:
            self.iconbitmap(str(ROOT / "wells.ico"))
        except Exception:
            pass

        self.root = self
        self.busy = False
        self.events = queue.Queue()
        self.last_selected_dir = load_last_dir()
        self.display_anchors = []
        self.pending_tl = None
        self.pending_session = None
        self.pending_format = None
        self.pending_json = None
        self.pending_json_session = None
        self.pending_json_format = None
        self.pending_json_button = None
        self.pending_json_original_text = None
        self.pending_json_original_command = None
        self.active_manual_button = None
        self.active_manual_original_text = None
        self.active_manual_original_command = None
        # Subpainéis não modais. Permanecem vivos/minimizáveis para que, por
        # exemplo, o Extractor aguarde enquanto o usuário trabalha no Revisor.
        self.tool_windows = {}
        self.persistent_log_path = app_dir() / "Wells_Manager.log"
        self.status_var = tk.StringVar(value="Status: Nenhuma operação iniciada.")
        self.status = self.status_var
        self._build_ui()
        self.after(60, self._poll_events)
        self._log("Wells Manager iniciado.")

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Wells.Horizontal.TProgressbar", troughcolor="#303030", background="#1595d3",
                        bordercolor="#555555", lightcolor="#1595d3", darkcolor="#1595d3")

        # O painel usa grid para funcionar tanto em modo janela quanto maximizado.
        # A janela normal mantém a composição original; ao maximizar, os blocos
        # acompanham a área disponível em vez de permanecerem presos a 702x553.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        tk.Label(self, text="WELLS MANAGER", bg="#222222", fg="#ff1010",
                 font=("Segoe UI", 20, "bold")).grid(row=0, column=0, pady=(14, 0))
        tk.Label(self, text="Ferramentas Ren'Py em uma única interface", bg="#222222", fg="#dddddd",
                 font=("Segoe UI", 9)).grid(row=1, column=0, pady=(0, 13))

        tools = tk.Frame(self, bg="#222222")
        tools.grid(row=2, column=0, sticky="new", padx=26)
        for col in range(3):
            tools.grid_columnconfigure(col, weight=1, uniform="cols")
        left = tk.Frame(tools, bg="#222222")
        center = tk.Frame(tools, bg="#222222")
        right = tk.Frame(tools, bg="#222222")
        left.grid(row=0, column=0, sticky="new", padx=(0, 18))
        center.grid(row=0, column=1, sticky="new", padx=9)
        right.grid(row=0, column=2, sticky="new", padx=(18, 0))
        for frame in (left, center, right):
            frame.grid_columnconfigure(0, weight=1)

        self.all_buttons = []

        # A janela principal agora é um painel de categorias. As operações já
        # validadas continuam usando os mesmos callbacks, apenas foram movidas
        # para subpainéis não modais.
        self.decompiler_button = self._button(left, "▣  Decompilador", self.open_decompiler)
        self.rpa_tools_button = self._button(left, "▣  Ferramentas RPA", self.open_rpa_tools)

        self.copy_project_button = self._button(center, "□  Copiar projeto", self.copy_project)
        self.translations_button = self._button(center, "▣  Extrair traduções", self.open_translations)

        self.revisor_button = self._button(right, "▣  Revisar tradução", self.open_revisor)

        info = tk.Frame(self, bg="#222222")
        info.grid(row=3, column=0, sticky="ew", padx=26, pady=(11, 0))
        info.grid_columnconfigure(0, weight=1)
        tk.Label(info, textvariable=self.status_var, bg="#222222", fg="#f0f0f0",
                 font=("Segoe UI", 10), anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.progress = ttk.Progressbar(info, style="Wells.Horizontal.TProgressbar", mode="determinate",
                                        maximum=100)
        self.progress.grid(row=1, column=0, sticky="ew", padx=(110, 110))
        self.bar = self.progress

        log_area = tk.Frame(self, bg="#222222")
        log_area.grid(row=4, column=0, sticky="nsew", padx=120, pady=(13, 32))
        log_area.grid_columnconfigure(0, weight=1)
        log_area.grid_rowconfigure(1, weight=1)
        tk.Label(log_area, text="Log de atividade", bg="#222222", fg="#f0f0f0",
                 font=("Segoe UI", 10), anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 2))
        log_frame = tk.Frame(log_area, bg="#222222")
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        self.log = tk.Text(log_frame, height=8, bg="#2b2b2b", fg="#eeeeee", insertbackground="white",
                           relief="solid", bd=1, font=("Consolas", 9), state="disabled", wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew")

    def _button(self, parent, text, command):
        b = tk.Button(parent, text=text, command=command, height=1,
                      bg="#b5b5b5", fg="#101010", activebackground="#c5c5c5",
                      activeforeground="#000000", relief="raised", bd=2,
                      font=("Segoe UI", 9, "bold"), anchor="w", padx=8)
        b.pack(fill="x", pady=3)
        self.all_buttons.append(b)
        return b

    def _tool_button(self, parent, text, command):
        """Botão de subpainel; participa do bloqueio global durante operações."""
        return self._button(parent, text, command)

    def _open_tool_window(self, key, title, builder, geometry):
        """Abre/restaura uma única instância não modal de cada ferramenta."""
        win = self.tool_windows.get(key)
        if win is not None:
            try:
                if win.winfo_exists():
                    win.deiconify()
                    win.lift()
                    win.focus_force()
                    return win
            except tk.TclError:
                pass

        win = tk.Toplevel(self)
        win.title(title)
        win.geometry(geometry)
        win.resizable(True, True)
        win.configure(bg="#222222")
        try:
            win.iconbitmap(str(ROOT / "wells.ico"))
        except Exception:
            pass

        self.tool_windows[key] = win

        def close_window():
            # Fechar a janela não apaga o estado de extração/reinjeção mantido
            # pelo WellsManager; apenas destrói esta representação visual.
            self.tool_windows.pop(key, None)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", close_window)
        body = tk.Frame(win, bg="#222222")
        body.pack(fill="both", expand=True, padx=15, pady=14)
        builder(body)
        return win

    def open_decompiler(self):
        def build(body):
            self.btn_rpyc_file = self._tool_button(body, "▣  RPYC → RPY", self.choose_rpyc)
            self.btn_rpyc_folder = self._tool_button(body, "□  Pasta RPYC → RPY", self.choose_rpyc_folder)
        return self._open_tool_window("decompiler", "Decompilador", build, "228x130")

    def open_rpa_tools(self):
        def build(body):
            self.btn_rpa_file = self._tool_button(body, "◉  Extrair RPA", self.choose_rpa)
            self.btn_rpa_folder = self._tool_button(body, "□  Pasta RPA", self.choose_rpa_folder)
            self.btn_rpa_create = self._tool_button(body, "◉  Compactar RPA", self.choose_rpa_create)
        return self._open_tool_window("rpa", "Ferramentas RPA", build, "228x165")

    def open_translations(self):
        def build(body):
            self.full_txt_button = self._tool_button(body, "▣  TL completa → TXT", self.extract_full_txt)
            self.blocks_txt_button = self._tool_button(body, "□  TL em blocos → TXT", self.extract_blocks_txt)
            self.full_docx_button = self._tool_button(body, "▣  TL completa → DOCX", self.extract_full_docx)
            self.blocks_docx_button = self._tool_button(body, "□  TL em blocos → DOCX", self.extract_blocks_docx)

            spacer = tk.Frame(body, bg="#222222", height=7)
            spacer.pack(fill="x")
            self.json_full_txt_button = self._tool_button(body, "▣  JSON completa → TXT", self.extract_json_full_txt)
            self.json_blocks_txt_button = self._tool_button(body, "□  JSON em blocos → TXT", self.extract_json_blocks_txt)
            self.json_full_docx_button = self._tool_button(body, "▣  JSON completa → DOCX", self.extract_json_full_docx)
            self.json_blocks_docx_button = self._tool_button(body, "□  JSON em blocos → DOCX", self.extract_json_blocks_docx)

            if self.pending_tl is not None and self.pending_format is not None:
                waiting_button = {
                    ("txt", "full"): self.full_txt_button,
                    ("txt", "blocks"): self.blocks_txt_button,
                    ("docx", "full"): self.full_docx_button,
                    ("docx", "blocks"): self.blocks_docx_button,
                }
                # O modo (full/blocks) não era persistido separadamente na base.
                # Identificamos o botão anterior quando ele ainda existe; se a
                # janela foi fechada, oferecemos a injeção no primeiro botão do
                # formato para não perder a sessão pendente.
                previous_text = self.active_manual_original_text or ""
                mode = "blocks" if "blocos" in previous_text.lower() else "full"
                button = waiting_button[(self.pending_format, mode)]
                original_command = button.cget("command")
                self.active_manual_button = button
                self.active_manual_original_text = button.cget("text")
                self.active_manual_original_command = (
                    self.extract_blocks_txt if (self.pending_format, mode) == ("txt", "blocks") else
                    self.extract_full_txt if (self.pending_format, mode) == ("txt", "full") else
                    self.extract_blocks_docx if mode == "blocks" else self.extract_full_docx
                )
                button.configure(text="Aguardando tradução...", command=self.inject)

            if self.pending_json is not None and self.pending_json_format is not None:
                previous = self.pending_json_original_text or ""
                mode = "blocks" if "blocos" in previous.lower() else "full"
                json_button = {
                    ("txt", "full"): self.json_full_txt_button,
                    ("txt", "blocks"): self.json_blocks_txt_button,
                    ("docx", "full"): self.json_full_docx_button,
                    ("docx", "blocks"): self.json_blocks_docx_button,
                }[(self.pending_json_format, mode)]
                self.pending_json_button = json_button
                self.pending_json_original_text = json_button.cget("text")
                self.pending_json_original_command = {
                    ("txt", "full"): self.extract_json_full_txt,
                    ("txt", "blocks"): self.extract_json_blocks_txt,
                    ("docx", "full"): self.extract_json_full_docx,
                    ("docx", "blocks"): self.extract_json_blocks_docx,
                }[(self.pending_json_format, mode)]
                json_button.configure(text="Aguardando revisão...", command=self.inject_json)

        return self._open_tool_window("translations", "Wells Extractor", build, "270x350")

    def open_revisor(self):
        def build(body):
            self.review_txt_button = self._tool_button(
                body, "▣  Revisar TXT", lambda: self.choose_and_review("txt")
            )
            self.review_docx_button = self._tool_button(
                body, "▣  Revisar DOCX", lambda: self.choose_and_review("docx")
            )
            self.blindagem_button = self._tool_button(
                body, "▣  Gerenciar blindagem", self.open_blindagem
            )

            # A revisão JSON pareada será integrada depois da persistência,
            # CRUD e política explícita de conflitos.
        return self._open_tool_window("revisor", "Revisor", build, "260x180")

    def _blindagem_path(self):
        # No executável fica fisicamente ao lado do Wells Manager.exe.
        # Em desenvolvimento, fica ao lado deste main.py.
        return app_dir() / "blindagem.txt"

    def open_blindagem(self):
        path = self._blindagem_path()

        def build(body):
            body.pack_configure(padx=12, pady=12)
            body.grid_columnconfigure(0, weight=1)
            body.grid_columnconfigure(1, weight=1)
            body.grid_rowconfigure(1, weight=1)

            tk.Label(
                body, text="Nomes blindados", bg="#222222", fg="#f0f0f0",
                font=("Segoe UI", 10, "bold")
            ).grid(row=0, column=0, sticky="w", padx=(0, 8))
            tk.Label(
                body, text="Nomes traduzíveis", bg="#222222", fg="#f0f0f0",
                font=("Segoe UI", 10, "bold")
            ).grid(row=0, column=1, sticky="w", padx=(8, 0))

            left = tk.Frame(body, bg="#222222")
            right = tk.Frame(body, bg="#222222")
            left.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(5, 0))
            right.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(5, 0))
            for frame in (left, right):
                frame.pack_propagate(False)

            blindados_box = tk.Listbox(
                left, bg="#2b2b2b", fg="#eeeeee", selectbackground="#555555",
                relief="solid", bd=1, font=("Segoe UI", 10)
            )
            traduziveis_box = tk.Listbox(
                right, bg="#2b2b2b", fg="#eeeeee", selectbackground="#555555",
                relief="solid", bd=1, font=("Segoe UI", 10)
            )
            blindados_box.pack(fill="both", expand=True)
            traduziveis_box.pack(fill="both", expand=True)

            status = tk.StringVar(value=f"Arquivo: {path.name}")
            tk.Label(
                body, textvariable=status, bg="#222222", fg="#cfcfcf",
                font=("Segoe UI", 9), anchor="w"
            ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

            def refresh():
                data = carregar_listas(path)
                blindados_box.delete(0, "end")
                traduziveis_box.delete(0, "end")
                for value in data[LISTA_BLINDADOS]:
                    blindados_box.insert("end", value)
                for value in data[LISTA_TRADUZIVEIS]:
                    traduziveis_box.insert("end", value)
                overlap = conflitos(data)
                if overlap:
                    status.set(
                        f"Conflito pendente: {len(overlap)} termo(s) presente(s) nas duas listas."
                    )
                else:
                    status.set(f"Arquivo: {path.name}")

            def selected(box):
                indexes = box.curselection()
                if not indexes:
                    return None
                return box.get(indexes[0])

            def add(kind):
                title = "Nome blindado" if kind == LISTA_BLINDADOS else "Nome traduzível"
                value = simpledialog.askstring(title, "Digite o termo:", parent=body.winfo_toplevel())
                if value is None:
                    return
                try:
                    adicionar_termo(path, kind, value)
                    refresh()
                except ValueError as exc:
                    messagebox.showwarning(APP, str(exc), parent=body.winfo_toplevel())

            def edit(kind, box):
                old = selected(box)
                if old is None:
                    messagebox.showinfo(APP, "Selecione uma entrada para editar.", parent=body.winfo_toplevel())
                    return
                value = simpledialog.askstring(
                    "Editar entrada", "Corrija o termo:", initialvalue=old,
                    parent=body.winfo_toplevel()
                )
                if value is None:
                    return
                try:
                    editar_termo(path, kind, old, value)
                    refresh()
                except ValueError as exc:
                    messagebox.showwarning(APP, str(exc), parent=body.winfo_toplevel())

            def remove(kind, box):
                value = selected(box)
                if value is None:
                    messagebox.showinfo(APP, "Selecione uma entrada para excluir.", parent=body.winfo_toplevel())
                    return
                if not messagebox.askyesno(
                    APP, f'Excluir "{value}" da lista?', parent=body.winfo_toplevel()
                ):
                    return
                try:
                    excluir_termo(path, kind, value)
                    refresh()
                except ValueError as exc:
                    messagebox.showwarning(APP, str(exc), parent=body.winfo_toplevel())

            controls_left = tk.Frame(body, bg="#222222")
            controls_right = tk.Frame(body, bg="#222222")
            controls_left.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(6, 0))
            controls_right.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))

            for frame, kind, box in (
                (controls_left, LISTA_BLINDADOS, blindados_box),
                (controls_right, LISTA_TRADUZIVEIS, traduziveis_box),
            ):
                tk.Button(frame, text="Adicionar", command=lambda k=kind: add(k),
                          font=("Segoe UI", 9)).pack(side="left", expand=True, fill="x")
                tk.Button(frame, text="Editar", command=lambda k=kind, b=box: edit(k, b),
                          font=("Segoe UI", 9)).pack(side="left", expand=True, fill="x", padx=4)
                tk.Button(frame, text="Excluir", command=lambda k=kind, b=box: remove(k, b),
                          font=("Segoe UI", 9)).pack(side="left", expand=True, fill="x")

            refresh()

        return self._open_tool_window(
            "blindagem", "Nomes blindados e traduzíveis", build, "650x420"
        )

    # O seletor lembra o local que estava sendo EXIBIDO, não a pasta que
    # acabou de ser selecionada. Assim, se o usuário vê "game" dentro da raiz
    # do jogo e seleciona "game", a próxima janela volta à raiz mostrando
    # "game", em vez de entrar automaticamente nela.
    def _remember_selected_directory(self, selected_dir):
        p = Path(selected_dir).resolve()
        shown_dir = p.parent
        self.last_selected_dir = str(shown_dir)
        save_last_dir(shown_dir)
        self._register_display_anchor(p)

    # Em seletores de arquivo, a janela já estava exibindo a pasta que contém
    # o arquivo; portanto é essa pasta que deve ser lembrada.
    def _remember_file_dialog_directory(self, directory):
        p = Path(directory).resolve()
        self.last_selected_dir = str(p)
        save_last_dir(p)
        self._register_display_anchor(p)

    def _register_display_anchor(self, selected_dir):
        p = Path(selected_dir).resolve()
        parent = p.parent
        pair = (str(parent), "")
        self.display_anchors = [x for x in self.display_anchors if x[0] != pair[0]]
        self.display_anchors.insert(0, pair)

    def _dialog_options(self, title):
        opts = {"title": title}
        if self.last_selected_dir and Path(self.last_selected_dir).is_dir():
            opts["initialdir"] = self.last_selected_dir
        return opts

    def _ask_directory(self, title):
        path = filedialog.askdirectory(**self._dialog_options(title))
        if path:
            self._remember_selected_directory(path)
        return path

    def _ask_openfilenames(self, title, filetypes):
        opts = self._dialog_options(title); opts["filetypes"] = filetypes
        files = filedialog.askopenfilenames(**opts)
        if files:
            self._remember_file_dialog_directory(Path(files[0]).parent)
        return files

    def _ask_openfilename(self, title, filetypes):
        opts = self._dialog_options(title); opts["filetypes"] = filetypes
        path = filedialog.askopenfilename(**opts)
        if path:
            self._remember_file_dialog_directory(Path(path).parent)
        return path

    def _compact_text(self, text):
        result = str(text)
        for full, replacement in self.display_anchors:
            prefix = full + os.sep
            result = result.replace(prefix, replacement)
            result = result.replace(prefix.replace("\\", "/"), replacement)
        return result

    def _log_panel(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", self._compact_text(text) + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _log_full(self, text):
        try:
            with self.persistent_log_path.open("a", encoding="utf-8") as f:
                f.write(str(text).rstrip() + "\n")
        except Exception:
            pass

    def _should_persist(self, text):
        line = str(text).strip()
        if not line:
            return False
        upper = line.upper()
        if "[ERRO]" in upper or "[FALHA]" in upper or upper.startswith("ERRO") or upper.startswith("FALHA"):
            return True
        summary_prefixes = (
            "CÓPIA CONCLUÍDA:", "DECOMPILAÇÃO COMPLETA!:", "EXTRAÇÃO COMPLETA!:",
            "COMPACTADOS:", "ERROS:", "[OK] EXTRAÇÃO ", "[OK] INJEÇÃO CONCLUÍDA:",
            "[OK] REVISÃO CONCLUÍDA:", "[OK] LINHAS ALTERADAS:",
        )
        return upper.startswith(summary_prefixes)

    def _log(self, text):
        # Painel: informação operacional compacta, com caminhos abreviados.
        self._log_panel(text)
        # Wells_Manager.log: somente falhas/erros e resumos quantitativos.
        if self._should_persist(text):
            self._log_full(text)

    def _write_log(self, text): self._log(text)
    def _write_persistent_log(self, text): self._log_full(text)

    def _begin_log_session(self, operation):
        stamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        # Cabeçalho visual do painel.
        for line in ("", "=" * 60, stamp, f"OPERAÇÃO: {operation}", "=" * 60):
            self._log_panel(line)
        # No arquivo persistente, um cabeçalho curto identifica a operação;
        # os detalhes só entram se houver erro ou um resumo quantitativo.
        for line in ("", "=" * 60, stamp, f"OPERAÇÃO: {operation}", "=" * 60):
            self._log_full(line)

    def _set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy else "normal"
        live_buttons = []
        for b in self.all_buttons:
            try:
                if b.winfo_exists():
                    b.configure(state=state)
                    live_buttons.append(b)
            except tk.TclError:
                pass
        self.all_buttons = live_buttons
        if not busy and self.active_manual_button is not None:
            try:
                if self.active_manual_button.winfo_exists():
                    self.active_manual_button.configure(state="normal")
            except tk.TclError:
                pass
        if not busy and self.pending_json_button is not None:
            try:
                if self.pending_json_button.winfo_exists():
                    self.pending_json_button.configure(state="normal")
            except tk.TclError:
                pass

    def _emit(self, kind, *args): self.events.put((kind, args))
    def _progress_from_worker(self, value, text=None): self.events.put(("translator_progress", (value, text)))

    def _poll_events(self):
        try:
            while True:
                kind, args = self.events.get_nowait()
                if kind == "log": self._log(args[0])
                elif kind == "status": self.status_var.set(args[0])
                elif kind == "progress": self.progress["value"] = args[0]
                elif kind == "finished":
                    self.progress["value"] = 100; self._set_busy(False); self.status_var.set(args[0])
                elif kind == "error":
                    self._set_busy(False); self.status_var.set("Status: Operação finalizada com erros.")
                    self._log(f"[ERRO] {args[0]}"); messagebox.showerror(APP, args[0])
                elif kind == "translator_progress":
                    value, text = args; self.progress["value"] = value
                    if text: self.status_var.set("Status: " + text)
                elif kind == "callback":
                    callback, result = args; self._set_busy(False); callback(result)
                elif kind == "callback_error":
                    status, exc = args; self._set_busy(False); self.status_var.set(status)
                    self._log(f"[ERRO] {exc}"); messagebox.showerror(APP, str(exc))
        except queue.Empty:
            pass
        self.after(60, self._poll_events)

    def _run_background(self, worker, callback, error_status):
        if self.busy: return
        self._set_busy(True)
        def run():
            try: self.events.put(("callback", (callback, worker())))
            except Exception as exc: self.events.put(("callback_error", (error_status, exc)))
        threading.Thread(target=run, daemon=True).start()

    # Copia apenas game e os tipos definidos para o backup estrutural leve.
    def copy_project(self):
        if self.busy: return
        selected = self._ask_directory("Selecione a pasta do jogo Ren'Py")
        if not selected: return
        project_root = Path(selected).resolve()
        game_dir = project_root / "game"
        if not game_dir.is_dir():
            messagebox.showerror(APP, "A pasta selecionada não contém a subpasta 'game'.")
            return
        destination = self._ask_directory("Selecione a pasta onde a cópia filtrada será salva")
        if not destination: return
        destination = Path(destination).resolve()
        output_game = destination / project_root.name / "game"
        self._set_busy(True); self.progress["value"] = 0
        self.status_var.set("Status: Preparando cópia do projeto...")
        self._begin_log_session("COPIAR PROJETO")
        self._log(f"Origem: {game_dir}"); self._log(f"Destino: {output_game}")
        def worker():
            try:
                # Só cria diretórios quando existe pelo menos um arquivo aprovado
                # pelo filtro dentro deles. Isso elimina images/audio/gui etc. vazios.
                files = [p for p in game_dir.rglob("*") if p.is_file() and p.suffix.lower() in SCRIPT_EXTENSIONS]
                total = len(files)
                for index, src in enumerate(files, 1):
                    rel = src.relative_to(game_dir); dst = output_game / rel
                    dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
                    self._emit("log", f"[OK] {src}")
                    self._emit("status", f"Status: Copiando {index} de {total}: {rel}")
                    self._emit("progress", (index / total) * 100 if total else 100)
                self._emit("log", f"CÓPIA CONCLUÍDA: {total} arquivos → {output_game}")
                self._emit("finished", f"Status: Cópia concluída: {total} arquivos.")
            except Exception as exc:
                self._emit("error", f"Falha ao copiar o projeto.\n{exc}")
        threading.Thread(target=worker, daemon=True).start()

    # Motor atual do Wells Extractor, sem reconstruí-lo.
    _start_rpyc = extractor.WellsExtractorGUI._start_rpyc
    _rpyc_worker = extractor.WellsExtractorGUI._rpyc_worker
    _start_rpa = extractor.WellsExtractorGUI._start_rpa
    _rpa_worker = extractor.WellsExtractorGUI._rpa_worker
    _start_rpa_create = extractor.WellsExtractorGUI._start_rpa_create
    _rpa_create_worker = extractor.WellsExtractorGUI._rpa_create_worker

    # Bloco FERRAMENTAS: mantém o fluxo funcional do Wells_Extractor original.
    # A única mudança nos diálogos é o initialdir persistente, sem permitir que
    # o processamento interno avance sozinho a pasta lembrada.
    _ask_folders_native = extractor.WellsExtractorGUI._ask_folders_native

    def choose_rpyc(self):
        if self.busy:
            return
        files = self._ask_openfilenames(
            "Selecionar arquivos RPYC/RPYMC",
            [
                ("Ren'Py Compiled Script", "*.rpyc"),
                ("Ren'Py Compiled Translation", "*.rpymc"),
            ],
        )
        if files:
            self._start_rpyc([Path(f) for f in files])
            return
        folder = self._ask_directory("Selecionar pasta contendo RPYC/RPYMC")
        if folder:
            files = [
                p for p in Path(folder).rglob("*")
                if p.is_file() and p.suffix.lower() in (".rpyc", ".rpymc")
            ]
            if not files:
                messagebox.showinfo(
                    "Wells Extractor",
                    "Nenhum arquivo .rpyc ou .rpymc foi encontrado na pasta selecionada.",
                )
                return
            self._start_rpyc(files)

    def choose_rpyc_folder(self):
        if self.busy:
            return
        folder = self._ask_directory("Selecionar pasta contendo RPYC/RPYMC")
        if not folder:
            return
        files = [
            p for p in Path(folder).rglob("*")
            if p.is_file() and p.suffix.lower() in (".rpyc", ".rpymc")
        ]
        if not files:
            messagebox.showinfo(
                "Wells Extractor",
                "Nenhum arquivo .rpyc ou .rpymc foi encontrado na pasta selecionada.",
            )
            return
        self._start_rpyc(files)

    def choose_rpa(self):
        if self.busy:
            return
        files = self._ask_openfilenames(
            "Selecionar arquivos RPA", [("Ren'Py Archive", "*.rpa")]
        )
        if files:
            self._start_rpa([Path(f) for f in files])
            return
        folder = self._ask_directory("Selecionar pasta contendo arquivos RPA")
        if folder:
            archives = [
                p for p in Path(folder).rglob("*")
                if p.is_file() and p.suffix.lower() == ".rpa"
            ]
            if not archives:
                messagebox.showinfo(
                    "Wells Extractor",
                    "Nenhum arquivo .rpa foi encontrado na pasta selecionada.",
                )
                return
            self._start_rpa(archives)

    def choose_rpa_folder(self):
        if self.busy:
            return
        folder = self._ask_directory("Selecionar pasta contendo arquivos RPA")
        if not folder:
            return
        archives = [
            p for p in Path(folder).rglob("*")
            if p.is_file() and p.suffix.lower() == ".rpa"
        ]
        if not archives:
            messagebox.showinfo(
                "Wells Extractor",
                "Nenhum arquivo .rpa foi encontrado na pasta selecionada.",
            )
            return
        self._start_rpa(archives)

    def choose_rpa_create(self):
        if self.busy:
            return

        selected_files = self._ask_openfilenames(
            "Selecionar arquivos para compactar em RPA",
            [("Todos os arquivos", "*.*")],
        )
        selected = []
        base_path = None

        if selected_files:
            selected = [Path(f).resolve() for f in selected_files]
            parents = [str(p.parent) for p in selected]
            base_path = Path(os.path.commonpath(parents)).resolve()
        else:
            selected_folders = self._ask_folders_native(
                "Selecionar pastas para compactar em RPA"
            )
            if not selected_folders:
                return
            selected = [Path(folder).resolve() for folder in selected_folders]
            # Esta é uma seleção explícita do usuário; lembra exatamente a pasta
            # selecionada quando há uma só, ou o ancestral comum quando há várias.
            if len(selected) == 1:
                self._remember_selected_directory(selected[0])
            else:
                self._remember_selected_directory(Path(os.path.commonpath([str(p.parent) for p in selected])))
            base_path = Path(
                os.path.commonpath([str(p.parent) for p in selected])
            ).resolve()

        opts = self._dialog_options("Salvar arquivo RPA")
        opts.update({
            "defaultextension": ".rpa",
            "filetypes": [("Ren'Py Archive", "*.rpa")],
        })
        output = filedialog.asksaveasfilename(**opts)
        if not output:
            return
        output_path = Path(output).resolve()
        entries = {}
        for selected_path in selected:
            if selected_path.is_dir():
                candidates = [p for p in selected_path.rglob("*") if p.is_file()]
            elif selected_path.is_file():
                candidates = [selected_path]
            else:
                continue
            for real_path in candidates:
                if real_path == output_path:
                    continue
                archive_name = real_path.relative_to(base_path).as_posix()
                entries[archive_name] = real_path
        file_entries = sorted(entries.items(), key=lambda item: item[0].lower())
        if not file_entries:
            messagebox.showinfo(
                "Wells Extractor", "A seleção não contém arquivos para compactar."
            )
            return
        self._start_rpa_create(file_entries, output_path)

    # Wells Translator atual.
    def choose_tl(self, title="Selecione a pasta de tradução dentro de game/tl"):
        return self._ask_directory(title)

    def _set_waiting(self, tl, session, fmt, button, original_text, original_command):
        if self.active_manual_button is not None and self.active_manual_button is not button:
            try:
                if self.active_manual_button.winfo_exists():
                    self.active_manual_button.configure(
                        text=self.active_manual_original_text,
                        command=self.active_manual_original_command
                    )
            except tk.TclError:
                pass
        self.pending_tl, self.pending_session, self.pending_format = str(tl), session, fmt
        self.active_manual_button, self.active_manual_original_text, self.active_manual_original_command = button, original_text, original_command
        try:
            if button.winfo_exists():
                button.configure(text="Aguardando tradução...", command=self.inject)
        except tk.TclError:
            pass

    def _clear_waiting(self):
        if self.active_manual_button is not None:
            try:
                if self.active_manual_button.winfo_exists():
                    self.active_manual_button.configure(
                        text=self.active_manual_original_text,
                        command=self.active_manual_original_command
                    )
            except tk.TclError:
                pass
        self.pending_tl = self.pending_session = self.pending_format = None
        self.active_manual_button = self.active_manual_original_text = self.active_manual_original_command = None

    def _extract_translation(self, kind, fmt):
        tl = self.choose_tl()
        if not tl: return
        self.progress["value"] = 0
        labels = {
            ("full","txt"): (export_full, self.full_txt_button, "▣  TL completa → TXT", self.extract_full_txt),
            ("blocks","txt"): (export_blocks, self.blocks_txt_button, "□  TL em blocos → TXT", self.extract_blocks_txt),
            ("full","docx"): (export_full_docx, self.full_docx_button, "▣  TL completa → DOCX", self.extract_full_docx),
            ("blocks","docx"): (export_blocks_docx, self.blocks_docx_button, "□  TL em blocos → DOCX", self.extract_blocks_docx),
        }
        fn, button, original, original_command = labels[(kind, fmt)]
        self.status_var.set(f"Status: Extraindo {fmt.upper()}..."); self._log(f"Pasta TL: {tl}")
        def worker(): return fn(tl, app_dir(), return_session=True, progress=self._progress_from_worker)
        def done(result):
            output, count, *rest = result
            session = rest[-1]
            self._set_waiting(tl, session, fmt, button, original, original_command)
            self.progress["value"] = 100
            if kind == "blocks":
                blocks = rest[0]
                self.status_var.set(f"Status: {count} textos em {blocks} blocos {fmt.upper()}.")
                self._log(f"[OK] Extração {fmt.upper()} em blocos: {count} registros / {blocks} blocos.")
            else:
                self.status_var.set(f"Status: {count} textos extraídos.")
                self._log(f"[OK] Extração {fmt.upper()} completa: {count} registros.")
                self._log(f"[OK] Arquivos: {output / ('old.' + fmt)}")
                self._log(f"[OK] Arquivos: {output / ('new.' + fmt)}")
        self._run_background(worker, done, f"Status: Erro na extração {fmt.upper()}.")

    def extract_full_txt(self): self._extract_translation("full", "txt")
    def extract_blocks_txt(self): self._extract_translation("blocks", "txt")
    def extract_full_docx(self): self._extract_translation("full", "docx")
    def extract_blocks_docx(self): self._extract_translation("blocks", "docx")

    # Ferramenta JSON: fluxo independente do TL/RPY tradicional.
    def _set_json_waiting(self, json_path, session, fmt, button, original_text, original_command):
        if self.pending_json_button is not None and self.pending_json_button is not button:
            try:
                if self.pending_json_button.winfo_exists():
                    self.pending_json_button.configure(
                        text=self.pending_json_original_text,
                        command=self.pending_json_original_command
                    )
            except tk.TclError:
                pass
        self.pending_json = str(Path(json_path).resolve())
        self.pending_json_session = session
        self.pending_json_format = fmt
        self.pending_json_button = button
        self.pending_json_original_text = original_text
        self.pending_json_original_command = original_command
        try:
            if button.winfo_exists():
                button.configure(text="Aguardando revisão...", command=self.inject_json)
        except tk.TclError:
            pass

    def _clear_json_waiting(self):
        if self.pending_json_button is not None:
            try:
                if self.pending_json_button.winfo_exists():
                    self.pending_json_button.configure(
                        text=self.pending_json_original_text,
                        command=self.pending_json_original_command
                    )
            except tk.TclError:
                pass
        self.pending_json = self.pending_json_session = self.pending_json_format = None
        self.pending_json_button = self.pending_json_original_text = self.pending_json_original_command = None

    def _extract_json(self, kind, fmt):
        if self.busy:
            return
        path = self._ask_openfilename(
            "Selecione o JSON da tradução automática",
            [("Arquivo JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        if not path:
            return

        labels = {
            ("full", "txt"): (export_json_full_txt, self.json_full_txt_button, "▣  JSON completa → TXT", self.extract_json_full_txt),
            ("blocks", "txt"): (export_json_blocks_txt, self.json_blocks_txt_button, "□  JSON em blocos → TXT", self.extract_json_blocks_txt),
            ("full", "docx"): (export_json_full_docx, self.json_full_docx_button, "▣  JSON completa → DOCX", self.extract_json_full_docx),
            ("blocks", "docx"): (export_json_blocks_docx, self.json_blocks_docx_button, "□  JSON em blocos → DOCX", self.extract_json_blocks_docx),
        }
        fn, button, original, original_command = labels[(kind, fmt)]
        self.progress["value"] = 0
        self.status_var.set(f"Status: Extraindo JSON para {fmt.upper()}...")
        self._begin_log_session(f"EXTRAIR JSON → {fmt.upper()}")
        self._log(f"JSON: {path}")

        def worker():
            return fn(path, app_dir(), return_session=True, progress=self._progress_from_worker)

        def done(result):
            output, count, *rest = result
            session = rest[-1]
            self._set_json_waiting(path, session, fmt, button, original, original_command)
            self.progress["value"] = 100
            if kind == "blocks":
                blocks = rest[0]
                self.status_var.set(f"Status: {count} entradas JSON em {blocks} blocos {fmt.upper()}.")
                self._log(f"[OK] Extração JSON {fmt.upper()} em blocos: {count} registros / {blocks} blocos.")
            else:
                self.status_var.set(f"Status: {count} entradas JSON extraídas.")
                self._log(f"[OK] Extração JSON {fmt.upper()} completa: {count} registros.")
                self._log(f"[OK] Arquivos: {output / ('nativo.' + fmt)}")
                self._log(f"[OK] Arquivos: {output / ('traduzido.' + fmt)}")

        self._run_background(worker, done, f"Status: Erro na extração JSON {fmt.upper()}.")

    def extract_json_full_txt(self): self._extract_json("full", "txt")
    def extract_json_blocks_txt(self): self._extract_json("blocks", "txt")
    def extract_json_full_docx(self): self._extract_json("full", "docx")
    def extract_json_blocks_docx(self): self._extract_json("blocks", "docx")

    def inject_json(self):
        if not self.pending_json:
            messagebox.showinfo(APP, "Não há uma extração JSON aguardando reinjeção.")
            return
        fmt = self.pending_json_format
        self.progress["value"] = 0
        self.status_var.set("Status: Validando e reinjetando revisão no JSON...")
        self._begin_log_session("REINJETAR JSON")
        self._log(f"JSON: {self.pending_json}")

        def worker():
            return inject_json_translations(
                self.pending_json,
                app_dir(),
                fmt,
                session=self.pending_json_session,
                progress=self._progress_from_worker,
            )

        def done(result):
            count, mode = result
            self.progress["value"] = 100
            self.status_var.set(f"Status: {count} entradas reinjetadas no JSON.")
            self._log(f"[OK] Injeção JSON concluída: {count} registros ({mode}).")
            self._clear_json_waiting()
            messagebox.showinfo(APP, f"Reinjeção JSON concluída.\n\n{count} entradas atualizadas.")

        self._run_background(worker, done, "Status: Erro na reinjeção JSON.")

    def inject(self):
        tl = self.pending_tl or self.choose_tl("Selecione a mesma pasta TL usada na extração")
        if not tl: return
        fmt = self.pending_format
        if fmt is None:
            has_docx = (app_dir() / "old.docx").exists() or any(app_dir().glob("old_*.docx"))
            has_txt = (app_dir() / "old.txt").exists() or any(app_dir().glob("old_*.txt"))
            if has_docx and not has_txt:
                fmt = "docx"
            elif has_txt and not has_docx:
                fmt = "txt"
            else:
                fmt = "docx" if has_docx else "txt"
        self.progress["value"] = 0; self.status_var.set("Status: Validando e injetando traduções..."); self._log(f"Pasta TL: {tl}")
        def worker():
            fn = inject_docx_translations if fmt == "docx" else inject_translations
            return fn(tl, app_dir(), session=self.pending_session, progress=self._progress_from_worker)
        def done(result):
            count, mode = result; self.progress["value"] = 100; self.status_var.set(f"Status: {count} traduções injetadas.")
            self._log(f"[OK] Injeção concluída: {count} registros ({mode})."); self._clear_waiting()
        self._run_background(worker, done, "Status: Erro na injeção.")

    # Wells Revisor atual.
    def choose_and_review(self, fmt):
        if self.busy: return
        types = [("Documento TXT", "*.txt")] if fmt == "txt" else [("Documento Word", "*.docx")]
        path = self._ask_openfilename("Selecione o documento traduzido para revisar", types + [("Todos os arquivos", "*.*")])
        if not path: return
        self.progress["value"] = 0; self.status_var.set("Status: Preparando revisão..."); self._log(f"Documento: {path}")
        def worker(): return review_file(Path(path), REVISOR_DIR, progress=self._revisor_progress)
        def done(result):
            self.progress["value"] = 100; self.status_var.set(f"Status: {result['records']} linhas revisadas.")
            self._log(f"[OK] Revisão concluída: {result['records']} linhas.")
            self._log(f"[OK] Linhas alteradas: {result['changed']}.")
            self._log(f"[OK] Alterações efetivas: {result['changed']}.")
            self._log(f"[INFO] Ajustes internos avaliados: {result.get('internal_adjustments', result['changed'])}.")
            self._log(f"[OK] Tokens Ren'Py preservados: {result['tokens']}.")
            self._log(f"[OK] Saída: {result['output']}")
            messagebox.showinfo(APP, f"Revisão concluída.\n\n{result['output']}")
        self._run_background(worker, done, "Status: Erro na revisão.")

    def _revisor_progress(self, value, text=None, log=None):
        self.events.put(("translator_progress", (value, text)))
        if log: self.events.put(("log", (log,)))


if __name__ == "__main__":
    WellsManager().mainloop()
