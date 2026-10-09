# Wells Extractor GUI
#
# Interface/orchestrator for:
#   - Unrpyc: .rpyc/.rpymc -> .rpy/.rpym
#   - Ren'Py RPA archive extraction
#
# The RPA reader is based on the open-source rpatool/RenPyArchive implementation.
# Keep the original upstream copyright/license notices when redistributing this file.

import os
import sys
import threading
import queue
import traceback
from datetime import datetime
import codecs
import errno
import pickle
from pathlib import Path

# PyInstaller --onefile bootstrap: unrpyc.py is loaded dynamically at runtime,
# so PyInstaller cannot see its imports during normal static analysis.
# Import its standard-library dependencies here to make sure they are bundled.
import argparse
import glob
import struct
import zlib
import base64
import pickletools
import types
import inspect
import hashlib
import re
import operator
import io
import contextlib
import copy
import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ---------------------------------------------------------------------------
# Locate and Dynamically Load the bundled Unrpyc source.
# ---------------------------------------------------------------------------
import importlib.util

def get_resource_dir():
    # Wells_Extractor keeps its own resources beside this module.  In a
    # PyInstaller one-file build, sys._MEIPASS points to the package root,
    # not specifically to Wells_Extractor.  Prefer the module directory and
    # fall back to the bundled Wells_Extractor directory when necessary.
    module_dir = Path(__file__).resolve().parent
    if (module_dir / "unrpyc").is_dir():
        return module_dir
    if getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / "Wells_Extractor"
        if (bundled / "unrpyc").is_dir():
            return bundled
    return module_dir

RESOURCE_DIR = get_resource_dir()
UNRPYC_DIR = RESOURCE_DIR / "unrpyc"

# Define o arquivo principal que serve de entrada para o motor do unrpyc
# Geralmente é o 'unrpyc.py' ou 'decompiler.py' dentro da pasta.
arquivo_motor = UNRPYC_DIR / "unrpyc.py"
if not arquivo_motor.exists():
    arquivo_motor = UNRPYC_DIR / "decompiler.py"

_unrpyc_module = None
_unrpyc_load_error = None

if arquivo_motor.exists():
    try:
        # Coloca a pasta no caminho de busca para os sub-arquivos internos do motor funcionarem
        if str(UNRPYC_DIR) not in sys.path:
            sys.path.insert(0, str(UNRPYC_DIR))
            
        # Carrega o arquivo principal dinamicamente apelidando-o de 'unrpyc' na memória
        spec = importlib.util.spec_from_file_location("unrpyc", str(arquivo_motor))
        module = importlib.util.module_from_spec(spec)
        sys.modules["unrpyc"] = module
        spec.loader.exec_module(module)
        _unrpyc_module = module
    except Exception as exc:
        _unrpyc_module = None
        _unrpyc_load_error = exc

# ---------------------------------------------------------------------------
# Ren'Py RPA reader.
#
# Based on the open-source rpatool RenPyArchive implementation.
# The implementation is intentionally kept close to the original logic:
# RPA 2.0, RPA 3.0 and RPA 3.2 are supported.
# ---------------------------------------------------------------------------

if sys.version_info[0] >= 3:
    def _unicode(text):
        return text

    def _printable(text):
        return text

    def _unmangle(data):
        if isinstance(data, bytes):
            return data
        return data.encode("latin1")

    def _unpickle(data):
        return pickle.loads(data, encoding="latin1")
else:
    def _unicode(text):
        if isinstance(text, unicode):
            return text
        return text.decode("utf-8")

    def _printable(text):
        return text.encode("utf-8")

    def _unmangle(data):
        return data

    def _unpickle(data):
        return pickle.loads(data)


