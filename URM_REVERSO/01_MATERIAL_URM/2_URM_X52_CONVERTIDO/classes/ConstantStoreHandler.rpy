



init 999 python in x52URM:
    _constant = True

    class ConstantStoreHandler(x52NonPicklable):
        def __init__(self):
            if renpy.version_tuple < (7, 6, 0, 0): 
                try:
                    renpy.python.StoreDict.get_changes = self.createGetChangesHandler(renpy.python.StoreDict.get_changes)
                    renpy.python.RollbackLog.complete = self.createRollbackCompleteHandler(renpy.python.RollbackLog.complete)
                    pass
                except Exception as e:
                    print('0x52: Failed to attach ConstantStoreHandler: {}'.format(e))
        
        def createGetChangesHandler(self, originalMethod):
            def handler(storeDict, *args, **kwargs):
                try:
                    if storeDict.get('_constant', False):
                        return ({}, set())
                except Exception as e:
                    print('0x52: Failed to handle get_changes. {}'.format(e))
                
                return originalMethod(storeDict, *args, **kwargs)
            
            return handler
        
        def createRollbackCompleteHandler(self, originalMethod):
            def handler(rollbackLog, *args, **kwargs):
                originalMethod(rollbackLog, *args, **kwargs)
                
                try:
                    for name in rollbackLog.current.stores.keys():
                        if renpy.python.store_dicts[name].get('_constant', False):
                            del rollbackLog.current.stores[name]
                            if hasattr(rollbackLog.current, 'delta_ebc'):
                                del rollbackLog.current.delta_ebc[name]
                except Exception as e:
                    print('0x52: Failed to handle RollbackLog.complete. {}'.format(e))
            
            return handler


    ConstantStoreHandler()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
