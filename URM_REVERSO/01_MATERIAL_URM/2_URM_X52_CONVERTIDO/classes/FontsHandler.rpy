



init 999 python in x52URM:
    _constant = True

    class FontsHandler(x52NonPicklable):
        iconFonts = ['MaterialIcons-Regular.ttf','MaterialIconsOutlined-Regular.otf']
        
        def __init__(self):
            if hasattr(renpy.config, 'font_transforms'):
                for font in renpy.config.font_transforms:
                    renpy.config.font_transforms[font] = self.createHandler(font, renpy.config.font_transforms[font])
        
        def createHandler(self, fontName, originalMethod):
            def handler(requestedFontName):
                if requestedFontName.endswith(FontsHandler.iconFonts[0]) or requestedFontName.endswith(FontsHandler.iconFonts[1]):
                    return requestedFontName
                elif originalMethod:
                    return originalMethod(requestedFontName)
            
            return handler


    FontsHandler()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