class RenPyArchive:
    RPA2_MAGIC = "RPA-2.0 "
    RPA3_MAGIC = "RPA-3.0 "
    RPA3_2_MAGIC = "RPA-3.2 "
    PICKLE_PROTOCOL = 2

    def __init__(self, file=None, version=3, padlength=0,
                 key=0xDEADBEEF, verbose=False):
        self.file = None
        self.handle = None
        self.files = {}
        self.indexes = {}
        self.version = None
        self.padlength = padlength
        self.key = key
        self.verbose = verbose

        if file is not None:
            self.load(file)
        else:
            self.version = version

    def close(self):
        if self.handle is not None:
            self.handle.close()
            self.handle = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def get_version(self):
        self.handle.seek(0)
        magic = self.handle.readline().decode("utf-8")

        if magic.startswith(self.RPA3_2_MAGIC):
            return 3.2
        elif magic.startswith(self.RPA3_MAGIC):
            return 3
        elif magic.startswith(self.RPA2_MAGIC):
            return 2
        elif self.file and self.file.endswith(".rpi"):
            return 1

        raise ValueError(
            "the given file is not a valid Ren'Py archive, "
            "or an unsupported version"
        )

    def extract_indexes(self):
        self.handle.seek(0)
        indexes = None

        if self.version in (2, 3, 3.2):
            metadata = self.handle.readline()
            vals = metadata.split()
            offset = int(vals[1], 16)

            if self.version == 3:
                self.key = 0
                for subkey in vals[2:]:
                    self.key ^= int(subkey, 16)
            elif self.version == 3.2:
                self.key = 0
                for subkey in vals[3:]:
                    self.key ^= int(subkey, 16)

            self.handle.seek(offset)
            contents = codecs.decode(self.handle.read(), "zlib")
            indexes = _unpickle(contents)

            if self.version in (3, 3.2):
                obfuscated_indexes = indexes
                indexes = {}

                for filename in obfuscated_indexes.keys():
                    if len(obfuscated_indexes[filename][0]) == 2:
                        indexes[filename] = [
                            (off ^ self.key, length ^ self.key)
                            for off, length in obfuscated_indexes[filename]
                        ]
                    else:
                        indexes[filename] = [
                            (off ^ self.key, length ^ self.key, prefix)
                            for off, length, prefix
                            in obfuscated_indexes[filename]
                        ]
        else:
            # Kept for compatibility with the original implementation.
            self.handle.seek(0)
            self.handle.readline()
            indexes = _unpickle(
                codecs.decode(self.handle.read(), "zlib")
            )

        return indexes

    def convert_filename(self, filename):
        drive, filename = os.path.splitdrive(
            os.path.normpath(filename).replace(os.sep, "/")
        )
        return filename

    def list(self):
        return list(self.indexes.keys()) + list(self.files.keys())

    def read(self, filename):
        filename = self.convert_filename(_unicode(filename))

        if filename not in self.files and filename not in self.indexes:
            raise IOError(
                errno.ENOENT,
                "The requested file '{}' does not exist in this archive."
                .format(filename)
            )

        if (
            filename not in self.files
            and filename in self.indexes
            and self.handle is None
        ):
            raise IOError(
                errno.ENOENT,
                "The requested file '{}' does not exist in this archive."
                .format(filename)
            )

        if filename in self.files:
            return self.files[filename]

        if len(self.indexes[filename][0]) == 3:
            offset, length, prefix = self.indexes[filename][0]
        else:
            offset, length = self.indexes[filename][0]
            prefix = b""

        self.handle.seek(offset)
        return _unmangle(prefix) + self.handle.read(length - len(prefix))

    def load(self, filename):
        if self.handle is not None:
            self.handle.close()

        self.file = _unicode(filename)
        self.files = {}
        self.handle = open(self.file, "rb")
        self.version = self.get_version()
        self.indexes = self.extract_indexes()


# ---------------------------------------------------------------------------
# RPA creator (new, isolated feature).
#
# This does not alter the existing extraction/decompilation code. It writes
# standard RPA-3.0 archives using the same index format already understood by
# the RenPyArchive reader above.
# ---------------------------------------------------------------------------

