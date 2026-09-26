
init 2 python in x52URM:
    _constant = True


    from collections import OrderedDict as _OrderedDict

    class OrderedDict(_OrderedDict):
        def changePos(self, sourceKey, targetKey):
            newDict = OrderedDict()
            
            for k in self:
                if k == targetKey: 
                    newDict[sourceKey] = self[sourceKey]
                
                if k != sourceKey: 
                    newDict[k] = self[k]
            
            
            self.clear()
            self.update(newDict)
        
        def sort(self, reverse=False, sortByAttr=None):
            try:
                items = list(self.items()) 
                newOrder = None
                if sortByAttr:
                    if len(items) > 0:
                        if hasattr(items[0][1], sortByAttr):
                            newOrder = sorted(items, reverse=reverse, key=lambda props: getattr(props[1], sortByAttr).lower())
                        elif sortByAttr in items[0][1]:
                            newOrder = sorted(items, reverse=reverse, key=lambda props: props[1][sortByAttr].lower())
                else:
                    newOrder = sorted(items, reverse=reverse, key=lambda props: props[0].lower())
                
                if newOrder:
                    self.clear()
                    self.update(newOrder)
            
            except Exception as e:
                print('0x52: Sorting failed with error: {}'.format(e))


    class ColorPicker(x52NonPicklable):
        def __init__(self, defaultColor=None):
            if isinstance(defaultColor, basestring) and defaultColor.startswith('#'):
                if len(defaultColor) == 4: 
                    self.rgba = (int(defaultColor[1]*2, 16), int(defaultColor[2]*2, 16), int(defaultColor[3]*2, 16), 1.0)
                if len(defaultColor) == 5: 
                    self.rgba = (int(defaultColor[1]*2, 16), int(defaultColor[2]*2, 16), int(defaultColor[3]*2, 16), int(defaultColor[4]*2, 16)/float(255))
                elif len(defaultColor) == 7: 
                    self.rgba = (int(defaultColor[1:3], 16), int(defaultColor[3:5], 16), int(defaultColor[5:7], 16), 1.0)
                elif len(defaultColor) == 9: 
                    self.rgba = (int(defaultColor[1:3], 16), int(defaultColor[3:5], 16), int(defaultColor[5:7], 16), int(defaultColor[7:9], 16)/float(255))
                else:
                    self.rgba = (255, 255, 255, 1.0)
            else:
                self.rgba = defaultColor or (255, 255, 255, 1.0)
        
        @property
        def hex(self):
            return '#{:02x}{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b, int(self.a * 255))
        
        @property
        def r(self):
            return self.rgba[0]
        
        @r.setter
        def r(self, val):
            self.rgba = (val or 0, self.g, self.b, self.a)
        
        @property
        def g(self):
            return self.rgba[1]
        
        @g.setter
        def g(self, val):
            self.rgba = (self.r, val or 0, self.b, self.a)
        
        @property
        def b(self):
            return self.rgba[2]
        
        @b.setter
        def b(self, val):
            self.rgba = (self.r, self.g, val or 0, self.a)
        
        @property
        def a(self):
            return self.rgba[3] if len(self.rgba) > 3 else 1.0
        
        @a.setter
        def a(self, val):
            self.rgba = (self.r, self.g, self.b, val or 1.0)


    def ScaleImage(img, maxWidth, maxHeight, scaleSmallestDiff=False):
        if isinstance(img, basestring):
            img = renpy.display.im.Image(img)
        elif isinstance(img, renpy.display.transform.ATLTransform) and len(img.block.statements) > 0:
            for statement in img.block.statements:
                if hasattr(statement, 'child') and isinstance(statement.child, renpy.display.im.Image):
                    img = statement.child
                    break
        
        imgSize = renpy.display.render.render(img, renpy.config.screen_width, renpy.config.screen_height, 0, 0)
        widthScale = maxWidth / imgSize.width if maxWidth < imgSize.width else 1.0
        heightScale = maxHeight / imgSize.height if maxHeight < imgSize.height else 1.0
        
        if widthScale > heightScale:
            if scaleSmallestDiff:
                return renpy.display.im.FactorScale(img, widthScale)
            else:
                return renpy.display.im.FactorScale(img, heightScale)
        else:
            if scaleSmallestDiff:
                return renpy.display.im.FactorScale(img, heightScale)
            else:
                return renpy.display.im.FactorScale(img, widthScale)

    class CancelSkipping(x52NonPicklable):
        def __call__(self):
            renpy.config.skipping = None

    def currentFileNameLine():
        try:
            fileLine = renpy.get_filename_line()
            return '{}:{}'.format(renpy.os.path.splitext(renpy.os.path.basename(fileLine[0]))[0], fileLine[1])
        except e as Exception:
            return 'Unknown'

    def currentFilePathLine():
        try:
            fileLine = renpy.get_filename_line()
            return '{}:{}'.format(fileLine[0], fileLine[1])
        except e as Exception:
            return 'Unknown'

    def getScreenSize(screenName):
        screen = renpy.display.screen.get_screen_variant(screenName)
        if not screen: raise Exception('0x52: Tried to get size for non existing screen "{}"'.format(screenName))
        screenLayer = renpy.display.screen.get_screen_layer(screenName)
        d = renpy.display.screen.ScreenDisplayable(screen, screen.tag, screenLayer)
        d.update()
        
        if hasattr(d, 'child') and d.child and hasattr(d.child, 'children') and len(d.child.children):
            return getDisplayableSize(d.child.children[0])
        else:
            raise Exception('0x52: Tried to get size for screen "{}", but the screen didn\'t have any children'.format(screenName))

    def getDisplayableSize(displayable):
        if not isinstance(displayable, renpy.display.core.Displayable):
            raise Exception('0x52: Tried to get the size of something else then a displayable. Supplied type: {}'.format(type(displayable)))
        
        rendered = renpy.display.render.render(displayable, renpy.config.screen_width, renpy.config.screen_height, 0, 0)
        return [int(rendered.width), int(rendered.height)]
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
