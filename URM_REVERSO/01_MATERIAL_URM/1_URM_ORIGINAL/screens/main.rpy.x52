
style x52URM_titleBarButton is x52URM_dialogCloseButton:
    background x52URM.Theme.colors.buttonBg
    hover_background x52URM.Theme.colors.buttonBgHover
    yoffset 0
    padding (x52URM.scalePxInt(8),0)

style x52URM_tab is x52URM_buttonSecondary:
    background x52URM.Theme.colorAlpha(x52URM.Theme.colors.buttonSecondaryBg, .4)
    hover_background x52URM.Theme.colors.buttonSecondaryBgHover
    selected_idle_background x52URM.Theme.colors.buttonSecondaryBgHover
    insensitive_background x52URM.Theme.colors.buttonSecondaryBgDisabled

transform x52URM_blink:
    linear .5 alpha .65
    linear .5 alpha 1.0
    pause 1.0
    repeat

screen URM_overlay():
    layer 'x52Overlay'
    style_prefix "x52URM"

    key "alt_K_m" action x52URM.Open()
    if x52URM.Settings.quickResumeSaveHotKey:
        key "alt_K_q" action x52URM.Gamesaves.Save('_reload-1', name='', overwrite=True, notify='Quick resume saved')
    if x52URM.Settings.quickSaveHotKey:
        key "alt_K_s" action QuickSave()
    if x52URM.Settings.quickLoadHotKey:
        key "alt_K_l" action QuickLoad()
    if x52URM.Settings.consoleHotKey:
        key "alt_K_o" action x52URM.OpenConsole()
    # Prevent the Shift+O when console is disabled
    if not config.console and not config.developer:
        key "shift_K_o" action NullAction()

    if x52URM.Settings.showWatchPanel:
        # Watchpanel toggle key
        if x52URM.Settings.watchpanelToggleKey and isinstance(x52URM.Settings.watchpanelToggleKey, basestring):
            key "K_{}".format(x52URM.Settings.watchpanelToggleKey[0].lower()) action ToggleField(x52URM.Settings, 'collapsedWatchPanel', True, False)

        if x52URM.Settings.collapsedWatchPanel:
            if not x52URM.Settings.watchpanelHideToggleButton or not x52URM.Settings.watchpanelToggleKey:
                if x52URM.Settings.watchPanelPos == 'r': # Position right
                    textbutton "\ue5cb" style_suffix "icon_button" align (1.0, 0.0) action SetField(x52URM.Settings, 'collapsedWatchPanel', False)
                else:
                    textbutton "\ue5cc" style_suffix "icon_button" align (0.0, 0.0) action SetField(x52URM.Settings, 'collapsedWatchPanel', False)
        else:
            use URM_watchpanel

    # # Detection notifications
    use URM_notifications

    # Show the touch buttton
    if x52URM.Settings.touchEnabled or (renpy.variant("touch") and not x52URM.States.gestureInitialized):
        drag:
            draggable True
            if x52URM.Settings.touchPosition:
                pos x52URM.Settings.touchPosition
            else:
                align (.5,.5)
            clicked x52URM.Open()
            dragged x52URM.touchDragged

            idle_child Transform('0x52-URM/images/logo.x52', alpha=.8, zoom=x52URM.getScaleFactor())
            hover_child Transform('0x52-URM/images/logo.x52', zoom=x52URM.getScaleFactor())

    # Show progressbar
    if x52URM.Settings.progressShown:
        use URM_progress