def create_rpa_archive(file_entries, output_path, progress_callback=None):
    """
    Create an RPA-3.0 archive.

    file_entries is an iterable of (archive_name, real_path) pairs.
    archive_name must use forward slashes and be relative to the selected
    base directory.
    """
    output_path = Path(output_path)
    key = 0xDEADBEEF
    header_size = 34  # len(b"RPA-3.0 " + 16 hex + b" " + 8 hex + b"\\n")
    indexes = {}
    total = len(file_entries)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "wb") as archive:
            # Reserve space for the header. It is written after the data/index.
            archive.write(b" " * header_size)

            for number, (archive_name, real_path) in enumerate(file_entries, 1):
                archive_name = str(archive_name).replace("\\", "/")
                real_path = Path(real_path)

                offset = archive.tell()
                length = real_path.stat().st_size

                with open(real_path, "rb") as source:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        archive.write(chunk)

                indexes[archive_name] = [
                    (offset ^ key, length ^ key)
                ]

                if progress_callback is not None:
                    progress_callback(number, total, archive_name)

            index_offset = archive.tell()
            packed_index = pickle.dumps(
                indexes,
                protocol=RenPyArchive.PICKLE_PROTOCOL
            )
            archive.write(zlib.compress(packed_index))

            archive.seek(0)
            header = "RPA-3.0 {:016x} {:08x}\n".format(
                index_offset,
                key
            ).encode("ascii")
            archive.write(header)

    except Exception:
        # Do not leave a half-written archive behind after an error.
        try:
            if output_path.exists():
                output_path.unlink()
        except Exception:
            pass
        raise



