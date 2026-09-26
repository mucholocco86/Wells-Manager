# -*- coding: utf-8 -*-
from __future__ import annotations
import os, sys, threading, queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ROOT=Path(__file__).resolve().parent
EXTRACTOR_DIR=ROOT/'Wells_Extractor'; TL_DIR=ROOT/'Wells_Translator'; REVISOR_DIR=ROOT/'Wells_Revisor'
for d in (EXTRACTOR_DIR,TL_DIR,REVISOR_DIR):
    if str(d) not in sys.path: sys.path.insert(0,str(d))
import extractor_core
import wells_translator_core as tl_core
from wells_revisor_core import review_file

APP='Wells Manager'

class WellsManager(tk.Tk):
    def __init__(self):
        super().__init__(); self.title(APP); self.geometry('700x520'); self.minsize(700,520); self.configure(bg='#222222')
        try: self.iconbitmap(str(ROOT/'wells.ico'))
        except Exception: pass
        self.events=queue.Queue(); self.busy=False; self.pending_tl=None; self.pending_session=None; self.pending_format=None
        self.status=tk.StringVar(value='Status: Nenhuma operação iniciada.')
        self._style(); self._build(); self.after(60,self._poll)
        self._log('Wells Manager iniciado.')
        self._log('Extractor, TL Manager e Revisor carregados em módulos independentes.')

    def _style(self):
        s=ttk.Style(self)
        try:s.theme_use('clam')
        except Exception:pass
        s.configure('Wells.Horizontal.TProgressbar',troughcolor='#303030',background='#1595d3',bordercolor='#555555',lightcolor='#1595d3',darkcolor='#1595d3')

    def _build(self):
        tk.Label(self,text='WELLS MANAGER',bg='#222222',fg='#ff1010',font=('Segoe UI',20,'bold')).pack(pady=(10,2))
        tk.Label(self,text='Ferramentas Ren\'Py em uma única interface',bg='#222222',fg='#d0d0d0',font=('Segoe UI',8)).pack(pady=(0,8))
        body=tk.Frame(self,bg='#222222'); body.pack(fill='x',padx=12)
        self.buttons=[]
        self._column(body,'FERRAMENTAS',[
            ('📄  RPYC → RPY',self.rpyc_file),('📁  Pasta RPYC → RPY',self.rpyc_folder),
            ('📦  Extrair RPA',self.rpa_file),('📁  Pasta RPA',self.rpa_folder),('📦  Compactar RPA',self.rpa_pack)],0)
        self._column(body,'GERENCIADOR',[
            ('📄  TXT completo',lambda:self.tl_export('txt',False)),('📁  TXT em blocos',lambda:self.tl_export('txt',True)),
            ('📄  DOCX completo',lambda:self.tl_export('docx',False)),('📁  DOCX em blocos',lambda:self.tl_export('docx',True)),
            ('💉  Injetar tradução',self.tl_inject)],1)
        self._column(body,'REVISOR',[
            ('📄  Revisar TXT',lambda:self.revise('txt')),('📄  Revisar DOCX',lambda:self.revise('docx'))],2)
        tk.Label(self,textvariable=self.status,bg='#222222',fg='#f0f0f0',font=('Segoe UI',10),anchor='center').pack(fill='x',padx=30,pady=(10,4))
        self.bar=ttk.Progressbar(self,style='Wells.Horizontal.TProgressbar',mode='determinate',maximum=100,length=430); self.bar.pack()
        log_area=tk.Frame(self,bg='#222222',width=460,height=158)
        log_area.pack(pady=(8,10))
        log_area.pack_propagate(False)
        tk.Label(log_area,text='Log de atividade',bg='#222222',fg='#f0f0f0',font=('Segoe UI',10),anchor='w').pack(fill='x',pady=(0,3))
        self.log=tk.Text(log_area,bg='#2b2b2b',fg='#eeeeee',insertbackground='white',relief='solid',bd=1,font=('Consolas',9),state='disabled',wrap='word',padx=5,pady=4)
        self.log.pack(fill='both',expand=True)

    def _column(self,parent,title,items,col):
        f=tk.Frame(parent,bg='#2b2b2b',bd=1,relief='solid'); f.grid(row=0,column=col,sticky='nsew',padx=4); parent.grid_columnconfigure(col,weight=1)
        tk.Label(f,text=title,bg='#2b2b2b',fg='#ff1010',font=('Segoe UI',11,'bold')).pack(pady=(9,7))
        for text,cmd in items:
            b=tk.Button(f,text=text,command=cmd,width=20,height=1,bg='#a6a6a6',fg='#101010',activebackground='#c5c5c5',relief='raised',bd=2,font=('Segoe UI',8,'bold'),anchor='w',padx=6)
            b.pack(padx=8,pady=2,fill='x'); self.buttons.append(b)
        tk.Frame(f,bg='#2b2b2b',height=6).pack()

    def _log(self,text):
        self.log.configure(state='normal'); self.log.insert('end',str(text)+'\n'); self.log.see('end'); self.log.configure(state='disabled')
    def _set_busy(self,v):
        self.busy=v
        for b in self.buttons:b.configure(state='disabled' if v else 'normal')
    def _progress(self,value,text=None,log=None): self.events.put(('progress',value,text,log))
    def _status_cb(self,text): self.events.put(('status',text))
    def _log_cb(self,text): self.events.put(('log',text))
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
                e=self.events.get_nowait(); kind=e[0]
                if kind=='progress':
                    _,v,t,l=e; self.bar['value']=v
                    if t:self.status.set('Status: '+t)
                    if l:self._log(l)
                elif kind=='status':self.status.set('Status: '+e[1])
                elif kind=='log':self._log(e[1])
                elif kind=='done':
                    _,result,cb=e; self._set_busy(False); self.bar['value']=100
                    if cb:cb(result)
                elif kind=='error':
                    self._set_busy(False); self.status.set('Status: Erro.'); self._log('[ERRO] '+str(e[1])); messagebox.showerror(APP,str(e[1]))
        except queue.Empty:pass
        self.after(60,self._poll)

    # Extractor
    def rpyc_file(self):
        fs=filedialog.askopenfilenames(title='Selecionar arquivos RPYC/RPYMC',filetypes=[('Ren\'Py compilado','*.rpyc *.rpymc'),('Todos','*.*')])
        if fs:
            paths=[Path(x) for x in fs]
            base=Path(os.path.commonpath([str(p.parent) for p in paths])).resolve()
            self._extract_rpyc(paths,display_root=base,root_name=base.name)
    def rpyc_folder(self):
        d=filedialog.askdirectory(title='Selecionar pasta contendo RPYC/RPYMC')
        if d:
            folder=Path(d).resolve()
            self._extract_rpyc([p for p in folder.rglob('*') if p.suffix.lower() in ('.rpyc','.rpymc')],display_root=folder,root_name=folder.name)
    def _extract_rpyc(self,files,display_root=None,root_name=None):
        self._log('=== RPYC → RPY ===')
        if root_name:self._log('Raiz: '+root_name)
        self._log('Arquivos: '+str(len(files)))
        def w():return extractor_core.decompile_rpyc_files(files,lambda v:self._progress(v),self._log_cb,self._status_cb,display_root=display_root)
        def d(r):self.status.set('Status: Decompilação concluída.'); self._log('[OK] {}, ignorados: {}, erros: {}'.format(r['ok'],r['skipped'],r['errors']))
        self._run('Preparando descompilação...',w,d)
    def rpa_file(self):
        fs=filedialog.askopenfilenames(title='Selecionar arquivos RPA',filetypes=[('Ren\'Py Archive','*.rpa')])
        if fs:
            paths=[Path(x).resolve() for x in fs]
            base=Path(os.path.commonpath([str(p.parent) for p in paths])).resolve()
            self._extract_rpa(paths,display_root=base,root_name=base.name)
    def rpa_folder(self):
        d=filedialog.askdirectory(title='Selecionar pasta contendo arquivos RPA')
        if d:
            folder=Path(d).resolve()
            self._extract_rpa([p for p in folder.rglob('*.rpa') if p.is_file()],display_root=folder,root_name=folder.name)
    def _extract_rpa(self,files,display_root=None,root_name=None):
        self._log('=== EXTRAIR RPA ===')
        if root_name:self._log('Raiz: '+root_name)
        self._log('Arquivos RPA: '+str(len(files)))
        def w():return extractor_core.extract_rpa_archives(files,lambda v:self._progress(v),self._log_cb,self._status_cb,display_root=display_root)
        def d(r):self.status.set('Status: Extração RPA concluída.'); self._log('[OK] Extraídos: {}; RPA: {}; erros: {}'.format(r['extracted'],r['archives'],r['errors']))
        self._run('Preparando extração RPA...',w,d)
    def rpa_pack(self):
        selected=filedialog.askopenfilenames(title='Selecionar arquivos para compactar em RPA',filetypes=[('Todos os arquivos','*.*')])
        selected=[Path(x).resolve() for x in selected]
        if selected: base=Path(os.path.commonpath([str(p.parent) for p in selected])).resolve()
        else:
            folder=filedialog.askdirectory(title='Selecionar pasta para compactar em RPA')
            if not folder:return
            selected=[Path(folder).resolve()]; base=selected[0].parent
        output=filedialog.asksaveasfilename(title='Salvar arquivo RPA',defaultextension='.rpa',filetypes=[('Ren\'Py Archive','*.rpa')])
        if not output:return
        op=Path(output).resolve(); entries={}
        self._log('=== COMPACTAR RPA ===')
        pack_root = selected[0].name if len(selected)==1 and selected[0].is_dir() else base.name
        self._log('Raiz: '+pack_root)
        for sp in selected:
            candidates=[p for p in sp.rglob('*') if p.is_file()] if sp.is_dir() else [sp]
            for rp in candidates:
                if rp!=op:entries[rp.relative_to(base).as_posix()]=rp
        fe=sorted(entries.items(),key=lambda x:x[0].lower())
        if not fe:return messagebox.showinfo(APP,'A seleção não contém arquivos para compactar.')
        def w():return extractor_core.pack_rpa(fe,op,lambda v:self._progress(v),self._log_cb,self._status_cb)
        def d(r):self.status.set('Status: Compactação RPA concluída.'); self._log('[OK] {} arquivos → {}'.format(r['compacted'],Path(r['output']).name))
        self._run('Preparando compactação RPA...',w,d)

    # TL Manager
    def _choose_tl(self):return filedialog.askdirectory(title='Selecione a pasta de tradução dentro de game/tl') or None
    def tl_export(self,fmt,blocks):
        tl=self._choose_tl()
        if not tl:return
        self._log('=== EXTRAIR {} ==='.format(fmt.upper()))
        self._log('Raiz: '+Path(tl).name)
        def prog(v,t=None):self._progress(v,t)
        def w():
            if fmt=='txt':return (tl_core.export_blocks if blocks else tl_core.export_full)(tl,ROOT,return_session=True,progress=prog)
            return (tl_core.export_blocks_docx if blocks else tl_core.export_full_docx)(tl,ROOT,return_session=True,progress=prog)
        def d(r):
            if blocks: output,count,nblocks,session=r; self._log('[OK] {} registros / {} blocos.'.format(count,nblocks))
            else: output,count,session=r; self._log('[OK] {} registros.'.format(count))
            self.pending_tl=tl; self.pending_session=session; self.pending_format=fmt; self.status.set('Status: Extração concluída; aguardando tradução.')
        self._run('Extraindo {}...'.format(fmt.upper()),w,d)
    def tl_inject(self):
        tl=self.pending_tl or self._choose_tl()
        if not tl:return
        self._log('=== INJETAR TRADUÇÃO ===')
        self._log('Raiz: '+Path(tl).name)
        fmt=self.pending_format
        if fmt is None:
            has_docx=(ROOT/'old.docx').exists() or any(ROOT.glob('old_*.docx')); has_txt=(ROOT/'old.txt').exists() or any(ROOT.glob('old_*.txt'))
            if has_docx and not has_txt:fmt='docx'
            elif has_txt and not has_docx:fmt='txt'
            else:return messagebox.showerror(APP,'Não foi possível determinar automaticamente se a injeção é TXT ou DOCX.')
        def prog(v,t=None):self._progress(v,t)
        def w():return (tl_core.inject_docx_translations if fmt=='docx' else tl_core.inject_translations)(tl,ROOT,session=self.pending_session,progress=prog)
        def d(r):
            count,mode=r; self.status.set('Status: {} traduções injetadas.'.format(count)); self._log('[OK] Injeção: {} registros ({}).'.format(count,mode)); self.pending_tl=self.pending_session=self.pending_format=None
        self._run('Validando e injetando traduções...',w,d)

    # Revisor
    def revise(self,fmt):
        types=[('Documento TXT','*.txt')] if fmt=='txt' else [('Documento Word','*.docx')]
        p=filedialog.askopenfilename(title='Selecione o documento traduzido para revisar',filetypes=types+[('Todos','*.*')])
        if not p:return
        self._log('=== REVISOR {} ==='.format(fmt.upper()))
        self._log('Documento: '+Path(p).name)
        def prog(v,text=None,log=None):self._progress(v,text,log)
        def w():return review_file(Path(p),REVISOR_DIR,progress=prog)
        def d(r):
            self.status.set('Status: {} linhas revisadas.'.format(r['records'])); self._log('[OK] Linhas alteradas: {}.'.format(r['changed'])); self._log('[OK] Tokens Ren\'Py preservados: {}.'.format(r['tokens'])); self._log('[OK] Saída: {}'.format(Path(r['output']).name)); messagebox.showinfo(APP,'Revisão concluída.\n\n'+str(r['output']))
        self._run('Preparando revisão...',w,d)

if __name__=='__main__': WellsManager().mainloop()
