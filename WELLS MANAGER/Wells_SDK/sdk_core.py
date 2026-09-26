# -*- coding: utf-8 -*-
"""Ren'Py 7.4.11 command bridge used by Wells Manager."""
from __future__ import annotations
import os, subprocess
from pathlib import Path

class SDKError(RuntimeError): pass

HERE=Path(__file__).resolve().parent
MANAGER_DIR=HERE.parent
REPO_ROOT=MANAGER_DIR.parent
SDK_DIR=REPO_ROOT/'renpy-7.4.11-sdk'

def _project_root(path):
    p=Path(path).expanduser().resolve()
    if p.name.lower()=='game' and p.is_dir(): p=p.parent
    if not p.is_dir() or not (p/'game').is_dir():
        raise SDKError("Selecione a pasta principal do jogo Ren'Py (a pasta que contém 'game').")
    return p

def _runner():
    if os.name=='nt' and (SDK_DIR/'renpy.exe').is_file(): return [str(SDK_DIR/'renpy.exe')]
    if (SDK_DIR/'renpy.sh').is_file(): return [str(SDK_DIR/'renpy.sh')]
    raise SDKError("O núcleo Ren'Py 7.4.11 do Wells Manager não foi encontrado.")

def run(project,args,log=None):
    project=_project_root(project); args=[str(x) for x in args]
    cmd=_runner()+[str(project)]+args
    if log: log("Ren'Py: "+' '.join(args))
    startup=None
    if os.name=='nt':
        startup=subprocess.STARTUPINFO(); startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    proc=subprocess.Popen(cmd,cwd=str(SDK_DIR),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,errors='replace',startupinfo=startup)
    output=[]
    for line in proc.stdout:
        line=line.rstrip('\r\n'); output.append(line)
        if log and line: log(line)
    code=proc.wait()
    if code:
        tail='\n'.join(output[-12:]).strip()
        raise SDKError(tail or "O Ren'Py encerrou a operação com erro (código {}).".format(code))
    return {'project':str(project),'command':args,'output':output}

def generate_translations(project,language,empty=True,log=None):
    language=(language or '').strip()
    if not language or not all(c.islower() or c.isdigit() or c=='_' for c in language):
        raise SDKError('Informe o idioma com letras minúsculas, números ou underscore.')
    args=['translate',language]
    if language=='rot13': args.append('--rot13')
    elif language=='piglatin': args.append('--piglatin')
    elif empty: args.append('--empty')
    return run(project,args,log)

def extract_string_translations(project,language,log=None):
    language=(language or '').strip()
    if not language: raise SDKError('Informe o idioma da tradução.')
    return run(project,['extract_strings',language],log)

def merge_string_translations(project,language,replace=False,log=None):
    language=(language or '').strip()
    if not language: raise SDKError('Informe o idioma da tradução.')
    args=['merge_strings',language]
    if replace: args.append('--replace')
    return run(project,args,log)

def reverse_language(project,language,log=None):
    language=(language or '').strip()
    if not language: raise SDKError('Informe o idioma que será invertido.')
    return run(project,['translate',language,'--reverse'],log)

def update_launcher_translations(project,log=None):
    return run(project,['translate','None'],log)

def extract_dialogue(project,fmt='tab',strings=False,notags=False,escape=False,log=None):
    if fmt not in ('tab','txt'): raise SDKError('Formato de diálogo inválido.')
    args=['dialogue']
    if fmt=='txt': args.append('--text')
    if strings: args.append('--strings')
    if notags: args.append('--notags')
    if escape: args.append('--escape')
    result=run(project,args,log)
    result['file']=str(_project_root(project)/('dialogue.txt' if fmt=='txt' else 'dialogue.tab'))
    return result

def lint(project,log=None):
    project=_project_root(project); report=project/'wells_lint.txt'
    result=run(project,['lint',str(report)],log); result['file']=str(report); return result

def delete_persistent(project,log=None): return run(project,['rmpersistent'],log)
def force_recompile(project,log=None): return run(project,['compile'],log)
