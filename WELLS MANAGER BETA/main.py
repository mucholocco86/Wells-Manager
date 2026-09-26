# -*- coding: utf-8 -*-
from __future__ import annotations
import json,os,sys,threading,queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox

ROOT=Path(__file__).resolve().parent
APP_DIR=Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else ROOT
EXTRACTOR_DIR=ROOT/'Wells_Extractor'; TL_DIR=ROOT/'Wells_Translator'; REVISOR_DIR=ROOT/'Wells_Revisor'; SDK_MODULE_DIR=ROOT/'Wells_SDK'
for d in (EXTRACTOR_DIR,TL_DIR,REVISOR_DIR,SDK_MODULE_DIR):
    if str(d) not in sys.path: sys.path.insert(0,str(d))
import extractor_core
import wells_translator_core as tl_core
from wells_revisor_core import review_file
import sdk_core
import dialogue_roundtrip
APP='Wells Manager'

class WellsManager(tk.Tk):
 def __init__(self):
  super().__init__(); self.title(APP); self.geometry('940x650'); self.minsize(820,600); self.configure(bg='#222222')
  try:self.iconbitmap(str(ROOT/'wells.ico'))
  except Exception:pass
  self.events=queue.Queue(); self.busy=False; self.pending_tl=None; self.pending_session=None; self.pending_format=None; self.pending_blocks=None; self.project=None; self.project_exe=None; self.last_browse_dir=APP_DIR
  self.settings_path=APP_DIR/'Wells_Settings.json'; self.last_translation='english'
  try:
   saved=json.loads(self.settings_path.read_text(encoding='utf-8'))
   if isinstance(saved.get('last_translation'),str) and saved['last_translation'].strip():self.last_translation=saved['last_translation'].strip()
  except Exception:pass
  self.log_path=APP_DIR/'Wells_Log.txt'
  try:self.log_path.write_text('',encoding='utf-8')
  except Exception:pass
  self.status=tk.StringVar(value='Status: Nenhuma operação iniciada.'); self.project_text=tk.StringVar(value='Projeto Ren\'Py: nenhum selecionado')
  self._style(); self._build(); self.after(60,self._poll); self._log('Wells Manager iniciado.'); self._log('Ferramentas Wells carregadas. O runtime Ren\'Py será usado a partir do jogo selecionado.'); self._log('Pasta de trabalho: '+str(APP_DIR))
 def _style(self):
  s=ttk.Style(self)
  try:s.theme_use('clam')
  except Exception:pass
  s.configure('Wells.Horizontal.TProgressbar',troughcolor='#303030',background='#1595d3',bordercolor='#555555',lightcolor='#1595d3',darkcolor='#1595d3')
 def _build(self):
  tk.Label(self,text='WELLS MANAGER',bg='#222222',fg='#ff1010',font=('Segoe UI',20,'bold')).pack(pady=(10,1))
  tk.Label(self,text='Ferramentas para jogos Ren\'Py',bg='#222222',fg='#d0d0d0',font=('Segoe UI',8)).pack(pady=(0,6))
  top=tk.Frame(self,bg='#222222'); top.pack(fill='x',padx=18,pady=(0,6))
  tk.Button(top,text='Selecionar projeto',command=self.select_project,bg='#a6a6a6',fg='#101010',font=('Segoe UI',8,'bold')).pack(side='left')
  tk.Label(top,textvariable=self.project_text,bg='#222222',fg='#e0e0e0',font=('Segoe UI',9),anchor='w').pack(side='left',padx=10,fill='x',expand=True)
  body=tk.Frame(self,bg='#222222'); body.pack(fill='x',padx=12); self.buttons=[]
  self._column(body,'REN\'PY', [('Gerar traduções',self.sdk_generate),('Extrair diálogos',self.sdk_dialogue),('Eliminar persistentes',self.sdk_persistent),('Checar script (Lint)',self.sdk_lint),('Forçar recompilação',self.sdk_compile)],0)
  self._column(body,'FERRAMENTAS', [('RPYC → RPY',self.rpyc_file),('Pasta RPYC → RPY',self.rpyc_folder),('Extrair RPA',self.rpa_file),('Pasta RPA',self.rpa_folder),('Compactar RPA',self.rpa_pack)],1)
  self._column(body,'GERENCIADOR', [('TXT completo',lambda:self.tl_action('txt',False)),('TXT em blocos',lambda:self.tl_action('txt',True)),('DOCX completo',lambda:self.tl_action('docx',False)),('DOCX em blocos',lambda:self.tl_action('docx',True))],2)
  self._column(body,'REVISOR',[('Revisar TXT',lambda:self.revise('txt')),('Revisar DOCX',lambda:self.revise('docx'))],3)
  tk.Label(self,textvariable=self.status,bg='#222222',fg='#f0f0f0',font=('Segoe UI',10)).pack(fill='x',padx=30,pady=(10,4)); self.bar=ttk.Progressbar(self,style='Wells.Horizontal.TProgressbar',maximum=100,length=560); self.bar.pack()
  la=tk.Frame(self,bg='#222222',height=205); la.pack(fill='both',expand=True,padx=50,pady=(8,12)); la.pack_propagate(False)
  tk.Label(la,text='Log de atividade',bg='#222222',fg='#f0f0f0',font=('Segoe UI',10),anchor='w').pack(fill='x',pady=(0,3)); self.log=tk.Text(la,bg='#2b2b2b',fg='#eee',insertbackground='white',relief='solid',bd=1,font=('Consolas',9),state='disabled',wrap='word',padx=5,pady=4); self.log.pack(fill='both',expand=True)
 def _column(self,parent,title,items,col):
  f=tk.Frame(parent,bg='#2b2b2b',bd=1,relief='solid'); f.grid(row=0,column=col,sticky='nsew',padx=4); parent.grid_columnconfigure(col,weight=1)
  tk.Label(f,text=title,bg='#2b2b2b',fg='#ff1010',font=('Segoe UI',11,'bold')).pack(pady=(9,7))
  for text,cmd in items:
   b=tk.Button(f,text=text,command=cmd,height=1,bg='#a6a6a6',fg='#101010',activebackground='#c5c5c5',relief='raised',bd=2,font=('Segoe UI',8,'bold')); b.pack(padx=8,pady=2,fill='x'); self.buttons.append(b)
  tk.Frame(f,bg='#2b2b2b',height=6).pack()
 def _log(self,text):
  text=str(text); self.log.configure(state='normal'); self.log.insert('end',text+'\n'); self.log.see('end'); self.log.configure(state='disabled')
  try:
   with self.log_path.open('a',encoding='utf-8',newline='\n') as f:f.write(text+'\n')
  except Exception:pass
 def _save_last_translation(self):
  try:self.settings_path.write_text(json.dumps({'last_translation':self.last_translation},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  except Exception:pass
 def _set_busy(self,v):
  self.busy=v
  for b in self.buttons:b.configure(state='disabled' if v else 'normal')
 def _progress(self,value,text=None,log=None):self.events.put(('progress',value,text,log))
 def _status_cb(self,text):self.events.put(('status',text))
 def _log_cb(self,text):self.events.put(('log',text))
 def _run(self,label,worker,done=None):
  if self.busy:return
  self._set_busy(True); self.bar['value']=0; self.status.set('Status: '+label)
  def go():
   try:self.events.put(('done',worker(),done))
   except Exception as e:self.events.put(('error',e))
  threading.Thread(target=go,daemon=True).start()
 def _poll(self):
  try:
   while True:
    e=self.events.get_nowait(); k=e[0]
    if k=='progress':
     _,v,t,l=e; self.bar['value']=v
     if t:self.status.set('Status: '+t)
     if l:self._log(l)
    elif k=='status':self.status.set('Status: '+e[1])
    elif k=='log':self._log(e[1])
    elif k=='done':
     _,r,cb=e; self._set_busy(False); self.bar['value']=100
     if cb:cb(r)
    elif k=='error':self._set_busy(False); self.status.set('Status: Erro.'); self._log('[ERRO] '+str(e[1])); messagebox.showerror(APP,str(e[1]))
  except queue.Empty:pass
  self.after(60,self._poll)
 def _browse_initialdir(self):
  p=Path(self.last_browse_dir)
  while not p.is_dir() and p.parent!=p:p=p.parent
  return str(p if p.is_dir() else APP_DIR)
 def _askdirectory(self,**kwargs):
  kwargs.setdefault('initialdir',self._browse_initialdir()); value=filedialog.askdirectory(**kwargs)
  if value:self.last_browse_dir=Path(value).resolve()
  return value
 def _askopenfilenames(self,**kwargs):
  kwargs.setdefault('initialdir',self._browse_initialdir()); values=filedialog.askopenfilenames(**kwargs)
  if values:self.last_browse_dir=Path(values[0]).resolve().parent
  return values
 def _askopenfilename(self,**kwargs):
  kwargs.setdefault('initialdir',self._browse_initialdir()); value=filedialog.askopenfilename(**kwargs)
  if value:self.last_browse_dir=Path(value).resolve().parent
  return value
 def _asksaveasfilename(self,**kwargs):
  kwargs.setdefault('initialdir',self._browse_initialdir()); value=filedialog.asksaveasfilename(**kwargs)
  if value:self.last_browse_dir=Path(value).resolve().parent
  return value
 def select_project(self):
  selected=self._askopenfilename(title="Selecione o executável do jogo Ren'Py",filetypes=[("Jogo Ren'Py",'*.exe'),('Executável','*.exe')])
  if not selected:return False
  try:runtime=sdk_core.select_game(selected)
  except Exception as exc:messagebox.showerror(APP,str(exc)); self._log('[ERRO] '+str(exc)); return False
  self.project=runtime['root']; self.project_exe=runtime['game_exe']; self.project_text.set("Projeto Ren'Py: "+self.project.name)
  self._log('Projeto: '+self.project.name); self._log('Executável: '+self.project_exe.name); self._log("Runtime do jogo: lib/{} ({}, {})".format(runtime['layout'],runtime['generation'],runtime['architecture'])); return True
 def _need_project(self):return bool(self.project or self.select_project())
 def _sdk(self,title,func,done='Operação concluída.'):
  if not self._need_project():return
  self._log('=== '+title.upper()+' ==='); self._log('Projeto: '+self.project.name)
  def w():return func(self.project,log=self._log_cb)
  def d(r):self.status.set('Status: '+done); self._log('[OK] '+done)
  self._run(title+'...',w,d)
 def sdk_generate(self):
  if not self._need_project():return
  win=tk.Toplevel(self); win.title('Gerar Traduções'); win.resizable(False,False); win.configure(bg='#222222'); win.transient(self); win.grab_set(); lang=tk.StringVar(value=self.last_translation); empty=tk.BooleanVar(value=True)
  tk.Label(win,text='Idioma',bg='#222',fg='white').grid(row=0,column=0,padx=12,pady=(12,5),sticky='w'); tk.Entry(win,textvariable=lang,width=25).grid(row=0,column=1,padx=12,pady=(12,5)); tk.Checkbutton(win,text='Gerar strings vazias',variable=empty,bg='#222',fg='white',selectcolor='#333',activebackground='#222',activeforeground='white').grid(row=1,column=0,columnspan=2,padx=12,sticky='w')
  def go(kind):
   l=lang.get().strip()
   if not l:return messagebox.showerror(APP,'Informe o idioma.',parent=win)
   self.last_translation=l; self._save_last_translation(); win.destroy()
   funcs={'generate':lambda p,log:sdk_core.generate_translations(p,l,empty.get(),log),'extract':lambda p,log:sdk_core.extract_string_translations(p,l,log),'merge':lambda p,log:sdk_core.merge_string_translations(p,l,False,log),'replace':lambda p,log:sdk_core.merge_string_translations(p,l,True,log),'reverse':lambda p,log:sdk_core.reverse_language(p,l,log)}
   names={'generate':'Gerar traduções','extract':'Extrair strings','merge':'Mesclar strings','replace':'Mesclar/substituir strings','reverse':'Inverter idioma'}; self._sdk(names[kind],funcs[kind])
  bf=tk.Frame(win,bg='#222'); bf.grid(row=2,column=0,columnspan=2,padx=10,pady=12)
  for i,(t,k) in enumerate([('Gerar','generate'),('Extrair strings','extract'),('Mesclar','merge'),('Substituir','replace'),('Inverter','reverse')]):tk.Button(bf,text=t,command=lambda x=k:go(x),width=14).grid(row=i//2,column=i%2,padx=3,pady=3)
 def sdk_dialogue(self):
  if not self._need_project():return
  win=tk.Toplevel(self); win.title('Extrair / Reinjetar Diálogos'); win.resizable(False,False); win.configure(bg='#222'); win.transient(self); win.grab_set()
  lang=tk.StringVar(value=self.last_translation); strings=tk.BooleanVar(value=True)
  tk.Label(win,text='Idioma da tradução',bg='#222',fg='white').grid(row=0,column=0,padx=12,pady=(12,5),sticky='w'); tk.Entry(win,textvariable=lang,width=24).grid(row=0,column=1,padx=12,pady=(12,5))
  tk.Checkbutton(win,text='Incluir strings traduzíveis (menus, botões etc.)',variable=strings,bg='#222',fg='white',selectcolor='#333',activebackground='#222',activeforeground='white').grid(row=1,column=0,columnspan=2,padx=12,pady=3,sticky='w')
  tk.Label(win,text='Fluxo Wells: clique uma vez para extrair e novamente, após traduzir, para reinjetar.',bg='#222',fg='#d0d0d0',wraplength=430,justify='left').grid(row=2,column=0,columnspan=2,padx=12,pady=(6,4),sticky='w')
  def wells(fmt):
   map_path=APP_DIR/dialogue_roundtrip.TEMP_DIR_NAME/dialogue_roundtrip.MAP_NAME
   if map_path.is_file():
    try:info=json.loads(map_path.read_text(encoding='utf-8'))
    except Exception as exc:return messagebox.showerror(APP,'Mapa Wells inválido: '+str(exc),parent=win)
    if info.get('format')!=fmt:return messagebox.showerror(APP,'Existe um fluxo {} pendente. Finalize-o pelo mesmo botão antes de iniciar outro.'.format(str(info.get('format','')).upper()),parent=win)
    document=APP_DIR/info.get('document','')
    if not document.is_file():return messagebox.showerror(APP,'Documento do fluxo pendente não foi encontrado: '+str(document),parent=win)
    win.destroy(); self._log('=== REINJETAR DIÁLOGOS WELLS {} ==='.format(fmt.upper()))
    def w():return dialogue_roundtrip.inject(self.project,document,log=self._log_cb,progress=lambda v,t=None:self._progress(v,t))
    def d(r):self.status.set('Status: Reinjeção Wells concluída.'); self._log('[OK] {} registros reinjetados em {} arquivos TL.'.format(r['entries'],r['files']))
    self._run('Validando e reinjetando diálogos...',w,d); return
   l=lang.get().strip()
   if not l:return messagebox.showerror(APP,'Informe o idioma da tradução.',parent=win)
   self.last_translation=l; self._save_last_translation(); include=strings.get(); win.destroy(); self._log('=== EXTRAIR DIÁLOGOS WELLS {} ==='.format(fmt.upper()))
   def w():return dialogue_roundtrip.prepare(self.project,l,fmt=fmt,output_dir=APP_DIR,include_strings=include,log=self._log_cb,progress=lambda v,t=None:self._progress(v,t))
   def d(r):self.status.set('Status: Documento Wells pronto; aguardando tradução.'); self._log('[OK] {} registros. Documento: {}'.format(r['entries'],Path(r['document']).name)); self._log('[OK] Mapa físico temporário: '+r['map'])
   self._run('Preparando diálogo Wells...',w,d)
  tk.Button(win,text='TXT Wells',command=lambda:wells('txt'),width=18).grid(row=3,column=0,padx=8,pady=8)
  tk.Button(win,text='DOCX Wells',command=lambda:wells('docx'),width=18).grid(row=3,column=1,padx=8,pady=8)
  tk.Label(win,text='Exportação técnica original do SDK',bg='#222',fg='#d0d0d0').grid(row=4,column=0,columnspan=2,pady=(8,2))
  def raw(fmt):
   include=strings.get(); l=lang.get().strip();
   if l:self.last_translation=l; self._save_last_translation()
   win.destroy(); self._sdk('Extrair diálogos '+fmt.upper(),lambda p,log:sdk_core.extract_dialogue(p,fmt,include,False,False,log),'Diálogos {} extraídos.'.format(fmt.upper()))
  tk.Button(win,text='TAB original',command=lambda:raw('tab'),width=18).grid(row=5,column=0,padx=8,pady=(2,12))
  tk.Button(win,text='TXT original',command=lambda:raw('txt'),width=18).grid(row=5,column=1,padx=8,pady=(2,12))
 def sdk_persistent(self):
  if not self._need_project():return
  if messagebox.askyesno(APP,'Eliminar os dados persistentes deste projeto?'):self._sdk('Eliminar dados persistentes',sdk_core.delete_persistent,'Dados persistentes eliminados.')
 def sdk_lint(self):self._sdk('Checar script (Lint)',sdk_core.lint,'Checagem concluída.') if self._need_project() else None
 def sdk_compile(self):self._sdk('Forçar recompilação',sdk_core.force_recompile,'Recompilação concluída.') if self._need_project() else None
 # Wells Extractor
 def rpyc_file(self):
  fs=self._askopenfilenames(title='Selecionar RPYC/RPYMC',filetypes=[("Ren'Py compilado",'*.rpyc *.rpymc'),('Todos','*.*')])
  if fs:
   ps=[Path(x) for x in fs]; base=Path(os.path.commonpath([str(p.parent) for p in ps])).resolve(); self._extract_rpyc(ps,base,base.name)
 def rpyc_folder(self):
  d=self._askdirectory(title='Selecionar pasta contendo RPYC/RPYMC')
  if d:
   f=Path(d).resolve(); self._extract_rpyc([p for p in f.rglob('*') if p.suffix.lower() in ('.rpyc','.rpymc')],f,f.name)
 def _extract_rpyc(self,files,display_root=None,root_name=None):
  self._log('=== RPYC → RPY ==='); self._log('Raiz: '+str(root_name)); self._log('Arquivos: '+str(len(files)))
  def w():return extractor_core.decompile_rpyc_files(files,lambda v:self._progress(v),self._log_cb,self._status_cb,display_root=display_root)
  def d(r):self.status.set('Status: Decompilação concluída.'); self._log('[OK] {}, ignorados: {}, erros: {}'.format(r['ok'],r['skipped'],r['errors']))
  self._run('Preparando descompilação...',w,d)
 def rpa_file(self):
  fs=self._askopenfilenames(title='Selecionar arquivos RPA',filetypes=[("Ren'Py Archive",'*.rpa')])
  if fs:
   ps=[Path(x).resolve() for x in fs]; base=Path(os.path.commonpath([str(p.parent) for p in ps])).resolve(); self._extract_rpa(ps,base,base.name)
 def rpa_folder(self):
  d=self._askdirectory(title='Selecionar pasta contendo RPA')
  if d:
   f=Path(d).resolve(); self._extract_rpa([p for p in f.rglob('*.rpa') if p.is_file()],f,f.name)
 def _extract_rpa(self,files,display_root=None,root_name=None):
  self._log('=== EXTRAIR RPA ==='); self._log('Raiz: '+str(root_name)); self._log('Arquivos RPA: '+str(len(files)))
  def w():return extractor_core.extract_rpa_archives(files,lambda v:self._progress(v),self._log_cb,self._status_cb,display_root=display_root)
  def d(r):self.status.set('Status: Extração RPA concluída.'); self._log('[OK] Extraídos: {}; RPA: {}; erros: {}'.format(r['extracted'],r['archives'],r['errors']))
  self._run('Preparando extração RPA...',w,d)
 def rpa_pack(self):
  selected=[Path(x).resolve() for x in self._askopenfilenames(title='Selecionar arquivos para compactar em RPA',filetypes=[('Todos','*.*')])]
  if selected:base=Path(os.path.commonpath([str(p.parent) for p in selected])).resolve()
  else:
   folder=self._askdirectory(title='Selecionar pasta para compactar em RPA')
   if not folder:return
   selected=[Path(folder).resolve()]; base=selected[0].parent
  output=self._asksaveasfilename(title='Salvar RPA',defaultextension='.rpa',filetypes=[("Ren'Py Archive",'*.rpa')])
  if not output:return
  op=Path(output).resolve(); entries={}; self._log('=== COMPACTAR RPA ===')
  for sp in selected:
   for rp in ([p for p in sp.rglob('*') if p.is_file()] if sp.is_dir() else [sp]):
    if rp!=op:entries[rp.relative_to(base).as_posix()]=rp
  fe=sorted(entries.items(),key=lambda x:x[0].lower())
  if not fe:return messagebox.showinfo(APP,'A seleção não contém arquivos.')
  def w():return extractor_core.pack_rpa(fe,op,lambda v:self._progress(v),self._log_cb,self._status_cb)
  def d(r):self.status.set('Status: Compactação RPA concluída.'); self._log('[OK] {} arquivos → {}'.format(r['compacted'],Path(r['output']).name))
  self._run('Preparando compactação RPA...',w,d)
 # TL Manager
 def _choose_tl(self):return self._askdirectory(title='Selecione a pasta de tradução dentro de game/tl') or None
 def tl_action(self,fmt,blocks):
  if self.pending_tl and self.pending_format==fmt and self.pending_blocks==blocks:return self.tl_inject()
  if self.pending_tl:return messagebox.showinfo(APP,'Existe uma extração aguardando tradução. Use o mesmo botão que iniciou essa extração para devolvê-la ao jogo.')
  return self.tl_export(fmt,blocks)
 def tl_export(self,fmt,blocks):
  tl=self._choose_tl()
  if not tl:return
  self._log('=== EXTRAIR {} ==='.format(fmt.upper())); self._log('Raiz: '+Path(tl).name)
  def prog(v,t=None):self._progress(v,t)
  def w():
   if fmt=='txt':return (tl_core.export_blocks if blocks else tl_core.export_full)(tl,APP_DIR,return_session=True,progress=prog)
   return (tl_core.export_blocks_docx if blocks else tl_core.export_full_docx)(tl,APP_DIR,return_session=True,progress=prog)
  def d(r):
   if blocks:output,count,nblocks,session=r; self._log('[OK] {} registros / {} blocos.'.format(count,nblocks))
   else:output,count,session=r; self._log('[OK] {} registros.'.format(count))
   self.pending_tl=tl; self.pending_session=session; self.pending_format=fmt; self.pending_blocks=blocks; self.status.set('Status: Extração concluída; aguardando tradução. Clique no mesmo botão para reinjetar.')
  self._run('Extraindo {}...'.format(fmt.upper()),w,d)
 def tl_inject(self):
  tl=self.pending_tl
  if not tl:return messagebox.showerror(APP,'Nenhuma extração desta sessão está aguardando reinjeção.')
  fmt=self.pending_format
  def prog(v,t=None):self._progress(v,t)
  def w():return (tl_core.inject_docx_translations if fmt=='docx' else tl_core.inject_translations)(tl,APP_DIR,session=self.pending_session,progress=prog)
  def d(r):count,mode=r; self.status.set('Status: {} traduções injetadas.'.format(count)); self._log('[OK] Injeção: {} registros ({}).'.format(count,mode)); self.pending_tl=self.pending_session=self.pending_format=self.pending_blocks=None
  self._run('Validando e injetando traduções...',w,d)
 def revise(self,fmt):
  types=[('Documento TXT','*.txt')] if fmt=='txt' else [('Documento Word','*.docx')]; p=self._askopenfilename(title='Selecione o documento para revisar',filetypes=types+[('Todos','*.*')])
  if not p:return
  self._log('=== REVISOR {} ==='.format(fmt.upper())); self._log('Documento: '+Path(p).name)
  def prog(v,text=None,log=None):self._progress(v,text,log)
  def w():return review_file(Path(p),REVISOR_DIR,progress=prog)
  def d(r):self.status.set('Status: {} linhas revisadas.'.format(r['records'])); self._log('[OK] Linhas alteradas: {}.'.format(r['changed'])); self._log('[OK] Tokens preservados: {}.'.format(r['tokens'])); self._log('[OK] Saída: {}'.format(Path(r['output']).name))
  self._run('Preparando revisão...',w,d)
if __name__=='__main__':WellsManager().mainloop()
