



































init -999 python in x52URM:
    _constant = True

    class Input(renpy.store.InputValue):
        def __init__(self, text='', autoFocus=False, mask=None, onEnter=None, editable=True, updateScreenVariable=None):
            self._m1_inputs__text = text
            self._m1_inputs__unmaskedText = text
            self.default = autoFocus
            self.mask = mask
            self.onEnter = onEnter
            self.editable = editable
            self.updateScreenVariable = updateScreenVariable 
        
        @property
        def autoFocus(self):
            return self.default
        
        @autoFocus.setter
        def autoFocus(self, val):
            self.default = val
        
        def get_text(self):
            if self.mask:
                return self.mask * len(self._m1_inputs__text)
            else:
                return self._m1_inputs__text
        
        def set_text(self, newText):
            if self.mask: 
                lenDiff = len(self._m1_inputs__text) - len(newText)
                if lenDiff < 0: 
                    self._m1_inputs__unmaskedText += newText[lenDiff:]
                elif lenDiff > 0: 
                    self._m1_inputs__unmaskedText = self._m1_inputs__unmaskedText[:-lenDiff]
                
                self._m1_inputs__text = newText
            else:
                self._m1_inputs__text = newText
            
            if self.updateScreenVariable:
                renpy.store.SetScreenVariable(self.updateScreenVariable, str(self))()
            else:
                renpy.restart_interaction()
        
        def enter(self):
            
            if renpy.variant('touch'): self.Disable()()
            
            
            if self.onEnter:
                actions = self.onEnter if isinstance(self.onEnter, list) else [self.onEnter]
                for action in actions:
                    action()
            
            raise renpy.IgnoreEvent()
        
        def __str__(self):
            if self.mask:
                return self._m1_inputs__unmaskedText
            else:
                return self._m1_inputs__text


    class InputGroup(x52NonPicklable):
        def __init__(self, inputs=None, focusFirst=False, onSubmit=None):
            """ `input` tuple, example: [('usernameInput', x52Input(autoFocus=True)),('passwordInput', x52Input(mask='*))] """
            self._m1_inputs__inputs = inputs or []
            self._m1_inputs__selectedIndex = None
            self.onSubmit = onSubmit
            for i in range(len(self._m1_inputs__inputs)):
                input = self._m1_inputs__inputs[i][1]
                if not input.onEnter: input.onEnter = onSubmit 
                if focusFirst: 
                    if self._m1_inputs__selectedIndex == None and input.editable:
                        self._m1_inputs__selectedIndex = i
                        input.autoFocus = True
                else:
                    if input.autoFocus:
                        self._m1_inputs__selectedIndex = i 
        
        def focus(self):
            input = self._m1_inputs__inputs[self._m1_inputs__selectedIndex][1]
            input.Enable()()
        
        def __getattr__(self, name):
            for input in self._m1_inputs__inputs:
                if input[0] == name:
                    return input[1]
        
        class _m1_inputs__NextInput(x52NonPicklable):
            def __init__(self, inputGroup):
                self.inputGroup = inputGroup
            
            def __call__(self):
                self.inputGroup.selectNext()
        
        def NextInput(self):
            return self._m1_inputs__NextInput(self)
        
        def selectNext(self):
            if self._m1_inputs__selectedIndex == None:
                self._m1_inputs__selectedIndex = 0
            else:
                self._m1_inputs__selectedIndex = (self._m1_inputs__selectedIndex + 1) % len(self._m1_inputs__inputs)
            
            if self._m1_inputs__inputs[self._m1_inputs__selectedIndex][1].editable:
                self._m1_inputs__inputs[self._m1_inputs__selectedIndex][1].Enable()()
        
        class _m1_inputs__PreviousInput(x52NonPicklable):
            def __init__(self, inputGroup):
                self.inputGroup = inputGroup
            
            def __call__(self):
                self.inputGroup.selectPrevious()
        
        def PreviousInput(self):
            return self._m1_inputs__PreviousInput(self)
        
        def selectPrevious(self):
            if self._m1_inputs__selectedIndex == None:
                self._m1_inputs__selectedIndex = len(self._m1_inputs__inputs)-1
            else:
                self._m1_inputs__selectedIndex = (self._m1_inputs__selectedIndex + len(self._m1_inputs__inputs) - 1) % len(self._m1_inputs__inputs)
            
            if self._m1_inputs__inputs[self._m1_inputs__selectedIndex][1].editable:
                self._m1_inputs__inputs[self._m1_inputs__selectedIndex][1].Enable()()


    class GetScreenInput(x52NonPicklable):
        """ Class that returns input value on a screen by calling it or by converting it to a string like `str(GetScreenInput('someInput', 'someOptionalInputGroup'))` """
        
        def __init__(self, inputName, groupName=None):
            self.inputName = inputName
            self.groupName = groupName
        
        def __str__(self):
            return self()
        
        def __call__(self):
            cs = renpy.current_screen()
            
            if not cs: 
                return
            else:
                scope = cs.scope
            
            input = None
            if self.groupName:
                if self.groupName in scope and hasattr(scope[self.groupName], self.inputName):
                    input = getattr(scope[self.groupName], self.inputName)
            elif self.inputName in scope:
                input = scope[self.inputName]
            
            if input == None:
                raise Exception('0x52: x52Input screenvariable "{}" not found'.format(self.groupName or self.inputName))
            else:
                return str(input)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
