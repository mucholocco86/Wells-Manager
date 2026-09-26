init 3 python in x52URM:
    _constant = True

    class CharactersClass(x52NonPicklable):
        def __init__(self):
            self._m1_Characters__characters = None
        
        def reload(self):
            self._m1_Characters__characters = []
            for key,value in renpy.store.__dict__.items():
                if isinstance(value, renpy.store.ADVCharacter) and hasattr(value, 'name') and isinstance(value.name, basestring):
                    self._m1_Characters__characters.append(Character(key))
        
        def getByVarName(self, varName):
            for char in self.all:
                if char.varName == varName:
                    return char
        
        @property
        def all(self):
            if self._m1_Characters__characters == None:
                self.reload()
            return self._m1_Characters__characters

    class Character(x52NonPicklable):
        def __init__(self, varName):
            if not hasattr(renpy.store, varName) or not isinstance(getattr(renpy.store, varName), renpy.store.ADVCharacter):
                raise Exception('Variable "{}" is not a character'.format(varName))
            self.varName = varName
            self._m1_Characters__substituionErrorLogged = False 
        
        def match(self, query):
            """ Check if this character matches `query` """
            if not isinstance(query, basestring): raise Exception('Characterquery should be a string, got {}'.format(type(query)))
            query = query.lower()
            return (query in self.name.lower() or query in self.displayName.lower() or query in self.varName.lower())
        
        @property
        def who(self):
            return getattr(renpy.store, self.varName)
        
        @property
        def name(self):
            """ The literal name value (before substitution) """
            if hasattr(self.who, 'name') and isinstance(self.who.name, basestring):
                return self.who.name
            else:
                return ''
        
        @property
        def displayName(self):
            """ The name after substitution """
            try:
                return renpy.substitute(self.name)
            except Exception as e:
                if not self._m1_Characters__substituionErrorLogged:
                    print('0x52: Failed to substitute name "{}" for character "{}". Error: {}'.format(self.name, self.varName, e))
                    self._m1_Characters__substituionErrorLogged = True
                return self.name
        
        @property
        def fullName(self):
            """ displayName and varName """
            return '{} ({})'.format(self.displayName, self.varName)

    Characters = CharactersClass()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
