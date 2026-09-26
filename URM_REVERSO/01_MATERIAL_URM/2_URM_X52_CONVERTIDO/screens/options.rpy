
# ====================
# SETTINGS MAIN SCREEN
# ====================
screen URM_options_main(selectedOption=None):
    style_prefix "x52URM"
    default currentOption = selectedOption
    default buttonWidth = x52URM.scaleX(15)
    
    hbox:
        vbox spacing 2:
            use x52URM_iconButton('\ue7f4', '{urm_notl}Notifications{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_notifications'), xsize=buttonWidth)
            use x52URM_iconButton('\ue8f4', '{urm_notl}Watch panel{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_watchpanel'), xsize=buttonWidth)
            use x52URM_iconButton('\ue161', '{urm_notl}Gamesaves{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_gamesaves'), xsize=buttonWidth)
            use x52URM_iconButton('\ue5d2', '{urm_notl}Quickmenu{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_quickmenu'), xsize=buttonWidth)
            use x52URM_iconButton('\ue8b8', '{urm_notl}Miscellaneous{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_misc'), xsize=buttonWidth)
            use x52URM_iconButton('\ue40a', '{urm_notl}Appearance{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_appearance'), xsize=buttonWidth)
            use x52URM_iconButton('\ue923', '{urm_notl}Updates{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_updates'), xsize=buttonWidth)
            use x52URM_iconButton('\ueb8b', '{urm_notl}About URM{/urm_notl}', action=SetField(x52URM.Settings, 'currentScreen', 'options_about'), xsize=buttonWidth)

        null width 5
        frame style_suffix "vseperator" xsize x52URM.scalePxInt(2)
        null width 5

        vbox:
            xfill True yfill True

            # if renpy.has_screen('URM_options_{}'.format(x52URM.Settings.currentScreen[8:])):
            #     use expression 'URM_options_{}'.format(x52URM.Settings.currentScreen[8:]) # THIS IS NOT AVAILABLE IN OLDER RENPY VERSIONS
            if x52URM.Settings.currentScreen[8:] == 'notifications':
                use URM_options_notifications()
            elif x52URM.Settings.currentScreen[8:] == 'watchpanel':
                use URM_options_watchpanel()
            elif x52URM.Settings.currentScreen[8:] == 'gamesaves':
                use URM_options_gamesaves()
            elif x52URM.Settings.currentScreen[8:] == 'quickmenu':
                use URM_options_quickmenu()
            elif x52URM.Settings.currentScreen[8:] == 'misc':
                use URM_options_misc()
            elif x52URM.Settings.currentScreen[8:] == 'appearance':
                use URM_options_appearance()
            elif x52URM.Settings.currentScreen[8:] == 'updates':
                use URM_options_updates()
            elif x52URM.Settings.currentScreen[8:] == 'about':
                use URM_options_about()
            else:
                label '{urm_notl}Select an option on the left{/urm_notl}' align (.5,.05)

