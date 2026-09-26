
init 3 python in x52URM:
    _constant = True

    class SearchClass(x52NonPicklable):
        searchQuery = "" 
        searchRecursive = False 
        _m1_search__results = []
        
        def __init__(self):
            self.queryInput = Input(autoFocus=not renpy.variant("touch"), onEnter=renpy.store.Function(self.doSearch))
            self.expandObjectVars = None 
        
        @property
        def lastLabel(self):
            """ Get last called label (note that ) """
            try:
                for rollback in reversed(renpy.game.log.log):
                    if isinstance(rollback.context.current, basestring):
                        return rollback.context.current
            except:
                pass
            return '(Unknown)'
        
        @property
        def results(self):
            return self._m1_search__results
        
        @property
        def searchType(self):
            return Settings.searchType
        
        @searchType.setter
        def searchType(self, newType):
            if Settings.searchType == 'labels' or newType == 'labels': 
                self.resetSearch(keepInputQuery=True)
            Settings.searchType = newType
        
        def doSearch(self):
            results = []
            self.searchQuery = str(self.queryInput)
            
            
            if renpy.variant('touch'): self.queryInput.Disable()()
            
            if Settings.searchRecursive and len(self.results) > 0: 
                varCollection = self.results
                self.searchRecursive = True
            
            else: 
                if self.searchType == 'labels':
                    varCollection = renpy.get_all_labels()
                else:
                    varCollection = renpy.store.__dict__
                self.searchRecursive = False
            
            
            if self.searchType == 'variable names' or self.searchType == 'labels': 
                for varName in varCollection:
                    if isinstance(varName, Var):
                        matchedVarNames = self.matchVarName(varName.name, self.searchQuery)
                    else:
                        matchedVarNames = self.matchVarName(varName, self.searchQuery)
                    
                    if matchedVarNames:
                        results += matchedVarNames
            
            elif self.searchType == 'values': 
                for varName in varCollection:
                    if isinstance(varName, Var):
                        matchedVarNames = self.matchVarValue(varName.name, self.searchQuery)
                    else:
                        matchedVarNames = self.matchVarValue(varName, self.searchQuery)
                    
                    if matchedVarNames:
                        results += matchedVarNames
            
            self._m1_search__results = results
            self._m1_search__currentPage = 1
        
        def sort(self, reverse=False):
            """ Order search results by name """
            if self._m1_search__results:
                self._m1_search__results = sorted(self._m1_search__results, reverse=reverse, key=lambda props: getattr(props, 'name').lower())
        
        def resetSearch(self, keepInputQuery=False):
            if not keepInputQuery: self.queryInput.set_text('')
            self.queryInput.Enable()()
            self.searchQuery = ''
            self._m1_search__results = []
            self.searchRecursive = False
            self._m1_search__currentPage = 1
        
        def _m1_search__getFullVarName(self, varName, parentVarName=None):
            """ Combine `varName` and `parentVarname` into one variable name """
            if parentVarName:
                if Var.getVarType(parentVarName) == 'dict':
                    return parentVarName+'["'+str(varName)+'"]'
                else:
                    return parentVarName+'.'+str(varName)
            else:
                return varName
        
        def matchVarValue(self, varName, query, parentVarName=None):
            """
            Match a `varName`'s value with the `query`

            Returns: array of matched varNames (could be multiple variables if the supplied var is a list or dict)
            """
            
            try:
                fullVarName = self._m1_search__getFullVarName(varName, parentVarName)
                varType = Var.getVarType(fullVarName)
                
                if not Var.isSupportedVarType(varType): 
                    return None
                
                elif varName.startswith('_') and not Settings.searchInternalVars:
                    return None
                
                elif varType == 'string':
                    return [Var(fullVarName)] if self._m1_search__matchStringValue(eval(fullVarName, renpy.store.__dict__), query) else None
                
                elif varType == 'boolean' and (query.lower() == 'true' or query.lower() == 'false'):
                    if eval(fullVarName, renpy.store.__dict__): 
                        return [Var(fullVarName)] if query.lower() == 'true' else None
                    else: 
                        return [Var(fullVarName)] if query.lower() == 'false' else None
                
                elif varType == 'int' and self.isInt(query):
                    return [Var(fullVarName)] if int(query) == eval(fullVarName, renpy.store.__dict__) else None
                
                elif varType == 'float' and self.isFloat(query):
                    return [Var(fullVarName)] if float(query) == eval(fullVarName, renpy.store.__dict__) else None
                
                elif varType == 'persistent' and Settings.searchPersistent:
                    varNames = []
                    for subVarName in eval(fullVarName, renpy.store.__dict__).__dict__.keys():
                        matchedVarNames = self.matchVarValue(subVarName, query, fullVarName)
                        if matchedVarNames:
                            varNames += matchedVarNames
                    
                    if len(varNames) > 0:
                        return varNames
                
                elif not parentVarName and Settings.searchObjects and varType == 'dict': 
                    varNames = []
                    for subVarName in eval(fullVarName, renpy.store.__dict__):
                        matchedVarNames = self.matchVarValue(subVarName, query, fullVarName)
                        if matchedVarNames:
                            varNames += matchedVarNames
                    
                    if len(varNames) > 0:
                        return varNames
                
                elif not parentVarName and Settings.searchObjects and hasattr(eval(fullVarName, renpy.store.__dict__), '__dict__'): 
                    varNames = []
                    for subVarName in eval(fullVarName, renpy.store.__dict__).__dict__:
                        matchedVarNames = self.matchVarValue(subVarName, query, fullVarName)
                        if matchedVarNames:
                            varNames += matchedVarNames
                    
                    if len(varNames) > 0:
                        return varNames
            except Exception as e:
                print('0x52: matchVarValue failed for variable "{}". {}'.format(varName, e))
        
        def matchVarName(self, varName, query, parentVarName=None):
            """
            Match a `varName` with the `query`

            Returns: array of matched varNames (could be multiple variables if the supplied var is a list, dict or object)
            """
            if not isinstance(varName, basestring):
                return
            
            try:
                fullVarName = self._m1_search__getFullVarName(varName, parentVarName)
                varType = 'label' if self.searchType == 'labels' else Var.getVarType(fullVarName)
                
                if fullVarName == 'store': 
                    return None
                
                elif varName.startswith('_') and not Settings.searchInternalVars:
                    return None
                
                elif varType == 'unknown' and not Settings.showUnsupportedVariables:
                    return None
                
                elif varType not in ['label','persistent','store','unknown'] and not Var.isSupportedVarType(varType): 
                    return None
                
                elif fullVarName == 'persistent': 
                    if Settings.searchPersistent:
                        varNames = []
                        for subVarName in eval(fullVarName, renpy.store.__dict__).__dict__.keys():
                            matchedVarNames = self.matchVarName(subVarName, query, varName)
                            if matchedVarNames:
                                varNames += matchedVarNames
                        
                        if len(varNames) > 0:
                            return varNames
                    else:
                        return None
                
                elif not parentVarName and Settings.searchObjects and varType == 'dict': 
                    varNames = [Var(varName)] if self._m1_search__matchStringValue(varName, query) else [] 
                    for subVarName in eval(fullVarName, renpy.store.__dict__).keys():
                        matchedVarNames = self.matchVarName(subVarName, query, fullVarName)
                        if matchedVarNames:
                            varNames += matchedVarNames
                    
                    if len(varNames) > 0:
                        return varNames
                
                elif not parentVarName and Settings.searchObjects and varType != 'label' and hasattr(eval(fullVarName, renpy.store.__dict__), '__dict__'): 
                    varNames = [Var(varName)] if self._m1_search__matchStringValue(varName, query) else [] 
                    for subVarName in eval(fullVarName, renpy.store.__dict__).__dict__.keys():
                        matchedVarNames = self.matchVarName(subVarName, query, fullVarName)
                        if matchedVarNames:
                            varNames += matchedVarNames
                    
                    if len(varNames) > 0:
                        return varNames
                
                else:
                    return [Var(fullVarName)] if self._m1_search__matchStringValue(varName, query) else None
            except Exception as e:
                print('0x52: matchVarName failed for variable "{}". {}'.format(varName, e))
        
        def _m1_search__matchStringValue(self, val, query):
            if Settings.useWildcardSearch:
                import re
                query = re.escape(query)
                query = query.replace('\\*', '.*').replace('\\?', '.')
                query = '^{}$'.format(query)
                
                return bool(re.match(query, val, re.IGNORECASE))
            else:
                return (query.lower() in val.lower())
        
        def isInt(self, value):
            try:
                int(value)
                return True
            except:
                return False
        
        def isFloat(self, value):
            try:
                float(value)
                return True
            except:
                return False
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
