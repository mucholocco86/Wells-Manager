
init 3 python in x52URM:
    _constant = True

    class SettingsClass(x52NonPicklable):
        defaultValues = {
            'warningDisabled': False,
            'seenWelcome': 0,
            'lastLoadedFile': None,
            'labelsView': 'thumbnails',
            'searchRecursive': False,
            'searchPersistent': True,
            'searchObjects': True,
            'showUnsupportedVariables': False,
            'searchInternalVars': False,
            'useWildcardSearch': False,
            'showWatchPanel': False,
            'collapsedWatchPanel': False,
            'watchpanelToggleKey': '',
            'watchpanelHideToggleButton': False,
            'watchPanelPos': 'l',
            'watchPanelFileLine': 0,
            'watchPanelCurrentLabel': 1,
            'watchPanelChoiceDetection': 1,
            'watchPanelPathDetection': 1,
            'watchPanelProgress': 0,
            'watchPanelVars': 1,
            'showChoicesNotification': True,
            'showPathsNotification': True,
            'stopSkippingOnPathDetection': False,
            'showReplayNotification': True,
            'currentScreen': 'search',
            'searchType': 'variable names',
            'askSaveName': True,
            'quickResumeSaveHotKey': False,
            'quickSaveHotKey': False,
            'quickLoadHotKey': False,
            'updateChannel': 'stable',
            'autoUpdateCheck': True,
            'skipUpdate': None,
            'consoleHotKey': False,
            'skipSplashscreen': False,
            'touchEnabled': renpy.variant('touch'),
            'touchPosition': None,
            'textboxesEnabled': False,
            'theme': 'Default',
            'themeTransparency': 0.1,
            'codeViewShowAll': False,
            'progressShown': False,
            'progressPosition': None,
            'progressShowNew': False, 
            'notificationTimeout': 0,
            
            'quickmenuEnabled': False,
            'quickmenuAlignX': 0.5,
            'quickmenuAlignY': 1.0,
            'quickmenuVertical': False,
            'quickmenuBtnBack': True,
            'quickmenuBtnSkip': True,
            'quickmenuBtnAuto': True,
            'quickmenuBtnQuicksave': True,
            'quickmenuBtnSave': False,
            'quickmenuBtnQuickload': True,
            'quickmenuBtnLoad': False,
            'quickmenuBtnMenu': True,
            'quickmenuBtnUrm': False,
            'quickmenuBtnExit': False,
            'quickmenuAutoHide': False,
            'quickmenuStyle': 'default',
        }
        
        _m1_settings__saveDir = None
        _m1_settings__globalSettings = {}
        _m1_settings__id = None
        
        def __init__(self):
            import __main__
            
            if renpy.android:
                if renpy.os.path.isdir('/sdcard/Documents'):
                    SettingsClass._m1_settings__saveDir = renpy.os.path.join(self._m1_settings__resolveSymlink('/sdcard'), 'Documents', '0x52-URM')
            else:
                SettingsClass._m1_settings__saveDir = __main__.path_to_saves(renpy.config.gamedir, '0x52-URM')
            
            
            if self.saveDir and not renpy.os.path.isdir(self.saveDir):
                try:
                    renpy.os.mkdir(self.saveDir)
                except Exception as e:
                    print('0x52: Failed to create dir "{}". {}'.format(self.saveDir, e))
                    SettingsClass._m1_settings__saveDir = None
            
            
            if self.saveDir:
                try:
                    settingsFile = renpy.os.path.join(self.saveDir, 'settings')
                    if renpy.os.path.isfile(settingsFile): 
                        f = renpy.os.open(settingsFile, renpy.os.O_WRONLY)
                        renpy.os.close(f)
                    else: 
                        fn = renpy.os.path.join(self.saveDir, "test")
                        f = renpy.os.open(fn, renpy.os.O_CREAT | renpy.os.O_WRONLY)
                        renpy.os.close(f)
                        f = renpy.os.open(fn, renpy.os.O_RDONLY)
                        renpy.os.close(f)
                        renpy.os.unlink(fn)
                except Exception as e:
                    print('0x52: Failed to write to dir "{}". {}'.format(self.saveDir, e))
                    SettingsClass._m1_settings__saveDir = None
            
            self._m1_settings__loadGlobalSettings()
        
        def _m1_settings__resolveSymlink(self, path):
            if renpy.os.path.islink(path):
                return self._m1_settings__resolveSymlink(renpy.os.readlink(path))
            else:
                return path
        
        @property
        def saveDir(self):
            return SettingsClass._m1_settings__saveDir
        
        @property
        def id(self):
            return SettingsClass._m1_settings__id
        
        @property
        def globalAvailable(self):
            """ Are global settings available? """
            return bool(self.saveDir)
        
        def saveId(self, val):
            SettingsClass._m1_settings__id = val
            self._m1_settings__saveGlobalSettings()
        
        def __getattr__(self, attr):
            if attr in SettingsClass.defaultValues:
                return self.get(attr)
            elif attr not in ['nosave','values']: 
                print('0x52: Something requested an unknown setting "{}"'.format(attr))
        
        def __setattr__(self, attr, value):
            if attr in SettingsClass.defaultValues:
                self.set(attr, value)
        
        def get(self, name, globalSetting=None):
            defaultValue = None
            if name in SettingsClass.defaultValues: defaultValue = SettingsClass.defaultValues[name]
            
            if globalSetting: 
                if name in SettingsClass._m1_settings__globalSettings:
                    return SettingsClass._m1_settings__globalSettings[name]
                else:
                    return defaultValue
            
            elif globalSetting == False: 
                if renpy.store.persistent.URMSettings != None and name in renpy.store.persistent.URMSettings:
                    return renpy.store.persistent.URMSettings[name]
            
            else: 
                if renpy.store.persistent.URMSettings != None and name in renpy.store.persistent.URMSettings:
                    return renpy.store.persistent.URMSettings[name]
                elif name in SettingsClass._m1_settings__globalSettings:
                    return SettingsClass._m1_settings__globalSettings[name]
                else:
                    return defaultValue
        
        def set(self, name, value, globalSetting=None):
            if globalSetting:
                if value == None: 
                    if name in SettingsClass._m1_settings__globalSettings:
                        del SettingsClass._m1_settings__globalSettings[name]
                else:
                    SettingsClass._m1_settings__globalSettings[name] = value
                
                self._m1_settings__saveGlobalSettings() 
            else:
                if renpy.store.persistent.URMSettings == None: renpy.store.persistent.URMSettings = {}
                if value == None: 
                    if name in renpy.store.persistent.URMSettings:
                        del renpy.store.persistent.URMSettings[name]
                else:
                    renpy.store.persistent.URMSettings[name] = value
            
            renpy.restart_interaction()
        
        def _m1_settings__loadGlobalSettings(self):
            if not self.saveDir: return 
            
            import zipfile, json
            fileName = renpy.os.path.join(self.saveDir, 'settings')
            if renpy.os.path.exists(fileName):
                try:
                    with zipfile.ZipFile(fileName, 'r') as zf:
                        jsonStr = zf.read('json')
                        SettingsClass._m1_settings__id = zf.read('id')
                        urmVersion = zf.read('urmVersion')
                    
                    
                    SettingsClass._m1_settings__globalSettings = json.loads(jsonStr)
                except Exception as e:
                    print('0x52: Failed to read global settings from {}. {}'.format(fileName, e))
        
        def _m1_settings__saveGlobalSettings(self):
            if not self.saveDir: return 
            
            import zipfile, shutil, json
            fileName = renpy.os.path.join(self.saveDir, 'settings')
            fileNameNew = fileName + '.new'
            try:
                with zipfile.ZipFile(fileNameNew, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr('json', json.dumps(SettingsClass._m1_settings__globalSettings))
                    if self.id: zf.writestr('id', self.id)
                    zf.writestr('urmVersion', version)
                
                shutil.move(fileNameNew, fileName)
            except Exception as e:
                print('0x52: Failed to save global settings to {}. {}'.format(fileName, e))
                raise e

    class SetURMSetting(renpy.ui.Action):
        def __init__(self, name, value, globalSetting=False):
            self.name = name
            self.value = value
            self.globalSetting = globalSetting
        
        def __call__(self):
            Settings.set(self.name, self.value, self.globalSetting)
        
        def get_selected(self):
            return Settings.get(self.name, self.globalSetting) == self.value
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
