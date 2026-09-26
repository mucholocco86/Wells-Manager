
style x52URM_dialog is x52URM_frame:
    background x52URM.generateDialogBackground()
    padding (2, 2)

style x52URM_dialogContent is x52URM_frame:
    background None
    yoffset x52URM.scalePxInt(-20)
    padding (x52URM.scalePxInt(20), 0, x52URM.scalePxInt(20), x52URM.scalePxInt(10))

style x52URM_dialogButtons:
    yoffset x52URM.scalePxInt(-40)
    xalign 1.0

style x52URM_dialogButton is x52URM_button:
    background Solid(x52URM.Theme.colors.buttonBg)
    hover_background Solid(x52URM.Theme.colors.buttonBgHover)
    ysize x52URM.scalePxInt(38)
    padding (x52URM.scalePxInt(16),0)

style x52URM_dialogCloseButton is x52URM_dialogButton:
    background Solid(x52URM.Theme.colors.errorText)
    hover_background Solid(x52URM.Theme.colorBrightness(x52URM.Theme.colors.errorText, 30))

style x52URM_dialogIcon is x52URM_iconSolid:
    size x52URM.scalePxInt(28)

# ======
# DIALOG
# ======
screen x52URM_Dialog(title=None, closeAction=None, xsize=None, modal=False, icon=None, backgroundColor=None, details=None, detailsTitle=None):
    style_prefix 'x52URM'
    default dialogBackground = backgroundColor and x52URM.generateDialogBackground(backgroundColor)

    if closeAction:
        key 'K_ESCAPE' action closeAction

    if modal:
        textbutton "" style_suffix "overlay" xfill True yfill True action NullAction() at x52URM_fadeinout

    drag:
        draggable True
        drag_handle (0, 0, 1.0, x52URM.scalePxInt(42))
        if renpy.variant('touch'):
            align (.5,.15)
        else:
            align (.5,.5)

        frame:
            style_suffix 'dialog'
            if dialogBackground:
                background dialogBackground
            vbox: # Do not use `has vbox` here, for older Ren'Py versions

                frame:
                    background None
                    ysize x52URM.scalePxInt(40)
                    padding (x52URM.scalePxInt(4), 0)
                    hbox spacing x52URM.scalePxInt(4) yalign .5:
                        if icon:
                            text icon style_suffix 'x52URM_dialogIcon' yalign .5
                        if title:
                            label title yalign .5

                hbox:
                    style_suffix 'dialogButtons'

                    if details:
                        button:
                            style_suffix 'dialogButton'
                            text '?' size x52URM.scalePxInt(24) yalign .5
                            action x52URM.Confirm(details, title=detailsTitle)
                    button:
                        style_suffix 'dialogCloseButton'
                        if closeAction:
                            text 'x' size x52URM.scalePxInt(24) yalign .5 color x52URM.Theme.colors.errorBg
                            action closeAction
                        else:
                            background None
                            text 'x' size x52URM.scalePxInt(24) yalign .5 color '#fff0'
                        

                button:
                    key_events True # We need this to still trigger key events defined inside of this button
                    action NullAction() # Prevent clicking through
                    style_suffix 'dialogContent'
                    has vbox
                    transclude


# ==============
# CONFIRM SCREEN
# ==============
screen x52URM_Confirm(prompt, yes=None, no=None, title=None, modal=True, promptSubstitution=True):
    layer 'x52Overlay'
    style_prefix 'x52URM'

    use x52URM_Dialog(title, closeAction=no, modal=modal):
        if promptSubstitution:
            text '[prompt]' xalign .5 text_align .5
        else:
            text '[prompt!q]' xalign .5 text_align .5

        hbox:
            yoffset x52URM.scalePxInt(15)
            xalign 0.5
            if yes:
                key 'K_KP_ENTER' action [Function(yes),Hide('x52URM_Confirm')]
                key 'K_RETURN' action [Function(yes),Hide('x52URM_Confirm')]
                textbutton "Yes" style_suffix "buttonPrimary" action [Function(yes),Hide('x52URM_Confirm')]
                null width x52URM.scalePxInt(20) # We don't use spacing on the hbox, because this will also space between `key` statements
                if no:
                    key 'K_ESCAPE' action [Function(no),Hide('x52URM_Confirm')]
                    textbutton "No" action [Function(no),Hide('x52URM_Confirm')]
                else:
                    key 'K_ESCAPE' action Hide('x52URM_Confirm')
                    textbutton "No" action Hide('x52URM_Confirm')
            else:
                key 'K_KP_ENTER' action Hide('x52URM_Confirm')
                key 'K_RETURN' action Hide('x52URM_Confirm')
                key 'K_ESCAPE' action Hide('x52URM_Confirm')
                textbutton "OK" style_suffix "buttonPrimary" action Hide('x52URM_Confirm')
