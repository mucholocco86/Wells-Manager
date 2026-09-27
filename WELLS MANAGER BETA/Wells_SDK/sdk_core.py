# -*- coding: utf-8 -*-
"""Ren'Py command bridge used by Wells Manager."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

class SDKError(RuntimeError): pass

HERE=Path(__file__).resolve().parent
MANAGER_DIR=HERE.parent


def _sdk_dir():
    """Find the physical Wells runtime, with legacy names kept as fallbacks."""
    candidates=[]
    override=os.environ.get('WELLS_RENPY_SDK')
    if override:
        candidates.append(Path(override))
    bundle=getattr(sys,'_MEIPASS',None)
    if bundle:
        b=Path(bundle)
        candidates += [b/'Wells_Runtime', b/'renpy-7.4.11-sdk', b/'Wells_SDK'/'renpy-7.4.11-sdk']
    candidates += [
        MANAGER_DIR.parent/'Wells_Runtime', MANAGER_DIR/'Wells_Runtime',
        MANAGER_DIR.parent/'renpy-7.4.11-sdk', MANAGER_DIR/'renpy-7.4.11-sdk'
    ]
    for p in candidates:
        if (p/'renpy.exe').is_file() or (p/'renpy.sh').is_file():
            return p.resolve()
    raise SDKError("O Wells Runtime incluído no Wells Manager não foi encontrado.")


def _project_root(path):
    p=Path(path).expanduser().resolve()
    if p.name.lower()=='game' and p.is_dir(): p=p.parent
    if not p.is_dir() or not (p/'game').is_dir():
        raise SDKError("Selecione a pasta 'game' do jogo ou a pasta principal que contém 'game'.")
    return p


def _language(language,message='Informe o idioma da tradução.'):
    language=(language or '').strip()
    if not language or not all(c.islower() or c.isdigit() or c=='_' for c in language):
        raise SDKError(message+' Use letras minúsculas, números ou underscore.')
    return language


def _translation_dir(project,language):
    return _project_root(project)/'game'/'tl'/language


def _strings_json(project,language):
    return _translation_dir(project,language)/'strings.json'


def _format_strings_json(path):
    """Rewrite Ren'Py's compact JSON as a readable, translator-friendly document."""
    path=Path(path)
    try:
        with path.open('r',encoding='utf-8') as f:
            data=json.load(f)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    except Exception as exc:
        raise SDKError('As strings foram extraídas, mas o JSON não pôde ser organizado: {}'.format(exc))


def _runner(sdk):
    """Reproduce the Windows command path used by the original Ren'Py Launcher."""
    if os.name=='nt':
        pythonw=sdk/'lib'/'windows-x86_64'/'pythonw.exe'
        renpy_py=sdk/'renpy.py'
        if pythonw.is_file() and renpy_py.is_file():
            return [str(pythonw),'-EO',str(renpy_py)]
        if (sdk/'renpy.exe').is_file():
            return [str(sdk/'renpy.exe')]
    if (sdk/'renpy.sh').is_file(): return [str(sdk/'renpy.sh')]
    raise SDKError("O executável do Wells Runtime não foi encontrado.")


def _launcher_dump_file(sdk,project):
    """Match Project.get_dump_filename() from the Ren'Py 7.4.11 Launcher."""
    saves=project/'game'/'saves'
    if saves.is_dir():
        return saves/'navigation.json'
    tmp=sdk/'tmp'/project.name
    try:
        tmp.mkdir(parents=True,exist_ok=True)
        probe=tmp/'write_test.txt'
        probe.write_text('Test',encoding='utf-8')
        probe.unlink()
        return tmp/'navigation.json'
    except Exception:
        import tempfile
        return Path(tempfile.mkdtemp(prefix='wells-renpy-'))/'navigation.json'


def run(project,args,log=None):
    project=_project_root(project); args=[str(x) for x in args]; sdk=_sdk_dir()
    runner=_runner(sdk)
    command_args=[str(project)]+args
    # The original Launcher appends these flags to every project command.
    command_args += ['--json-dump',str(_launcher_dump_file(sdk,project)),'--errors-in-editor']
    cmd=runner+command_args
    if log:
        log("Ren'Py: "+' '.join(args))
        log("Modo SDK: Launcher 7.4.11 nativo (-EO renpy.py)" if '-EO' in runner else "Modo SDK: renpy.exe compatível")
    startup=None
    if os.name=='nt':
        startup=subprocess.STARTUPINFO(); startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    env=dict(os.environ)
    env.setdefault('RENPY_LAUNCHER_LANGUAGE','english')
    proc=subprocess.Popen(cmd,cwd=str(sdk),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,errors='replace',startupinfo=startup)
    output=[]
    for line in proc.stdout:
        line=line.rstrip('\r\n'); output.append(line)
        if log and line: log(line)
    code=proc.wait()
    if code:
        tail='\n'.join(output[-12:]).strip()
        raise SDKError(tail or "O Ren'Py encerrou a operação com erro (código {}).".format(code))
    return {'project':str(project),'command':args,'output':output,'runner':runner}


def generate_translations(project,language,empty=True,log=None):
    """Expose Ren'Py SDK's native Generate Translations action in the Wells panel."""
    language=_language(language,'Informe o idioma.')
    args=['translate',language]
    if language=='rot13': args.append('--rot13')
    elif language=='piglatin': args.append('--piglatin')
    elif empty: args.append('--empty')
    # Wells only replaces the SDK panel/button. Ren'Py performs the operation.
    return run(project,args,log)


def extract_string_translations(project,language,log=None,destination=None):
    language=_language(language)
    destination=Path(destination).expanduser().resolve() if destination else _strings_json(project,language)
    destination.parent.mkdir(parents=True,exist_ok=True)
    result=run(project,['extract_strings',language,str(destination)],log)
    _format_strings_json(destination)
    if log: log('Strings organizadas em: '+str(destination))
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
