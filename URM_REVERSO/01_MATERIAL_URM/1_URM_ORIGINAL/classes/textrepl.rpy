
init 3 python in x52URM:
    _constant = True

    class TextReplacementsClass(x52NonPicklable):
        def __init__(self):
            self._m1_textrepl__defaultTextFilter = None
            self._m1_textrepl__defaultSayFilter = None
        
        @property
        def store(self):
            if URMFiles.file['replacements'] == None: URMFiles.file.addStore('replacements')
            return URMFiles.file['replacements']
        
        def clear(self):
            URMFiles.file.clearStore('replacements')
        
        def changePos(self, sourceReplOriginal, targetReplOriginal):
            if sourceReplOriginal in self.store and targetReplOriginal in self.store:
                self.store.changePos(sourceReplOriginal, targetReplOriginal)
        
        def sort(self, reverse=False, sortReplacement=False):
            self.store.sort(reverse, sortByAttr=('replacement' if sortReplacement else None))
        
        class AddReplacement(x52NonPicklable):
            def __init__(self, original, replacement, characterVar=None, caseInsensitive=False, replacePartialWords=False):
                self.original = original
                self.replacement = replacement
                self.characterVar = characterVar
                self.caseInsensitive = caseInsensitive
                self.replacePartialWords = replacePartialWords
            
            def __call__(self):
                original = self.original if not callable(self.original) else self.original()
                replacement = self.replacement if not callable(self.replacement) else self.replacement()
                characterVar = self.characterVar if not callable(self.characterVar) else self.characterVar()
                caseInsensitive = self.caseInsensitive if not callable(self.caseInsensitive) else self.caseInsensitive()
                replacePartialWords = self.replacePartialWords if not callable(self.replacePartialWords) else self.replacePartialWords()
                
                TextRepl.add(original, replacement, characterVar, caseInsensitive, replacePartialWords)
        
        def add(self, original, replacement, characterVar=None, caseInsensitive=False, replacePartialWords=False):
            """ Add or update a replacement """
            self.store[original] = {
                'original': original,
                'replacement': replacement,
                'characterVar': characterVar,
                'caseInsensitive': caseInsensitive,
                'replacePartialWords': replacePartialWords,
            }
        
        def remove(self, original):
            if original in self.store:
                del self.store[original]
        
        def attachFilters(self):
            if not self.incompatible:
                if renpy.config.say_menu_text_filter != self._m1_textrepl__textFilter: 
                    self._m1_textrepl__defaultTextFilter = renpy.config.say_menu_text_filter
                    renpy.config.say_menu_text_filter = self._m1_textrepl__textFilter
                
                if renpy.config.say_arguments_callback != self._m1_textrepl__sayFilter: 
                    self._m1_textrepl__defaultSayFilter = renpy.config.say_arguments_callback
                    renpy.config.say_arguments_callback = self._m1_textrepl__sayFilter
        
        @property
        def incompatible(self):
            return not hasattr(renpy.config, 'say_arguments_callback')
        
        def _m1_textrepl__textFilter(self, text):
            if self._m1_textrepl__defaultTextFilter:
                text = self._m1_textrepl__defaultTextFilter(text)
            
            for original,replacement in self.store.items():
                text = self._m1_textrepl__replace(text, original)
            
            return text
        
        def _m1_textrepl__sayFilter(self, who, *args, **kwargs):
            if self._m1_textrepl__defaultSayFilter:
                args, kwargs = self._m1_textrepl__defaultSayFilter(who, *args, **kwargs)
            
            if isinstance(who, basestring):
                if who in self.store and 'characterVar' in self.store[who] and self.store[who]['characterVar']:
                    kwargs['name'] = self._m1_textrepl__replace(who, who)
            elif isinstance(who, renpy.store.ADVCharacter) and hasattr(who, 'name') and isinstance(who.name, basestring):
                if who.name in self.store and 'characterVar' in self.store[who.name] and self.store[who.name]['characterVar']:
                    if hasattr(who, 'dynamic') and who.dynamic:
                        kwargs['name'] = repr(self._m1_textrepl__replace(who.name, who.name))
                    else:
                        kwargs['name'] = self._m1_textrepl__replace(who.name, who.name)
            
            return args, kwargs
        
        def _m1_textrepl__replace(self, text, original):
            if original not in self.store: return text 
            
            import re
            
            if 'characterVar' in self.store[original] and self.store[original]['characterVar']: 
                char = eval(self.store[original]['characterVar'], renpy.store.__dict__)
                if isinstance(char, renpy.store.ADVCharacter):
                    text = text.replace('[{}]'.format(self.store[original]['characterVar']), self.store[original]['replacement'])
                    text = text.replace('[{}.name]'.format(self.store[original]['characterVar']), self.store[original]['replacement'])
            
            if original[:1] == '[' and original[-1:] == ']': 
                text = text.replace(original, self.store[original]['replacement'])
            else:
                caseInsensitive = bool('caseInsensitive' in self.store[original] and self.store[original]['caseInsensitive'])
                if 'replacePartialWords' in self.store[original] and self.store[original]['replacePartialWords']:
                    replacement = re.compile(re.escape(original), re.IGNORECASE if caseInsensitive else 0)
                else:
                    replacement = re.compile('\\b{}(?!\\w)'.format(re.escape(original)), re.IGNORECASE if caseInsensitive else 0) 
                text = replacement.sub(self.store[original]['replacement'], text)
            
            return text


init 999 python in x52URM:
    if not pendingUpdate:
        
        TextRepl.attachFilters()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
