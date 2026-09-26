
init 3 python in x52URM:
    _constant = True

    class VarsStoreClass(x52NonPicklable):
        @property
        def store(self):
            if URMFiles.file['vars'] == None: URMFiles.file.addStore('vars')
            return URMFiles.file['vars']
        
        def clear(self):
            URMFiles.file.clearStore('vars')
        
        @property
        def watchedStore(self):
            if URMFiles.file['watched'] == None: URMFiles.file.addStore('watched')
            return URMFiles.file['watched']
        
        def clearWatched(self):
            URMFiles.file.clearStore('watched')
        
        def remember(self, varName, displayName=None):
            """ Add `varName` to remembered list """
            if callable(displayName): displayName = displayName()
            
            if varName in self.store:
                self.store[varName] = {'name': displayName or self.store[varName]['name']}
            else:
                self.store[varName] = {'name': displayName or varName}
        
        def forget(self, varName):
            """ Remove `varName` from remembered list """
            if self.has(varName):
                del self.store[varName]
        
        def has(self, varName):
            return varName in self.store
        
        def changePos(self, sourceVarName, targetVarName):
            if self.has(sourceVarName) and self.has(targetVarName):
                self.store.changePos(sourceVarName, targetVarName)
        
        def sort(self, reverse=False):
            self.store.sort(reverse, sortByAttr='name')
        
        def freeze(self, varName):
            if not self.has(varName): self.remember(varName)
            self.store[varName]['frozen'] = True
        
        def unfreeze(self, varName):
            if self.has(varName) and 'frozen' in self.store[varName]:
                del self.store[varName]['frozen']
        
        def isFreezable(self, varName):
            if '.' in varName or '[' in varName: 
                return False
            elif Var.getVarType(varName) in ['string','boolean','int','float']:
                return True
            else:
                return False
        
        def isFrozen(self, varName):
            return (self.has(varName) and 'frozen' in self.store[varName] and self.store[varName]['frozen'])
        
        def monitor(self, varName):
            if not self.has(varName): self.remember(varName)
            self.store[varName]['monitor'] = True
        
        def unmonitor(self, varName):
            if self.has(varName) and 'monitor' in self.store[varName]:
                del self.store[varName]['monitor']
        
        def isMonitorable(self, varName):
            return self.isFreezable(varName)
        
        def isMonitored(self, varName):
            return (self.has(varName) and 'monitor' in self.store[varName] and self.store[varName]['monitor'])
        
        def watch(self, varName, displayName):
            """Add `varName` to watchlist """
            if callable(displayName): displayName = displayName()
            
            self.watchedStore[varName] = {'name': displayName}
            Settings.showWatchPanel = True 
        
        def unwatch(self, varName):
            """ Remove `varName` from watch list """
            if self.isWatched(varName):
                del self.watchedStore[varName]
        
        def isWatched(self, varName):
            return (varName in self.watchedStore)
        
        def changePosWatched(self, sourceVarName, targetVarName):
            if self.isWatched(sourceVarName) and self.isWatched(targetVarName):
                self.watchedStore.changePos(sourceVarName, targetVarName)
        
        def sortWatched(self, reverse=False):
            self.watchedStore.sort(reverse, sortByAttr='name')
        
        def ignore(self, varName, when):
            """Add `varName` to ignore list """
            if not self.has(varName): self.remember(varName)
            if 'ignored' in self.store[varName]:
                self.store[varName]['ignored'].append(when)
            else:
                self.store[varName]['ignored'] = [when]
            self.store.unsaved = True
        
        def unignore(self, varName, when):
            """ Remove `varName` from ignore list """
            if self.has(varName) and 'ignored' in self.store[varName]:
                
                if when in self.store[varName]['ignored']: self.store[varName]['ignored'].remove(when)
                
                if not self.store[varName]['ignored']: del self.store[varName]['ignored']
                self.store.unsaved = True
        
        def isIgnored(self, varName, when=None):
            if (self.has(varName) and 'ignored' in self.store[varName] and self.store[varName]['ignored']): 
                if when:
                    return when in self.store[varName]['ignored']
                else:
                    return True
            else:
                return False
        
        def ignoredList(self, when=None):
            output = []
            for varName in self.store:
                if self.isIgnored(varName, when):
                    output.append(varName)
            return output
        
        def strContainsIgnored(self, text, when=None):
            pattern = r'\b' + r'|'.join(self.ignoredList(when)) + r'\b'
            if r'\b\b' == pattern: return False 
            return bool(renpy.re.search(pattern, text))

    class Var(x52NonPicklable):
        
        def __init__(self, varName, storeDict=None):
            self._m1_vars__varName = varName
            self._m1_vars__storeDict = storeDict
        
        @property
        def name(self):
            return self._m1_vars__varName
        
        @property
        def nameShortened(self):
            if len(self.name) > 30 and len(self.namePath) > 1:
                return '{} ... {}'.format(self.namePath[0], self.namePath[-1])
            else:
                return self.name
        
        @property
        def storeDict(self):
            return self._m1_vars__storeDict or renpy.store.__dict__
        
        @property
        def varType(self):
            if not hasattr(self, '__varType'):
                self._m1_vars__varType = Var.getValType(self.value)
            return self._m1_vars__varType
        
        @property
        def isExpandable(self):
            if not hasattr(self, '__isExpandable'):
                self._m1_vars__isExpandable = (self.varType in ['list', 'dict', 'store'] or self.varType.startswith('<class'))
            return self._m1_vars__isExpandable
        
        
        @property
        def isSupported(self):
            if not hasattr(self, '__isSupported'):
                self._m1_vars__isSupported = Var.isSupportedVarType(self.varType)
            return self._m1_vars__isSupported
        
        @property
        def isEditable(self):
            return not bool(self._m1_vars__storeDict)
        
        @property
        def namePath(self):
            """
            Split list, dict and object names.
            `var1.var2[3].var4["var 5"]` will become a list ['var1','.var2','[3]','.var4','["var 5"]']
            """
            parentName = renpy.re.findall(r"^(\w+)[\.\]]?", self.name)
            if len(parentName) != 1:
                return [self.name]
            
            children = renpy.re.findall(r"(\.\w+|\[\d+\]|\[[\"\'][\w\ ]+[\"\']\])", self.name)
            return parentName + children
        
        @property
        def value(self):
            try:
                
                currentValue = None
                for index,currentPath in enumerate(self.namePath):
                    if index == 0:
                        if currentPath in self.storeDict:
                            currentValue = self.storeDict[currentPath]
                        else:
                            return None 
                    else: 
                        if currentPath.startswith('.'): 
                            if hasattr(currentValue, currentPath[1:]):
                                currentValue = getattr(currentValue, currentPath[1:])
                            else:
                                return None
                        elif renpy.re.match(r"^\[[\"\'].+[\"\']\]$", currentPath): 
                            if currentPath[2:-2] in currentValue:
                                currentValue = currentValue[currentPath[2:-2]]
                            else:
                                return None
                        elif renpy.re.match(r"^\[\d+\]$", currentPath): 
                            currentIndex = int(currentPath[1:-1])
                            if isinstance(currentValue, list) and len(currentValue) > currentIndex:
                                currentValue = currentValue[currentIndex]
                            elif isinstance(currentValue, dict) and currentIndex in currentValue:
                                currentValue = currentValue[currentIndex]
                            else:
                                return None
                
                return currentValue
            except:
                pass
        
        def setValue(self, newValue, overruleVarType=None, operator='=', varChildKey=None):
            if not self.isEditable: return False 
            if callable(newValue): newValue = newValue()
            if callable(overruleVarType): overruleVarType = overruleVarType()
            if callable(operator): operator = operator()
            if callable(varChildKey): varChildKey = varChildKey()
            
            settableVar = self if not varChildKey else self.getChild(varChildKey)
            
            varType = overruleVarType or settableVar.varType
            isFrozen = VarsStore.isFrozen(self._m1_vars__varName)
            try:
                settableValue = None
                if varType == 'string':
                    settableValue = '"""'+newValue+'"""'
                elif varType == 'boolean':
                    settableValue = str(bool(newValue))
                elif varType == 'int' and Search.isInt(newValue):
                    settableValue = str(int(newValue))
                elif varType == 'float' and Search.isFloat(newValue):
                    settableValue = str(float(newValue))
                
                if settableValue:
                    if isFrozen: VarsStore.unfreeze(self._m1_vars__varName)
                    
                    if operator == 'append':
                        exec('renpy.store.'+settableVar.name+'.append('+settableValue+')')
                    else:
                        exec('renpy.store.'+settableVar.name+operator+settableValue)
                    return True
                else:
                    print("0x52: No valid value for {} (varType: {})".format(settableVar.name, varType))
            except Exception as e:
                print("0x52: Couldn't set value for "+settableVar.name+'. '+str(e))
                pass
            finally:
                if isFrozen: VarsStore.freeze(self._m1_vars__varName)
            return False 
        
        def delete(self):
            try:
                
                currentValue = None
                namePath = self.namePath
                lastIndex = len(namePath)-1
                for index,currentPath in enumerate(namePath):
                    if index == 0:
                        if currentPath in self.storeDict:
                            if index == lastIndex: 
                                del self.storeDict[currentPath]
                                break
                            else:
                                currentValue = self.storeDict[currentPath]
                        else:
                            break 
                    else: 
                        if currentPath.startswith('.'): 
                            if hasattr(currentValue, currentPath[1:]):
                                if index == lastIndex: 
                                    delattr(currentValue, currentPath[1:])
                                    break
                                else:
                                    currentValue = getattr(currentValue, currentPath[1:])
                            else:
                                break
                        elif renpy.re.match(r"^\[[\"\'].+[\"\']\]$", currentPath): 
                            if currentPath[2:-2] in currentValue:
                                if index == lastIndex: 
                                    del currentValue[currentPath[2:-2]]
                                    break
                                else:
                                    currentValue = currentValue[currentPath[2:-2]]
                            else:
                                break
                        elif renpy.re.match(r"^\[\d+\]$", currentPath): 
                            currentIndex = int(currentPath[1:-1])
                            if isinstance(currentValue, list) and len(currentValue) > currentIndex:
                                if index == lastIndex: 
                                    del currentValue[currentIndex]
                                    break
                                else:
                                    currentValue = currentValue[currentIndex]
                            else:
                                break
            except Exception as e:
                print('0x52: Failed to delete variable "{}": {}'.format(self.name, e))
                pass
        
        def getButtonValue(self, scalePercentage=None):
            """ Get a value to display on the result button """
            if self.varType in ['string', 'boolean', 'int', 'float']:
                val = str(self.value)
            elif self.varType == 'list':
                val = 'list ('+str(len(self.value))+' items)'
            elif self.varType == 'dict':
                val = 'dict ('+str(len(self.value))+' items)'
            else:
                val = self.varType
            
            if isinstance(val, basestring):
                if scalePercentage:
                    val = scaleText(val.replace('\n', ' '), scalePercentage, 'x52URM_button_text')
            else:
                val = 'unknown type'
            
            return val
        
        def getChild(self, childVarName):
            if callable(childVarName): childVarName = childVarName()
            
            if self.varType in ['dict', 'list']:
                if isinstance(childVarName, int):
                    return Var(self.name+'['+str(childVarName)+']')
                else:
                    return Var(self.name+'["'+str(childVarName)+'"]')
            else:
                return Var(self.name+'.'+str(childVarName))
        
        @property
        def children(self):
            if not hasattr(self, '__children'):
                self._m1_vars__children = []
                if self.varType == 'dict':
                    for key in self.value.keys():
                        childVar = self.getChild(key)
                        if childVar.isSupported: self._m1_vars__children.append(childVar)
                elif self.varType == 'list':
                    for key in range(0, len(self.value)):
                        childVar = self.getChild(key)
                        if childVar.isSupported: self._m1_vars__children.append(childVar)
                elif self.varType == 'store':
                    for key in self.value.__dict__.keys():
                        childVar = self.getChild(key)
                        if childVar.isSupported: self._m1_vars__children.append(childVar)
                elif self.varType.startswith('<class '):
                    for key in self.value.__dict__.keys():
                        childVar = self.getChild(key)
                        if childVar.isSupported: self._m1_vars__children.append(childVar)
            
            return self._m1_vars__children
        
        @staticmethod
        def getValType(val):
            import types
            
            try:
                if isinstance(val, basestring): 
                    return 'string'
                elif isinstance(val, bool): 
                    return 'boolean'
                elif isinstance(val, int): 
                    return 'int'
                elif isinstance(val, float): 
                    return 'float'
                elif isinstance(val, list): 
                    return 'list'
                elif isinstance(val, dict): 
                    return 'dict'
                elif isinstance(val, types.FunctionType):
                    return 'function'
                elif isinstance(val, renpy.python.StoreModule): 
                    return 'store'
                elif isinstance(val, renpy.persistent.Persistent): 
                    return 'persistent'
                elif isinstance(val, SearchClass):
                    return 'urmsearch'
                elif isinstance(val, renpy.python.StoreDeleted):
                    return 'deleted'
                elif hasattr(val, '__dict__'):
                    return str(type(val))
            except:
                pass
            
            return 'unknown'
        
        @staticmethod
        def getVarType(varName):
            try:
                val = eval(varName, renpy.store.__dict__)
                return Var.getValType(val)
            except:
                pass
            
            return 'unknown'
        
        @staticmethod
        def isSupportedVarType(varType):
            return varType in ['string', 'boolean', 'int', 'float', 'list', 'dict', 'store'] or varType.startswith('<class ')

    class SetVarValue(x52NonPicklable):
        """ This class calls `setValue` on the passed `Var` """
        def __init__(self, var, onSuccess, screenErrorVariable, *args, **kwargs):
            self.var = var
            self.onSuccess = onSuccess
            self.screenErrorVariable = screenErrorVariable
            self.args = args
            self.kwargs = kwargs
        
        def __call__(self):
            if self.var.setValue(*self.args, **self.kwargs):
                if callable(self.onSuccess):
                    self.onSuccess()
            elif self.screenErrorVariable:
                renpy.store.SetScreenVariable(self.screenErrorVariable, 'Unable to set variable, the value is probably invalid')()

    class CreateVar(x52NonPicklable):
        def __init__(self, varName, varVal, varType, onSuccess, screenErrorVariable, overwrite=False):
            self.varName = varName
            self.varVal = varVal
            self.varType = varType
            self.onSuccess = onSuccess
            self.screenErrorVariable = screenErrorVariable
            self.overwrite = overwrite
        
        def __call__(self):
            varName = self.varName() if callable(self.varName) else self.varName
            varVal = self.varVal() if callable(self.varVal) else self.varVal
            varType = self.varType() if callable(self.varType) else self.varType
            overwrite = self.overwrite() if callable(self.overwrite) else self.overwrite
            
            if not overwrite and hasattr(renpy.store, varName):
                renpy.store.SetScreenVariable(self.screenErrorVariable, 'A variable with this name already exists')()
                return
            
            isFrozen = VarsStore.isFrozen(varName)
            try:
                settableValue = None
                if varType == 'string':
                    settableValue = varVal
                elif varType == 'boolean':
                    settableValue = bool(varVal)
                elif varType == 'int' and Search.isInt(varVal):
                    settableValue = int(varVal)
                elif varType == 'float' and Search.isFloat(varVal):
                    settableValue = float(varVal)
                
                if settableValue:
                    if isFrozen: VarsStore.unfreeze(varName)
                    setattr(renpy.store, varName, settableValue)
                    self.onSuccess()
                else:
                    print("0x52: No valid value for {} (varType: {})".format(varName, varType))
                    renpy.store.SetScreenVariable(self.screenErrorVariable, 'Invalid value for variable type')()
            except Exception as e:
                print('0x52: Couldn\'t set value for "{}". {}'.format(varName, e))
                renpy.store.SetScreenVariable(self.screenErrorVariable, 'Failed to set variable. Check log for details')()
            finally:
                if isFrozen: VarsStore.freeze(varName)



    class StoreMonitorClass(x52NonPicklable):
        def __init__(self):
            self.originalSetField = None
            self._m1_vars__setFieldMethods = [
                '_m1_00action_data__set_field', 
                '_set_field', 
            ]
            self._m1_vars__isSupported = None
        
        def init(self):
            try:
                if self.isSupported and not self.isAttached:
                    renpy.config.python_callbacks.append(self._m1_vars__pythonCallback)
                    
                    if self.originalSetField == None:
                        for method in self._m1_vars__setFieldMethods:
                            if hasattr(renpy.store, method):
                                
                                originalMethod = getattr(renpy.store, method)
                                self.originalSetField = self._m1_vars__cloneMethod(originalMethod)
                                originalMethod.__code__ = StoreMonitorClass._m1_vars__injectableSetField.__code__
                                return
                return True
            
            except Exception as e:
                print('0x52: Failed to attach URM StoreMonitor: {}'.format(e))
                return False
        
        def _m1_vars__cloneMethod(self, method):
            import types
            return types.FunctionType(
                code=method.__code__,
                globals=method.__globals__,
                name=method.__name__,
                argdefs=method.__defaults__,
                closure=method.__closure__,
            )
        
        @staticmethod
        def _m1_vars__injectableSetField(obj, name, value, *args, **kwargs):
            if x52URM.StoreMonitor.handleVarChange(name, x52URM.Var(name).value, value):
                x52URM.StoreMonitor.originalSetField(obj, name, value, *args, **kwargs)
        
        def handleVarChange(self, varName, oldVal, newVal):
            
            if VarsStore.isFrozen(varName):
                if newVal != oldVal:
                    Var(varName).setValue(oldVal) 
                return False
            
            
            elif VarsStore.isMonitored(varName):
                if not renpy.get_screen('URM_modify_value') and oldVal != newVal: 
                    Notifications.add(label='Variable changed', text=varName, action=renpy.store.Show('URM_var_changed', varName=varName, prevVal=oldVal))
            
            return True
        
        def _m1_vars__pythonCallback(self):
            """ Called when a Python node just got executed """
            try:
                renpy.game.context().force_checkpoint = True 
                if renpy.store.__dict__.get_changes.__code__.co_argcount == 3: 
                    changes = renpy.store.__dict__.get_changes(False, previous=None)
                else:
                    changes = renpy.store.__dict__.get_changes(False)
                
                if isinstance(changes, tuple): 
                    changes = changes[0]
                else:
                    return
                
                for varName in changes:
                    oldVal = changes[varName]
                    
                    
                    if isinstance(oldVal, renpy.python.StoreDeleted): return
                    
                    self.handleVarChange(varName, oldVal, Var(varName).value)
            
            except Exception as e:
                print('0x52: Failed to process variable changes. {}'.format(e))
        
        @property
        def isSupported(self):
            if self._m1_vars__isSupported == None:
                for method in self._m1_vars__setFieldMethods:
                    if hasattr(renpy.store, method):
                        self._m1_vars__isSupported = True
                        break
                self._m1_vars__isSupported = self._m1_vars__isSupported or False
            return self._m1_vars__isSupported
        
        @property
        def isAttached(self):
            return (self._m1_vars__pythonCallback in renpy.config.python_callbacks)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
