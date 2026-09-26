
init 3 python in x52URM:
    _constant = True

    class ProgressBarClass():
        def __init__(self):
            self.lastLine = None
            self.new = None
            self.seen = renpy.count_seen_dialogue_blocks()
            self.total = renpy.count_dialogue_blocks()
            self._m1_progressbar__text = None
            self._m1_progressbar__textWidth = None
        
        def _m1_progressbar__seenCountCorrection(self):
            try:
                node = renpy.game.script.lookup('URM_textboxCustomizer').next
                while node:
                    if isinstance(node, renpy.ast.Translate) and node.identifier not in renpy.game.persistent._seen_translates:
                        renpy.game.persistent._seen_translates.add(node.identifier)
                        renpy.game.seen_translates_count += 1
                        renpy.game.new_translates_count += 1
                    node = node.next
            except Exception as e:
                print('0x52: Failed to correct progress count. {}'.format(e))
        
        @property
        def percentage(self):
            self._m1_progressbar__calculate()
            try:
                return round((float(self.seen)/float(self.total))*100, 1)
            except:
                return 0
        
        @property
        def text(self):
            self._m1_progressbar__calculate()
            if self._m1_progressbar__text is None:
                if Settings.progressShowNew:
                    self._m1_progressbar__text = '{}% ({}/{}/{})'.format(self.percentage, self.new, self.seen, self.total)
                else:
                    self._m1_progressbar__text = '{}% ({}/{})'.format(self.percentage, self.seen, self.total)
            
            return self._m1_progressbar__text
        
        @property
        def textWidth(self):
            self._m1_progressbar__calculate()
            if self._m1_progressbar__textWidth is None:
                self._m1_progressbar__textWidth = renpy.store.Text(self.text, None, False, False, style='x52URM_text').size()[0]
            
            return self._m1_progressbar__textWidth
        
        def _m1_progressbar__calculate(self):
            if self.lastLine != currentFilePathLine(): 
                self._m1_progressbar__seenCountCorrection()
                self.lastLine = currentFilePathLine()
                if Settings.progressShowNew:
                    self.new = renpy.count_newly_seen_dialogue_blocks()
                else:
                    self.new = None
                self.seen = renpy.count_seen_dialogue_blocks()
                self.total = renpy.count_dialogue_blocks()
                self._m1_progressbar__text = None
                self._m1_progressbar__textWidth = None
            elif Settings.progressShowNew and self.new is None:
                self.new = renpy.count_newly_seen_dialogue_blocks()
                self._m1_progressbar__text = None
                self._m1_progressbar__textWidth = None
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
