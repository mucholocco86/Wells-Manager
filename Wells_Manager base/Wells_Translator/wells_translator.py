# -*- coding: utf-8 -*-
import sys
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from wells_translator_core import (
    export_full,
    export_blocks,
    inject_translations,
    export_full_docx,
    export_blocks_docx,
    inject_docx_translations,
)

APP = "Wells Translator"


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def load_last_parent():
    """Usa o Registro do Windows para não criar arquivo de configuração ao lado do programa."""
    if sys.platform != "win32":
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\WellsTranslator") as key:
            value, _ = winreg.QueryValueEx(key, "LastParentFolder")
            if value and Path(value).is_dir():
                return value
    except Exception:
        pass
    return None


def save_last_parent(path):
    if sys.platform != "win32":
        return
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\WellsTranslator") as key:
            winreg.SetValueEx(key, "LastParentFolder", 0, winreg.REG_SZ, str(path))
    except Exception:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP)
        self.geometry("620x610")
        self.resizable(False, False)
        self.configure(bg="#222222")

        self.pending_tl = None
        self.pending_session = None
        self.pending_format = None
        self.last_parent = load_last_parent()
        self.busy = False
        self.event_queue = queue.Queue()
        self.after(50, self._poll_worker_events)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Wells.Horizontal.TProgressbar",
            troughcolor="#303030",
            background="#1595d3",
            bordercolor="#555555",
            lightcolor="#1595d3",
            darkcolor="#1595d3",
        )

        tk.Label(
            self,
            text="Wells Translator",
            bg="#222222",
            fg="#ff1010",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(20, 10))

        self.buttons = tk.Frame(self, bg="#222222")
        self.buttons.pack()

        self.full_txt_button = self._button("📄  Extrair TXT completo", self.extract_full_txt)
        self.blocks_txt_button = self._button("📁  Extrair TXT em blocos de 200 KB", self.extract_blocks_txt)
        self.full_docx_button = self._button("📄  Extrair DOCX completo", self.extract_full_docx)
        self.blocks_docx_button = self._button("📁  Extrair DOCX em blocos de até 190 KB", self.extract_blocks_docx)

        self.all_buttons = [
            self.full_txt_button,
            self.blocks_txt_button,
            self.full_docx_button,
            self.blocks_docx_button,
        ]

        self.active_manual_button = None
        self.active_manual_original_text = None
        self.active_manual_original_command = None

        self.status = tk.StringVar(value="Status: Nenhuma operação iniciada.")
        tk.Label(
            self,
            textvariable=self.status,
            anchor="w",
            bg="#222222",
            fg="#f0f0f0",
            font=("Segoe UI", 10),
        ).pack(fill="x", padx=130, pady=(14, 6))

        self.bar = ttk.Progressbar(
            self,
            style="Wells.Horizontal.TProgressbar",
            mode="determinate",
            maximum=100,
            length=360,
        )
        self.bar.pack()

        tk.Label(
            self,
            text="Log de atividade",
            anchor="w",
            bg="#222222",
            fg="#f0f0f0",
            font=("Segoe UI", 10),
        ).pack(fill="x", padx=20, pady=(14, 2))

        log_frame = tk.Frame(self, bg="#222222")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self.log = tk.Text(
            log_frame,
            height=9,
            bg="#2b2b2b",
            fg="#eeeeee",
            insertbackground="white",
            relief="solid",
            bd=1,
            font=("Consolas", 9),
            state="disabled",
            wrap="word",
        )
        self.log.pack(fill="both", expand=True)

        self._log("Wells Translator iniciado.")
        self._log("TXT e DOCX serão criados diretamente ao lado do programa.")

    def _button(self, text, command):
        button = tk.Button(
            self.buttons,
            text=text,
            command=command,
            width=39,
            height=1,
            bg="#a6a6a6",
            fg="#101010",
            activebackground="#c5c5c5",
            activeforeground="#000000",
            relief="raised",
            bd=2,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=12,
        )
        button.pack(pady=3)
        return button

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _progress_from_worker(self, value, text=None):
        # A thread de trabalho nunca toca diretamente no Tkinter.
        self.event_queue.put(("progress", value, text))

    def _apply_progress(self, value, text=None):
        self.bar["value"] = value
        if text:
            self.status.set(f"Status: {text}")

    def _poll_worker_events(self):
        try:
            while True:
                event = self.event_queue.get_nowait()
                kind = event[0]
                if kind == "progress":
                    _, value, text = event
                    self._apply_progress(value, text)
                elif kind == "error":
                    _, status_text, error = event
                    self._background_error(status_text, error)
                elif kind == "success":
                    _, callback, result = event
                    self._background_success(callback, result)
        except queue.Empty:
            pass
        self.after(50, self._poll_worker_events)

    def _set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy else "normal"
        for button in self.all_buttons:
            button.configure(state=state)

    def _run_background(self, worker, on_success, error_status):
        if self.busy:
            return
        self._set_busy(True)

        def run():
            try:
                result = worker()
            except Exception as error:
                self.event_queue.put(("error", error_status, error))
                return
            self.event_queue.put(("success", on_success, result))

        threading.Thread(target=run, daemon=True).start()

    def _background_error(self, status_text, error):
        self._set_busy(False)
        self.status.set(status_text)
        self._log(f"[ERRO] {error}")
        messagebox.showerror(APP, str(error))

    def _background_success(self, callback, result):
        self._set_busy(False)
        callback(result)

    def _set_waiting(self, tl, session, fmt, button, original_text, original_command):
        if self.active_manual_button is not None and self.active_manual_button is not button:
            self.active_manual_button.configure(
                text=self.active_manual_original_text,
                command=self.active_manual_original_command,
            )
        self.pending_tl = str(tl)
        self.pending_session = session
        self.pending_format = fmt
        self.active_manual_button = button
        self.active_manual_original_text = original_text
        self.active_manual_original_command = original_command
        button.configure(text="💉  Aguardando tradução...", command=self.inject)

    def _clear_waiting(self):
        self.pending_tl = None
        self.pending_session = None
        self.pending_format = None
        if self.active_manual_button is not None:
            self.active_manual_button.configure(
                text=self.active_manual_original_text,
                command=self.active_manual_original_command,
            )
        self.active_manual_button = None
        self.active_manual_original_text = None
        self.active_manual_original_command = None

    def choose_tl(self, title="Selecione a pasta de tradução dentro de game/tl"):
        options = {"title": title}
        if self.last_parent and Path(self.last_parent).is_dir():
            options["initialdir"] = self.last_parent
        path = filedialog.askdirectory(**options)
        if not path:
            return None

        # Na próxima escolha, abre na pasta ONDE a TL selecionada estava localizada.
        parent = str(Path(path).resolve().parent)
        self.last_parent = parent
        save_last_parent(parent)
        return path

    # ---------- EXTRAÇÃO TXT ----------
    def extract_full_txt(self):
        tl = self.choose_tl()
        if not tl:
            return
        self.bar["value"] = 0
        self.status.set("Status: Extraindo TXT completo...")
        self._log(f"Pasta TL: {tl}")

        def worker():
            return export_full(tl, app_dir(), return_session=True, progress=self._progress_from_worker)

        def done(result):
            output, count, session = result
            self._set_waiting(tl, session, "txt", self.full_txt_button, "📄  Extrair TXT completo", self.extract_full_txt)
            self.bar["value"] = 100
            self.status.set(f"Status: {count} textos extraídos.")
            self._log(f"[OK] Extração TXT completa: {count} registros.")
            self._log(f"[OK] Arquivos: {output / 'old.txt'}")
            self._log(f"[OK] Arquivos: {output / 'new.txt'}")

        self._run_background(worker, done, "Status: Erro na extração TXT.")

    def extract_blocks_txt(self):
        tl = self.choose_tl()
        if not tl:
            return
        self.bar["value"] = 0
        self.status.set("Status: Extraindo blocos TXT...")
        self._log(f"Pasta TL: {tl}")

        def worker():
            return export_blocks(tl, app_dir(), return_session=True, progress=self._progress_from_worker)

        def done(result):
            output, count, blocks, session = result
            self._set_waiting(tl, session, "txt", self.blocks_txt_button, "📁  Extrair TXT em blocos de 200 KB", self.extract_blocks_txt)
            self.bar["value"] = 100
            self.status.set(f"Status: {count} textos em {blocks} blocos TXT.")
            self._log(f"[OK] Extração TXT em blocos: {count} registros / {blocks} blocos.")

        self._run_background(worker, done, "Status: Erro na extração TXT.")

    # ---------- EXTRAÇÃO DOCX ----------
    def extract_full_docx(self):
        tl = self.choose_tl()
        if not tl:
            return
        self.bar["value"] = 0
        self.status.set("Status: Extraindo DOCX completo...")
        self._log(f"Pasta TL: {tl}")

        def worker():
            return export_full_docx(tl, app_dir(), return_session=True, progress=self._progress_from_worker)

        def done(result):
            output, count, session = result
            self._set_waiting(tl, session, "docx", self.full_docx_button, "📄  Extrair DOCX completo", self.extract_full_docx)
            self.bar["value"] = 100
            self.status.set(f"Status: {count} textos extraídos em DOCX.")
            self._log(f"[OK] Extração DOCX completa: {count} registros.")
            self._log(f"[OK] Arquivos: {output / 'old.docx'}")
            self._log(f"[OK] Arquivos: {output / 'new.docx'}")

        self._run_background(worker, done, "Status: Erro na extração DOCX.")

    def extract_blocks_docx(self):
        tl = self.choose_tl()
        if not tl:
            return
        self.bar["value"] = 0
        self.status.set("Status: Extraindo blocos DOCX...")
        self._log(f"Pasta TL: {tl}")

        def worker():
            return export_blocks_docx(tl, app_dir(), return_session=True, progress=self._progress_from_worker)

        def done(result):
            output, count, blocks, session = result
            self._set_waiting(tl, session, "docx", self.blocks_docx_button, "📁  Extrair DOCX em blocos de até 190 KB", self.extract_blocks_docx)
            self.bar["value"] = 100
            self.status.set(f"Status: {count} textos em {blocks} blocos DOCX.")
            self._log(f"[OK] Extração DOCX em blocos: {count} registros / {blocks} blocos.")

        self._run_background(worker, done, "Status: Erro na extração DOCX.")

    # ---------- INJEÇÃO ----------
    def inject(self):
        tl = self.pending_tl
        session = self.pending_session
        fmt = self.pending_format

        if not tl:
            self._log("Nenhuma sessão ativa. Selecione a mesma pasta TL usada na extração.")
            tl = self.choose_tl("Selecione a mesma pasta TL usada na extração")
            if not tl:
                return

        # Se a aplicação foi reaberta, descobre o formato pelos arquivos existentes.
        if fmt is None:
            has_docx = (app_dir() / "old.docx").exists() or any(app_dir().glob("old_*.docx"))
            has_txt = (app_dir() / "old.txt").exists() or any(app_dir().glob("old_*.txt"))
            if has_docx and not has_txt:
                fmt = "docx"
            elif has_txt and not has_docx:
                fmt = "txt"
            else:
                raise ValueError("Não foi possível determinar automaticamente se a injeção é TXT ou DOCX.")

        self.bar["value"] = 0
        self.status.set("Status: Validando e injetando traduções...")
        self._log(f"Pasta TL: {tl}")

        def worker():
            if fmt == "docx":
                return inject_docx_translations(tl, app_dir(), session=session, progress=self._progress_from_worker)
            return inject_translations(tl, app_dir(), session=session, progress=self._progress_from_worker)

        def done(result):
            count, mode = result
            self.bar["value"] = 100
            self.status.set(f"Status: {count} traduções injetadas.")
            self._log(f"[OK] Injeção concluída: {count} registros ({mode}).")
            self._clear_waiting()

        self._run_background(worker, done, "Status: Erro na injeção.")


if __name__ == "__main__":
    App().mainloop()
