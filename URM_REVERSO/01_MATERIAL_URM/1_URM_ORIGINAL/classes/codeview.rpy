
init 2 python in x52URM:
    _constant = True

    class CodeViewClass(x52NonPicklable):
        def __init__(self):
            self._m1_codeview__colors = {
                'light': {
                    'comments': '#008000',
                    'functions': '#795E26',
                    'keywords': '#AF00DB',
                    'specialKeywords': '#0070C1',
                    'numbers': '#098658',
                    'strings': '#a31515',
                    'variables': '#001080',
                    'types': '#267f99',
                    'background': '#ffffff',
                },
                'dark': {
                    'comments': '#6A9955',
                    'functions': '#DCDCAA',
                    'keywords': '#C586C0',
                    'specialKeywords': '#4FC1FF',
                    'numbers': '#b5cea8',
                    'strings': '#ce9178',
                    'variables': '#9CDCFE',
                    'types': '#4EC9B0',
                    'background': '#1f1f1f',
                },
            }
            self._m1_codeview__varOperators = [
                r'==?', r'<=?', r'>=?',
                r'\+=', r'-=', r'\*=', r'\/=', r'%=', r'\^=', r'&=', r'\|=', r'!=',
                r'\+', r'-', r'\*', r'\/', r'%', r'\^', r'&', r'\|', r'!',
            ]
            self._m1_codeview__tokenPatterns = [
                ('strings', [
                    r'(".*?"|\'.*?\')',
                ]),
                ('comments', [
                    r'(#[ \t]*.*)$',
                ]),
                ('types', [
                    r'\bclass[ ]+(\w+\(.*\)):',
                ]),
                ('specialKeywords', [
                    r'\b(def|class|self)\b',
                    r'\b(True|False)\b', 
                ]),
                ('variables', [
                    r'\b((?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*) ?(?:' + r'|'.join(self._m1_codeview__varOperators) + r')',
                    r'(?:' + r'|'.join(self._m1_codeview__varOperators) + r') ?((?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*)\b',
                    r'\b((?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*) (?:not )?(?:is|in|and|or)(?: not)?',
                    r'(?:not )?(?:is|in|and|or)(?: not)? ((?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*)\b',
                    r'\breturn ((?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*)\b',
                    (
                        r'\(((?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*(?:, ?(?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*)*)\)', 
                        r'((?!URMTKN[0-9]+URMTKN)[A-Za-z_]{1}[\w\.]*)(?:, )?', 
                    ),
                ]),
                ('specialKeywords', [
                    r'\b(is|not|in)\b', 
                    r'\b(show|hide|screen)\b',
                ]),
                ('numbers', [
                    r'\b([0-9]+)\b',
                ]),
                ('functions', [
                    r'\b(\w+)\(.*\)',
                    r'\b(?:jump|call) ([\w\.]+)(?: ?\(.+\))?$', 
                ]),
                ('keywords', [
                    r'\b(and|or|jump|call|return|if|elif|else|for|while|import|from|as|continue|del|break|finnaly|except|pass|raise|try|with)\b',
                ]),
            ]
            renpy.config.hyperlink_handlers['URMVarDialog'] = self.handleVarClicked
            renpy.config.hyperlink_handlers['URMLabelDialog'] = self.handleLabelClicked
        
        def handleVarClicked(self, varName):
            renpy.show_screen('URM_modify_value', Var(varName), allowRemember=True)
            renpy.restart_interaction()
        
        def handleLabelClicked(self, label):
            renpy.show_screen('URM_replay_jump', label)
            renpy.restart_interaction()
        
        @property
        def colors(self):
            if Theme.isDark:
                return self._m1_codeview__colors['dark']
            else:
                return self._m1_codeview__colors['light']
        
        def colorize(self, code, interactiveVariables=True, interactiveLabels=True, evaluateConditions=True):
            
            code = code.replace('{', '{{')
            
            if evaluateConditions:
                code = self.evaluateConditions(code)
            
            
            tokens = []
            
            def replaceWithToken(subpattern=None):
                def subCall(match):
                    if subpattern:
                        return renpy.re.sub(subpattern, replaceWithToken(), match.group(), flags=renpy.re.MULTILINE)
                    else:
                        tokens.append('{{color={}}}{}{{/color}}'.format(self.colors[color], match.group(1)))
                        return match.group().replace(match.group(1), 'URMTKN{}URMTKN'.format(len(tokens)-1))
                return subCall
            
            for (color, patterns) in self._m1_codeview__tokenPatterns:
                for pattern in patterns:
                    if isinstance(pattern, tuple) and len(pattern) == 2:
                        code = renpy.re.sub(pattern[0], replaceWithToken(pattern[1]), code, flags=renpy.re.MULTILINE)
                    else:
                        code = renpy.re.sub(pattern, replaceWithToken(), code, flags=renpy.re.MULTILINE)
            
            
            def insertToken(match):
                return tokens[int(match.group(1))]
            
            code = renpy.re.sub(r'URMTKN([0-9]+)URMTKN', insertToken, code)
            
            if interactiveVariables:
                code = self.interactiveVariables(code)
            
            if interactiveLabels:
                code = self.interactiveLabels(code)
            
            return code
        
        def interactiveVariables(self, coloredCode):
            pattern = r'{color=' + self.colors['variables'] + r'}([\w\.]+){/color}'
            
            def addLink(match):
                return '{{a=URMVarDialog:{}}}{}{{/a}}'.format(match.group(1), match.group())
            
            return renpy.re.sub(pattern, addLink, coloredCode)
        
        def interactiveLabels(self, coloredCode):
            pattern = r'{color=' + self.colors['keywords'] + r'}(?:call|jump){/color} {color=' + self.colors['functions'] + r'}([\w\.]+){/color}'
            
            def addLink(match):
                return '{{a=URMLabelDialog:{}}}{}{{/a}}'.format(match.group(1), match.group())
            
            return renpy.re.sub(pattern, addLink, coloredCode)
        
        def evaluateConditions(self, code):
            pattern = r'\s*(?:el)?if (.+):(?: )*$'
            
            def evalCondition(match):
                try:
                    if eval(match.group(1), renpy.store.__dict__):
                        return '{} # V - Condition is met'.format(match.group())
                    else:
                        return '{} # X - Condition not met'.format(match.group())
                except Exception as e:
                    print('0x52: CodeView: Failed to evaluatie condition: "{}". {}'.format(match.group(), e))
                    return '{} # ? - Unable to evaluate condition'.format(match.group())
            
            return renpy.re.sub(pattern, evalCondition, code, flags=renpy.re.MULTILINE)
        
        def nodesToCode(self, nodes, indentCount=0):
            """ Transform Ren'Py nodes to code """
            output = ''
            
            def createLine(line):
                return '{}{}\n'.format('    '*indentCount, line)
            
            if hasattr(nodes, '__iter__'):
                for node in nodes:
                    if isinstance(node, renpy.ast.Python) and hasattr(node, 'code') and hasattr(node.code, 'source'):
                        if VarsStore.strContainsIgnored(node.code.source, 'code'): continue 
                        output += createLine(node.code.source)
                    elif isinstance(node, renpy.ast.If): 
                        for i,(condition, conditionNodes) in enumerate(node.entries):
                            if i == 0: 
                                if VarsStore.strContainsIgnored(condition, 'code'): break 
                                output += createLine('if {}:'.format(condition))
                            elif condition == 'True':
                                output += createLine('else:')
                            else:
                                output += createLine('elif {}:'.format(condition))
                            output += createLine(self.nodesToCode(conditionNodes, indentCount+1))
                    elif isinstance(node, renpy.ast.Jump):
                        output += createLine('jump {}\n'.format(node.target))
                        break 
                    elif isinstance(node, renpy.ast.Call):
                        if node.arguments:
                            if hasattr(node.arguments, 'get_code'):
                                output += createLine('call {} {}\n'.format(node.label, node.arguments.get_code()))
                            else:
                                output += createLine('call {} # This call has arguments URM could not show\n'.format(node.label))
                        else:
                            output += createLine('call {}\n'.format(node.label))
                    elif isinstance(node, renpy.ast.UserStatement):
                        if node.parsed[0] in [('call','screen'),('show','screen'),('hide','screen')] and hasattr(node, 'get_code'):
                            output += createLine(node.get_code())
                    elif isinstance(node, renpy.ast.Translate):
                        if not output.endswith('# Some dialogue\n'):
                            output += createLine('# Some dialogue')
                
                
                if not Settings.codeViewShowAll:
                    output = self.stripRenpyCode(output)
                
                output = output.rstrip()
                
                if output == '# Some dialogue': 
                    output = ''
            
            return output
        
        def stripRenpyCode(self, code):
            """ Strip all code that's probably no relevant """
            patterns = [
                r'^.*\brenpy\.(?!jump|call|show_screen).+\n',
                r'^.*\bui\..+\n',
            ]
            
            for pattern in patterns:
                code = renpy.re.sub(pattern, '', code, flags=renpy.re.MULTILINE)
            
            return code
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
