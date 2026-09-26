
init 1 python in x52URM:

    class StatesClass(x52NonPicklable):
        defaultValues = {
            'updateNotificationShown': False, 
            'gestureInitialized': False,
        }
        _m1_states__states = {}
        
        def __init__(self):
            self._m1_states__states = {}
        
        def __getattr__(self, attr):
            if attr in StatesClass.defaultValues:
                if attr in self._m1_states__states:
                    return self._m1_states__states[attr]
                else:
                    return StatesClass.defaultValues[attr]
            else:
                print('0x52: Something requested an unknown state "{}"'.format(attr))
        
        def __setattr__(self, attr, value):
            if attr in StatesClass.defaultValues:
                self._m1_states__states[attr] = value    
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
