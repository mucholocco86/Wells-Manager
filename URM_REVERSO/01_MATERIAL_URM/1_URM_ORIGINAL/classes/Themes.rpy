
init 1 python in x52URM:
    _constant = True

    from collections import OrderedDict

    availableThemes = OrderedDict([
        ('Default', ThemeProvider.defaultTheme),
        ('Darker', {'text': '#ccc', 'primary': '#5C469C', 'secondary': '#1D267D', 'tertiary': '#0C134F', 'background': '#000000'}),
        ('Sci-fi', {'text': '#fff', 'primary': '#00FFCA', 'secondary': '#05BFDB', 'tertiary': '#088395', 'background': '#0A4D68'}),
        ('Vulcano', {'text': '#fff', 'primary': '#F05941', 'secondary': '#BE3144', 'tertiary': '#872341', 'background': '#22092C'}),
        ('Dark vulcano', {'text': '#ccc', 'primary': '#BE3144', 'secondary': '#872341', 'tertiary': '#22092C', 'background': '#000'}),
        ('Forest', {'text': '#f0f0f0', 'primary': '#D8E9A8', 'secondary': '#4E9F3D', 'tertiary': '#1E5128', 'background': '#191A19'}),
        ('Dark forest', {'text': '#c0c0c0', 'primary': '#4E9F3D', 'secondary': '#1E5128', 'tertiary': '#191A19', 'background': '#000'}),
        ('Traffic light', {'text': '#000', 'primary': '#FF8F8F', 'secondary': '#EEF296', 'tertiary': '#9ADE7B', 'background': '#508D69'}),
        ('Sunny', {'text': '#000', 'primary': '#E7B10A', 'secondary': '#898121', 'tertiary': '#4C4B16', 'background': '#F7F1E5'}),
        ('Earth', {'text': '#000', 'primary': '#884A39', 'secondary': '#C38154', 'tertiary': '#FFC26F', 'background': '#F9E0BB'}),
        ('Icecream', {'text': '#000', 'primary': '#FFCFDF', 'secondary': '#FEFDCA', 'tertiary': '#E0F9B5', 'background': '#A5DEE5'}),
        ('Beach', {'text': '#000', 'primary': '#E0F4FF', 'secondary': '#87C4FF', 'tertiary': '#39A7FF', 'background': '#FFEED9'}),
        ('Night beach', {'text': '#ccc', 'primary': '#E3C4A8', 'secondary': '#4592AF', 'tertiary': '#226089', 'background': '#000000'}),
    ])

    class SetTheme(renpy.ui.Action):
        def __init__(self, name, globalSetting=None, doNotSave=False):
            self.name = name
            self.globalSetting = globalSetting
            self.doNotSave = doNotSave
        
        def __call__(self):
            if self.name == None: 
                prevValue = Settings.theme
                Settings.set('theme', None, globalSetting=self.globalSetting)
                if prevValue != Settings.theme: 
                    self.name = Settings.theme
                    self.doNotSave = True
                    self.__call__()
            elif self.name in availableThemes:
                Theme.setTheme(availableThemes[self.name])
                if not self.doNotSave: Settings.set('theme', self.name, globalSetting=self.globalSetting)
        
        def get_selected(self):
            return Settings.get('theme', self.globalSetting) == self.name

    class SetDialogTransparency(renpy.ui.Action):
        def __init__(self, transparency, doNotRebuild=False, globalSetting=None, doNotSave=False):
            self.transparency = transparency
            self.doNotRebuild = doNotRebuild
            self.globalSetting = globalSetting
            self.doNotSave = doNotSave
        
        @property
        def translucency(self):
            if self.transparency == None:
                return int(Settings.defaultValues['themeTransparency']*255)
            else:
                return int(self.transparency*255)
        
        def __call__(self, doNotSave=False):
            if self.transparency == None: 
                prevValue = Settings.themeTransparency
                Settings.set('themeTransparency', None, globalSetting=self.globalSetting)
                if prevValue != Settings.themeTransparency: 
                    self.transparency = Settings.themeTransparency
                    self.doNotSave = True
                    self.__call__()
            elif not self.get_selected() and 0 <= self.transparency <= 1: 
                Theme.colors.overrideMappings['dialogBg'] = 'backgroundTranslucent{}'.format(self.translucency)
                if not self.doNotRebuild: renpy.store.gui.rebuild()
                if not self.doNotSave: Settings.set('themeTransparency', self.transparency, globalSetting=self.globalSetting)
        
        def get_selected(self):
            if 'dialogBg' in Theme.colors.overrideMappings:
                return Theme.colors.overrideMappings['dialogBg'] == 'backgroundTranslucent{}'.format(self.translucency)
            elif 'dialogBg' in Theme.colors.mappings:
                return Theme.colors.mappings['dialogBg'] == 'backgroundTranslucent{}'.format(self.translucency)
            else:
                return False
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
