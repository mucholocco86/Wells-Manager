
init 3 python in x52URM:
    _constant = True

    class SnapshotsClass(x52NonPicklable):
        def __init__(self):
            self._m1_snapshots__currentPage = 1
            self._m1_snapshots__snapshots = OrderedDict()
            self._m1_snapshots__snapshotTimes = {}
        
        def exists(self, name):
            return name in self._m1_snapshots__snapshots
        
        def create(self, name=None, overwrite=False):
            import datetime, time
            
            if callable(name):
                name = name()
            if not name: 
                name = 'snapshot{}'.format(int(time.time()*1000))
            
            if not overwrite and self.exists(name):
                Confirm('A snapshot with the same name already exits, do you want to overwrite it?', renpy.store.Function(self.create, name=name, overwrite=True))()
            else:
                self._m1_snapshots__snapshots[name] = renpy.python.DictItems(renpy.store.__dict__).as_dict()
                self._m1_snapshots__snapshotTimes[name] = datetime.datetime.now()
        
        def delete(self, name):
            if self.exists(name):
                del self._m1_snapshots__snapshots[name]
                del self._m1_snapshots__snapshotTimes[name]
        
        def _m1_snapshots__getDictDiff(self, oldDict, newDict): 
            changes = {}
            
            
            for key in oldDict:
                if not key in newDict or oldDict[key] != newDict[key]:
                    changes[key] = oldDict[key]
            
            
            for key in newDict:
                if not key in oldDict:
                    changes[key] = None
            
            return changes
        
        def findDictChanges(self, oldDict, newDict=None, ignoreInternal=False):
            changes = self._m1_snapshots__getDictDiff(oldDict, newDict if newDict != None else renpy.store.__dict__)
            
            changedVars = []
            for varName in changes:
                if not (varName.startswith('_') and ignoreInternal): 
                    changedVars.append({'old': Var(varName, oldDict), 'new': Var(varName, newDict)})
            
            return changedVars
        
        def findListChanges(self, oldList, newList):
            oldSet = set(oldList)
            newSet = set(newList)
            added = newSet - oldSet
            removed = oldSet - newSet
            
            changes = []
            for change in added:
                changes.append({'type': 'Added', 'val': change})
            for change in removed:
                changes.append({'type': 'Removed', 'val': change})
            
            return changes
        
        def findChanges(self, name, newName=None):
            if self.exists(name):
                changes = None
                if newName: 
                    if self.exists(newName):
                        return self.findDictChanges(self._m1_snapshots__snapshots[name], self._m1_snapshots__snapshots[newName], ignoreInternal=True)
                
                else: 
                    return self.findDictChanges(self._m1_snapshots__snapshots[name], None, ignoreInternal=True)
            
            return []
        
        @property
        def snapshotNames(self):
            return list(self._m1_snapshots__snapshots)
        
        def getSnapshotTime(self, name):
            if self.exists(name):
                return self._m1_snapshots__snapshotTimes[name].strftime('%X')
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
