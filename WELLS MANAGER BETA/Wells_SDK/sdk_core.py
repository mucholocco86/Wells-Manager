# -*- coding: utf-8 -*-
"""Ren'Py 7.4.11 command bridge used by Wells Manager."""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

class SDKError(RuntimeError): pass

HERE=Path(__file__).resolve().parent
MANAGER_DIR=HERE.parent


def _sdk_dir():
    """Find the SDK both from source checkout and from a PyInstaller build."""
    candidates=[]
    override=os.environ.get('WELLS_RENPY_SDK')
    if override:
        candidates.append(Path(override))
    bundle=getattr(sys,'_MEIPASS',None)
    if bundle:
        b=Path(bundle)
        candidates += [b/'renpy-7.4.11-sdk', b/'Wells_SDK'/'renpy-7.4.11-sdk']
    candidates += [MANAGER_DIR.parent/'renpy-7.4.11-sdk', MANAGER_DIR/'renpy-7.4.11-sdk']
    for p in candidates:
        if (p/'renpy.exe').is_file() or (p/'renpy.sh').is_file():
            return p.resolve()
    raise SDKError("O núcleo Ren'Py 7.4.11 incluído no Wells Manager não foi encontrado.")


def _project_root(path):
    p=Path(path).expanduser().resolve()
    if p.name.lower()=='game' and p.is_dir(): p=p.parent
    if not p.is_dir() or not (p/'game').is_dir():
        raise SDKError("Selecione a pasta principal do jogo Ren'Py (a pasta que contém 'game').")
    return p


def _language(language,message='Informe o idioma da tradução.'):
    language=(language or '').strip()
    if not language or not all(c.islower() or c.isdigit() or c=='_' for c in language):
        raise SDKError(message+' Use letras minúsculas, números ou underscore.')
    return language


def _strings_json(project,language):
    return _project_root(project)/('wells_strings_'+language+'.json')


def _runner(sdk):
    if os.name=='nt' and (sdk/'renpy.exe').is_file(): return [str(sdk/'renpy.exe')]
    if (sdk/'renpy.sh').is_file(): return [str(sdk/'renpy.sh')]
    raise SDKError("O executável do núcleo Ren'Py 7.4.11 não foi encontrado.")


def run(project,args,log=None):
    project=_project_root(project); args=[str(x) for x in args]; sdk=_sdk_dir()
    cmd=_runner(sdk)+[str(project)]+args
    if log: log("Ren'Py: "+' '.join(args))
    startup=None
    if os.name=='nt':
        startup=subprocess.STARTUPINFO(); startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    proc=subprocess.Popen(cmd,cwd=str(sdk),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,errors='replace',startupinfo=startup)
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
    language=_language(language,'Informe o idioma.')
    args=['translate',language]
    if language=='rot13': args.append('--rot13')
    elif language=='piglatin': args.append('--piglatin')
    elif empty: args.append('--empty')
    return run(project,args,log)


def extract_string_translations(project,language,log=None,destination=None):
    language=_language(language)
    destination=Path(destination).expanduser().resolve() if destination else _strings_json(project,language)
    result=run(project,['extract_strings',language,str(destination)],log)
    result['file']=str(destination)
    return result


def merge_string_translations(project,language,replace=False,log=None,source=None,reverse=False):
    language=_language(language)
    source=Path(source).expanduser().resolve() if source else _strings_json(project,language)
    if not source.is_file():
        raise SDKError("Arquivo de strings não encontrado: {}. Use 'Extrair strings' primeiro.".format(source))
    args=['merge_strings',language,str(source)]
    if reverse: args.append('--reverse')
    if replace: args.append('--replace')
    result=run(project,args,log)
    result['file']=str(source)
    return result


def reverse_language(project,language,log=None):
    return merge_string_translations(project,language,replace=False,log=log,reverse=True)


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