# ===========
# MAIN SCREEN
# ===========
screen URM_main():
    layer 'x52Overlay'
    style_prefix "x52URM"
    modal True

    key "ctrl_K_n" action x52URM.URMFiles.Clear()
    key "ctrl_K_o" action x52URM.URMFiles.Load()
    key "ctrl_K_s" action x52URM.URMFiles.Save()
    key 'K_ESCAPE' action Hide('URM_main')

    frame:
        at x52URM_fadeinout
        style_suffix 'dialog'
        xfill True yfill True
        xmargin x52URM.scalePxInt(-3) ymargin x52URM.scalePxInt(-3)

        hbox:
            ysize x52URM.scalePxInt(42) xoffset x52URM.scalePxInt(3)
            add renpy.display.im.FactorScale('0x52-URM/images/logo.x52', x52URM.getScaleFactor()*.95) yalign .5

        hbox:
            align (1.0, 0.0)
            spacing 2
            button: # Update
                style_suffix 'titleBarButton'
                if x52URM.API.updateAvailable:
                    at x52URM_blink
                text '\ue923' style_suffix 'icon_button_text' yalign .5
                hovered x52URM.Tooltip("{urm_notl}Check for update{/urm_notl}") unhovered x52URM.Tooltip()
                action Show('URM_update')
            button: # Panel
                style_suffix 'titleBarButton'
                text If(x52URM.Settings.showWatchPanel, '\ue8f4', '\ue8f5') style_suffix 'icon_button_text' yalign .5
                hovered x52URM.Tooltip("{urm_notl}Toggle watchpanel{/urm_notl}") unhovered x52URM.Tooltip()
                action ToggleField(x52URM.Settings, 'showWatchPanel', True, False)
            button: # Close
                style_suffix 'dialogCloseButton'
                yoffset 0
                hovered x52URM.Tooltip('{urm_notl}Close URM{/urm_notl}') unhovered x52URM.Tooltip()
                text 'x' size x52URM.scalePxInt(24) yalign .5 color x52URM.Theme.colors.errorBg
                action Hide('URM_main')

        vbox:
            xfill True

            # Header
            vbox:
                ysize x52URM.scalePxInt(46)
                align (0.5, 0.0)
                text "Universal Ren'Py Mod" style_suffix "header_text" yalign .5

            # File buttons
            hbox:
                xalign 1.0 spacing 2
                if x52URM.Tooltip.currentText:
                    text x52URM.Tooltip.currentText yalign 0.5
                else:
                    if x52URM.URMFiles.file.filename:
                        text 'Loaded: [x52URM.URMFiles.file.filename]' yalign 0.5
                        if x52URM.URMFiles.file.unsaved:
                            label "*" yalign 0.5
                    elif x52URM.URMFiles.file.unsaved:
                        label "{urm_notl}Unsaved{/urm_notl}" yalign 0.5
                null width x52URM.scalePxInt(10)
                textbutton "\ue24d" style_suffix "icon_button" hovered x52URM.Tooltip('New (Ctrl+N)') unhovered x52URM.Tooltip() action x52URM.URMFiles.Clear() # New
                textbutton "\ue2c7" style_suffix "icon_button" hovered x52URM.Tooltip('Open (Ctrl+O)') unhovered x52URM.Tooltip() action x52URM.URMFiles.Load() # Open
                textbutton "\ue161" style_suffix "icon_button" hovered x52URM.Tooltip('Save (Ctrl+S)') unhovered x52URM.Tooltip() action x52URM.URMFiles.Save() # Save
                null width x52URM.scalePxInt(10)

            null height x52URM.scalePxInt(10)
            frame style_suffix "seperator"
            hbox:
                # Tabs
                vbox:
                    use URM_tabbutton('{urm_notl}Search{/urm_notl}', '\ue880', 'search')
                    use URM_tabbutton('{urm_notl}Variables{/urm_notl}', '\uef54', 'variables')
                    use URM_tabbutton('{urm_notl}Snapshots{/urm_notl}', '\ue412', 'snapshots')
                    use URM_tabbutton('{urm_notl}Labels{/urm_notl}', '\ue54e', 'labels')
                    use URM_tabbutton('{urm_notl}Renaming{/urm_notl}', '\ue560', 'textrepl')
                    use URM_tabbutton('{urm_notl}Textboxes{/urm_notl}', '\ue0b7', 'textboxCustomizations')
                    use URM_tabbutton('{urm_notl}Gamesaves{/urm_notl}', '\ue161', 'gamesaves')
                    use URM_tabbutton('{urm_notl}Options{/urm_notl}', '\ue8b8', 'options')
                frame style_suffix "vseperator"
                null width x52URM.scalePxInt(10)

                # Content
                vbox:
                    null height x52URM.scalePxInt(10)

                    if x52URM.Settings.currentScreen == 'search':
                        use URM_search()
                    elif x52URM.Settings.currentScreen == 'variables':
                        use URM_variables()
                    elif x52URM.Settings.currentScreen == 'snapshots':
                        use URM_snapshots()
                    elif x52URM.Settings.currentScreen == 'labels':
                        use URM_labels()
                    elif x52URM.Settings.currentScreen == 'textrepl':
                        use URM_textrepl()
                    elif x52URM.Settings.currentScreen == 'textboxCustomizations':
                        use URM_textboxCustomizations()
                    elif x52URM.Settings.currentScreen == 'gamesaves':
                        use URM_gamesaves()
                    elif isinstance(x52URM.Settings.currentScreen, basestring) and x52URM.Settings.currentScreen.startswith('options'):
                        use URM_options_main(x52URM.Settings.currentScreen[8:])

