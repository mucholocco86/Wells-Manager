# -*- coding: utf-8 -*-
from __future__ import annotations
import os,sys,threading,queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,simpledialog

ROOT=Path(__file__).resolve().parent
EXTRACTOR_DIR=ROOT/'Wells_Extractor'; TL_DIR=ROOT/'Wells_Translator'; REVISOR_DIR=ROOT/'Wells_Revisor'; SDK_MODULE_DIR=ROOT/'Wells_SDK'
for d in (EXTRACTOR_DIR,TL_DIR,REVISOR_DIR,SDK_MODULE_DIR):
    if str(d) not in sys.path: sys.path.insert(0,str(d))
import extractor_core
import wells_translator_core as tl_core
from wells_revisor_core import review_file
import sdk_core
APP='Wells Manager'

class WellsManager(tk.Tk):
 def __init__(self):
  super().__init__(); self.title(APP); self.geometry('940x650'); self.minsize(820,600); self.configure(bg='#222222')
  try:self.iconbitmap(str(ROOT/'wells.ico'))
  except Exception:pass
  self.events=queue.Queue(); self.busy=False; self.pending_tl=None; self.pending_session=None; self.pending_format=None; self.project=None
  self.status=tk.StringVar(value='Status: Nenhuma operação iniciada.'); self.project_text=tk.StringVar(value='Projeto Ren\'Py: nenhum selecionado')
  self._style(); self._build(); self.after(60,self._poll); self._log('Wells Manager iniciado.'); self._log('Ferramentas Wells e núcleo Ren\'Py carregados.')
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
  self._column(body,'FERRAMENTAS', [('RPYC → RPY',self.rpyc_file),('Pasta RPYC → RPY',self.rpyc_folder),('Extrair RPA',self.rpa_file),('Pasta RPA',self.rpa_folder),('Compactar RPA',self.rpa_pack)],0)
  self._column(body,'REN\'PY', [('Gerar traduções',self.sdk_generate),('Extrair diálogos',self.sdk_dialogue),('Eliminar persistentes',self.sdk_persistent),('Checar script (Lint)',self.sdk_lint),('Forçar recompilação',self.sdk_compile)],1)
  self._column(body,'GERENCIADOR', [('TXT completo',lambda:self.tl_export('txt',False)),('TXT em blocos',lambda:self.tl_export('txt',True)),('DOCX completo',lambda:self.tl_export('docx',False)),('DOCX em blocos',lambda:self.tl_export('docx',True)),('Injetar tradução',self.tl_inject)],2)
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
 def _log(self,text): self.log.configure(state='normal'); self.log.insert('end',str(text)+'\n'); self.log.see('end'); self.log.configure(state='disabled')
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
 def select_project(self):
  d=filedialog.askdirectory(title="Selecione a pasta principal do jogo Ren'Py")
  if not d:return False
  p=Path(d).resolve(); p=p.parent if p.name.lower()=='game' else p
  if not (p/'game').is_dir():messagebox.showerror(APP,"A pasta selecionada não contém a pasta 'game'."); return False
  self.project=p; self.project_text.set("Projeto Ren'Py: "+p.name); self._log('Projeto: '+p.name); return True
 def _need_project(self):return bool(self.project or self.select_project())
 def _sdk(self,title,func,done='Operação concluída.'):
  if not self._need_project():return
  self._log('=== '+title.upper()+' ==='); self._log('Projeto: '+self.project.name)
  def w():return func(self.project,log=self._log_cb)
  def d(r):self.status.set('Status: '+done); self._log('[OK] '+done)
  self._run(title+'...',w,d)
 def sdk_generate(self):
  if not self._need_project():return
  win=tk.Toplevel(self); win.title('Gerar Traduções'); win.resizable(False,False); win.configure(bg='#222222'); win.transient(self); win.grab_set(); lang=tk.StringVar(); empty=tk.BooleanVar(value=True)
  tk.Label(win,text='Idioma',bg='#222',fg='white').grid(row=0,column=0,padx=12,pady=(12,5),sticky='w'); tk.Entry(win,textvariable=lang,width=25).grid(row=0,column=1,padx=12,pady=(12,5)); tk.Checkbutton(win,text='Gerar strings vazias',variable=empty,bg='#222',fg='white',selectcolor='#333',activebackground='#222',activeforeground='white').grid(row=1,column=0,columnspan=2,padx=12,sticky='w')
  def go(kind):
   l=lang.get().strip()
   if not l:return messagebox.showerror(APP,'Informe o idioma.',parent=win)
   win.destroy()
   funcs={'generate':lambda p,log:sdk_core.generate_translations(p,l,empty.get(),log),'extract':lambda p,log:sdk_core.extract_string_translations(p,l,log),'merge':lambda p,log:sdk_core.merge_string_translations(p,l,False,log),'replace':lambda p,log:sdk_core.merge_string_translations(p,l,True,log),'reverse':lambda p,log:sdk_core.reverse_language(p,l,log)}
   names={'generate':'Gerar traduções','extract':'Extrair strings','merge':'Mesclar strings','replace':'Mesclar/substituir strings','reverse':'Inverter idioma'}; self._sdk(names[kind],funcs[kind])
  bf=tk.Frame(win,bg='#222'); bf.grid(row=2,column=0,columnspan=2,padx=10,pady=12)
  for i,(t,k) in enumerate([('Gerar','generate'),('Extrair strings','extract'),('Mesclar','merge'),('Substituir','replace'),('Inverter','reverse')]):tk.Button(bf,text=t,command=lambda x=k:go(x),width=14).grid(row=i//2,column=i%2,padx=3,pady=3)
 def sdk_dialogue(self):
  if not self._need_project():return
  win=tk.Toplevel(self); win.title('Extrair Diálogos'); win.resizable(False,False); win.configure(bg='#222'); win.transient(self); win.grab_set(); fmt=tk.StringVar(value='tab'); strings=tk.BooleanVar(); notags=tk.BooleanVar(); escape=tk.BooleanVar()
  for text,val in [('Planilha TAB (dialogue.tab)','tab'),('Texto (dialogue.txt)','txt')]:tk.Radiobutton(win,text=text,value=val,variable=fmt,bg='#222',fg='white',selectcolor='#333',activebackground='#222',activeforeground='white').pack(anchor='w',padx=15,pady=3)
  for text,var in [('Extrair todas as strings traduzíveis',strings),('Remover tags de texto',notags),('Escapar caracteres especiais',escape)]:tk.Checkbutton(win,text=text,variable=var,bg='#222',fg='white',selectcolor='#333',activebackground='#222',activeforeground='white').pack(anchor='w',padx=15,pady=3)
  def go():
   f=fmt.get(); s=strings.get(); n=notags.get(); e=escape.get(); win.destroy(); self._sdk('Extrair diálogos',lambda p,log:sdk_core.extract_dialogue(p,f,s,n,e,log),'Diálogos extraídos.')
  tk.Button(win,text='Extrair',command=go,width=18).pack(pady=12)
 def sdk_persistent(self):
  if not self._need_project():return
  if messagebox.askyesno(APP,'Eliminar os dados persistentes deste projeto?'):self._sdk('Eliminar dados persistentes',sdk_core.delete_persistent,'Dados persistentes eliminados.')
 def sdk_lint(self):self._sdk('Checar script (Lint)',sdk_core.lint,'Checagem concluída.') if self._need_project() else None
 def sdk_compile(self):self._sdk('Forçar recompilação',sdk_core.force_recompile,'Recompilação concluída.') if self._need_project() else None
 # Wells Extractor
 def rpyc_file(self):
  fs=filedialog.askopenfilenames(title='Selecionar RPYC/RPYMC',filetypes=[("Ren'Py compilado",'*.rpyc *.rpymc'),('Todos','*.*')])
  if fs:
   ps=[Path(x) for x in fs]; base=Path(os.path.commonpath([str(p.parent) for p in ps])).resolve(); self._extract_rpyc(ps,base,base.name)
 def rpyc_folder(self):
  d=filedialog.askdirectory(title='Selecionar pasta contendo RPYC/RPYMC')
  if d:
   f=Path(d).resolve(); self._extract_rpyc([p for p in f.rglob('*') if p.suffix.lower() in ('.rpyc','.rpymc')],f,f.name)
 def _extract_rpyc(self,files,display_root=None,root_name=None):
  self._log('=== RPYC → RPY ==='); self._log('Raiz: '+str(root_name)); self._log('Arquivos: '+str(len(files)))
  def w():return extractor_core.decompile_rpyc_files(files,lambda v:self._progress(v),self._log_cb,self._status_cb,display_root=display_root)
  def d(r):self.status.set('Status: Decompilação concluída.'); self._log('[OK] {}, ignorados: {}, erros: {}'.format(r['ok'],r['skipped'],r['errors']))
  self._run('Preparando descompilação...',w,d)
 def rpa_file(self):
  fs=filedialog.askopenfilenames(title='Selecionar arquivos RPA',filetypes=[("Ren'Py Archive",'*.rpa')])
  if fs:
   ps=[Path(x).resolve() for x in fs]; base=Path(os.path.commonpath([str(p.parent) for p in ps])).resolve(); self._extract_rpa(ps,base,base.name)
 def rpa_folder(self):
  d=filedialog.askdirectory(title='Selecionar pasta contendo RPA')
  if d:
   f=Path(d).resolve(); self._extract_rpa([p for p in f.rglob('*.rpa') if p.is_file()],f,f.name)
 def _extract_rpa(self,files,display_root=None,root_name=None):
  self._log('=== EXTRAIR RPA ==='); self._log('Raiz: '+str(root_name)); self._log('Arquivos RPA: '+str(len(files)))
  def w():return extractor_core.extract_rpa_archives(files,lambda v:self._progress(v),self._log_cb,self._status_cb,display_root=display_root)
  def d(r):self.status.set('Status: Extração RPA concluída.'); self._log('[OK] Extraídos: {}; RPA: {}; erros: {}'.format(r['extracted'],r['archives'],r['errors']))
  self._run('Preparando extração RPA...',w,d)
 def rpa_pack(self):
  selected=[Path(x).resolve() for x in filedialog.askopenfilenames(title='Selecionar arquivos para compactar em RPA',filetypes=[('Todos','*.*')])]
  if selected:base=Path(os.path.commonpath([str(p.parent) for p in selected])).resolve()
  else:
   folder=filedialog.askdirectory(title='Selecionar pasta para compactar em RPA')
   if not folder:return
   selected=[Path(folder).resolve()]; base=selected[0].parent
  output=filedialog.asksaveasfilename(title='Salvar RPA',defaultextension='.rpa',filetypes=[("Ren'Py Archive",'*.rpa')])
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
 def _choose_tl(self):return filedialog.askdirectory(title='Selecione a pasta de tradução dentro de game/tl') or None
 def tl_export(self,fmt,blocks):
  tl=self._choose_tl()
  if not tl:return
  self._log('=== EXTRAIR {} ==='.format(fmt.upper())); self._log('Raiz: '+Path(tl).name)
  def prog(v,t=None):self._progress(v,t)
  def w():
   if fmt=='txt':return (tl_core.export_blocks if blocks else tl_core.export_full)(tl,ROOT,return_session=True,progress=prog)
   return (tl_core.export_blocks_docx if blocks else tl_core.export_full_docx)(tl,ROOT,return_session=True,progress=prog)
  def d(r):
   if blocks:output,count,nblocks,session=r; self._log('[OK] {} registros / {} blocos.'.format(count,nblocks))
   else:output,count,session=r; self._log('[OK] {} registros.'.format(count))
   self.pending_tl=tl; self.pending_session=session; self.pending_format=fmt; self.status.set('Status: Extração concluída; aguardando tradução.')
  self._run('Extraindo {}...'.format(fmt.upper()),w,d)
 def tl_inject(self):
  tl=self.pending_tl or self._choose_tl()
  if not tl:return
  fmt=self.pending_format
  if fmt is None:
   hd=(ROOT/'old.docx').exists() or any(ROOT.glob('old_*.docx')); ht=(ROOT/'old.txt').exists() or any(ROOT.glob('old_*.txt'))
   if hd and not ht:fmt='docx'
   elif ht and not hd:fmt='txt'
   else:return messagebox.showerror(APP,'Não foi possível determinar TXT ou DOCX.')
  def prog(v,t=None):self._progress(v,t)
  def w():return (tl_core.inject_docx_translations if fmt=='docx' else tl_core.inject_translations)(tl,ROOT,session=self.pending_session,progress=prog)
  def d(r):count,mode=r; self.status.set('Status: {} traduções injetadas.'.format(count)); self._log('[OK] Injeção: {} registros ({}).'.format(count,mode)); self.pending_tl=self.pending_session=self.pending_format=None
  self._run('Validando e injetando traduções...',w,d)
 def revise(self,fmt):
  types=[('Documento TXT','*.txt')] if fmt=='txt' else [('Documento Word','*.docx')]; p=filedialog.askopenfilename(title='Selecione o documento para revisar',filetypes=types+[('Todos','*.*')])
  if not p:return
  self._log('=== REVISOR {} ==='.format(fmt.upper())); self._log('Documento: '+Path(p).name)
  def prog(v,text=None,log=None):self._progress(v,text,log)
  def w():return review_file(Path(p),REVISOR_DIR,progress=prog)
  def d(r):self.status.set('Status: {} linhas revisadas.'.format(r['records'])); self._log('[OK] Linhas alteradas: {}.'.format(r['changed'])); self._log('[OK] Tokens preservados: {}.'.format(r['tokens'])); self._log('[OK] Saída: {}'.format(Path(r['output']).name))
  self._run('Preparando revisão...',w,d)
if __name__=='__main__':WellsManager().mainloop()
