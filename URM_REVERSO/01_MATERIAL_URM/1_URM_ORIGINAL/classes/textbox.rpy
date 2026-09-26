
init 3 python in x52URM:
    _constant = True

    class TextBoxClass(x52NonPicklable):
        def __init__(self):
            self._m1_textbox__originalSayArgCallback = None
            self._m1_textbox__originalShowScreen = None
            self.whoArgs = {}
            self.whatArgs = {}
            self._m1_textbox__imageTag = None
            self.previewCharacterVarName = None
            self.Settings = TextBoxSettings()
            self.demoCharacter = renpy.character.ADVCharacter('0x52', image='x52Logo', color='#D4ADFC')
        
        @property
        def enabled(self):
            return renpy.has_screen('URM_say') and bool(Settings.textboxesEnabled or (self.Settings and self.Settings.tempValues != None))
        
        @enabled.setter
        def enabled(self, val):
            Settings.textboxesEnabled = val
        
        def openCustomizer(self, charVarName=None, beforeOpenAction=None, afterCloseAction=None):
            self.Settings = TextBoxSettings(charVarName)
            self.previewCharacter = charVarName
            if callable(beforeOpenAction): beforeOpenAction()
            renpy.call_in_new_context('URM_textboxCustomizer', charVarName=charVarName)
            if callable(afterCloseAction): afterCloseAction()
            
            
            raise renpy.game.RestartContext(None) 
        
        def closeCustomizer(self, save=False):
            if save:
                self.Settings.commitTemp(self.previewCharacterVarName)
            else:
                self.Settings.dismissTemp()
            renpy.jump('URM_textboxCustomizer_return')
        
        @property
        def previewCharacter(self):
            if self.previewCharacterVarName and hasattr(renpy.store, self.previewCharacterVarName):
                return getattr(renpy.store, self.previewCharacterVarName)
            
            return self.demoCharacter
        
        @previewCharacter.setter
        def previewCharacter(self, val):
            if val and hasattr(renpy.store, val) and isinstance(getattr(renpy.store, val), renpy.store.ADVCharacter):
                self.previewCharacterVarName = val
            else:
                self.previewCharacterVarName = None
        
        @property
        def textHeight(self):
            return scalePxInt(self.Settings.whatHeight)
        
        @property
        def textWidth(self):
            return scaleX(self.Settings.whatWidth)
        
        @property
        def whoWidth(self):
            return scaleX(self.Settings.whoWidth)
        
        @property
        def sideImage(self):
            if not self._m1_textbox__imageTag: return None
            
            if self._m1_textbox__imageTag == 'x52Logo':
                img = '0x52-URM/images/logoBig.x52'
            else:
                img = renpy.get_registered_image('{} {}'.format(renpy.config.side_image_prefix_tag, self._m1_textbox__imageTag))
            
            if img:
                try:
                    return ScaleImage(img, TextBox.textHeight, TextBox.textHeight)
                except Exception as e:
                    print('0x52: Failed to get side image "{}" with error: {}'.format(self._m1_textbox__imageTag, e))
        
        @property
        def whatXPadding(self):
            return scalePxInt(self.Settings.whatXPadding or 0)
        
        @property
        def whoXPadding(self):
            return scalePxInt(self.Settings.whoXPadding or 0)
        
        @property
        def whoXAlign(self):
            return self.Settings.whoXAlign or 0.0
        
        @property
        def whoBackground(self):
            if self.Settings.whoBackgroundEnabled:
                if self.Settings.whoBackgroundCharacterColor and ('color' in self.whoArgs or self.Settings.whoColor):
                    if 'color' in self.whoArgs:
                        color = self._m1_textbox__appendColorAlpha(self.whoArgs['color'], self.Settings.whoBackground)
                    else:
                        color = self._m1_textbox__appendColorAlpha(self.Settings.whoColor, self.Settings.whoBackground)
                else:
                    color = self.Settings.whoBackground
                
                if self.Settings.whoBackgroundGradient:
                    return renpy.display.layout.AlphaMask(renpy.display.imagelike.Solid(color), renpy.display.imagelike.Frame('0x52-URM/images/textboxGradientCentered.x52'))
                else:
                    return renpy.display.imagelike.Solid(color)
        
        @property
        def whoFont(self):
            if self.Settings.whoFont and self.Settings.whoFont in TextBoxSettings.fontOptions and renpy.loadable(TextBoxSettings.fontOptions[self.Settings.whoFont]):
                return TextBoxSettings.fontOptions[self.Settings.whoFont]
            else:
                return list(TextBoxSettings.fontOptions.values())[0]
        
        @property
        def whatBackground(self):
            if self.Settings.whatBackgroundEnabled:
                if self.Settings.whatBackgroundCharacterColor and ('color' in self.whoArgs or self.Settings.whoColor):
                    if 'color' in self.whoArgs:
                        color = self._m1_textbox__appendColorAlpha(self.whoArgs['color'], self.Settings.whatBackground)
                    else:
                        color = self._m1_textbox__appendColorAlpha(self.Settings.whoColor, self.Settings.whatBackground)
                else:
                    color = self.Settings.whatBackground
                
                if self.Settings.whatBackgroundGradient:
                    return renpy.display.layout.AlphaMask(renpy.display.imagelike.Solid(color), renpy.display.imagelike.Frame('0x52-URM/images/textboxGradient.x52'))
                else:
                    return renpy.display.imagelike.Solid(color)
        
        @property
        def whatFont(self):
            if self.Settings.whatFont and self.Settings.whatFont in TextBoxSettings.fontOptions and renpy.loadable(TextBoxSettings.fontOptions[self.Settings.whatFont]):
                return TextBoxSettings.fontOptions[self.Settings.whatFont]
            else:
                return list(TextBoxSettings.fontOptions.values())[0]
        
        def _m1_textbox__appendColorAlpha(self, baseColor, alphaColor):
            """ Transfer the alpha channel from `alphaColor` to `baseColor` """
            if len(alphaColor) == 5:
                alphaValue = alphaColor[-1:]*2
            elif len(alphaColor) == 9:
                alphaValue = alphaColor[-2:]
            else:
                return baseColor 
            
            if len(baseColor) == 4 or len(baseColor) == 5:
                return '#{}{}{}{}'.format(baseColor[1]*2, baseColor[2]*2, baseColor[3]*2, alphaValue)
            elif len(baseColor) == 7 or len(baseColor) == 9:
                return '#{}{}{}{}'.format(baseColor[1:3], baseColor[3:5], baseColor[5:7], alphaValue)
            else:
                return baseColor
        
        def _m1_textbox__createWhoArgs(self, args):
            args = self._m1_textbox__stripUnwantedStyleArgs(args)
            
            
            if self.Settings.customSayScreen or self.Settings.whoFont != None: args['font'] = self.whoFont
            if self.Settings.whoColor != None: args['color'] = self.Settings.whoColor
            if self.Settings.whoOutlinesEnabled:
                args['outlines'] = [(renpy.display.core.absolute(self.Settings.whoOutlinesWidth or 0), self.Settings.whoOutlinesColor or '#000', renpy.display.core.absolute(1), renpy.display.core.absolute(1)),(renpy.display.core.absolute(self.Settings.whoOutlinesWidth or 0), self.Settings.whoOutlinesColor or '#000', renpy.display.core.absolute(-1), renpy.display.core.absolute(-1))]
            else:
                args['outlines'] = []
            if self.Settings.whoBold != None: args['bold'] = self.Settings.whoBold
            if self.Settings.whoItalic != None: args['italic'] = self.Settings.whoItalic
            if self.Settings.whoXAlign != None: args['xalign'] = self.Settings.whoXAlign
            args['size'] = scalePxInt(self.Settings.whoSize or TextBoxSettings.defaultValues['whoSize'])
            
            if not self.Settings.customSayScreen:
                args = self._m1_textbox__stripDisallowedSayArgs(args)
            
            return args
        
        def _m1_textbox__createWhatArgs(self, args):
            args = self._m1_textbox__stripUnwantedStyleArgs(args)
            
            
            args['style'] = 'URMSay_text'
            if self.Settings.customSayScreen or self.Settings.whatFont != None: args['font'] = self.whatFont
            if self.Settings.whatColorFromCharacter and 'color' in self.whoArgs:
                args['color'] = self._m1_textbox__appendColorAlpha(self.whoArgs['color'], self.Settings.whatColor or '#fff')
            elif self.Settings.whatColor != None:
                args['color'] = self.Settings.whatColor
            if self.Settings.whatOutlinesEnabled:
                args['outlines'] = [(renpy.display.core.absolute(self.Settings.whatOutlinesWidth or 0), self.Settings.whatOutlinesColor or '#000', renpy.display.core.absolute(1), renpy.display.core.absolute(1)),(renpy.display.core.absolute(self.Settings.whatOutlinesWidth or 0), self.Settings.whatOutlinesColor or '#000', renpy.display.core.absolute(-1), renpy.display.core.absolute(-1))]
            else:
                args['outlines'] = []
            if self.Settings.whatBold != None: args['bold'] = self.Settings.whatBold
            if self.Settings.whatItalic != None: args['italic'] = self.Settings.whatItalic
            args['size'] = scalePxInt(self.Settings.whatSize or TextBoxSettings.defaultValues['whatSize'])
            args['textalign'] = self.Settings.whatAlign
            args['xalign'] = self.Settings.whatAlign
            
            
            prefixedArgs = {}
            for key,val in args.items():
                prefixedArgs['what_{}'.format(key)] = val
            
            if not self.Settings.customSayScreen:
                prefixedArgs = self._m1_textbox__stripDisallowedSayArgs(prefixedArgs)
            
            return prefixedArgs
        
        def _m1_textbox__stripUnwantedStyleArgs(self, args):
            """ Remove unwanted styling arguments """
            allowedArgs = ['color','italic','bold','outlines','slow_abortable']
            overrideArgs = {'ypos': None, 'xpos': None, 'xalign': None, 'yalign': None, 'xoffset': None, 'yoffset': None} 
            newArgs = {}
            
            for arg in args:
                if not self.Settings.customSayScreen or arg in allowedArgs:
                    newArgs[arg] = args[arg]
                elif arg in overrideArgs: 
                    newArgs[arg] = overrideArgs[arg]
            
            return newArgs
        
        def _m1_textbox__stripDisallowedSayArgs(self, args):
            """ Strip argument that are not allowed when using the default say screen """
            disallowedArgs = ['xalign','textalign','style','what_xalign','what_textalign','what_style']
            newArgs = {}
            
            for arg in args:
                if not arg in disallowedArgs:
                    newArgs[arg] = args[arg]
            
            return newArgs
        
        def _m1_textbox__sayReplace(self, who, *args, **kwargs):
            if self._m1_textbox__originalSayArgCallback:
                args, kwargs = self._m1_textbox__originalSayArgCallback(who, *args, **kwargs)
            
            if self.enabled:
                if not renpy.get_screen('URM_textboxCustomizer'): 
                    self.Settings = TextBoxSettings(who)
                if self.Settings.customSayScreen:
                    kwargs['screen'] = 'URM_say' 
                self._m1_textbox__imageTag = who.image_tag if hasattr(who, 'image_tag') else None
                self.whoArgs = self._m1_textbox__createWhoArgs(who.who_args if hasattr(who, 'who_args') else {})
                self.whatArgs = self._m1_textbox__createWhatArgs(who.what_args if hasattr(who, 'what_args') else {})
                kwargs.update(self.whoArgs)
                kwargs.update(self.whatArgs)
            
            return args, kwargs
        
        def _m1_textbox__captureSayScreen(self, screenName, *args, **kwargs):
            """
            Ren'Py will call the original say screen with kwargs={'who': None, 'what': ''} to show the screen's transition, before opening the actual (filled) say screen.
            This will prevent Ren'Py from showing the `renpy.config.window_show_transition` and `renpy.config.window_hide_transition`.
            """
            if self.enabled and screenName == 'say' and 'who' in kwargs and not kwargs['who'] and 'what' in kwargs and not kwargs['what']: 
                pass
            else:
                self._m1_textbox__originalShowScreen(screenName, *args, **kwargs)
        
        def attach(self):
            if renpy.config.say_arguments_callback != self._m1_textbox__sayReplace: 
                self._m1_textbox__originalSayArgCallback = renpy.config.say_arguments_callback
                renpy.config.say_arguments_callback = self._m1_textbox__sayReplace
            
            if renpy.display.screen.show_screen != self._m1_textbox__captureSayScreen:
                self._m1_textbox__originalShowScreen = renpy.display.screen.show_screen
                renpy.display.screen.show_screen = self._m1_textbox__captureSayScreen

    class TextBoxSettings(x52NonPicklable):
        defaultValues = {
            
            'customSayScreen': True, 
            
            'whoShown': True,
            'whoColor': None,
            'whoOutlinesEnabled': True,
            'whoOutlinesWidth': 2,
            'whoOutlinesColor': '#000',
            'whoBold': None,
            'whoItalic': None,
            'whoSize': 32,
            'whoXAlign': 0.0,
            'whoXPadding': 10,
            'whoHeight': 150,
            'whoWidth': 100,
            'whoPosition': 0.5,
            'whoResizeBackground': False,
            'whoBackgroundEnabled': False,
            'whoBackground': '#1D267D99',
            'whoBackgroundGradient': False,
            'whoBackgroundCharacterColor': False,
            'whoFont': None,
            
            'sideImageShown': True,
            'sideImagePos': 'left',
            
            'whatColor': None,
            'whatColorFromCharacter': False,
            'whatOutlinesEnabled': True,
            'whatOutlinesWidth': 2,
            'whatOutlinesColor': '#000',
            'whatBold': None,
            'whatItalic': None,
            'whatSize': 32,
            'whatAlign': 0.0,
            'whatXPadding': 10,
            'whatHeight': 150,
            'whatWidth': 100,
            'whatPosition': 0.5,
            'whatResizeBackground': False,
            'whatBackgroundEnabled': True,
            'whatBackground': '#5C469C99',
            'whatBackgroundGradient': True,
            'whatBackgroundCharacterColor': False,
            'whatFont': None,
        }
        fontOptions = OrderedDict([
            ('DejaVu Sans', 'DejaVuSans.ttf'),
            ('Roboto', '0x52-URM/framework/Roboto-Regular.ttf'),
            ('Roboto Mono', '0x52-URM/RobotoMono.ttf'),
            ('Dancing Script', '0x52-URM/DancingScript.ttf'),
            ('Caveat', '0x52-URM/Caveat.ttf'),
            ('Comfortaa', '0x52-URM/Comfortaa.ttf'),
        ])
        
        _m1_textbox__tempValues = None
        _m1_textbox__values = None
        _m1_textbox__valuesChar = None 
        
        def __init__(self, char=None):
            TextBoxSettings._m1_textbox__tempValues = None
            
            if TextBoxSettings._m1_textbox__valuesChar != char: 
                TextBoxSettings._m1_textbox__values = self._m1_textbox__getSettingsForChar(char)
                TextBoxSettings._m1_textbox__valuesChar = char 
        
        @property
        def store(self):
            if URMFiles.file['textboxCustomizations'] == None: URMFiles.file.addStore('textboxCustomizations')
            return URMFiles.file['textboxCustomizations']
        
        def clear(self):
            URMFiles.file.clearStore('textboxCustomizations')
        
        def remove(self, charVarName):
            if charVarName in self.store:
                del self.store[str(charVarName)]
        
        @property
        def tempValues(self):
            return TextBoxSettings._m1_textbox__tempValues
        
        @property
        def values(self):
            return TextBoxSettings._m1_textbox__values
        
        def _m1_textbox__getSettingsForChar(self, char):
            if self.store: 
                if isinstance(char, basestring) and char in self.store: 
                    return self.store[char]
                elif isinstance(char, renpy.store.ADVCharacter): 
                    for charVarName in self.store.keys():
                        if hasattr(renpy.store, charVarName) and getattr(renpy.store, charVarName) == char:
                            return self.store[charVarName]
                
                
                if 'None' in self.store:
                    return self.store['None']
        
        def enableTemp(self, charVarName):
            TextBoxSettings._m1_textbox__tempValues = (self._m1_textbox__getSettingsForChar(charVarName) or {}).copy()
        
        def commitTemp(self, charVarName):
            if self.tempValues: 
                self.store[str(charVarName)] = self.tempValues
            elif str(charVarName) in self.store: 
                del self.store[str(charVarName)]
            TextBoxSettings._m1_textbox__tempValues = None
        
        def dismissTemp(self):
            TextBoxSettings._m1_textbox__tempValues = None
            renpy.restart_interaction()
        
        def __getattr__(self, attr):
            if attr in TextBoxSettings.defaultValues:
                return self.get(attr)
        
        def __setattr__(self, attr, value):
            if attr in TextBoxSettings.defaultValues:
                self.set(attr, value)
        
        def get(self, name):
            if self.tempValues != None:
                if name in self.tempValues:
                    return self.tempValues[name]
            elif self.values and name in self.values:
                return self.values[name]
            
            
            if name in TextBoxSettings.defaultValues:
                return TextBoxSettings.defaultValues[name]
        
        def set(self, name, value):
            if self.tempValues != None:
                self.tempValues[name] = value
            
            renpy.restart_interaction()

    class TextBoxSettingCallback(x52NonPicklable):
        def __init__(self, settingName):
            self.settingName = settingName
        
        def __call__(self, value):
            setattr(TextBox.Settings, self.settingName, value)

init 999 python in x52URM:
    _constant = True

    if not pendingUpdate:
        
        TextBox.attach()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
