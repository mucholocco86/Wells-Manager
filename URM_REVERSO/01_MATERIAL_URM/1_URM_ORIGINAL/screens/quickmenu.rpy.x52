
transform URM_quickmenu_hover:
    on show:
        linear .2 alpha 1.0
    on hide:
        linear .2 alpha 0.0

screen URM_quickmenu:
    layer 'x52Overlay'
    style_prefix 'x52URM'
    default hovered = False

    if x52URM.Settings.quickmenuEnabled:
        if x52URM.Settings.quickmenuAutoHide:
            mousearea:
                xalign x52URM.Settings.quickmenuAlignX
                yalign x52URM.Settings.quickmenuAlignY
                xysize x52URM.getScreenSize('URM_quickmenu_contentWrapper')
                hovered SetScreenVariable('hovered', True)
                unhovered SetScreenVariable('hovered', False)

        showif not x52URM.Settings.quickmenuAutoHide or hovered:
            use URM_quickmenu_contentWrapper

screen URM_quickmenu_contentWrapper:
    hbox:
        style_prefix 'quick'
        at URM_quickmenu_hover
        spacing x52URM.scalePxInt(4)
        xalign x52URM.Settings.quickmenuAlignX
        yalign x52URM.Settings.quickmenuAlignY

        if x52URM.Settings.quickmenuVertical:
            vbox:
                spacing x52URM.scalePxInt(4)
                use URM_quickmenu_content
        else:
            use URM_quickmenu_content

screen URM_quickmenu_content:
    if x52URM.Settings.quickmenuBtnBack:
        use URM_quickmenu_button('\ue045', '{urm_notl}Back{/urm_notl}', Rollback())
    if x52URM.Settings.quickmenuBtnSkip:
        use URM_quickmenu_button('\ue044', '{urm_notl}Skip{/urm_notl}', Skip(), Skip(True))
    if x52URM.Settings.quickmenuBtnAuto:
        use URM_quickmenu_button('\ue01f', '{urm_notl}Auto{/urm_notl}', Preference("auto-forward", "toggle"))
    if x52URM.Settings.quickmenuBtnQuicksave:
        use URM_quickmenu_button('\ue161', '{urm_notl}Q.Save{/urm_notl}', QuickSave())
    if x52URM.Settings.quickmenuBtnSave:
        use URM_quickmenu_button('\ueb60', '{urm_notl}Save{/urm_notl}', ShowMenu('save'))
    if x52URM.Settings.quickmenuBtnQuickload:
        use URM_quickmenu_button('\ue2c7', '{urm_notl}Q.Load{/urm_notl}', QuickLoad())
    if x52URM.Settings.quickmenuBtnLoad:
        use URM_quickmenu_button('\uf1c7', '{urm_notl}Load{/urm_notl}', ShowMenu('load'))
    if x52URM.Settings.quickmenuBtnMenu:
        use URM_quickmenu_button('\ue8b8', '{urm_notl}Prefs{/urm_notl}', ShowMenu('preferences'))
    if x52URM.Settings.quickmenuBtnUrm:
        use URM_quickmenu_button('\ue3c9', '{urm_notl}URM{/urm_notl}', x52URM.Open())
    if x52URM.Settings.quickmenuBtnExit:
        use URM_quickmenu_button('\ueb4f', '{urm_notl}Exit{/urm_notl}', Quit())

screen URM_quickmenu_button(icon, txt, action, alternate=None):
    if x52URM.Settings.quickmenuStyle == 'buttons':
        use x52URM_iconButton(icon, txt, action, alternate=alternate)
    elif x52URM.Settings.quickmenuStyle == 'iconbuttons':
        use x52URM_iconButton(icon, action=action, alternate=alternate)
    elif x52URM.Settings.quickmenuStyle == 'icons':
        textbutton icon xalign x52URM.Settings.quickmenuAlignX action action alternate alternate style 'x52URM_icon_textbutton' text_outlines [(absolute(2), '#222', 0, 0)] text_size x52URM.scalePxInt(28)
    else:
        textbutton txt xalign x52URM.Settings.quickmenuAlignX action action alternate alternate