# =============
# NOTIFICATIONS
# =============
screen URM_options_notifications():
    style_prefix 'x52URM'

    vbox yfill True:
        vbox yoffset 20:
            use URM_options_settings({
                'showReplayNotification': {
                    'title': '{urm_notl}Replay notification{/urm_notl}',
                    'description': """This option makes URM display a notification when you're in a replay\nand gives the option to quickly end it""",
                    'effective': If(x52URM.Settings.showReplayNotification, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                },
                'showChoicesNotification': {
                    'title': '{urm_notl}Choices notification{/urm_notl}',
                    'description': """This option makes URM display a notification when it detected choices\n\nThis notification also reports the number of hidden choices\nand gives quick access to more options regarding the choices\n\nYou can open the choices dialog by pressing Alt+C""",
                    'effective': If(x52URM.Settings.showChoicesNotification, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                },
                'showPathsNotification': {
                    'title': '{urm_notl}Paths notification{/urm_notl}',
                    'description': """This option makes URM display a notification when it detected a path/if-statement\nand gives quick access to more options/infor regarding the paths\n\nYou can open the choices dialog by pressing Alt+A""",
                    'effective': If(x52URM.Settings.showPathsNotification, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                },
                'stopSkippingOnPathDetection': {
                    'title': '{urm_notl}Stop skipping on path detection{/urm_notl}',
                    'description': """When you're skipping content and this option is enabled, skipping will be canceled on path detection""",
                    'effective': If(x52URM.Settings.stopSkippingOnPathDetection, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                },
                'notificationTimeout': {
                    'title': '{urm_notl}Time-out{/urm_notl}',
                    'description': """Automatically close the notification after this number of seconds""",
                    'effective': If(x52URM.Settings.notificationTimeout, '{urm_notl}[x52URM.Settings.notificationTimeout]s{/urm_notl}', '{urm_notl}Never{/urm_notl}'),
                    'options': {
                        '{urm_notl}Never{/urm_notl}': 0,
                        '{urm_notl}5s{/urm_notl}': 5,
                        '{urm_notl}10s{/urm_notl}': 10,
                    },
                },
            }, colWidth=[x52URM.scaleX(22),x52URM.scaleX(8),x52URM.scaleX(22),x52URM.scaleX(22)])

# ==========
# WATCHPANEL
# ==========
screen URM_options_watchpanel():
    style_prefix 'x52URM'

    vbox yfill True:
        vbox yoffset 20:
            use URM_options_settings(x52URM.OrderedDict([
                ('showWatchPanel', {
                    'title': '{urm_notl}Enable watchpanel{/urm_notl}',
                    'effective': If(x52URM.Settings.showWatchPanel, '{urm_notl}Enabled{/urm_notl}', '{urm_notl}Disabled{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('watchpanelToggleKey', {
                    'title': '{urm_notl}Toggle using M-key{/urm_notl}',
                    'description': """Quickly open/close the watchpanel using this key""",
                    'effective': If(x52URM.Settings.watchpanelToggleKey, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': 'M',
                        '{urm_notl}Off{/urm_notl}': '',
                    },
                }),
                ('watchpanelHideToggleButton', {
                    'title': '{urm_notl}Hide togglebutton{/urm_notl}',
                    'description': """This removes the arrow button in the top corner\nNote: This only works when "Toggle using M-key" is enabled""",
                    'effective': If(x52URM.Settings.watchpanelHideToggleButton, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('watchPanelPos', {
                    'title': '{urm_notl}Panel position{/urm_notl}',
                    'effective': If(x52URM.Settings.watchPanelPos=='r', '{urm_notl}Right{/urm_notl}', '{urm_notl}Left{/urm_notl}'),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Left{/urm_notl}', 'l'),
                        ('{urm_notl}Right{/urm_notl}', 'r'),
                    ]),
                }),
                ('watchPanelFileLine', {
                    'title': '{urm_notl}Current file:line{/urm_notl}',
                    'description': 'Show the last ran file:line of code',
                    'effective': If(x52URM.Settings.watchPanelFileLine==2, '{urm_notl}Compact{/urm_notl}', If(x52URM.Settings.watchPanelFileLine==1, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}')),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Show{/urm_notl}', 1),
                        ('{urm_notl}Compact{/urm_notl}', 2),
                        ('{urm_notl}Hide{/urm_notl}', 0),
                    ]),
                }),
                ('watchPanelCurrentLabel', {
                    'title': '{urm_notl}Last seen label{/urm_notl}',
                    'description': 'Shows the current label we\'re in',
                    'effective': If(x52URM.Settings.watchPanelCurrentLabel==2, '{urm_notl}Compact{/urm_notl}', If(x52URM.Settings.watchPanelCurrentLabel==1, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}')),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Show{/urm_notl}', 1),
                        ('{urm_notl}Compact{/urm_notl}', 2),
                        ('{urm_notl}Hide{/urm_notl}', 0),
                    ]),
                }),
                ('watchPanelChoiceDetection', {
                    'title': '{urm_notl}Choice detection{/urm_notl}',
                    'description': '{urm_notl}Shows information about the current choice{/urm_notl}',
                    'effective': If(x52URM.Settings.watchPanelChoiceDetection==2, '{urm_notl}Compact{/urm_notl}', If(x52URM.Settings.watchPanelChoiceDetection==1, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}')),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Show{/urm_notl}', 1),
                        ('{urm_notl}Compact{/urm_notl}', 2),
                        ('{urm_notl}Hide{/urm_notl}', 0),
                    ]),
                }),
                ('watchPanelPathDetection', {
                    'title': '{urm_notl}Path detection{/urm_notl}',
                    'description': '{urm_notl}Shows information about a detected path{/urm_notl}',
                    'effective': If(x52URM.Settings.watchPanelPathDetection==2, '{urm_notl}Compact{/urm_notl}', If(x52URM.Settings.watchPanelPathDetection==1, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}')),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Show{/urm_notl}', 1),
                        ('{urm_notl}Compact{/urm_notl}', 2),
                        ('{urm_notl}Hide{/urm_notl}', 0),
                    ]),
                }),
                ('watchPanelProgress', {
                    'title': '{urm_notl}Progress{/urm_notl}',
                    'description': '{urm_notl}Shows how much of the content has been seen (in all playthroughs combined){/urm_notl}',
                    'effective': If(x52URM.Settings.watchPanelProgress==2, '{urm_notl}Compact{/urm_notl}', If(x52URM.Settings.watchPanelProgress==1, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}')),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Show{/urm_notl}', 1),
                        ('{urm_notl}Compact{/urm_notl}', 2),
                        ('{urm_notl}Hide{/urm_notl}', 0),
                    ]),
                }),
                ('watchPanelVars', {
                    'title': '{urm_notl}Watched variables{/urm_notl}',
                    'effective': If(x52URM.Settings.watchPanelVars==2, '{urm_notl}Compact{/urm_notl}', If(x52URM.Settings.watchPanelVars==1, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}')),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Show{/urm_notl}', 1),
                        ('{urm_notl}Compact{/urm_notl}', 2),
                        ('{urm_notl}Hide{/urm_notl}', 0),
                    ]),
                }),
            ]), colWidth=[x52URM.scaleX(16),x52URM.scaleX(9),x52URM.scaleX(25),x52URM.scaleX(25)])

