




init python:
    x52MF2.load(['dialogs','api','inputs','tooltips'], 'x52URM', '0x52-URM/framework')










init 52 python in x52URM:
    _constant = True 

    version = '2.6.2'
    apiId = 'mznoxpzn4w/93nmxxw1zm'


    Settings = SettingsClass()
    States = StatesClass()
    URMFiles = URMFilesClass()
    VarsStore = VarsStoreClass()
    LabelsStore = LabelsStoreClass()
    Search = SearchClass()
    Choices = ChoicesClass()
    PathDetection = PathDetectionClass()
    TextBox = TextBoxClass()
    TextRepl = TextReplacementsClass()
    Gamesaves = GameSavesClass()
    API = APIClass(apiId, devMode=renpy.loadable('0x52-URM/.gitignore'))
    LabelMon = LabelMonClass()
    Notifications = NotificationsClass()
    Snapshots = SnapshotsClass()
    StoreMonitor = StoreMonitorClass()
    CodeView = CodeViewClass()
    ProgressBar = ProgressBarClass()

    def init():
        LabelMon.init()
        if not 's_e_n' in renpy.config.gestures:
            renpy.config.gestures['s_e_n'] = 'alt_K_m'
            States.gestureInitialized = True
        
        if not 'urm_notl' in renpy.config.custom_text_tags: 
            def notl(tag, argument, contents): return contents
            renpy.config.custom_text_tags['urm_notl'] = notl

    def afterLoad(): 
        renpy.show_screen('URM_overlay')
        if 'URM_quickmenu' not in renpy.config.overlay_screens: renpy.config.overlay_screens.append('URM_quickmenu')
        StoreMonitor.init()
        
        SetDialogTransparency(Settings.themeTransparency, doNotRebuild=True, doNotSave=True)()
        if Settings.theme != 'Default':
            SetTheme(Settings.theme, doNotSave=True)()
        
        URMFiles.autoLoad()
        if Settings.seenWelcome < 2:
            renpy.run(renpy.store.Show('URM_welcome'))
        elif not States.updateNotificationShown:
            States.updateNotificationShown = True
            if API.updateAvailable and API.updateAvailable != Settings.skipUpdate:
                renpy.show_screen('URM_update', isNotification=True)

    def onLabelCalled(label, called):
        if label == 'start':
            afterLoad()
        elif label == '_start_replay':
            renpy.show_screen('URM_overlay')

    class Open(x52NonPicklable):
        def __init__(self, screen=None):
            self.screen = screen
        
        def __call__(self):
            if renpy.store._in_replay:
                Confirm("Do you want to end the current replay?", renpy.end_replay, title='End replay')()
            else:
                if self.screen:
                    Settings.currentScreen = self.screen
                
                if Settings.warningDisabled:
                    renpy.take_screenshot()
                    renpy.run(renpy.store.Show('URM_main'))
                else:
                    renpy.run(renpy.store.Show('URM_warning'))

    def scale(percentage, size):
        return int((percentage / 100.0) * size)

    def scaleX(percentage):
        return scale(percentage, renpy.config.screen_width)

    def scaleY(percentage):
        return scale(percentage, renpy.config.screen_height)

    def scaleText(text, percentageOrPixels, style='x52URM_text', pixelTarget=False, escapeStyling=False, reverse=False):
        try:
            import re
            
            if pixelTarget:
                targetSize = scalePx(percentageOrPixels)
            else:
                targetSize = scaleX(percentageOrPixels)
            if escapeStyling:
                text = re.sub('\{.*?\}', '{\g<0>', text)
            else:
                text = re.sub('\{.*?\}', '', text)
            textLength = len(text)
            
            for currentLength in range(5, textLength+1):
                shortenedText = text[len(text)-currentLength:] if reverse else text[:currentLength]
                if renpy.store.Text(shortenedText, None, False, False, style=style).size()[0] > targetSize: 
                    textLength = currentLength-1 
                    break
            
            if textLength < len(text):
                if reverse:
                    return '...'+text[len(text)-textLength+1:]
                else:
                    return text[:textLength-1]+'...'
            else:
                return text[:textLength]
        except:
            return text

    def touchDragged(drags, *args, **kwargs):
        try:
            Settings.touchPosition = (drags[0].x, drags[0].y)
        except Exception as e:
            print('0x52: Failed to save touchbutton position: {}'.format(e))

    def progressDragged(drags, *args, **kwargs):
        try:
            Settings.progressPosition = (drags[0].x, drags[0].y)
        except Exception as e:
            print('0x52: Failed to save progress position: {}'.format(e))

    class OpenConsole(x52NonPicklable):
        def __call__(self):
            renpy.store._console.enter()

    class URMReplay(x52NonPicklable):
        def __init__(self, label, finishAction=None, screenErrorVariable=None):
            self.label = label
            self.finishAction = finishAction
            self.screenErrorVariable = screenErrorVariable
            self._m1_main__error = None
            self._m1_main__currentScreen = None
        
        def _m1_main__replayErrorHandler(self, short, full, traceback_fn):
            self._m1_main__error = short
            return True
        
        def __call__(self):
            if not renpy.has_label(self.label):
                x52URM.Confirm('The selected label does not exist')()
            else:
                if self.screenErrorVariable:
                    self._m1_main__currentScreen = renpy.current_screen()
                
                
                replayScope = {}
                for k, v in renpy.store.__dict__.items():
                    if not k.startswith('_') and k != 'suppress_overlay':
                        replayScope[k] = v
                
                defaultErrorHandler = renpy.display.error.report_exception 
                renpy.display.error.report_exception = self._m1_main__replayErrorHandler 
                try:
                    renpy.call_replay(self.label, replayScope)
                except:
                    pass
                renpy.display.error.report_exception = defaultErrorHandler 
                
                if self._m1_main__error and self.screenErrorVariable and self._m1_main__currentScreen: 
                    if self.screenErrorVariable in self._m1_main__currentScreen.scope:
                        self._m1_main__currentScreen.scope['errorMessage'] = 'Replay failed with error:\n{}'.format(self._m1_main__error)
                elif self.finishAction:
                    self.finishAction()
                
                renpy.restart_interaction()


init 1999 python in _console:
    console = DebugConsole()

init 999 python:
    if not x52URM.pendingUpdate:
        x52URM.init()
        
        x52MF2.loadFile('0x52-URM/URM_styles.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/main.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/search.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/vars.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/snapshots.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/labels.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/watchpanel.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/textbox.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/textrepl.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/choices.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/gamesaves.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/update.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/paths.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/progress.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/options.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/utils.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/quickmenu.rpy.x52', 'x52URM')
        x52MF2.loadFile('0x52-URM/screens/codeview.rpy.x52', 'x52URM')
        
        renpy.config.after_load_callbacks.append(x52URM.afterLoad)
        x52URM.LabelMon.onLabelCalled.append(x52URM.onLabelCalled)
        
        if x52URM.Settings.autoUpdateCheck:
            x52URM.API.fetchUpdate(NullAction(), NullActionWithArgs())
        
        if x52URM.Settings.skipSplashscreen:
            renpy.config.label_overrides['splashscreen'] = 'URM_splashscreen'

    else: 
        renpy.config.after_load_callbacks.append(x52URM.pendingUpdate)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
