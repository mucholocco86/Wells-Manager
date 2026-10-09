# -*- coding: utf-8 -*-
import sys
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from wells_revisor_core import review_file, find_dictionary

APP = "Wells Revisor PT-BR"

def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry("620x530")
        self.resizable(False, False)
        self.configure(bg="#222222")

        self.busy = False
        self.events = queue.Queue()
        self.after(50, self._poll)

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
            self, text="Wells Revisor PT-BR",
            bg="#222222", fg="#ff1010",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(22, 8))

        tk.Label(
            self,
            text="Revisa traduções TXT/DOCX antes da injeção pelo Wells Translator",
            bg="#222222", fg="#dddddd",
            font=("Segoe UI", 9),
        ).pack(pady=(0, 12))

        self.buttons = tk.Frame(self, bg="#222222")
        self.buttons.pack()

        self.txt_button = self._button("📄  Revisar documento TXT", lambda: self.choose_and_review("txt"))
        self.docx_button = self._button("📄  Revisar documento DOCX", lambda: self.choose_and_review("docx"))
        self.all_buttons = [self.txt_button, self.docx_button]

        self.status = tk.StringVar(value="Status: Aguardando documento.")
        tk.Label(
            self, textvariable=self.status, anchor="w",
            bg="#222222", fg="#f0f0f0", font=("Segoe UI", 10),
        ).pack(fill="x", padx=130, pady=(16, 6))

        self.bar = ttk.Progressbar(
            self, style="Wells.Horizontal.TProgressbar",
            mode="determinate", maximum=100, length=360,
        )
        self.bar.pack()

        tk.Label(
            self, text="Log de atividade", anchor="w",
            bg="#222222", fg="#f0f0f0", font=("Segoe UI", 10),
        ).pack(fill="x", padx=20, pady=(14, 2))

        frame = tk.Frame(self, bg="#222222")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self.log = tk.Text(
            frame, height=10, bg="#2b2b2b", fg="#eeeeee",
            insertbackground="white", relief="solid", bd=1,
            font=("Consolas", 9), state="disabled", wrap="word",
        )
        self.log.pack(fill="both", expand=True)

        dictionary = find_dictionary(app_dir())
        self._log("Wells Revisor iniciado.")
        if dictionary:
            self._log(f"[OK] Dicionário PT-BR localizado: {dictionary.name}")
        else:
            self._log("[AVISO] Palavras_PT-BR.txt não foi encontrado em dados_linguisticos.")
            self._log("A revisão estrutural funcionará, mas a revisão ortográfica por dicionário ficará desativada.")

    def _button(self, text, command):
        b = tk.Button(
            self.buttons, text=text, command=command,
            width=39, height=1, bg="#a6a6a6", fg="#101010",
            activebackground="#c5c5c5", activeforeground="#000000",
            relief="raised", bd=2, font=("Segoe UI", 10, "bold"),
            anchor="w", padx=12,
        )
        b.pack(pady=4)
        return b

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_busy(self, value):
        self.busy = value
        state = "disabled" if value else "normal"
        for b in self.all_buttons:
            b.configure(state=state)

    def _progress(self, value, text=None, log=None):
        self.events.put(("progress", value, text, log))

    def _poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "progress":
                    _, value, text, log = event
                    self.bar["value"] = value
                    if text:
                        self.status.set("Status: " + text)
                    if log:
                        self._log(log)
                elif kind == "done":
                    _, result = event
                    self._set_busy(False)
                    self.bar["value"] = 100
                    self.status.set(f"Status: {result['records']} linhas revisadas.")
                    self._log(f"[OK] Revisão concluída: {result['records']} linhas.")
                    self._log(f"[OK] Linhas alteradas: {result['changed']}.")
                    self._log(f"[OK] Alterações efetivas: {result['changed']}.")
                    self._log(f"[INFO] Ajustes internos avaliados: {result.get('internal_adjustments', result['changed'])}.")
                    self._log(f"[OK] Tokens Ren'Py preservados: {result['tokens']}.")
                    self._log(f"[OK] Saída: {result['output']}")
                    messagebox.showinfo(APP, f"Revisão concluída.\n\n{result['output']}")
                elif kind == "error":
                    _, error = event
                    self._set_busy(False)
                    self.status.set("Status: Erro na revisão.")
                    self._log(f"[ERRO] {error}")
                    messagebox.showerror(APP, str(error))
        except queue.Empty:
            pass
        self.after(50, self._poll)

    def choose_and_review(self, fmt):
        if self.busy:
            return
        types = [("Documento TXT", "*.txt")] if fmt == "txt" else [("Documento Word", "*.docx")]
        path = filedialog.askopenfilename(
            title="Selecione o documento traduzido para revisar",
            filetypes=types + [("Todos os arquivos", "*.*")]
        )
        if not path:
            return

        self._set_busy(True)
        self.bar["value"] = 0
        self.status.set("Status: Preparando revisão...")
        self._log(f"Documento: {path}")

        def worker():
            try:
                result = review_file(
                    Path(path),
                    app_dir(),
                    progress=self._progress,
                )
                self.events.put(("done", result))
            except Exception as exc:
                self.events.put(("error", exc))

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()
