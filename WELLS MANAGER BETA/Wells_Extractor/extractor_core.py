# Wells Extractor - núcleo funcional
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


# ---------------------------------------------------------------------------
# Locate and Dynamically Load the bundled Unrpyc source.
# ---------------------------------------------------------------------------
import importlib.util

def get_resource_dir():
    # extractor_core.py e a pasta unrpyc ficam juntos em Wells_Extractor,
    # inclusive no diretório temporário _MEI... do PyInstaller --onefile.
    return Path(__file__).resolve().parent

RESOURCE_DIR = get_resource_dir()
UNRPYC_DIR = RESOURCE_DIR / "unrpyc"

arquivo_motor = UNRPYC_DIR / "unrpyc.py"
if not arquivo_motor.exists():
    arquivo_motor = UNRPYC_DIR / "decompiler.py"

_unrpyc_module = None
_unrpyc_load_error = None

if not arquivo_motor.exists():
    _unrpyc_load_error = FileNotFoundError(
        "Motor Unrpyc não encontrado em: {}".format(UNRPYC_DIR)
    )

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





def decompile_rpyc_files(files, progress=None, log=None, status=None, display_root=None):
    if _unrpyc_module is None:
        raise RuntimeError("Não foi possível carregar o motor Unrpyc: {}".format(_unrpyc_load_error))
    files=[Path(f) for f in files]; total=len(files); ok=skipped=errors=0
    display_root = Path(display_root).resolve() if display_root else None

    def short_path(value):
        path = Path(value).resolve()
        if display_root:
            try:
                return str(path.relative_to(display_root)).replace("/", "\\")
            except Exception:
                pass
        return path.name

    for index, filename in enumerate(files,1):
        if status: status("Decompilando RPYC: {} de {}: {}".format(index,total,filename.name))
        try:
            context=_unrpyc_module.Context(); _unrpyc_module.decompile_rpyc(filename,context,overwrite=True)
            out_name = filename.with_suffix('.rpy').name
            if context.state=='ok':
                ok+=1
                if log: log("[RPYC] {} → {}".format(short_path(filename), out_name))
            elif context.state=='skip':
                skipped+=1
                if log: log("[IGNORADO] {}".format(short_path(filename)))
            else:
                errors+=1
                if log: log("[ERRO] {}: falha na decompilação.".format(short_path(filename)))
        except Exception as exc:
            errors+=1
            if log: log("[ERRO] {}: {}".format(short_path(filename),exc))
        if progress: progress((index/total)*100 if total else 100)
    return {'ok':ok,'skipped':skipped,'errors':errors,'total':total}

def extract_rpa_archives(archives, progress=None, log=None, status=None, display_root=None):
    archives=[Path(a) for a in archives]; total=len(archives); ok=errors=extracted=0
    display_root = Path(display_root).resolve() if display_root else None

    def short_path(value):
        path = Path(value).resolve()
        if display_root:
            try:
                return str(path.relative_to(display_root)).replace("/", "\\")
            except Exception:
                pass
        return path.name

    for index,rpa_path in enumerate(archives,1):
        if status: status("Extraindo {} de {}: {}".format(index,total,rpa_path.name))
        try:
            archive=RenPyArchive(str(rpa_path)); file_list=archive.list(); base_dir=rpa_path.parent
            archive_count=0
            for filename in file_list:
                try:
                    contents=archive.read(filename); relative=Path(str(filename).replace('/',os.sep)); out_path=base_dir/relative
                    out_path.parent.mkdir(parents=True,exist_ok=True); out_path.write_bytes(contents); extracted+=1; archive_count+=1
                except Exception as exc:
                    errors+=1
                    if log: log("[ERRO] {} → {}: {}".format(short_path(rpa_path), filename, exc))
            archive.close(); ok+=1
            if log: log("[RPA] {} → {} arquivos".format(short_path(rpa_path), archive_count))
        except Exception as exc:
            errors+=1
            if log: log("[ERRO] {}: {}".format(short_path(rpa_path),exc))
        if progress: progress((index/total)*100 if total else 100)
    return {'archives':ok,'extracted':extracted,'errors':errors}

def pack_rpa(file_entries, output_path, progress=None, log=None, status=None):
    compacted=0
    def report(number,total,archive_name):
        nonlocal compacted; compacted=number
        if status: status("Compactando {} de {}: {}".format(number,total,archive_name))
        if progress: progress((number/total)*100 if total else 100)
    create_rpa_archive(file_entries,Path(output_path),progress_callback=report)
    return {'compacted':compacted,'output':str(output_path)}
