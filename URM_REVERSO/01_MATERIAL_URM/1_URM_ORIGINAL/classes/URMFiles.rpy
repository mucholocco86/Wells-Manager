
init 3 python in x52URM:
    _constant = True

    class URMFilesClass(x52NonPicklable):
        def __init__(self):
            self.file = URMFile()
            
            self._m1_URMFiles__saveDir = None 
            self.gameDir = renpy.os.path.abspath(renpy.os.path.join(renpy.config.basedir, "game"))
        
        @property
        def saveDir(self):
            if self._m1_URMFiles__saveDir == None:
                if Settings.saveDir:
                    self._m1_URMFiles__saveDir = renpy.os.path.abspath(renpy.os.path.join(Settings.saveDir, renpy.config.save_directory)) 
                elif renpy.os.path.isdir(renpy.config.savedir):
                    self._m1_URMFiles__saveDir = renpy.config.savedir 
                
                
                try:
                    renpy.os.makedirs(self.saveDir)
                except Exception:
                    pass
            
            return self._m1_URMFiles__saveDir
        
        def fileExists(self, filename):
            return renpy.exists(renpy.os.path.join(self.gameDir, filename)) or (self.saveDir and renpy.exists(renpy.os.path.join(self.saveDir, filename)))
        
        def stripSpecialChars(self, str):
            import re
            return re.sub('[^A-Za-z0-9 _-]', '_', str)
        
        def listFiles(self):
            import re
            from glob import glob
            from collections import OrderedDict
            
            files = {}
            
            
            gameDirFiles = glob(renpy.os.path.join(re.sub(r'(\[|\])', r'[\1]', self.gameDir), '*.urm')) 
            for i,filename in enumerate(gameDirFiles):
                files[filename[len(self.gameDir)+1:]] = URMFile(filename) 
            
            
            if self.saveDir:
                saveDirFiles = glob(renpy.os.path.join(re.sub(r'(\[|\])', r'[\1]', self.saveDir), '*.urm')) 
                for i,filename in enumerate(saveDirFiles):
                    mtime = renpy.os.path.getmtime(filename)
                    name = filename[len(self.saveDir)+1:]
                    if not hasattr(files, name) or files[name].mtime < mtime:
                        files[name] = URMFile(filename) 
            
            
            files = OrderedDict(sorted(files.items()))
            
            return files
        
        def autoLoad(self):
            """ Auto load the `lastLoadedFile` if nothing is loaded """
            if not self.file.unsaved and Settings.lastLoadedFile != None and Settings.lastLoadedFile != self.file.filename:
                self.load(Settings.lastLoadedFile)
        
        def clear(self, confirm=False):
            """ Start a new file """
            if self.file.unsaved and not confirm:
                Confirm('Unsaved changes will be lost, do you want to continue?', renpy.store.Function(self.clear, confirm=True))()
            else:
                self.file = URMFile()
                Settings.lastLoadedFile = None
        
        class Clear(x52NonPicklable):
            def __call__(self):
                URMFiles.clear()
        
        def load(self, filename):
            urmFile = URMFile(filename)
            
            
            filepath = urmFile.lastModifiedPath
            if filepath:
                urmFile = self.loadLegacyURMFile(filepath) or urmFile
                
                self.file = urmFile
                Settings.lastLoadedFile = filename
                
                return True
            else:
                return False
        
        class Load(x52NonPicklable):
            def __init__(self, filename=None, finishAction=None, screenErrorVariable=None):
                self.filename = filename
                self.finishAction = finishAction
                self.screenErrorVariable = screenErrorVariable
            
            def __call__(self):
                if not self.filename:
                    if URMFiles.file.unsaved:
                        Confirm('Unsaved changes will be lost, do you want to continue?', renpy.store.Show('URM_load_file'))()
                    else:
                        renpy.show_screen('URM_load_file')
                        renpy.restart_interaction()
                else:
                    if URMFiles.load(self.filename):
                        if self.finishAction:
                            self.finishAction()
                    elif self.screenErrorVariable: 
                        cs = renpy.current_screen()
                        if cs and self.screenErrorVariable in cs.scope:
                            cs.scope[self.screenErrorVariable] = 'Failed to load file'
                            renpy.restart_interaction()
        
        def loadLegacyURMFile(self, filepath):
            import json
            
            jsonData = None
            try:
                f = renpy.os.open(filepath, renpy.os.O_RDONLY)
                if renpy.os.read(f, 1).decode() == '{': 
                    renpy.os.lseek(f, 0, renpy.os.SEEK_SET)
                    jsonData = json.loads(renpy.os.read(f, renpy.os.path.getsize(filepath)), object_pairs_hook=OrderedDict)
                renpy.os.close(f)
            except Exception as e:
                print('0x52: Loading file "{}" failed with error: {}'.format(filepath, e))
                return None
            
            if jsonData:
                try:
                    newfile = URMFile(renpy.os.path.split(filepath)[1])
                    for store in jsonData:
                        if store == 'replacements':
                            jsonData[store] = OrderedDict([(r['original'], r) for r in jsonData[store]]) 
                        
                        newfile.addStore(store, URMFileStore(jsonData[store]))
                    
                    return newfile
                except Exception as e:
                    print('0x52: Failed to parse contents for file "{}" with error: {}'.format(filepath, e))
                    return None
        
        def save(self, name, successAction=None, failureAction=None, overwrite=False):
            filename = self.stripSpecialChars(name)+'.urm'
            if self.fileExists(filename) and not overwrite:
                return Confirm('Do you want to overwrite the existing file?', renpy.store.Function(self.save, name, successAction, failureAction, True))()
            elif self.file and isinstance(self.file, URMFile):
                if self.file.save(filename):
                    Settings.lastLoadedFile = filename
                    
                    if successAction:
                        successAction()
                    else:
                        return True
                else:
                    if failureAction:
                        failureAction()
                    else:
                        return False
        
        class Save(x52NonPicklable):
            def __init__(self, name=None, finishAction=None, screenErrorVariable=None):
                self.name = name
                self.finishAction = finishAction
                self.screenErrorVariable = screenErrorVariable
            
            def __call__(self):
                if self.name == None: 
                    renpy.show_screen('URM_save_file')
                    renpy.restart_interaction()
                else:
                    cs = renpy.current_screen()
                    
                    def onSuccess():
                        if self.finishAction:
                            self.finishAction()
                    
                    def onFailure():
                        if self.screenErrorVariable and cs and self.screenErrorVariable in cs.scope:
                            cs.scope[self.screenErrorVariable] = 'Failed to save file'
                            renpy.restart_interaction()
                    
                    URMFiles.save(self.name if not callable(self.name) else self.name(), onSuccess, onFailure)
        
        class Delete(x52NonPicklable):
            def __init__(self, urmFile):
                self.urmFile = urmFile
            
            def __call__(self):
                if isinstance(self.urmFile, URMFile):
                    self.urmFile.delete()

    class URMFileStore(OrderedDict):
        def __init__(self, data=None, unsaved=False):
            super(OrderedDict, self).__init__(data or {})
            self.unsaved = unsaved
        
        def __setitem__(self, key, val):
            super(OrderedDict, self).__setitem__(key, val)
            self.unsaved = True
        
        def __delitem__(self, key):
            if key in self:
                super(OrderedDict, self).__delitem__(key)
                self.unsaved = True
        
        def update(self, data):
            super(OrderedDict, self).update(data)
            self.unsaved = True
        
        def clear(self):
            if not self.isEmpty: self.unsaved = True
            super(OrderedDict, self).clear()
        
        @property
        def isEmpty(self):
            return not bool(self)
        
        def toJSON(self):
            import json
            return json.dumps(self)

    class URMFile(x52NonPicklable):
        def __init__(self, filename=None):
            self.filename = renpy.os.path.split(filename)[1] if filename else filename
            self.mtime = self.mtime = renpy.os.path.getmtime(self.lastModifiedPath) if self.lastModifiedPath else None
            self._m1_URMFiles__stores = None
            self._m1_URMFiles__storeNames = None
        
        def getStore(self, name, doNotLoad=False):
            if self._m1_URMFiles__stores and name in self._m1_URMFiles__stores: 
                return self._m1_URMFiles__stores[name]
            elif self._m1_URMFiles__storeNames != None and name not in self._m1_URMFiles__storeNames: 
                return None
            elif self._m1_URMFiles__stores == None and doNotLoad == False: 
                self.load()
                return self.getStore(name, doNotLoad=True)
        
        def __getitem__(self, key):
            return self.getStore(key)
        
        def addStore(self, name, data=None):
            if self._m1_URMFiles__stores == None: self._m1_URMFiles__stores = {}
            if isinstance(data, URMFileStore):
                self._m1_URMFiles__stores[name] = data
            else:
                self._m1_URMFiles__stores[name] = URMFileStore(data)
        
        def clearStore(self, name):
            if self._m1_URMFiles__stores and name in self._m1_URMFiles__stores:
                self._m1_URMFiles__stores[name].clear()
        
        @property
        def storeNames(self):
            """ Names of stores present in this file """
            if self._m1_URMFiles__stores:
                return self._m1_URMFiles__stores.keys()
            elif self._m1_URMFiles__storeNames != None:
                return self._m1_URMFiles__storeNames
            else:
                self._m1_URMFiles__storeNames = self._m1_URMFiles__loadStoreNames()
                return self._m1_URMFiles__storeNames
        
        @property
        def unsaved(self):
            if self._m1_URMFiles__stores:
                for name in self._m1_URMFiles__stores:
                    if self._m1_URMFiles__stores[name].unsaved:
                        return True
            return False
        
        @unsaved.setter
        def unsaved(self, val):
            if self._m1_URMFiles__stores:
                for name in self._m1_URMFiles__stores:
                    self._m1_URMFiles__stores[name].unsaved = val
        
        @property
        def gameDirPath(self):
            if self.filename:
                return renpy.os.path.join(URMFiles.gameDir, self.filename)
        
        @property
        def saveDirPath(self):
            if self.filename and URMFiles.saveDir:
                return renpy.os.path.join(URMFiles.saveDir, self.filename)
        
        @property
        def lastModifiedPath(self):
            if self.filename:
                
                gameDirMtime = renpy.os.path.getmtime(self.gameDirPath) if renpy.os.path.isfile(self.gameDirPath) else 0
                saveDirMtime = renpy.os.path.getmtime(self.saveDirPath) if renpy.os.path.isfile(self.saveDirPath or '') else 0
                
                
                selectedFile = None
                if gameDirMtime >= saveDirMtime and gameDirMtime > 0:  
                    selectedFile = self.gameDirPath
                elif saveDirMtime > 0: 
                    selectedFile = self.saveDirPath
                
                return selectedFile
        
        def _m1_URMFiles__initProperties(self):
            self.addStore('properties', {'urmVersion': version, 'gameId': renpy.config.save_directory})
        
        def save(self, filename=None):
            import json, zipfile, shutil
            
            if filename: self.filename = filename
            
            if self.filename:
                self._m1_URMFiles__initProperties()
                
                
                filenameNew = self.gameDirPath + '.new'
                try:
                    with zipfile.ZipFile(filenameNew, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for entry in self._m1_URMFiles__stores or {}:
                            if not self._m1_URMFiles__stores[entry].isEmpty: 
                                zf.writestr(entry, self._m1_URMFiles__stores[entry].toJSON())
                    
                    shutil.move(filenameNew, self.gameDirPath)
                except Exception as e:
                    print('0x52: Failed to save file "{}" with error: {}'.format(self.gameDirPath, e))
                    return False
                
                
                if self.saveDirPath:
                    try:
                        shutil.copy(self.gameDirPath, self.saveDirPath)
                    except Exception as e:
                        print('0x52: Failed to save file "{}" with error: {}'.format(self.saveDirPath, e))
                
                self.unsaved = False
                return True
            
            else: 
                return False
        
        def _m1_URMFiles__loadStoreNames(self):
            import zipfile
            selectedFile = self.lastModifiedPath
            
            if selectedFile:
                if not zipfile.is_zipfile(selectedFile): return [] 
                
                try:
                    with zipfile.ZipFile(selectedFile, 'r') as zf:
                        return zf.namelist()
                except Exception as e:
                    print('0x52: Loading storenames from file "{}" failed with error: {}'.format(selectedFile, e))
                    return []
        
        def load(self):
            import json, zipfile
            self._m1_URMFiles__stores = {}
            selectedFile = self.lastModifiedPath
            
            
            if selectedFile:
                try:
                    with zipfile.ZipFile(selectedFile, 'r') as zf:
                        for entry in zf.namelist():
                            try:
                                self._m1_URMFiles__stores[entry] = URMFileStore(json.loads(zf.read(entry), object_pairs_hook=OrderedDict))
                            except Exception as e:
                                print('0x52: Failed to parse json for entry "{}" in file "{}". {}'.format(entry, selectedFile, e))
                except Exception as e:
                    print('0x52: Loading file "{}" failed with error: {}'.format(selectedFile, e))
                    return None
        
        def delete(self):
            try:
                if renpy.os.path.isfile(self.gameDirPath):
                    renpy.os.remove(self.gameDirPath)
            except Exception as e:
                print('0x52: Failed to delete file "{}" with error: {}'.format(self.gameDirPath, e))
            
            if self.saveDirPath:
                try:
                    if renpy.os.path.isfile(self.saveDirPath):
                        renpy.os.remove(self.saveDirPath)
                except Exception as e:
                    print('0x52: Failed to delete file "{}" with error: {}'.format(self.saveDirPath, e))
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
