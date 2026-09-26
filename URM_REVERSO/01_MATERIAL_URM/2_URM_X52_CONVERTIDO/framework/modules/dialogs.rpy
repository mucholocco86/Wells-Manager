
init -999 python in x52URM:
    _constant = True

    def generateDialogBackground(backgroundColor=None):
        titlebarHeight = scalePxInt(42)
        contentHeight = 18
        height = titlebarHeight+contentHeight
        width = 60
        borderSize = 2
        if backgroundColor is None: backgroundColor = Theme.colors.dialogBg
        
        return renpy.display.imagelike.Frame(renpy.store.LiveComposite(
                (width,height),
                (0, 0), renpy.store.LiveComposite((width, titlebarHeight), (0,0), renpy.display.imagelike.Solid(Theme.colors.dialogTitleBar)), 
                (0, titlebarHeight), renpy.store.LiveComposite((width,contentHeight), (0,0), renpy.display.imagelike.Solid(backgroundColor)), 
                (0, titlebarHeight-borderSize), renpy.store.LiveComposite((width, borderSize), (0,0), renpy.display.imagelike.Solid(Theme.colors.dialogBorder)), 
                (0, 0), renpy.store.LiveComposite((width, borderSize), (0,0), renpy.display.imagelike.Solid(Theme.colors.dialogBorder)), 
                (0, 0), renpy.store.LiveComposite((borderSize, height), (0,0), renpy.display.imagelike.Solid(Theme.colors.dialogBorder)), 
                (width-borderSize, 0), renpy.store.LiveComposite((borderSize, height), (0,0), renpy.display.imagelike.Solid(Theme.colors.dialogBorder)), 
                (0, height-borderSize), renpy.store.LiveComposite((width, borderSize), (0,0), renpy.display.imagelike.Solid(Theme.colors.dialogBorder)), 
            ), borderSize, titlebarHeight, borderSize, borderSize)

    class Confirm(x52NonPicklable):
        def __init__(self, prompt, yes=None, no=None, title=None, modal=True, promptSubstitution=True):
            self.prompt = prompt
            self.yes = yes
            self.no = no
            self.title = title
            self.modal = modal
            self.promptSubstitution = promptSubstitution
        
        def __call__(self):
            renpy.show_screen('x52URM_Confirm', self.prompt, self.yes, self.no, self.title, self.modal, self.promptSubstitution)
            renpy.restart_interaction()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
