
transform URM_choicesnotification_slide(width, position='l'):
    xoffset If(position == 'r', width, -width)
    alpha 0.0
    on show, appear:
        linear .2 xoffset 0 alpha 1.0
    on hide:
        linear .2 xoffset If(position == 'r', width, -width) alpha 0.0

transform URM_notification_slide(width, position='l'):
    xoffset If(position == 'r', width, -width)
    linear .2 xoffset 0
    on hide:
        linear .2 xoffset If(position == 'r', width, -width)

style x52URM_watchpanelItem is x52URM_frame:
    padding (6, 4)
    background None

style x52URM_watchpanelItemButton is x52URM_watchpanelItem:
    hover_background x52URM.Theme.colors.buttonBgHover
    selected_idle_background x52URM.Theme.colors.buttonBgHover
    insensitive_background None

# ===========
# MAIN SCREEN
# ===========
screen URM_watchpanel():
    layer 'x52Overlay'
    style_prefix "x52URM"
    modal True
    default movingVarName = None
    default panelWidth = x52URM.scaleX(15)

    frame:
        xalign If(x52URM.Settings.watchPanelPos == 'r', 1.0, 0.0)
        style_suffix 'dialog'
        at x52URM_fadeinout
        xmargin -3 ymargin -3
        xsize panelWidth
        yfill True
        has vbox
        xfill True

        hbox:
            xfill True ysize x52URM.scalePx(46)
            text "{urm_notl}URM{/urm_notl}" style_suffix "header_text" yalign .5 xoffset x52URM.scalePx(3)
            hbox spacing 2:
                xalign 1.0
                button:
                    style_suffix 'titleBarButton'
                    text "\ue895" style_suffix 'icon_button_text' yalign .5
                    hovered x52URM.Tooltip('{urm_notl}Open URM{/urm_notl}') unhovered x52URM.Tooltip()
                    action x52URM.Open()
                button:
                    style_suffix 'titleBarButton'
                    text If(x52URM.Settings.watchPanelPos == 'r', "\ue5cc","\ue5cb") style_suffix 'icon_button_text' yalign .5
                    hovered x52URM.Tooltip('{urm_notl}Hide panel{/urm_notl}') unhovered x52URM.Tooltip()
                    action SetField(x52URM.Settings, 'collapsedWatchPanel', True)
        if x52URM.Tooltip.get('URM_overlay'):
            text x52URM.Tooltip.get('URM_overlay') xalign .5
        else:
            label '{urm_notl}Watchpanel{/urm_notl}' xalign .5

        frame style_suffix "seperator" background x52URM.Theme.secondary

        use URM_watchPanelFileLine(panelWidth)
        use URM_watchPanelLabel(panelWidth)
        use URM_watchPanelChoiceDetection(panelWidth)
        use URM_watchPanelPathDetection(panelWidth)
        use URM_watchPanelProgress(panelWidth)

        #
        # Watching
        #
        if x52URM.Settings.watchPanelVars > 0:
            if len(x52URM.VarsStore.watchedStore) == 0:
                null height 2
                text "{urm_notl}There are no watched variables{/urm_notl}" text_align .5 xalign .5
            else:
                vpgrid:
                    yfill True
                    xfill True
                    mousewheel True
                    draggable True
                    scrollbars "vertical"
                    cols 1

                    for varName,varProps in list(x52URM.VarsStore.watchedStore.items()):
                        vbox:
                            frame:
                                style_suffix 'watchpanelItem'
                                has vbox
                                spacing 5
                                if 'name' in varProps:
                                    text x52URM.scaleText(varProps['name'], 12) bold True substitute False
                                else:
                                    text x52URM.scaleText(varName, 12) bold True substitute False
                                textbutton x52URM.Var(varName).getButtonValue(12) hovered x52URM.Tooltip('{urm_notl}Modify value{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_modify_value', var=x52URM.Var(varName)) substitute False
                                if x52URM.Settings.watchPanelVars < 2: # NOT compact
                                    hbox spacing 2:
                                        textbutton "\ue8f4" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Change variable{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_remember_var', varName=varName, rememberType='watchVar', defaultName=If('name' in varProps, varProps['name'], varName))
                                        textbutton "\ue872" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Remove from list{/urm_notl}') unhovered x52URM.Tooltip() action x52URM.Confirm('Are you sure you want to remove this variable?', Function(x52URM.VarsStore.unwatch, varName), title='{urm_notl}Remove variable{/urm_notl}')
                                        if movingVarName:
                                            if movingVarName == varName:
                                                textbutton '\uf230' style_suffix 'icon_button' hovered x52URM.Tooltip('{urm_notl}Cancel{/urm_notl}') unhovered x52URM.Tooltip() action SetLocalVariable('movingVarName', None)
                                            else:
                                                textbutton '\ue55c' style_suffix 'icon_button' hovered x52URM.Tooltip('{urm_notl}Before this{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.VarsStore.changePosWatched, movingVarName, varName),SetLocalVariable('movingVarName', None)]
                                        else:
                                            textbutton '\ue89f' style_suffix 'icon_button' hovered x52URM.Tooltip('{urm_notl}Move{/urm_notl}') unhovered x52URM.Tooltip() action SetLocalVariable('movingVarName', varName)
                            
                            frame style_suffix "seperator" background x52URM.Theme.secondary

screen URM_watchPanelFileLine(panelWidth):
    style_prefix "x52URM"

    if x52URM.Settings.watchPanelFileLine > 0:
        button xsize panelWidth:
            style_suffix 'watchpanelItemButton'
            if x52URM.Settings.watchPanelFileLine == 2: # Compact
                hbox:
                    text '\ue86f' style_suffix 'icon_button_text'
                    null width 2
                    text x52URM.scaleText(x52URM.currentFileNameLine(), 13, reverse=True) style_suffix 'button_text' substitute False
            else:
                vbox:
                    label '{urm_notl}Current file:line{/urm_notl}'
                    text x52URM.scaleText(x52URM.currentFileNameLine(), 14, reverse=True) style_suffix 'button_text' substitute False
            hovered x52URM.Tooltip('{urm_notl}Show full name:line{/urm_notl}') unhovered x52URM.Tooltip()
            action x52URM.Confirm('Last executed line:\n{}'.format(x52URM.currentFilePathLine()), title='{urm_notl}Current file:line{/urm_notl}')

        frame style_suffix "seperator" background x52URM.Theme.secondary

screen URM_watchPanelLabel(panelWidth):
    style_prefix "x52URM"

    if x52URM.Settings.watchPanelCurrentLabel > 0:
        if x52URM.Settings.watchPanelCurrentLabel == 2: # Compact
            button xsize panelWidth:
                style_suffix 'watchpanelItemButton'
                hbox:
                    text '\ue54e' style_suffix 'icon_button_text'
                    null width 2
                    text x52URM.scaleText(x52URM.Search.lastLabel, 13) style_suffix 'button_text' substitute False
                hovered x52URM.Tooltip('{urm_notl}Show label info{/urm_notl}') unhovered x52URM.Tooltip()
                action Show('URM_replay_jump', jumpTo=x52URM.Search.lastLabel, dialogTitle='{urm_notl}Last seen label{/urm_notl}')

        else:
            frame:
                style_suffix 'watchpanelItem'
                has vbox

                label '{urm_notl}Last seen label{/urm_notl}'
                text x52URM.scaleText(x52URM.Search.lastLabel, 14) yalign 0.5 substitute False
                if renpy.has_label(x52URM.Search.lastLabel):
                    hbox spacing 2:
                        if not x52URM.LabelsStore.has(x52URM.Search.lastLabel):
                            textbutton "\ue609" style_suffix "icon_button" yalign 0.5 hovered x52URM.Tooltip('{urm_notl}Remember label{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_remember_var', varName=x52URM.Search.lastLabel, rememberType='label')
                        textbutton "\ue1c4" style_suffix "icon_button" yalign 0.5 hovered x52URM.Tooltip('{urm_notl}Replay label{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_replay', labelName=x52URM.Search.lastLabel)

        frame style_suffix "seperator" background x52URM.Theme.secondary

screen URM_watchPanelChoiceDetection(panelWidth):
    style_prefix "x52URM"

    if x52URM.Settings.watchPanelChoiceDetection > 0:
        if x52URM.Settings.watchPanelChoiceDetection == 2: # Compact
            button xsize panelWidth:
                style_suffix 'watchpanelItemButton'
                hbox:
                    text '\ue896' style_suffix 'icon_button_text'
                    null width 2
                    if x52URM.Choices.isDisplayingChoice:
                        text '[x52URM.Choices.hiddenCount] hidden choices' style_suffix 'button_text'
                    else:
                        text '{urm_notl}No choices detected{/urm_notl}' style_suffix 'button_text'
                if x52URM.Choices.isDisplayingChoice:
                    hovered x52URM.Tooltip('{urm_notl}Show choices{/urm_notl}') unhovered x52URM.Tooltip()
                    action Show('URM_choices')

        else:
            frame:
                style_suffix 'watchpanelItem'
                has vbox

                label '{urm_notl}Displaying choice?{/urm_notl}'
                if x52URM.Choices.isDisplayingChoice:
                    hbox:
                        xfill True
                        text 'Yes ([x52URM.Choices.hiddenCount] hidden)' yalign .5
                        textbutton '\ue896' style_suffix 'icon_button' xalign 1.0 hovered x52URM.Tooltip('Show choices') unhovered x52URM.Tooltip() action Show('URM_choices')
                else:
                    text '{urm_notl}No{/urm_notl}'

        frame style_suffix "seperator" background x52URM.Theme.secondary

screen URM_watchPanelPathDetection(panelWidth):
    style_prefix "x52URM"

    if x52URM.Settings.watchPanelPathDetection > 0:
        if x52URM.Settings.watchPanelPathDetection == 2: # Compact
            button xsize panelWidth:
                style_suffix 'watchpanelItemButton'
                hbox:
                    text '\uf184' style_suffix 'icon_button_text'
                    null width 2
                    if x52URM.PathDetection.pathIsNext:
                        text '[x52URM.PathDetection.statementsCount] paths detected' style_suffix 'button_text'
                    else:
                        text '{urm_notl}No path detected{/urm_notl}' style_suffix 'button_text'
                if x52URM.PathDetection.pathIsNext:
                    hovered x52URM.Tooltip('{urm_notl}Show paths{/urm_notl}') unhovered x52URM.Tooltip()
                    action Show('URM_paths')

        else:
            frame:
                style_suffix 'watchpanelItem'
                has vbox

                label 'Detected path?'
                if x52URM.PathDetection.pathIsNext:
                    hbox:
                        xfill True
                        text '[x52URM.PathDetection.statementsCount] paths' yalign .5
                        textbutton '\uf184' style_suffix 'icon_button' xalign 1.0 hovered x52URM.Tooltip('Show options') unhovered x52URM.Tooltip() action Show('URM_paths')
                else:
                    text '{urm_notl}No{/urm_notl}'

        frame style_suffix "seperator" background x52URM.Theme.secondary

screen URM_watchPanelProgress(panelWidth):
    style_prefix "x52URM"

    if x52URM.Settings.watchPanelProgress > 0:
        button xsize panelWidth:
            style_suffix 'watchpanelItemButton'
            if x52URM.Settings.watchPanelProgress == 2: # Compact
                hbox:
                    text '\uf1c5' style_suffix 'icon_button_text'
                    null width 2
                    text "[x52URM.ProgressBar.percentage]% {size=-8}([x52URM.ProgressBar.seen]/[x52URM.ProgressBar.total]){/size}" style_suffix 'button_text'
            else:
                vbox:
                    label 'Progress'
                    text '[x52URM.ProgressBar.percentage]% {size=-8}([x52URM.ProgressBar.seen]/[x52URM.ProgressBar.total]){/size}' style_suffix 'button_text'
            action ToggleField(x52URM.Settings, 'progressShown', True, False)

        frame style_suffix "seperator" background x52URM.Theme.secondary

style x52URM_notification is x52URM_default:
    background AlphaMask(Solid(x52URM.Theme.colors.buttonBg), Frame('0x52-URM/images/notificationMask.x52', 236, 0, 0, 0))
    hover_background AlphaMask(Solid(x52URM.Theme.colors.buttonBgHover), Frame('0x52-URM/images/notificationMask.x52', 236, 0, 0, 0))
    selected_idle_background AlphaMask(Solid(x52URM.Theme.colors.buttonBgHover), Frame('0x52-URM/images/notificationMask.x52', 236, 0, 0, 0))
    insensitive_background AlphaMask(Solid(x52URM.Theme.colors.buttonBgDisabled), Frame('0x52-URM/images/notificationMask.x52', 236, 0, 0, 0))
    padding (_x52ModName_.scalePxInt(8), _x52ModName_.scalePxInt(8))

style x52URM_notification_text is x52URM_button_text:
    outlines [(absolute(1), x52URM.Theme.colors.buttonBg, 0, 0)]

screen URM_notifications():
    layer 'x52Overlay'
    style_prefix "x52URM"
    default width = x52URM.scalePxInt(270)

    vbox:
        yoffset If(x52URM.Settings.showWatchPanel and x52URM.Settings.collapsedWatchPanel, x52URM.scalePxInt(45), 5) # We need some yoffset if the watchpanel togglebutton is there
        xalign If(x52URM.Settings.watchPanelPos == 'r', 1.0, 0.0)
        xoffset (If(x52URM.Settings.showWatchPanel and not x52URM.Settings.collapsedWatchPanel, x52URM.scaleX(15), 0) * If(x52URM.Settings.watchPanelPos == 'r', -1, 1)) # Offset notification when the panel is open, multiply by 1 or -1 for left or right panel
        spacing 2

        # ==========
        # END REPLAY
        # ==========
        showif x52URM.Settings.showReplayNotification and _in_replay and (not x52URM.Settings.showWatchPanel or x52URM.Settings.collapsedWatchPanel):
            key 'alt_K_e' action EndReplay(False)
            button:
                style_suffix 'notification'
                xminimum width
                action x52URM.Confirm("Do you want to end the current replay?", renpy.end_replay, title='End replay')
                
                vbox:
                    hbox:
                        text '\uef71' style_suffix 'icon_button_text'
                        null width x52URM.scalePxInt(4)
                        text '{u}E{/u}nd replay' style_suffix 'notification_text' bold True

        # ====================
        # Choices notification
        # ====================
        showif x52URM.Settings.showChoicesNotification and x52URM.Choices.isDisplayingChoice and (not x52URM.Settings.showWatchPanel or x52URM.Settings.collapsedWatchPanel):
            key 'alt_K_c' action Show('URM_choices')
            button:
                at URM_choicesnotification_slide(width, x52URM.Settings.watchPanelPos)
                style_suffix 'notification'
                xminimum width
                action Show('URM_choices')

                vbox:
                    hbox:
                        text '\ue896' style_suffix 'icon_button_text'
                        null width x52URM.scalePxInt(4)
                        text '{u}C{/u}hoices detected' style_suffix 'notification_text' bold True
                    if x52URM.Choices.hiddenCount > 0:
                        text '[x52URM.Choices.hiddenCount] hidden' style_suffix 'notification_text'

        # ==================
        # Paths notification
        # ==================
        showif x52URM.Settings.showPathsNotification and x52URM.PathDetection.pathIsNext and (not x52URM.Settings.showWatchPanel or x52URM.Settings.collapsedWatchPanel):
            if x52URM.Settings.stopSkippingOnPathDetection:
                on 'show' action x52URM.CancelSkipping()

            key 'alt_K_a' action Show('URM_paths')
            button:
                at URM_choicesnotification_slide(width, x52URM.Settings.watchPanelPos)
                style_suffix 'notification'
                xminimum width
                action Show('URM_paths')

                vbox:
                    hbox:
                        text '\uf184' style_suffix 'icon_button_text'
                        null width x52URM.scalePxInt(4)
                        text 'P{u}a{/u}th detected' style_suffix 'notification_text' bold True
                    text '[x52URM.PathDetection.statementsCount] options' style_suffix 'notification_text'

        # ==================
        # TEMP NOTIFICATIONS
        # ==================
        for notif in x52URM.Notifications.notifications:
            button:
                at URM_notification_slide(width, x52URM.Settings.watchPanelPos)
                style_suffix 'notification'
                xminimum width
                action notif

                vbox:
                    text x52URM.scaleText(notif.label, 260, style='URM_label_text', pixelTarget=True) style_suffix 'notification_text' bold True
                    if notif.text:
                        text x52URM.scaleText(notif.text, 260, pixelTarget=True) style_suffix 'notification_text'

        if len(x52URM.Notifications.notifications):
            button:
                at URM_notification_slide(width, x52URM.Settings.watchPanelPos)
                style_suffix 'notification'
                xminimum width
                action Function(x52URM.Notifications.clear)

                hbox:
                    text '\ue92b' style_suffix 'icon_button_text' yalign .5
                    text '{urm_notl}Dismiss all{/urm_notl}' style_suffix 'notification_text'
