
init -1000 python in x52MF2:
    _constant = True


    from collections import OrderedDict
    availableModules = OrderedDict([
        ('main', ['bootstrap.rpy','modules/01utils.x52rpy']), 
        ('fonts', ['MaterialIcons-Regular.ttf','MaterialIconsOutlined-Regular.otf','Roboto-Regular.ttf']),
        ('theming', ['fonts','modules/10theme.x52rpy','theme.rpy.x52','screens/buttons.rpy.x52','screens/messagebars.rpy.x52']),
        ('dialogs', ['theming','modules/dialogs.x52rpy','screens/dialogs.rpy.x52']),
        ('api', ['modules/API.x52rpy']),
        ('inputs', ['modules/inputs.x52rpy']),
        ('screeninjector', ['modules/screeninjector.x52rpy']),
        ('screenreader', ['modules/screenreader.x52rpy']),
        ('tooltips', ['modules/tooltips.x52rpy']),
    ])

    def load(modules, modName, mfPath, minVersion='6.99.14'):
        
        if renpy.version_only < minVersion: raise Exception('0x52: This mod ({}) does not support Ren\'Py version {}. Lowest supported version is {}'.format(modName, renpy.version_only, minVersion))
        
        if not 'main' in modules: modules.append('main') 
        
        archivePath = findArchivePath('{}/bootstrap.rpyc'.format(mfPath))
        if archivePath: 
            if hasattr(renpy.store, modName) and isinstance(getattr(renpy.store, modName), renpy.python.StoreModule):
                getattr(renpy.store, modName).archivePath = archivePath
                
                if renpy.os.path.isfile(archivePath+'.update'): 
                    def pendingUpdate():
                        applyUpdate(archivePath)
                    getattr(renpy.store, modName).pendingUpdate = pendingUpdate
        
        else: 
            import hashlib, random, string
            renpy.game.script.digest = hashlib.md5(''.join(random.choice(string.ascii_letters + string.digits) for i in range(20)).encode())
        
        
        filesToLoad = []
        def addFilesToLoad(files):
            for file in files:
                if file in availableModules: 
                    addFilesToLoad(availableModules[file])
                elif file not in filesToLoad:
                    filesToLoad.append(file)
        
        for availableModule in availableModules:
            if availableModule in modules:
                addFilesToLoad(availableModules[availableModule])
        
        
        for fn in filesToLoad:
            fullFn = '{}/{}'.format(mfPath, fn)
            loadFile(fullFn, modName, mfPath)

    def loadFile(fullFn, modName, mfPath=None):
        ext = renpy.os.path.splitext(fullFn)[1].lower()
        
        if ext in ['.x52rpy','.x52']: 
            loadableSource = renpy.loadable(fullFn)
            loadableTransformed = renpy.loadable(fullFn+'t')
            
            if loadableSource or loadableTransformed: 
                try:
                    modFile = renpy.loader.load(fullFn+'t') if loadableTransformed else renpy.loader.load(fullFn)
                    modFileContents = modFile.read().decode()
                    if loadableSource: 
                        modFileContents = modFileContents.replace('_x52ModName_', modName) 
                        if mfPath: modFileContents = modFileContents.replace('_x52MFPath_', mfPath) 
                    modFileLoaded = (renpy.load_string(modFileContents, fullFn) != None) 
                    if not modFileLoaded: raise Exception(renpy.get_parse_errors()) 
                except Exception as e:
                    raise Exception('0x52: Failed to load file "{}". {}'.format(fullFn, e))
            
            elif ext == '.x52rpy': 
                fullFn = fullFn[:-6] + 'rpyc'
                if not renpy.loadable(fullFn):
                    raise Exception('0x52: File "{}" not found'.format(fullFn))
            
            else:
                raise Exception('0x52: File "{}" not found'.format(fullFn))

    def findArchivePath(fullFn):
        """ Find the archive path for a certain file """
        for archiveName,files in renpy.loader.archives:
            if fullFn in files:
                archivePath = renpy.os.path.abspath(renpy.os.path.join(renpy.config.basedir, 'game', archiveName))
                if not renpy.os.path.isfile(archivePath) and renpy.os.path.isfile(archivePath+'.rpa'): 
                    archivePath = archivePath+'.rpa'
                return archivePath

    def applyUpdate(archivePath):
        """ Apply mod update, if there is one """
        import shutil
        
        updateFilePath = archivePath+'.update'
        if renpy.os.path.isfile(updateFilePath): 
            try:
                shutil.move(updateFilePath, archivePath)
            except Exception as e:
                print('0x52: Failed to apply update. {}'.format(e))
                try:
                    if renpy.os.path.isfile(updateFilePath):
                        renpy.os.remove(updateFilePath)
                except Exception as e:
                    print('0x52: Failed to delete update file after failed update. {}'.format(e))
                return
            
            print('0x52: Applied mod update. Reloading...')
            renpy.reload_script()


init 999 python:
    if not 'x52Overlay' in config.layers: config.layers.append('x52Overlay') 
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