class WellsExtractorGUI(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack(fill="both", expand=True)
        self.root.title("Wells Extractor GUI")
        self.root.geometry("580x420")
        self.root.minsize(620, 520)

        self.events = queue.Queue()
        self.busy = False
        self.status_var = tk.StringVar(value="Status: Nenhuma operação iniciada.")

        # Log cumulativo persistente. Quando compilado, fica ao lado do .exe.
        # Em modo .py, fica ao lado do main.py. Falhas ao gravar o log nunca
        # interrompem as funções principais da ferramenta.
        if getattr(sys, "frozen", False):
            log_dir = Path(sys.executable).resolve().parent
        else:
            log_dir = Path(__file__).resolve().parent
        self.persistent_log_path = log_dir / "Wells_Extractor.log"

        self._build_ui()
        self._poll_events()

    def _build_ui(self):
        # -------------------------------------------------------------
        # WELLS EXTRACTOR GUI - VISUAL THEME
        # -------------------------------------------------------------
        # Extraction functions and button commands are intentionally
        # preserved. This section changes only the visual presentation.
        # -------------------------------------------------------------

        self.configure(bg="#303030")

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Main panel
        style.configure(
            "Wells.TFrame",
            background="#242424"
        )

        # Title
        style.configure(
            "WellsTitle.TLabel",
            background="#2C2C2C",
            foreground="#FF0000",
            font=("Segoe UI", 20, "bold")
        )

        # Normal labels
        style.configure(
            "Wells.TLabel",
            background="#2E2D2D",
            foreground="#D8D8D8",
            font=("Segoe UI", 12)
        )

        # Buttons: red, slightly lighter than the title.
        # Width is controlled in characters; height is approximated
        # through vertical padding so the visual button is about 16 px.
        style.configure(
            "Wells.TButton",
            background="#8D8C8C",
            foreground="#0A0A0A",
            borderwidth=1,
            relief="raised",
            focusthickness=1,
            padding=(10, 2),
            font=("Segoe UI", 11, "bold")
        )

        style.map(
            "Wells.TButton",
            background=[
                ("active", "#EF6A6A"),
                ("pressed", "#C94444"),
                ("disabled", "#6B3A3A")
            ],
            foreground=[
                ("disabled", "#888888")
            ]
        )

        # Separator
        style.configure(
            "Wells.Horizontal.TSeparator",
            background="#FC0D0D"
        )

        # Progress bar
        style.configure(
            "Wells.Horizontal.TProgressbar",
            troughcolor="#242424",
            background="#E05252",
            bordercolor="#555555",
            lightcolor="#E05252",
            darkcolor="#B83D3D"
        )

        outer = ttk.Frame(self, style="Wells.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        title = ttk.Label(
            outer,
            text="Wells Extractor GUI",
            style="WellsTitle.TLabel"
        )
        title.pack(pady=(0, 12))

        # Four original buttons. Commands are untouched.
        buttons = ttk.Frame(outer, style="Wells.TFrame")
        buttons.pack(fill="x", pady=(0, 10))

        self.btn_rpyc_file = ttk.Button(
            buttons,
            text="📄  Extrair RPYC → RPY (Arquivo)",
            command=self.choose_rpyc,
            style="Wells.TButton",
            width=27
        )
        self.btn_rpyc_file.pack(anchor="center", pady=(0, 6))

        self.btn_rpyc_folder = ttk.Button(
            buttons,
            text="📁  Extrair RPYC → RPY (Pasta)",
            command=self.choose_rpyc_folder,
            style="Wells.TButton",
            width=27
        )
        self.btn_rpyc_folder.pack(anchor="center", pady=(0, 6))

        self.btn_rpa_file = ttk.Button(
            buttons,
            text="📦  Extrair RPA (Arquivo)",
            command=self.choose_rpa,
            style="Wells.TButton",
            width=27
        )
        self.btn_rpa_file.pack(anchor="center", pady=(0, 6))

        self.btn_rpa_folder = ttk.Button(
            buttons,
            text="📁  Extrair RPA (Pasta)",
            command=self.choose_rpa_folder,
            style="Wells.TButton",
            width=27
        )
        self.btn_rpa_folder.pack(anchor="center", pady=(0, 6))

        self.btn_rpa_create = ttk.Button(
            buttons,
            text="📦  Compactar → RPA",
            command=self.choose_rpa_create,
            style="Wells.TButton",
            width=27
        )
        self.btn_rpa_create.pack(anchor="center")

        # Status area centered between buttons and activity log.
        status_frame = ttk.Frame(outer, style="Wells.TFrame")
        status_frame.pack(fill="x", pady=(4, 10))

        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Wells.TLabel",
            anchor="center",
            justify="center"
        )
        self.status_label.pack(anchor="center")

        self.progress = ttk.Progressbar(
            status_frame,
            orient="horizontal",
            mode="determinate",
            style="Wells.Horizontal.TProgressbar",
            length=360
        )
        self.progress.pack(anchor="center", pady=(7, 0))

        # Activity log: deliberately darker than the panel, creating
        # a framed/recessed-box appearance.
        log_label = ttk.Label(
            outer,
            text="Log de atividade",
            style="Wells.TLabel"
        )
        log_label.pack(anchor="w", pady=(0, 4))

        log_frame = tk.Frame(
            outer,
            bg="#202020",
            highlightbackground="#555555",
            highlightcolor="#777676",
            highlightthickness=1,
            bd=2,
            relief="sunken"
        )
        log_frame.pack(fill="both", expand=True)

        self.log = tk.Text(
            log_frame,
            height=8,
            wrap="word",
            bg="#2C2C2C",
            fg="#D0D0D0",
            insertbackground="#FFFFFF",
            selectbackground="#4A4A4A",
            selectforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
            font=("Consolas", 11)
        )
        self.log.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scrollbar.set)

    def _set_busy(self, busy):
        state = "disabled" if busy else "normal"

        self.btn_rpyc_file.configure(state=state)
        self.btn_rpyc_folder.configure(state=state)
        self.btn_rpa_file.configure(state=state)
        self.btn_rpa_folder.configure(state=state)
        self.btn_rpa_create.configure(state=state)

    def _write_persistent_log(self, text):
        # O arquivo cumulativo guarda apenas o resumo de cada operação e
        # detalhes de erros. Os milhares de [OK] continuam somente no painel.
        try:
            with open(self.persistent_log_path, "a", encoding="utf-8") as logfile:
                logfile.write(text.rstrip() + "\n")
        except Exception:
            pass

    def _write_log(self, text):
        line = text.rstrip()

        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

        # No .txt persistente, registra somente erros e resumos úteis.
        if "[ERRO]" in line:
            self._write_persistent_log(line)
        elif line.startswith("COMPACTADOS:") or line.startswith("ERROS:"):
            self._write_persistent_log(line)
        elif line.startswith("DECOMPILAÇÃO COMPLETA!:"):
            self._write_persistent_log(line)
        elif line.startswith("EXTRAÇÃO COMPLETA!:"):
            self._write_persistent_log(line)

    def _begin_log_session(self, operation):
        # O painel mantém o comportamento visual original.
        self._write_log("")
        self._write_log("=" * 60)
        self._write_log(datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
        self._write_log("OPERAÇÃO: {}".format(operation))
        self._write_log("=" * 60)

        # O .txt recebe apenas um cabeçalho compacto para localizar a sessão.
        self._write_persistent_log("")
        self._write_persistent_log("=" * 60)
        self._write_persistent_log(datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
        self._write_persistent_log("OPERAÇÃO: {}".format(operation))
        self._write_persistent_log("=" * 60)

    def _emit(self, kind, *args):
        self.events.put((kind, args))

    def _poll_events(self):
        try:
            while True:
                kind, args = self.events.get_nowait()

                if kind == "log":
                    self._write_log(args[0])

                elif kind == "status":
                    self.status_var.set(args[0])

                elif kind == "progress":
                    self.progress["value"] = args[0]

                elif kind == "finished":
                    self.progress["value"] = 100
                    self._set_busy(False)
                    self.status_var.set(args[0])

                elif kind == "error":
                    self._set_busy(False)
                    self.status_var.set("Operação finalizada com erros.")
                    messagebox.showerror("Erro", args[0])

        except queue.Empty:
            pass

        self.root.after(100, self._poll_events)

    # ------------------------------------------------------------------
    # RPA creation - fifth button only
    # ------------------------------------------------------------------

    def _ask_folders_native(self, title):
        """Seletor nativo do Windows com suporte a múltiplas pastas."""
        if sys.platform != "win32":
            folder = filedialog.askdirectory(title=title)
            return [folder] if folder else []

        import ctypes
        from ctypes import wintypes

        HRESULT = ctypes.c_long
        ULONG = ctypes.c_ulong
        DWORD = ctypes.c_ulong
        UINT = ctypes.c_uint
        LPVOID = ctypes.c_void_p

        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", DWORD),
                ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort),
                ("Data4", ctypes.c_ubyte * 8),
            ]

        def guid(value):
            import uuid
            u = uuid.UUID(value)
            data = u.bytes_le
            result = GUID()
            ctypes.memmove(ctypes.byref(result), data, 16)
            return result

        def vcall(ptr, index, restype, argtypes, *args):
            vtable = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(LPVOID))).contents
            fn = ctypes.WINFUNCTYPE(restype, LPVOID, *argtypes)(vtable[index])
            return fn(ptr, *args)

        CLSID_FileOpenDialog = guid("DC1C5A9C-E88A-4DDE-A5A1-60F82A20AEF7")
        IID_IFileOpenDialog = guid("D57C7288-D4AD-4768-BE02-9D969532D960")

        CLSCTX_INPROC_SERVER = 0x1
        FOS_PICKFOLDERS = 0x00000020
        FOS_FORCEFILESYSTEM = 0x00000040
        FOS_ALLOWMULTISELECT = 0x00000200
        FOS_PATHMUSTEXIST = 0x00000800
        SIGDN_FILESYSPATH = 0x80058000
        ERROR_CANCELLED_HRESULT = 0x800704C7

        ole32 = ctypes.windll.ole32
        ole32.CoInitialize.argtypes = [LPVOID]
        ole32.CoInitialize.restype = HRESULT
        ole32.CoCreateInstance.argtypes = [
            ctypes.POINTER(GUID), LPVOID, DWORD,
            ctypes.POINTER(GUID), ctypes.POINTER(LPVOID)
        ]
        ole32.CoCreateInstance.restype = HRESULT
        ole32.CoTaskMemFree.argtypes = [LPVOID]

        dialog = LPVOID()
        initialized = False

        try:
            hr = ole32.CoInitialize(None)
            initialized = hr >= 0

            hr = ole32.CoCreateInstance(
                ctypes.byref(CLSID_FileOpenDialog), None, CLSCTX_INPROC_SERVER,
                ctypes.byref(IID_IFileOpenDialog), ctypes.byref(dialog)
            )
            if hr < 0:
                raise OSError("Não foi possível abrir o seletor de pastas do Windows.")

            # IFileDialog::SetOptions (índice 9)
            options = DWORD()
            vcall(dialog, 10, HRESULT, [ctypes.POINTER(DWORD)], ctypes.byref(options))
            options.value |= (
                FOS_PICKFOLDERS | FOS_FORCEFILESYSTEM |
                FOS_ALLOWMULTISELECT | FOS_PATHMUSTEXIST
            )
            vcall(dialog, 9, HRESULT, [DWORD], options)

            # IFileDialog::SetTitle (índice 17)
            vcall(dialog, 17, HRESULT, [wintypes.LPCWSTR], title)

            # IModalWindow::Show (índice 3)
            hwnd = self.root.winfo_id()
            hr = vcall(dialog, 3, HRESULT, [wintypes.HWND], hwnd)
            if ctypes.c_ulong(hr).value == ERROR_CANCELLED_HRESULT:
                return []
            if hr < 0:
                raise OSError("O seletor de pastas do Windows retornou um erro.")

            # IFileOpenDialog::GetResults (índice 27)
            items = LPVOID()
            hr = vcall(dialog, 27, HRESULT, [ctypes.POINTER(LPVOID)], ctypes.byref(items))
            if hr < 0 or not items:
                return []

            try:
                count = DWORD()
                vcall(items, 7, HRESULT, [ctypes.POINTER(DWORD)], ctypes.byref(count))
                result = []

                for index in range(count.value):
                    item = LPVOID()
                    hr = vcall(items, 8, HRESULT, [DWORD, ctypes.POINTER(LPVOID)], index, ctypes.byref(item))
                    if hr < 0 or not item:
                        continue
                    try:
                        path_ptr = wintypes.LPWSTR()
                        hr = vcall(item, 5, HRESULT, [DWORD, ctypes.POINTER(wintypes.LPWSTR)], SIGDN_FILESYSPATH, ctypes.byref(path_ptr))
                        if hr >= 0 and path_ptr.value:
                            result.append(path_ptr.value)
                        if path_ptr:
                            ole32.CoTaskMemFree(path_ptr)
                    finally:
                        vcall(item, 2, ULONG, [])

                return result
            finally:
                vcall(items, 2, ULONG, [])

        finally:
            if dialog:
                vcall(dialog, 2, ULONG, [])
            if initialized:
                ole32.CoUninitialize()

    def choose_rpa_create(self):
        if self.busy:
            return

        # Usa somente as janelas nativas do sistema.
        # Primeiro permite selecionar um ou mais arquivos.
        selected_files = filedialog.askopenfilenames(
            title="Selecionar arquivos para compactar em RPA",
            filetypes=[("Todos os arquivos", "*.*")]
        )

        selected = []
        base_path = None

        if selected_files:
            selected = [Path(f).resolve() for f in selected_files]
            parents = [str(p.parent) for p in selected]
            base_path = Path(os.path.commonpath(parents)).resolve()
        else:
            # Cancelando a seleção de arquivos, abre o seletor NATIVO do Windows
            # em modo de múltiplas pastas. Nenhuma janela própria é criada.
            selected_folders = self._ask_folders_native(
                "Selecionar pastas para compactar em RPA"
            )
            if not selected_folders:
                return

            selected = [Path(folder).resolve() for folder in selected_folders]
            # As pastas selecionadas ficam no RPA com seus próprios nomes,
            # preservando a estrutura relativa a partir do ancestral comum.
            base_path = Path(os.path.commonpath([str(p.parent) for p in selected])).resolve()

        output = filedialog.asksaveasfilename(
            title="Salvar arquivo RPA",
            defaultextension=".rpa",
            filetypes=[("Ren'Py Archive", "*.rpa")]
        )
        if not output:
            return

        output_path = Path(output).resolve()
        entries = {}

        for selected_path in selected:
            if selected_path.is_dir():
                candidates = [
                    p for p in selected_path.rglob("*")
                    if p.is_file()
                ]
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
                "Wells Extractor",
                "A seleção não contém arquivos para compactar."
            )
            return

        self._start_rpa_create(file_entries, output_path)

    def _start_rpa_create(self, file_entries, output_path):
        self._set_busy(True)
        self.progress["value"] = 0
        self.status_var.set("Preparando compactação RPA...")
        self._begin_log_session("COMPACTAR RPA")
        self._write_log("=== Wells Extractor — Compactar → RPA ===")
        self._write_log("Arquivos selecionados: {}".format(len(file_entries)))
        self._write_log("Saída: {}".format(output_path))

        thread = threading.Thread(
            target=self._rpa_create_worker,
            args=(file_entries, output_path),
            daemon=True
        )
        thread.start()

    def _rpa_create_worker(self, file_entries, output_path):
        compacted = 0
        errors = 0

        try:
            def report(number, total, archive_name):
                nonlocal compacted
                compacted = number
                self._emit(
                    "status",
                    "Compactando {} de {}: {}".format(
                        number, total, archive_name
                    )
                )
                self._emit("log", "    [OK] {}".format(archive_name))
                self._emit("progress", (number / total) * 100)

            create_rpa_archive(
                file_entries,
                output_path,
                progress_callback=report
            )

            self._emit("log", "")
            self._emit("log", "COMPACTADOS: {}".format(compacted))
            self._emit("log", "ERROS: {}".format(errors))
            summary = (
                "COMPACTAÇÃO COMPLETA!: {} arquivos → {}"
                .format(compacted, output_path.name)
            )
            self._emit("log", summary)
            self._emit("finished", summary)

        except Exception as exc:
            errors += 1
            self._emit("log", "[ERRO] {}".format(exc))
            self._emit("log", "")
            self._emit("log", "COMPACTADOS: {}".format(compacted))
            self._emit("log", "ERROS: {}".format(errors))
            self._emit("error", "Falha ao criar o arquivo RPA.\n{}".format(exc))

    # ------------------------------------------------------------------
    # RPYC
    # ------------------------------------------------------------------

    def choose_rpyc(self):
        if self.busy:
            return

        # Janela normal de seleção de arquivos do Windows.
        files = filedialog.askopenfilenames(
            title="Selecionar arquivos RPYC/RPYMC",
            filetypes=[
                ("Ren'Py Compiled Script", "*.rpyc"),
                ("Ren'Py Compiled Translation", "*.rpymc"),
            ]
        )

        if files:
            self._start_rpyc([Path(f) for f in files])
            return

        # Se o usuário cancelar a seleção de arquivos, pode selecionar uma pasta.
        folder = filedialog.askdirectory(
            title="Selecionar pasta contendo RPYC/RPYMC"
        )

        if folder:
            files = [
                p for p in Path(folder).rglob("*")
                if p.is_file()
                and p.suffix.lower() in (".rpyc", ".rpymc")
            ]

            if not files:
                messagebox.showinfo(
                    "Wells Extractor",
                    "Nenhum arquivo .rpyc ou .rpymc foi encontrado na pasta selecionada."
                )
                return

            self._start_rpyc(files)

    def choose_rpyc_folder(self):
        if self.busy:
            return

        folder = filedialog.askdirectory(
            title="Selecionar pasta contendo RPYC/RPYMC"
        )

        if not folder:
            return

        files = [
            p for p in Path(folder).rglob("*")
            if p.is_file()
            and p.suffix.lower() in (".rpyc", ".rpymc")
        ]

        if not files:
            messagebox.showinfo(
                "Wells Extractor",
                "Nenhum arquivo .rpyc ou .rpymc foi encontrado na pasta selecionada."
            )
            return

        self._start_rpyc(files)

    def choose_rpa_folder(self):
        if self.busy:
            return

        folder = filedialog.askdirectory(
            title="Selecionar pasta contendo arquivos RPA"
        )

        if not folder:
            return

        archives = [
            p for p in Path(folder).rglob("*")
            if p.is_file() and p.suffix.lower() == ".rpa"
        ]

        if not archives:
            messagebox.showinfo(
                "Wells Extractor",
                "Nenhum arquivo .rpa foi encontrado na pasta selecionada."
            )
            return

        self._start_rpa(archives)

    def _start_rpyc(self, files):
        self._set_busy(True)
        self.progress["value"] = 0
        self.status_var.set("Preparando descompilação...")
        self._begin_log_session("DESCOMPILAR RPYC → RPY")
        self._write_log("=== Wells Extractor — RPYC → RPY ===")
        self._write_log("Arquivos encontrados: {}".format(len(files)))

        thread = threading.Thread(
            target=self._rpyc_worker,
            args=(files,),
            daemon=True
        )
        thread.start()

    def _rpyc_worker(self, files):
        if _unrpyc_module is None:
            self._emit(
                "error",
                "Não foi possível carregar o motor Unrpyc.\n"
                "Erro interno: {}".format(_unrpyc_load_error)
            )
            return

        total = len(files)
        ok = 0
        skipped = 0
        errors = 0

        for index, filename in enumerate(files, 1):
            self._emit(
                "status",
                "Decompilando RPYC: {} de {}: {}".format(
                    index, total, filename.name
                )
            )
            self._emit("log", "[RPYC] {}".format(filename))

            try:
                context = _unrpyc_module.Context()
                _unrpyc_module.decompile_rpyc(
                    Path(filename),
                    context,
                    overwrite=True
                )

                for line in context.log_contents:
                    self._emit("log", "    " + str(line))

                if context.state == "ok":
                    ok += 1
                    self._emit(
                        "log",
                        "[OK] {}".format(filename.with_suffix(
                            ".rpy" if filename.suffix.lower() == ".rpyc"
                            else ".rpym"
                        ))
                    )
                elif context.state == "skip":
                    skipped += 1
                else:
                    errors += 1
                    self._emit(
                        "log",
                        "[ERRO] {}".format(filename)
                    )

            except Exception as exc:
                errors += 1
                self._emit(
                    "log",
                    "[ERRO] {}: {}".format(filename, exc)
                )

            self._emit("progress", (index / total) * 100)

        summary = (
            "DECOMPILAÇÃO COMPLETA!: {}, ignorados: {}, erros: {}"
            .format(ok, skipped, errors)
        )
        self._emit("log", "")
        self._emit("log", summary)
        self._emit("finished", summary)

    # ------------------------------------------------------------------
    # RPA
    # ------------------------------------------------------------------

    def choose_rpa(self):
        if self.busy:
            return

        # Janela normal de seleção de arquivos do Windows.
        files = filedialog.askopenfilenames(
            title="Selecionar arquivos RPA",
            filetypes=[("Ren'Py Archive", "*.rpa")]
        )

        if files:
            self._start_rpa([Path(f) for f in files])
            return

        # Se o usuário cancelar a seleção de arquivos, pode selecionar uma pasta.
        folder = filedialog.askdirectory(
            title="Selecionar pasta contendo arquivos RPA"
        )

        if folder:
            archives = [
                p for p in Path(folder).rglob("*")
                if p.is_file() and p.suffix.lower() == ".rpa"
            ]

            if not archives:
                messagebox.showinfo(
                    "Wells Extractor",
                    "Nenhum arquivo .rpa foi encontrado na pasta selecionada."
                )
                return

            self._start_rpa(archives)

    def _start_rpa(self, archives):
        self._set_busy(True)
        self.progress["value"] = 0
        self.status_var.set("Preparando extração RPA...")
        self._begin_log_session("EXTRAIR RPA")
        self._write_log("=== Wells Extractor — RPA ===")
        self._write_log("Arquivos RPA encontrados: {}".format(len(archives)))

        thread = threading.Thread(
            target=self._rpa_worker,
            args=(archives,),
            daemon=True
        )
        thread.start()

    def _rpa_worker(self, archives):
        total = len(archives)
        ok = 0
        errors = 0
        extracted = 0

        for index, rpa_path in enumerate(archives, 1):
            self._emit(
                "status",
                "_Extraindo {} de {}: {}".format(
                    index, total, rpa_path.name
                )
            )
            self._emit("log", "[RPA] {}".format(rpa_path))

            try:
                archive = RenPyArchive(str(rpa_path))
                file_list = archive.list()

                self._emit(
                    "log",
                    "    Arquivos dentro do RPA: {}".format(len(file_list))
                )

                base_dir = rpa_path.parent

                for filename in file_list:
                    try:
                        contents = archive.read(filename)

                        relative = Path(str(filename).replace("/", os.sep))
                        out_path = base_dir / relative

                        out_path.parent.mkdir(
                            parents=True,
                            exist_ok=True
                        )

                        with open(out_path, "wb") as outfile:
                            outfile.write(contents)

                        extracted += 1
                        self._emit("log", "    [OK] {}".format(out_path))

                    except Exception as exc:
                        errors += 1
                        self._emit(
                            "log",
                            "    [ERRO] {}: {}".format(filename, exc)
                        )

                archive.close()
                ok += 1

            except Exception as exc:
                errors += 1
                self._emit(
                    "log",
                    "[ERRO] {}: {}".format(rpa_path, exc)
                )

            self._emit("progress", (index / total) * 100)

        summary = (
            "EXTRAÇÃO COMPLETA!: {}, "
            "arquivos processados: {}, erros: {}"
            .format(extracted, ok, errors)
        )
        self._emit("log", "")
        self._emit("log", summary)
        self._emit("finished", summary)


def main():
    root = tk.Tk()
    WellsExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