# =========
# TABBUTTON
# =========
screen URM_tabbutton(title, icon, name):
    button:
        style_suffix 'tab'
        xsize x52URM.scalePxInt(100) ysize x52URM.scalePxInt(80)
        vbox:
            yalign .5 xalign .5
            text icon style_suffix 'icon_button_text' xalign .5 size x52URM.scalePxInt(38)
            null width 2
            label title xalign .5 text_size x52URM.scalePxInt(12)
        selected (isinstance(x52URM.Settings.currentScreen, basestring) and x52URM.Settings.currentScreen.startswith(name))
        action SetField(x52URM.Settings, 'currentScreen', name)
    frame style_suffix "seperator" xsize x52URM.scalePxInt(100) background x52URM.Theme.secondary

# ==============
# WARNING SCREEN
# ==============
screen URM_warning():
    layer 'x52Overlay'
    style_prefix "x52URM"
    modal True

    use x52URM_Dialog("{color=#f42929}Warning!{/color}", closeAction=Hide('URM_warning'), icon='\ue8b2'):
        text "Using this mod is at your own risk!" xalign .5
        text "Modifying values could break the game!" xalign .5
        hbox:
            yoffset x52URM.scalePxInt(15)
            xalign 0.5
            textbutton "{urm_notl}Got it!{/urm_notl}" style_suffix "buttonPrimary" action [Hide('URM_warning'),Show('URM_main')]
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Sure, don't warn me again{/urm_notl}" action [x52URM.SetURMSetting('warningDisabled',True,globalSetting=True),x52URM.SetURMSetting('warningDisabled',True,globalSetting=False),Hide('URM_warning'),Show('URM_main')]

# ==============
# WELCOME SCREEN
# ==============
screen URM_welcome():
    layer 'x52Overlay'
    style_prefix "x52URM"

    use x52URM_Dialog("Universal Ren'Py Mod [x52URM.version]", closeAction=Hide('URM_welcome')):
        if x52URM.Settings.seenWelcome == 1:
            text "IMPORTANT:\nThe shortcut for opening URM changed to {b}Alt+M{/b}!"
        else:
            text "You've just installed URM." xalign .5
            if x52URM.Settings.touchEnabled:
                text "Since you're on a touch device, there's a 0x52 logo that can be dragged around and used to open URM" xalign .5
                text "You can disable this logo in the options and open URM by drawing an U on screen (swipe down-right-up)" xalign .5
            elif renpy.variant("touch") and x52URM.States.gestureInitialized:
                text "You can open URM by drawing an U on screen (swipe down-right-up)" xalign .5
            else:
                text "You can open it by pressing {b}Alt+M{/b} at any point in the game" xalign .5
        hbox:
            yoffset x52URM.scalePxInt(15)
            xalign 0.5
            textbutton "{urm_notl}Okay{/urm_notl}" style_suffix "buttonPrimary" action [SetField(x52URM.Settings,'seenWelcome',2),Hide('URM_welcome')]

# =====================
# SPLASHSCREEN OVERRIDE
# =====================
label URM_splashscreen:
    $ del config.label_overrides['splashscreen']
    if not x52URM.Settings.skipSplashscreen and renpy.has_label('splashscreen'):
        call _splashscreen

    return

# =============================================================================
# Pages screen to use inside other screens (pass x52URM.Pages() object as argument)
# =============================================================================
screen URM_pages(pages):
    if pages.pageCount:
        textbutton "\ue5dc" style_suffix 'icon_button' sensitive (pages.currentPage>1) action SetField(pages, 'currentPage', 1) yalign .5 hovered x52URM.Tooltip('{urm_notl}Go to first page{/urm_notl}') unhovered x52URM.Tooltip()
        textbutton "\ue408" style_suffix 'icon_button' sensitive (pages.currentPage>1) action SetField(pages, 'currentPage', pages.currentPage-1) yalign .5 hovered x52URM.Tooltip('{urm_notl}Go to previous page{/urm_notl}') unhovered x52URM.Tooltip()

        for page in pages.pageRange:
            textbutton If(page<10, '0[page]', '[page]') sensitive (page != pages.currentPage) action SetField(pages, 'currentPage', page)

        textbutton "\ue409" style_suffix 'icon_button' sensitive (pages.currentPage<pages.pageCount) action SetField(pages, 'currentPage', pages.currentPage+1) yalign .5 hovered x52URM.Tooltip('{urm_notl}Go to next page{/urm_notl}') unhovered x52URM.Tooltip()
        textbutton "\ue5dd" style_suffix 'icon_button' sensitive (pages.currentPage<pages.pageCount) action SetField(pages, 'currentPage', pages.pageCount) yalign .5 hovered x52URM.Tooltip('{urm_notl}Go to last page{/urm_notl}') unhovered x52URM.Tooltip()