# =========
# LOAD/SAVE
# =========
screen URM_options_gamesaves():
    style_prefix 'x52URM'

    vbox yfill True:
        vbox yoffset 20:
            use URM_options_settings(x52URM.OrderedDict([
                ('askSaveName', {
                    'title': '{urm_notl}Ask name before saving{/urm_notl}',
                    'effective': If(x52URM.Settings.askSaveName, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('quickResumeSaveHotKey', {
                    'title': 'Save {b}quick resume{/b} with Alt+Q',
                    'effective': If(x52URM.Settings.quickResumeSaveHotKey, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('quickSaveHotKey', {
                    'title': '{b}Quick save{/b} with Alt+S',
                    'effective': If(x52URM.Settings.quickSaveHotKey, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('quickLoadHotKey', {
                    'title': 'Load last {b}quick save{/b} with Alt+L',
                    'effective': If(x52URM.Settings.quickLoadHotKey, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
            ]))

# ==================
# Quickmenu settings
# ==================
screen URM_options_quickmenu():
    style_prefix 'x52URM'
    default colWidth = [x52URM.scaleX(15),x52URM.scaleX(10),x52URM.scaleX(25),x52URM.scaleX(25)]

    vbox yfill True:
        vbox yoffset 20:
            use URM_options_settings(x52URM.OrderedDict([
                ('quickmenuEnabled', {
                    'title': '{urm_notl}Quickmenu{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuEnabled, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('quickmenuAlignX', {
                    'title': '{urm_notl}Horizontal alignment{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuAlignX==0, '{urm_notl}Left{/urm_notl}', If(x52URM.Settings.quickmenuAlignX==.5, '{urm_notl}Center{/urm_notl}', '{urm_notl}Right{/urm_notl}')),
                    'options': {
                        '{urm_notl}Left{/urm_notl}': 0.0,
                        '{urm_notl}Center{/urm_notl}': 0.5,
                        '{urm_notl}Right{/urm_notl}': 1.0,
                    },
                }),
                ('quickmenuAlignY', {
                    'title': '{urm_notl}Vertical alignment{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuAlignY==0, '{urm_notl}Top{/urm_notl}', If(x52URM.Settings.quickmenuAlignY==.5, '{urm_notl}Middle{/urm_notl}', '{urm_notl}Bottom{/urm_notl}')),
                    'options': {
                        '{urm_notl}Top{/urm_notl}': 0.0,
                        '{urm_notl}Middle{/urm_notl}': 0.5,
                        '{urm_notl}Bottom{/urm_notl}': 1.0,
                    },
                }),
                ('quickmenuVertical', {
                    'title': '{urm_notl}Orientation{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuVertical, '{urm_notl}Vertical{/urm_notl}', '{urm_notl}Horizontal{/urm_notl}'),
                    'options': {
                        '{urm_notl}Vertical{/urm_notl}': True,
                        '{urm_notl}Horizontal{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnBack', {
                    'title': '{urm_notl}{b}Button:{/b} Back{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnBack, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnSkip', {
                    'title': '{urm_notl}{b}Button:{/b} Skip{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnSkip, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnAuto', {
                    'title': '{urm_notl}{b}Button:{/b} Auto{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnAuto, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnQuicksave', {
                    'title': '{urm_notl}{b}Button:{/b} Quicksave{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnQuicksave, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnSave', {
                    'title': '{urm_notl}{b}Button:{/b} Save{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnSave, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnQuickload', {
                    'title': '{urm_notl}{b}Button:{/b} Quickload{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnQuickload, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnLoad', {
                    'title': '{urm_notl}{b}Button:{/b} Load{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnLoad, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnMenu', {
                    'title': '{urm_notl}{b}Button:{/b} Menu{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnMenu, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnUrm', {
                    'title': '{urm_notl}{b}Button:{/b} URM{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnUrm, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuBtnExit', {
                    'title': '{urm_notl}{b}Button:{/b} Exit{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuBtnExit, '{urm_notl}Show{/urm_notl}', '{urm_notl}Hide{/urm_notl}'),
                    'options': {
                        '{urm_notl}Show{/urm_notl}': True,
                        '{urm_notl}Hide{/urm_notl}': False,
                    },
                }),
                ('quickmenuAutoHide', {
                    'title': '{urm_notl}Auto hide{/urm_notl}',
                    'description': 'Only show the quickmenu when you hover the area',
                    'effective': If(x52URM.Settings.quickmenuAutoHide, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('quickmenuStyle', {
                    'title': '{urm_notl}Style{/urm_notl}',
                    'effective': If(x52URM.Settings.quickmenuStyle=='buttons', '{urm_notl}Buttons{/urm_notl}', If(x52URM.Settings.quickmenuStyle=='iconbuttons', '{urm_notl}Iconbuttons{/urm_notl}', If(x52URM.Settings.quickmenuStyle=='icons', '{urm_notl}Icons{/urm_notl}', '{urm_notl}Default{/urm_notl}'))),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Default{/urm_notl}', 'default'),
                        ('{urm_notl}Buttons{/urm_notl}', 'buttons'),
                        ('{urm_notl}Iconbuttons{/urm_notl}', 'iconbuttons'),
                        ('{urm_notl}Icons{/urm_notl}', 'icons'),
                    ]),
                }),
            ]), colWidth)

# =============
# MISCELLANEOUS
# =============
screen URM_options_misc():
    style_prefix 'x52URM'

    vbox yfill True:
        vbox yoffset 20:
            use URM_options_settings(x52URM.OrderedDict([
                ('consoleHotKey', {
                    'title': '{urm_notl}Open console with Alt+O{/urm_notl}',
                    'description': """Open the Ren'Py console. Even when it's disabled in the Ren'Py config""",
                    'effective': If(x52URM.Settings.consoleHotKey, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('skipSplashscreen', {
                    'title': '{urm_notl}Skip splashscreen{/urm_notl}',
                    'description': """This option skips the splashscreen at the start of the game (if any) and takes you directly to the menu""",
                    'effective': If(x52URM.Settings.skipSplashscreen, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('codeViewShowAll', {
                    'title': '{urm_notl}Show all code in the codeview{/urm_notl}',
                    'description': """When this option is turned off, all less relevant code is hidden in choice/path detection\nStuff like \"renpy.pause()\" and \"renpy.play('someaudio.mp3')\"""",
                    'effective': If(x52URM.Settings.codeViewShowAll, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('progressShown', {
                    'title': '{urm_notl}Show progressbar{/urm_notl}',
                    'description': "Shows a draggable progressbar, this bar shows how much of the dialogue has been seen (in all playthroughs combined)",
                    'effective': If(x52URM.Settings.progressShown, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
                ('progressShowNew', {
                    'title': '{urm_notl}Show progressbar newly seen{/urm_notl}',
                    'description': "Show the amount of dialogue that has been seen for the first time during the current session in the progressbar",
                    'effective': If(x52URM.Settings.progressShowNew, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
            ] + ([
                ('touchEnabled', { # We only show this option on non-touch devices
                    'title': '{urm_notl}Enable touch control{/urm_notl}',
                    'description': """This will show a 0x52 logo on screen that you can drag around and click to open URM\n{size=-6}{alpha=.9}When you disable this on a touch device, you're still able to open URM by drawing an U on screen (down-right-up){/alpha}{/size}""",
                    'effective': If(x52URM.Settings.touchEnabled, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                }),
            ] if not renpy.variant('touch') or x52URM.States.gestureInitialized else [])))

# ==========
# APPEARANCE
# ==========
screen URM_options_appearance():
    style_prefix 'x52URM'
    default colWidth = [x52URM.scaleX(15),x52URM.scaleX(10),x52URM.scaleX(20),x52URM.scaleX(20)]

    vbox:
        use URM_tableRow():
            hbox xsize colWidth[0]:
                hbox:
                    label '{urm_notl}Setting{/urm_notl}'
                    textbutton '\uf1c0' yoffset -x52URM.scalePxInt(4) style_suffix 'icon_textbutton' action x52URM.Confirm("""There are 2 settings levels:\n{b}Local{/b}: The setting for the current game\n{b}Global{/b}: The setting for all games (that don't have a local setting)\n\nThe value under {b}Effective{/b} is the setting used in the current game""", title='Settings explanation')
            hbox xsize colWidth[1]:
                label '{urm_notl}Effective{/urm_notl}'
            hbox xsize colWidth[2]:
                label '{urm_notl}Local{/urm_notl}'
            hbox xsize colWidth[3]:
                hbox:
                    label '{urm_notl}Global{/urm_notl}'
                    if x52URM.Settings.globalAvailable == False:
                        textbutton '\uf1c0' yoffset -x52URM.scalePxInt(4) text_color x52URM.Theme.colors.errorText style_suffix 'icon_textbutton' action x52URM.Confirm('Global settings are unavailable in this game', title='{urm_notl}Global settings unavailable{/urm_notl}')

        use URM_table(spacing=x52URM.scalePxInt(10)):
            use URM_tableRow(0, True):
                hbox xsize colWidth[0]:
                    text '{urm_notl}Transparency{/urm_notl}'
                hbox xsize colWidth[1]:
                    text str(int(x52URM.Settings.themeTransparency*100))+'%'
                vbox xsize colWidth[2] spacing x52URM.scalePxInt(10):
                    hbox spacing x52URM.scalePxInt(10):
                        textbutton '0%' action x52URM.SetDialogTransparency(0, globalSetting=False)
                        textbutton '10%' action x52URM.SetDialogTransparency(0.1, globalSetting=False)
                        textbutton '20%' action x52URM.SetDialogTransparency(0.2, globalSetting=False)
                        textbutton '30%' action x52URM.SetDialogTransparency(0.3, globalSetting=False)
                        textbutton '40%' action x52URM.SetDialogTransparency(0.4, globalSetting=False)
                    hbox spacing x52URM.scalePxInt(10):
                        textbutton '5%' action x52URM.SetDialogTransparency(0.05, globalSetting=False)
                        textbutton '15%' action x52URM.SetDialogTransparency(0.15, globalSetting=False)
                        textbutton '25%' action x52URM.SetDialogTransparency(0.25, globalSetting=False)
                        textbutton '35%' action x52URM.SetDialogTransparency(0.35, globalSetting=False)
                        textbutton '45%' action x52URM.SetDialogTransparency(0.45, globalSetting=False)
                    use x52URM_iconButton('\ue872', '{urm_notl}Clear{/urm_notl}', x52URM.SetDialogTransparency(None, globalSetting=False), sensitive=(x52URM.Settings.get('themeTransparency', globalSetting=False)!=None))
                vbox xsize colWidth[3] spacing x52URM.scalePxInt(10):
                    hbox spacing x52URM.scalePxInt(10):
                        textbutton '0%' action x52URM.SetDialogTransparency(0, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '10%' action x52URM.SetDialogTransparency(0.1, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '20%' action x52URM.SetDialogTransparency(0.2, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '30%' action x52URM.SetDialogTransparency(0.3, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '40%' action x52URM.SetDialogTransparency(0.4, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                    hbox spacing x52URM.scalePxInt(10):
                        textbutton '5%' action x52URM.SetDialogTransparency(0.05, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '15%' action x52URM.SetDialogTransparency(0.15, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '25%' action x52URM.SetDialogTransparency(0.25, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '35%' action x52URM.SetDialogTransparency(0.35, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                        textbutton '45%' action x52URM.SetDialogTransparency(0.45, globalSetting=True) sensitive If(x52URM.Settings.globalAvailable, None, False)
                    use x52URM_iconButton('\ue872', '{urm_notl}Default{/urm_notl}', x52URM.SetDialogTransparency(None, globalSetting=True), sensitive=If(x52URM.Settings.globalAvailable, None, False))

            use URM_tableRow(1, True):
                hbox xsize colWidth[0]:
                    text '{urm_notl}Theme{/urm_notl}'
                hbox xsize colWidth[1]:
                    text '[x52URM.Settings.theme]'
                vbox xsize colWidth[2] spacing x52URM.scalePxInt(10):
                    for name in x52URM.availableThemes:
                        use URM_options_themeOption(name, globalSetting=False)
                    use x52URM_iconButton('\ue872', '{urm_notl}Clear{/urm_notl}', x52URM.SetTheme(None, globalSetting=False), sensitive=(x52URM.Settings.get('theme', globalSetting=False)!=None))
                vbox xsize colWidth[3] spacing x52URM.scalePxInt(10):
                    for name in x52URM.availableThemes:
                        use URM_options_themeOption(name, globalSetting=True)


screen URM_options_themeOption(themeName, globalSetting=None):
    style_prefix 'x52URM'

    hbox:
        spacing x52URM.scalePxInt(10)
        frame:
            background x52URM.Theme.getButtonBg(x52URM.availableThemes[themeName]['background'], x52URM.availableThemes[themeName]['text'])
            ysize x52URM.scalePxInt(36)
            yalign .5
            hbox:
                spacing x52URM.scalePxInt(10)
                frame:
                    background x52URM.Theme.getButtonBg(x52URM.availableThemes[themeName]['primary'], x52URM.availableThemes[themeName]['text'])
                    xsize x52URM.scalePxInt(28)
                frame:
                    background x52URM.Theme.getButtonBg(x52URM.availableThemes[themeName]['secondary'], x52URM.availableThemes[themeName]['text'])
                    xsize x52URM.scalePxInt(28)
                frame:
                    background x52URM.Theme.getButtonBg(x52URM.availableThemes[themeName]['tertiary'], x52URM.availableThemes[themeName]['text'])
                    xsize x52URM.scalePxInt(28)
        use x52URM_radiobutton(x52URM.Settings.get('theme', globalSetting)==themeName, themeName, x52URM.SetTheme(themeName, globalSetting), sensitive=If(not globalSetting or x52URM.Settings.globalAvailable, None, False))


# =======
# UPDATES
# =======
screen URM_options_updates():
    style_prefix 'x52URM'

    on 'show' action If(x52URM.API.updates==None, Function(x52URM.API.fetchUpdate, renpy.restart_interaction, renpy.restart_interaction), None)

    vbox yfill True:
        vbox:
            hbox:
                text 'Your version: '
                label "[x52URM.version]"
            hbox:
                text 'Latest version: ' yalign .5
                if x52URM.API.updates == None and not x52URM.API.latestError:
                    label '{urm_notl}Loading...{/urm_notl}' yalign .5
                elif x52URM.API.updateAvailable:
                    label x52URM.API.updateAvailable yalign .5
                    null width 5
                    use x52URM_iconButton('\ue923', '{urm_notl}Details{/urm_notl}', action=Show('URM_update'))
                else:
                    label 'N/A' yalign .5

            null height 20
            use URM_options_settings({
                'updateChannel': {
                    'title': '{urm_notl}Update channel{/urm_notl}',
                    'effective': If(x52URM.Settings.updateChannel=='beta', '{urm_notl}Beta{/urm_notl}', '{urm_notl}Stable{/urm_notl}'),
                    'options': x52URM.OrderedDict([
                        ('{urm_notl}Stable{/urm_notl}', 'stable'),
                        ('{urm_notl}Beta{/urm_notl}', 'beta'),
                    ]),
                },
                'autoUpdateCheck': {
                    'title': '{urm_notl}Check for update at startup{/urm_notl}',
                    'effective': If(x52URM.Settings.autoUpdateCheck, '{urm_notl}On{/urm_notl}', '{urm_notl}Off{/urm_notl}'),
                    'options': {
                        '{urm_notl}On{/urm_notl}': True,
                        '{urm_notl}Off{/urm_notl}': False,
                    },
                },
            })

# ======================
# CREATE A SETTINGS GRID
# ======================
screen URM_options_settings(settings, colWidth=[x52URM.scaleX(25),x52URM.scaleX(10),x52URM.scaleX(20),x52URM.scaleX(20)]):
    style_prefix 'x52URM'

    use URM_tableRow():
        hbox xsize colWidth[0]:
            hbox:
                label '{urm_notl}Setting{/urm_notl}'
                textbutton '\uf1c0' yoffset -x52URM.scalePxInt(4) style_suffix 'icon_textbutton' action x52URM.Confirm("""There are 2 settings levels:\n{b}Local{/b}: The setting for the current game\n{b}Global{/b}: The setting for all games (that don't have a local setting)\n\nThe value under {b}Effective{/b} is the setting used in the current game""", title='Settings explanation')
        hbox xsize colWidth[1]:
            label '{urm_notl}Effective{/urm_notl}'
        hbox xsize colWidth[2]:
            label '{urm_notl}Local{/urm_notl}'
        hbox xsize colWidth[3]:
            hbox:
                label '{urm_notl}Global{/urm_notl}'
                if x52URM.Settings.globalAvailable == False:
                    textbutton '\uf1c0' yoffset -x52URM.scalePxInt(4) text_color x52URM.Theme.colors.errorText style_suffix 'icon_textbutton' action x52URM.Confirm('Global settings are unavailable in this game', title='{urm_notl}Global settings unavailable{/urm_notl}')

    use URM_table():
        for i,(settingName,setting) in enumerate(settings.items()):
            use URM_tableRow(i, True):
                hbox xsize colWidth[0] yalign .5:
                    hbox yalign .5 spacing 2:
                        text setting['title'] yalign .5
                        if 'description' in setting:
                            textbutton '{size=-8}\uf1c0{/size}' style_suffix 'icon_textbutton' action x52URM.Confirm(setting['description'], title=setting['title'])
                hbox xsize colWidth[1] yalign .5:
                    text setting['effective']
                hbox xsize colWidth[2]:
                    hbox spacing 2 box_wrap True:
                        for option in setting['options']:
                            use x52URM_radiobutton(x52URM.Settings.get(settingName, globalSetting=False)==setting['options'][option], option, x52URM.SetURMSetting(settingName, setting['options'][option]))
                        use x52URM_iconButton('\ue872', '{urm_notl}Clear{/urm_notl}', x52URM.SetURMSetting(settingName, None), sensitive=(x52URM.Settings.get(settingName, globalSetting=False)!=None))
                hbox xsize colWidth[3]:
                    hbox spacing 2 box_wrap True:
                        for option in setting['options']:
                            use x52URM_radiobutton(x52URM.Settings.get(settingName, globalSetting=True)==setting['options'][option], option, x52URM.SetURMSetting(settingName, setting['options'][option], globalSetting=True), sensitive=If(x52URM.Settings.globalAvailable, None, False))
                        use x52URM_iconButton('\ue872', '{urm_notl}Default{/urm_notl}', x52URM.SetURMSetting(settingName, None, globalSetting=True), sensitive=If(x52URM.Settings.globalAvailable, None, False))


# =====
# ABOUT
# =====
screen URM_options_about():
    style_prefix 'x52URM'

    hbox:
        add '0x52-URM/images/logoBig.x52' zoom x52URM.getScaleFactor()*0.2
        null width x52URM.scalePxInt(10)
        vbox:
            label "Universal Ren'Py Mod [x52URM.version] by 0x52"
            text "I hope you enjoy using Universal Ren'Py Mod.\nIf you want to support development, consider becoming my Patron or by donating.\nYou can find more on my website {a=https://0x52.dev}0x52.dev{/a}."

    null height x52URM.scalePxInt(15)

    label 'Changelog'
    frame style_suffix "seperator" ysize 2
    viewport:
        draggable True
        mousewheel True
        scrollbars "vertical"

        vbox:
            use URM_about_version('2.6.2', '2025-07-01', ['Fix: Prevent URM screens from stretching when a game has fixed scrollbar heights','Fix: Additional error handling for search'])
            use URM_about_version('2.6.1', '2025-04-07', ['Added option to show/hide unsupported variables from search results','Prevent static URM data from ending up in the game save for VN\'s using Ren\'Py < 7.6','Fix: Save "warning disabled" both local and global (because some environments don\'t support global settings)'])
            use URM_about_version('2.6', '2025-02-24', ['Added option to create variables (and change variable types)','Made searching internal variables optional','Disable risk warning for every game, instead of only the current','Fix: Crash when gamesave doesn\'t contain a screenshot'])
            use URM_about_version('2.5', '2024-12-11', ['Added option to ignore variables in path detection and/or codeview (available after remembering a variable)','Implemented custom tooltips system (prevents issues with games that use Ren\'Py\'s system in an unconventional way)','List all possible items when searching nothing (an empty string)','Fix: Progressbar total could be 1 off'])
            use URM_about_version('2.4.2', '2024-11-13', ['Added time-out option for notifications','Added option to dismiss all notifications at once','Fix: possible self-update issue on Linux'])
            use URM_about_version('2.4.1', '2024-10-13', ['Progressbar: performance improvements','Progressbar: auto sizing (content dependent width)','Progressbar: Add option to show amount of newly seen dialogue','Support replacing text/names with nothing (empty text)','Add URM version to traceback.txt in case of a game crash','Fix: Scale touchbutton based on game\'s resolution'])
            use URM_about_version('2.4', '2024-09-23', ['Added a progressbar that indicates how much of the content has been seen (all playthroughs combined)','Fix: Prevent crash when game devs broke Ren\'Py by assigning something to the variable "Character"'])
            use URM_about_version('2.3.1', '2024-07-14', ['Added option to remember and watch variables from the codeview','Close codeview when the parent dialog (paths/choices) is closed','Larger codeview text','Added option to open lists/dicts/objects from codeview','Show a comments in the code (instead of an empty line) where there\'s dialogue','Fix: Variable freezing/monitoring for some specific Ren\'Py versions'])
            use URM_about_version('2.3', '2024-07-06', ['Intelligent codeview (for paths and choices)','Fix: Correctly disable freeze/monitor buttons for unsupported variables','Fix: Variable freezing/monitoring for games using a Ren\'Py version after 8.2.0 and 7.7.0'])
            use URM_about_version('2.2.1', '2024-06-08', ['Quickmenu: Skip button now supports fast skipping to the next choice (right click / long press)','Quickmenu: Additional buttons: Load, Save, URM and Exit','Fix: Variables could appear multiple times in the search result','Fix: The option to disable searching persistent variables didn\'t work anymore','Fix: In some cases the same "variable changed" notification could popup multiple times'])
            use URM_about_version('2.2', '2024-06-01', ['Custom quickmenu option','Support browsing variables inside custom variable stores'])
            use URM_about_version('2.1.4', '2024-04-17', ['New/improved implementation for freezing/monitoring variables','Fix: Android: Save .urm files to saves dir when global settings are not supported'])
            use URM_about_version('2.1.3', '2024-04-07', ['Fix: Improved permissions validation for Android (global settings)','Fix: Implemented a workaround for some games that broke a Ren\'Py feature that URM needs'])
            use URM_about_version('2.1.2', '2024-03-30', ['Fix: Validate write access for global settings (prevents crash on some Android games)'])
            use URM_about_version('2.1.1', '2024-03-20', ['Added positioning options for custom textboxes/dialogue','Search results are now sortable (by name)','Fix: Prevent Ren\'Py translations from translating URM','Fix: Global settings on Android'])
            use URM_about_version('2.1', '2024-03-13', ['Configurable watchpanel contents + compact mode','New watchpanel option to view last executed filename:line','Configurable width for custom textboxes/dialogue','Choices dialog is now able to bypass fixed choices ("fixed rollback")','Added some low contrast themes','Fix: Character renaming didn\'t always work in dialogue','Fix: Unable to determine variable type in specific cases','Fix: Notification was hidden after loading a save at a choice/path','Fix: Accessibility features broke URM icons'])
            use URM_about_version('2.0.3', '2024-01-13', ['Fix: Possible crash while browsing object variables'])
            use URM_about_version('2.0.2', '2024-01-10', ['Fix: self-update didn\'t work properly','Fix: Loading old .urm files in newer Ren\'Py games','Fix: Allow self-voicing of custom textboxes'])
            use URM_about_version('2.0.1', '2024-01-03', ['Fix: Issue with Ren\'Py 7.5+ and 8.0+'])
            use URM_about_version('2.0', '2023-12-23', ['A lot has been optimized and improved. Some highlight below;','New design + theming engine (pick different themes)','Row highlighting, to easier distinguish between rows','More advanced browsing variables containing dicts, lists, classes, etc.','New mod framework (which will not conflict with my game specific mods)','New .urm fileformat (it\'s still able to read old .urm files)','Improved character search (for renaming and textbox customization)','Fix: Compatibility with Ren\'Py 8.1.3+','Fix: Some characters properties would be applied to the custom textbox, while they shouldn\'t'])
            use URM_about_version('1.15.2', '2023-07-23', ['Added option to cancel skipping on path detection','Fix: Prevent self-voicing of URM screens','Fix: Prevent original textbox/dialogue from briefly appearing in certain cases','Fix: URM scaling if game\'s resolution is set late','Fix: Don\'t show tooltips from outside of URM inside URM'])
            use URM_about_version('1.15.1', '2023-06-29', ['Some fixes related to the new textbox customization feature'])
            use URM_about_version('1.15', '2023-06-24', ['Added textbox customizing feature','Fix: Auto update issue on Ren\'Py 8+'])
            use URM_about_version('1.14.1', '2023-04-27', ['Fix: Detached URM from overlays (this makes sure URM is always available, even if overlays are hidden)','Fix: Prevent error when a game assigned something Ren\'Py\'s reserved variable "Action"'])
            use URM_about_version('1.14', '2023-03-18', ['Added snapshot feature (list/compare changed variables)','Fix: Object search wasn\'t working correctly in Ren\'Py 8.x games'])
            use URM_about_version('1.13.4', '2023-02-25', ['Fix: Compatibility with Ren\'Py 8.1'])
            use URM_about_version('1.13.3', '2023-01-31', ['Fix: The was an intermittent issue with variables not changing back during a rollback','Fix: Renaming characters with parentheses in the name now works'])
            use URM_about_version('1.13.2', '2022-12-18', ['Fix: In specific cases loading a save with a frozen variable could erase the variable'])
            use URM_about_version('1.13.1', '2022-12-14', ['Added gesture for opening URM on touch devices (draw an U / swipe down-right-up)','Fix: Prevent autofocusing search input on touch devices (because this opens the on-screen keyboard)'])
            use URM_about_version('1.13', '2022-12-11', ['New option to freeze variables','New option to monitor variables (receive a notification when it changes)','URM is now (officially) compatible with touchscreens','Fix: Searching variable names wasn\'t working for persistent variables'])
            use URM_about_version('1.12', '2022-10-30', ['Option to skip the splashscreen','Hugely improved path detection','Made sorting case insensitive','Added sorting option to "renaming" tab','Fix: Sorting is now working on Ren\'Py 8.x games'])
            use URM_about_version('1.11', '2022-09-21', ['Improved path detection (detect paths behind transitions)','Extended keyboard controls (control detected paths and choices using your keyboard)','Added option to open Ren\'Py console using Alt+O','Keep search input when changing search mode','Fix: Prevent crash when a game has assigned something to the "os" variable'])
            use URM_about_version('1.10.3', '2022-08-24', ['Fix: Creating .URM files in Ren\'Py 8.x','Fix: Labels tab crashed on Ren\'Py 7.5 and up'])
            use URM_about_version('1.10.2', '2022-08-24', ['Added paging to renaming tab (to improve performance)','Optimized text scaling on renaming tab','Prevent codeview from parsing variables and styling','Hide "ui." methods from codeview','Fix: Prevent error when showing save paths with special characters','Fix: Hover effect for settings'])
            use URM_about_version('1.10.1', '2022-08-19', ['Fix: Self-update was broken','Fix: Will now work on games that overwrite the built-in Button variable'])
            use URM_about_version('1.10', '2022-08-06', ['Implemented keyboard controls','Added persistent .URM files location','Improved .URM file load screen','Fix: Ren\'Py 7.5 compatibility'])
            use URM_about_version('1.9.4', '2022-07-19', ['URM is now compatible with Ren\'Py 8.0','Potential fix: Made some more changes to prevent rare crash when saving a game'])
            use URM_about_version('1.9.3', '2022-06-07', ['Fix: some rare issues with saving games when using Ren\'Py 7.4.11','Fix: issue where saves created when using older URM version wouldn\'t work correctly'])
            use URM_about_version('1.9.2', '2022-05-30', ['Fix: Very rare crash when saving a game'])
            use URM_about_version('1.9.1', '2022-05-29', ['Fix: Added watchpanel position setting to the new options screen'])
            use URM_about_version('1.9', '2022-05-27', ['Added global options (this enables you to use the same URM settings across multiple games)','Restyled tabs','Fix: Prevent crash when ssl module is not found','Fix: Prevent crash if text substitution fails for detected choices'])
            use URM_about_version('1.8', '2022-04-28', ['Added path (if-statement) detection','Added persistent "end replay" button','Fix: Prevent accessibility mode from changing URM icons','Fix: Rare crash when using JoiPlay','Fix: Rare crash when dict size changes while searching'])
            use URM_about_version('1.7', '2022-04-16', ['Add the option to show next label following a choice','Prevent clicking through dialogs','Fix: Auto-update issue in Ren\'Py 7.4','Fix: Dialogue related to choicemenu shown as choice','Decreased dialogs transparency'])
            use URM_about_version('1.6.1', '2022-03-29', ['Fix: Error in games listening for label calls','Fix: Possible crash on HTTP error (when manually checking for updates)','Improved error handling for automatic updates'])
            use URM_about_version('1.6', '2022-03-22', ['Added auto-update feature','Fix: Ren\'Py 7.0.0 compatibility'])
            use URM_about_version('1.5.3', '2022-02-20', ['Fix: URM prevented dialogue and choices from being displayed at the same time'])
            use URM_about_version('1.5.2', '2022-01-18', ['Fix: Added support for renaming dynamic characters','Fix: Search on actual character name instead of varname'])
            use URM_about_version('1.5.1', '2022-01-01', ['Fix: Issue where games would overwrite built-in Python methods'])
            use URM_about_version('1.5', '2021-12-21', ['Added extensive load/save options','Huge performance improvements with large seach results','Fix: Recursive search was broken','Fix: Scrollbar scaling (for higher/lower resolution games)'])
            use URM_about_version('1.4.1', '2021-09-29', ['A lot of styling improvements (to get it more consistent across different games)'])
            use URM_about_version('1.4', '2021-09-01', ['Added option to jump to labels instead of replaying them','Fix: URM now forces itself to be on top','Fix: Saving issue in the game ARTEMIS'])
            use URM_about_version('1.3.2', '2021-07-01', ['Fix: Sort variables and labels by custom name instead of by the original name'])
            use URM_about_version('1.3.1', '2021-06-30', ['Fix: Stop showing variable values defined in strings (between square brackets), because Ren\'Py 7.4.x crashes on non existing variables'])
            use URM_about_version('1.3', '2021-06-29', ['Added option to sort variables and labels','Added a scrollbar to the choices dialog','URM now forces itself to be on the foreground','Fix: Renaming characters with a variable as name was broken in 1.2','Fix: Crash with Ren\'Py 7.4.x games when a variablename is shortened','Fix: Rare crash when URM is trying to look for choices','Fix: Make sure URM is initialized correctly after loading a saved game (some game\'s code was breaking this)'])
            use URM_about_version('1.2', '2021-05-22', ['Added choices detection notification','Added watchpanel toggle hotkey','Text replacement now (by default) only replaces full words','Ignore {b}renpy.pause{/b} in choices code view','Fix: Rare URM loading issue (were files would load in an incorrect order)'])
            use URM_about_version('1.1.1', '2021-04-30', ['Fixed issue when games have reassigned Ren\'Py\'s global {b}im{/b} variable'])
            use URM_about_version('1.1', '2021-04-18', ['Added wildcard search','Added search options quick toggles','Improved UI scaling (for different resolution games)','Added explanation for all search options','Added options to rename remembered variables','Now remembering selected tab and searchtype after closing the game','Fixed: Crash when searching through numeric dict keys'])
            use URM_about_version('1.0', '2021-03-14', ['{b}URM 1 year anniversary!{/b}','Huge interface redesign','Movable/draggable dialogs','Added this changelog to URM','A lot of small "under the hood" changes'])
            use URM_about_version('0.8', '2021-03-07', ['Added option to see/modify choices','- You can also see hidden choices and select them','- Show the conditions on which a choice is visible','- See python code behind a choice','- Change the choice text'])
            use URM_about_version('0.7.4', '2021-02-17', ['Changed hotkey to Alt+M'])
            use URM_about_version('0.7.3', '2021-01-15', ['Fix: Crash on non string variablenames!?','Fix: Possible layout issue (frame padding)'])
            use URM_about_version('0.7.2', '2021-01-10', ["Don't require focusing input field when there's only a single inputfield"])
            use URM_about_version('0.7.1', '2021-01-01', ['Fix: Unable to change int/float values since 0.7'])
            use URM_about_version('0.7', '2020-12-30', ['Added support for lists, dicts and objects','Added option to delete variables (use with caution)','Moved search options to "search type" dialog','Small GUI improvements','Fix: Possible crash when text tags are used in a value','Fix: Scale last seen label in watchpanel','Fix: Ability to edit float variables'])
            use URM_about_version('0.6.2', '2020-12-09', ['Fix: possible issue with text replacement module'])
            use URM_about_version('0.6.1', '2020-12-07', ['Fix: On some games URM could cause an error when showing a dialogue'])
            use URM_about_version('0.6', '2020-09-25', ['Added character renaming and text replacement','Small GUI optimizations',"Fix: Support uncommon characters in game's path when saving/loading settings"])
            use URM_about_version('0.5.1', '2020-06-08', ['Improved UI scaling (to fit better on lower resolution games)'])
            use URM_about_version('0.5', '2020-06-07', ['Added watchpanel (keep track of variable and labels while playing the game)','Added options screen (right top) (moved search options to the new screen)','Different icons style','Fix: Support square brackets in game path'])
            use URM_about_version('0.4.1', '2020-06-06', ['Fix: Strip special character from filename','Fix: Corrected catching file load errors (if they happen for some reason)',"Fix: Override game's minimum button height for URM buttons"])
            use URM_about_version('0.4', '2020-04-20', ['Persistent variables are now supported','Huge performance improvement when using the labels tab with thumbnails','Added an option to disable recursive search',"Fix: labels view is now loading thumbnails on games using a Ren'Py version before 7.0.0.106",'Fix: Now clears already loaded labels and vars when loading a new file without labels of vars',"Fix: Unique case where Shift+M didn't work"])
            use URM_about_version('0.3', '2020-04-05', ['Added labels/scenes options (create you own replay/gallery mod!)','A couple of GUI changes'])
            use URM_about_version('0.2.4', '2020-03-28', ['Auto load URM file that was loaded while closing the game last time','Made search case-insensitive','Improved screen structure (to make the mod easier to maintain with a lot of features)','Improved URM settings structure'])
            use URM_about_version('0.2', '2020-03-21', ['Added save/load feature (this creates and loads .urm files from the "game" directory. You can share those files with others)'])
            use URM_about_version('0.1.1', '2020-03-17', ['Fixed issue where value changes before pressing "Change"-button'])
            use URM_about_version('0.1', '2020-03-15', ['Initial release'])

screen URM_about_version(version, date, features=[]):
    style_prefix 'x52URM'

    hbox:
        label version
        text ' [date]'
    for feature in features:
        hbox:
            text '- '
            text '[feature]'
    null height x52URM.scalePxInt(10)