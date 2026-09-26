
init 1 python:
    if not 'SetLocalVariable' in globals():
        def SetLocalVariable(name, value): 
            return SetDict(renpy.sys._getframe(1).f_locals, name, value)


    if not hasattr(renpy, 'get_registered_image'):
        def getRegisteredImage(name):
            if not isinstance(name, tuple):
                name = tuple(name.split())
            return renpy.display.image.images.get(name)
        
        setattr(renpy, 'get_registered_image', getRegisteredImage)

    class NullActionWithArgs(NullAction):
        def __call__(self, *args, **kwargs):
            return

    class URMFunctionWithArgs(Function):
        """ Like Ren'Py's Function class, but ignoring arguments """
        def __call__(self, *args, **kwargs):
            return self.callable(*self.args, **self.kwargs)

    class URMGetScreenVariable(x52URM.x52NonPicklable):
        def __init__(self, name, key=None):
            self.name = name
            self.key = key
        
        def __call__(self):
            cs = renpy.current_screen()
            
            if not cs or not self.name in cs.scope:
                return
            
            if(self.key):
                key = self.key if not callable(self.key) else self.key()
                return cs.scope[self.name][key]
            else:
                return cs.scope[self.name]

    def URMTimeToText(t):
        if t:
            import time
            return _strftime('%a, %b %d %Y, %H:%M', time.localtime(t))
        else:
            return 'unknown date'
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
