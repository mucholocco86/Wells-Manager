
init -1000 python in x52URM:
    _constant = True


    archivePath = None

    pendingUpdate = None

    class x52NonPicklable(python_object):
        
        def __setstate__(self, d):
            pass
        def __getstate__(self):
            return {}
        def __getnewargs__(self):
            return ()
        def __iter__(self):
            return None
        def itervalues(self):
            return None

    def getScaleFactor():
        return renpy.config.screen_height / 1080.0 

    def scalePx(size):
        """ Change size from 1080p to game resolution """
        return size*getScaleFactor()

    def scalePxInt(size):
        return int(scalePx(size))

    def max(val1, val2):
        return val1 if val1 > val2 else val2

    def min(val1, val2):
        return val1 if val1 < val2 else val2
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
