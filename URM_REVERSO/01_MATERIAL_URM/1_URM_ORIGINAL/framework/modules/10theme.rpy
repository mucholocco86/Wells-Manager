
init -999 python in x52URM:
    _constant = True
    import re

    class ThemeProvider(x52NonPicklable):
        defaultTheme = {
            'text': '#e4e4e4',
            'primary': '#D4ADFC',
            'secondary': '#5C469C',
            'tertiary': '#1D267D',
            'background': '#0C134F',
        }
        
        def __init__(self):
            self._m1_10theme__theme = ThemeProvider.defaultTheme.copy()
            self._m1_10theme__isDark = None
            self.colors = ThemeColors(self, {
                'warningBg': '#fff4ce',
                'warningText': '#797673',
                'severeWarningBg': '#fed9cc',
                'severeWarningText': '#d83b01',
                'errorBg': '#fde7e9',
                'errorText': '#a80000',
                'successBg': '#dff6dd',
                'successText': '#107c10',
            })
        
        def __getattr__(self, key):
            if key in self._m1_10theme__theme:
                return self._m1_10theme__theme[key]
            elif key.endswith('Darker') and key[:-6] in self._m1_10theme__theme:
                return self.colorBrightness(self._m1_10theme__theme[key[:-6]], -30)
            elif key.endswith('Lighter') and key[:-7] in self._m1_10theme__theme:
                return self.colorBrightness(self._m1_10theme__theme[key[:-7]], 30)
            else:
                translucent = re.search(r'(.+)Translucent(\d+)$', key)
                if translucent and translucent.group(1) in self._m1_10theme__theme:
                    return self.colorAlpha(self._m1_10theme__theme[translucent.group(1)], float(255-int(translucent.group(2)))/255)
        
        def getButtonBg(self, bgColor, borderColor):
            return renpy.display.imagelike.Frame(renpy.store.LiveComposite(
                    (6,6),
                    (0,0), renpy.store.LiveComposite((2,6), (0,0), renpy.display.imagelike.Solid(borderColor)), 
                    (0,0), renpy.store.LiveComposite((6,2), (0,0), renpy.display.imagelike.Solid(borderColor)), 
                    (4,0), renpy.store.LiveComposite((2,6), (0,0), renpy.display.imagelike.Solid(borderColor)), 
                    (0,4), renpy.store.LiveComposite((6,2), (0,0), renpy.display.imagelike.Solid(borderColor)), 
                    (2,2), renpy.store.LiveComposite((2,2), (0,0), renpy.display.imagelike.Solid(bgColor)), 
                ), 2, 2)
        
        def setTheme(self, theme):
            if not isinstance(theme, dict):
                raise Exception('0x52: supplied theme is not a dict')
            elif not self.isCurrentTheme(theme):
                self._m1_10theme__theme.update(theme)
                self._m1_10theme__isDark = None
                renpy.store.gui.rebuild()
        
        def isCurrentTheme(self, theme):
            """ Check if `theme` equals the current theme """
            if isinstance(theme, dict):
                for key in theme:
                    if key in self._m1_10theme__theme and theme[key] != self._m1_10theme__theme[key]:
                        return False
                return True
            else:
                return False
        
        def colorBrightness(self, color, change):
            rgba = self.hex2rgba(color)
            r = max(0, min(255, rgba[0] + change))
            g = max(0, min(255, rgba[1] + change))
            b = max(0, min(255, rgba[2] + change))
            return self.rgba2hex((r, g, b, rgba[3]))
        
        def hex2rgba(self, color):
            if not color.startswith('#'):
                raise Exception('Hex color should start with #')
            elif len(color) == 4: 
                return (int(color[1]*2, 16), int(color[2]*2, 16), int(color[3]*2, 16), 255)
            elif len(color) == 5: 
                return (int(color[1]*2, 16), int(color[2]*2, 16), int(color[3]*2, 16), int(color[4]*2, 16))
            elif len(color) == 7: 
                return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), 255)
            elif len(color) == 9: 
                return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), int(color[7:9], 16))
            else:
                raise Exception('Invalid hex color "{}"'.format(color))
        
        def rgba2hex(self, rgba):
            if not len(rgba) == 4:
                raise Exception('RGBA should exists out of 4 parts. Got {} parts'.format(len(rgba)))
            else:
                return '#{:02x}{:02x}{:02x}{:02x}'.format(rgba[0], rgba[1], rgba[2], rgba[3])
        
        def colorAlpha(self, color, alpha):
            """ `color` should be a hex representation and `alpha` should be between 0 and 1 """
            if 0 < alpha > 1:
                raise Exception('Alpha value should be between 0 and 1. Got {}'.format(alpha))
            else:
                rgba = self.hex2rgba(color)
                return self.rgba2hex((rgba[0], rgba[1], rgba[2], int(255*alpha)))
        
        @property
        def isDark(self):
            if self._m1_10theme__isDark is None:
                self._m1_10theme__isDark = not self.isLightColor(self.background)
            return self._m1_10theme__isDark
        
        def isLightColor(self, color):
            """ Determine if `color` is on the lighter or darker side """
            import math
            rgba = self.hex2rgba(color)
            hsp = math.sqrt(0.299 * (rgba[0] * rgba[0]) + 0.587 * (rgba[1] * rgba[1]) + 0.114 * (rgba[2] * rgba[2])) 
            return (hsp > 127.5)            


    class ThemeColors(x52NonPicklable):
        def __init__(self, themeProvider, colors, overrideMappings=None):
            self._m1_10theme__provider = themeProvider
            self._m1_10theme__colors = colors
            self._m1_10theme__themeMappings = {
                'dialogBg': 'backgroundTranslucent25',
                'dialogTitleBar': 'primaryTranslucent25',
                'dialogBorder': 'textTranslucent180',
                
                'buttonBg': 'background',
                'buttonBgHover': 'backgroundLighter',
                'buttonBgDisabled': 'backgroundDarker',
                'buttonBorder': 'text',
                'buttonBorderDisabled': 'textTranslucent100',
                'buttonText': 'text',
                'buttonTextDisabled': 'textTranslucent100',
                
                'buttonPrimaryBg': 'primary',
                'buttonPrimaryBgHover': 'primaryLighter',
                'buttonPrimaryBgDisabled': 'primaryDarker',
                'buttonPrimaryBorder': 'primary',
                'buttonPrimaryText': 'background',
                'buttonPrimaryTextDisabled': 'backgroundTranslucent100',
                
                'buttonSecondaryBg': 'secondary',
                'buttonSecondaryBgHover': 'secondaryLighter',
                'buttonSecondaryBgDisabled': 'secondaryDarker',
                'buttonSecondaryBorder': 'text',
                'buttonSecondaryBorderDisabled': 'textTranslucent100',
                'buttonSecondaryText': 'text',
                'buttonSecondaryTextDisabled': 'textTranslucent100',
                
                'buttonCancelBg': 'errorBg',
                'buttonCancelBgHover': 'errorBgLighter',
                'buttonCancelBgDisabled': 'errorBgDarker',
                'buttonCancelBorder': 'errorText',
                'buttonCancelBorderDisabled': 'errorTextTranslucent100',
                'buttonCancelText': 'errorText',
                'buttonCancelTextDisabled': 'errorTextTranslucent100',
                
                'buttonSuccessBg': 'successBg',
                'buttonSuccessBgHover': 'successBgLighter',
                'buttonSuccessBgDisabled': 'successBgDarker',
                'buttonSuccessBorder': 'successText',
                'buttonSuccessBorderDisabled': 'successTextTranslucent100',
                'buttonSuccessText': 'successText',
                'buttonSuccessTextDisabled': 'successTextTranslucent100',
                
                'scrollBg': 'secondary',
                'scrollThumb': 'primary',
                'scrollThumbHover': 'primaryLighter',
            }
            self.overrideMappings = overrideMappings or {}
        
        @property
        def mappings(self):
            return self._m1_10theme__themeMappings
        
        def __getattr__(self, key):
            if key in self.overrideMappings or key in self._m1_10theme__themeMappings:
                mapping = self.overrideMappings[key] if key in self.overrideMappings else self._m1_10theme__themeMappings[key]
                if mapping in self._m1_10theme__colors:
                    return self._m1_10theme__colors[mapping]
                elif mapping.endswith('Darker') and mapping[:-6] in self._m1_10theme__colors:
                    return self._m1_10theme__provider.colorBrightness(self._m1_10theme__colors[mapping[:-6]], -30)
                elif mapping.endswith('Lighter') and mapping[:-7] in self._m1_10theme__colors:
                    return self._m1_10theme__provider.colorBrightness(self._m1_10theme__colors[mapping[:-7]], 30)
                else:
                    translucent = re.search(r'(.+)Translucent(\d+)$', mapping)
                    if translucent and translucent.group(1) in self._m1_10theme__colors:
                        return self._m1_10theme__provider.colorAlpha(self._m1_10theme__colors[translucent.group(1)], float(255-int(translucent.group(2)))/255)
                
                if hasattr(self._m1_10theme__provider, mapping):
                    return getattr(self._m1_10theme__provider, mapping)
            
            return self._m1_10theme__colors[key]

    Theme = ThemeProvider()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
