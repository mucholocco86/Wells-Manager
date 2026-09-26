
init 2 python in x52URM:
    _constant = True

    class APIClass(x52API):
        
        @property
        def updateAvailable(self):
            return x52API.updateAvailable(self, Settings.updateChannel)
        
        @property
        def hwid(self):
            if self._m1_API__hwid == None:
                if Settings.id: 
                    self._m1_API__hwid = Settings.id
                else:
                    self._m1_API__hwid = self._m1_API__generateHwid() 
                    Settings.saveId(self._m1_API__hwid)
            
            return self._m1_API__hwid
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
