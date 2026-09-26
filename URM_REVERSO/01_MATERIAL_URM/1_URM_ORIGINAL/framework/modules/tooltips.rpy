
init -999 python in x52URM:
    _constant = True

    class Tooltip(x52NonPicklable):
        currentText = None
        currentTextByScreenname = {}
        
        def __init__(self, text=None):
            self.text = text
        
        def __call__(self):
            Tooltip.currentText = self.text
            
            currentScreen = renpy.current_screen()
            if currentScreen and hasattr(currentScreen, 'screen_name') and isinstance(currentScreen.screen_name, tuple) and len(currentScreen.screen_name) >= 1:
                Tooltip.currentTextByScreenname[currentScreen.screen_name[0]] = self.text
            
            renpy.restart_interaction()
        
        def __str__(self):
            return Tooltip.currentText
        
        @staticmethod
        def get(screenName=None):
            if screenName:
                if screenName in Tooltip.currentTextByScreenname:
                    return Tooltip.currentTextByScreenname[screenName]
            else:
                return Tooltip.currentText
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
