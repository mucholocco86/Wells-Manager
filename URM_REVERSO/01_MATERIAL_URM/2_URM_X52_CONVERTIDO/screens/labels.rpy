
# =============
# LABELS SCREEN
# =============
screen URM_labels():
    style_prefix "x52URM"
    default thumbnailScale = 22.8
    default movingLabelName = None
    default colWidth = [x52URM.scaleX(20), x52URM.scaleX(20)]
    default labelListPages = x52URM.Pages(len(x52URM.LabelsStore.store), itemsPerPage=20)
    default labelThumbPages = x52URM.Pages(len(x52URM.LabelsStore.store), itemsPerPage=12)
    default nameSorted = None
    
    hbox:
        xfill True
        hbox:
            spacing x52URM.scalePxInt(5)
            if x52URM.URMFiles.file.filename or len(x52URM.LabelsStore.store) > 0:
                text "Remembered labels: "+str(len(x52URM.LabelsStore.store)) yalign 0.5
                textbutton "\ue16c" style_suffix "icon_button" action If(x52URM.LabelsStore.store.unsaved, x52URM.Confirm('This will clear the list below, are you sure?', Function(x52URM.LabelsStore.clear)), Function(x52URM.LabelsStore.clear))
            else:
                text "Load a file or add labels using the search option"

        hbox:
            xalign 1.0
            if x52URM.Settings.labelsView == 'list':
                textbutton "\ue3b6" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Show thumbnails{/urm_notl}') unhovered x52URM.Tooltip() action SetField(x52URM.Settings, 'labelsView', 'thumbnails')
            else:
                textbutton "\ue8ef" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Show list{/urm_notl}') unhovered x52URM.Tooltip() action SetField(x52URM.Settings, 'labelsView', 'list')
    null height x52URM.scalePxInt(5)
    frame style_suffix "seperator" ysize x52URM.scalePxInt(2)
    
    if len(x52URM.LabelsStore.store) > 0:
        # =========
        # LIST VIEW
        # =========
        if x52URM.Settings.labelsView == 'list':
            python:
                if len(x52URM.LabelsStore.store) != labelListPages.itemCount:
                    SetField(labelListPages, 'itemCount', len(x52URM.LabelsStore.store))()

            # PAGES
            fixed ysize x52URM.scalePxInt(50):
                hbox xalign .5 yoffset 4 spacing 2:
                    use URM_pages(labelListPages)

            use URM_tableRow(): # Headers
                hbox xsize colWidth[0]:
                    hbox:
                        label "{urm_notl}Name{/urm_notl}"
                        if nameSorted == 'asc':
                            textbutton '{size=-6}\ue316{/size}' yoffset x52URM.scalePxInt(-4) style_suffix 'icon_textbutton' hovered x52URM.Tooltip('{urm_notl}Sort descending{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.LabelsStore.sort, reverse=True),SetLocalVariable('nameSorted', 'desc')]
                        else:
                            textbutton If(nameSorted,'{size=-6}\ue313{/size}','{size=-6}\ue5d7{/size}') yoffset x52URM.scalePxInt(-4) style_suffix 'icon_textbutton' hovered x52URM.Tooltip('{urm_notl}Sort ascending{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.LabelsStore.sort),SetLocalVariable('nameSorted', 'asc')]
                label "{urm_notl}Replay{/urm_notl}" xsize colWidth[1]

            viewport:
                xfill True
                yfill True
                mousewheel True
                draggable True
                scrollbars "vertical"

                # Results
                use URM_table():
                    for i,(labelName,props) in enumerate(list(x52URM.LabelsStore.store.items())[labelListPages.pageStartIndex:labelListPages.pageEndIndex]):
                        use URM_tableRow(i, True):
                            hbox xsize colWidth[0] yalign .5:
                                if 'name' in props:
                                    text x52URM.scaleText(props['name'], 20) substitute False
                                else:
                                    text x52URM.scaleText(labelName, 20) substitute False
                            hbox xsize colWidth[1]:
                                hbox spacing 2:
                                    use x52URM_iconButton('\ue1c4', '{urm_notl}Play{/urm_notl}', action=Show('URM_replay', labelName=labelName))
                                    use x52URM_iconButton('\ue163', '{urm_notl}Jump{/urm_notl}', action=Show('URM_jump', labelName=labelName))
                            hbox spacing 2:
                                use x52URM_iconButton('\ue3c9', '{urm_notl}Edit{/urm_notl}', action=Show('URM_remember_var', varName=labelName, rememberType='label', defaultName=If('name' in props, props['name'], labelName)))
                                use x52URM_iconButton('\ue872', '{urm_notl}Remove{/urm_notl}', action=x52URM.Confirm('Are you sure you want to remove this label?', Function(x52URM.LabelsStore.forget, labelName), title='Remove label'))
                                if movingLabelName:
                                    if movingLabelName == labelName:
                                        use x52URM_iconButton('\uf230', '{urm_notl}Cancel{/urm_notl}', action=SetLocalVariable('movingLabelName', None))
                                    else:
                                        use x52URM_iconButton('\ue55c', '{urm_notl}Before this{/urm_notl}', action=[Function(x52URM.LabelsStore.changePos, movingLabelName, labelName),SetLocalVariable('movingLabelName', None)])
                                else:
                                    use x52URM_iconButton('\ue89f', '{urm_notl}Move{/urm_notl}', action=SetLocalVariable('movingLabelName', labelName))

        # ===============
        # THUMBNAILS VIEW
        # ===============
        else:
            python:
                if len(x52URM.LabelsStore.store) != labelThumbPages.itemCount:
                    SetField(labelThumbPages, 'itemCount', len(x52URM.LabelsStore.store))()

            # PAGES
            fixed ysize x52URM.scalePxInt(50):
                hbox xalign .5 yoffset 4 spacing 2:
                    use URM_pages(labelThumbPages)

            vpgrid:
                xfill True
                yfill True
                mousewheel True
                draggable True
                scrollbars "vertical"
                cols 4
                spacing x52URM.scalePxInt(10)

                for i,(labelName,props) in enumerate(list(x52URM.LabelsStore.store.items())[labelThumbPages.pageStartIndex:labelThumbPages.pageEndIndex]):
                    vbox:
                        button:
                            style_suffix 'thumbnailButton'
                            xsize x52URM.scaleX(thumbnailScale) ysize x52URM.scaleY(thumbnailScale)
                            action Show('URM_replay', labelName=labelName)
                            add Transform(x52URM.LabelImage(x52URM.Label(labelName)), alpha=.7)
                            if 'name' in props:
                                text x52URM.scaleText(props['name'], thumbnailScale-2) color If(renpy.has_label(labelName), '#fff', '#d00') xalign .5 yalign 1.0 substitute False
                            else:
                                text x52URM.scaleText(labelName, thumbnailScale-2) color If(renpy.has_label(labelName), '#fff', '#d00') xalign .5 yalign 1.0 substitute False

                        null height 2
                        hbox:
                            xsize x52URM.scaleX(thumbnailScale)
                            hbox spacing 2:
                                textbutton "\ue1c4" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Replay{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_replay', labelName=labelName)
                                textbutton "\ue163" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Jump{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_jump', labelName=labelName)
                            hbox spacing 2:
                                xalign 1.0
                                textbutton "\ue3c9" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Edit{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_remember_var', varName=labelName, rememberType='label', defaultName=If('name' in props, props['name'], labelName))
                                textbutton "\ue872" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Remove{/urm_notl}') unhovered x52URM.Tooltip() action x52URM.Confirm('Are you sure you want to remove this label?', Function(x52URM.LabelsStore.forget, labelName), title='{urm_notl}Remove label{/urm_notl}')
                                if movingLabelName:
                                    if movingLabelName == labelName:
                                        textbutton '\uf230' style_suffix 'icon_button' hovered x52URM.Tooltip('{urm_notl}Cancel{/urm_notl}') unhovered x52URM.Tooltip() action SetLocalVariable('movingLabelName', None)
                                    else:
                                        textbutton '\ue55c' style_suffix 'icon_button' hovered x52URM.Tooltip('{urm_notl}Before this{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.LabelsStore.changePos, movingLabelName, labelName),SetLocalVariable('movingLabelName', None)]
                                else:
                                    textbutton '\ue89f' style_suffix 'icon_button' hovered x52URM.Tooltip('{urm_notl}Move{/urm_notl}') unhovered x52URM.Tooltip()  action SetLocalVariable('movingLabelName', labelName)

                # Fill up till we have 4 columns (this is needed since Ren'Py 7.5)
                for i in range(len(list(x52URM.LabelsStore.store.items())[labelThumbPages.pageStartIndex:labelThumbPages.pageEndIndex]) % 4):
                    null
            

    else:
        vbox:
            yoffset x52URM.scaleY(1.5)
            xalign 0.5
            label "{urm_notl}There are no remembered labels{/urm_notl}" xalign 0.5

# =============
# REPLAY SCREEN
# =============
screen URM_replay(labelName):
    layer 'x52Overlay'
    style_prefix "x52URM"
    default errorMessage = None

    use x52URM_Dialog('Start a replay', closeAction=Hide('URM_replay'), modal=True, icon='\ue1c4'):
        if renpy.has_label(labelName):
            text 'You can end the replay by pressing Alt+M or by choosing "End Replay" in the game menu'
        else:
            text '{urm_notl}The selected label does not exist{/urm_notl}'

        if errorMessage != None:
            null height x52URM.scalePxInt(10)
            hbox xalign .5:
                use x52URM_messagebar('error', errorMessage)

        hbox:
            yoffset x52URM.scalePxInt(15) xalign .5
            if renpy.has_label(labelName):
                key 'K_KP_ENTER' action x52URM.URMReplay(labelName, Hide('URM_replay'), 'errorMessage')
                key 'K_RETURN' action x52URM.URMReplay(labelName, Hide('URM_replay'), 'errorMessage')
                textbutton "{urm_notl}Start{/urm_notl}" style_suffix "buttonPrimary" action x52URM.URMReplay(labelName, Hide('URM_replay'), 'errorMessage')
                null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_replay')

# ===========
# JUMP SCREEN
# ===========
screen URM_jump(labelName):
    layer 'x52Overlay'
    style_prefix "x52URM"

    use x52URM_Dialog('{urm_notl}Jump to label{/urm_notl}', closeAction=Hide('URM_jump'), modal=True, icon='\ue163'):
        if renpy.has_label(labelName):
            text 'You are about to jump to a label, this will affect your game' color '#990000' bold True xalign .5
            text 'If you want to play the label without it affecting your game, go back and choose the replay option' xalign .5
            null height 10
            text '(Only use this option if you know what you\'re doing. Your game will continue from the label you\'re jumping to)' color '#AAA' style_suffix 'text_small' xalign .5
        else:
            text '{urm_notl}The selected label does not exist{/urm_notl}'

        hbox:
            yoffset x52URM.scalePxInt(15) xalign .5
            if renpy.has_label(labelName):
                key 'K_KP_ENTER' action [Hide('URM_jump'),Hide('URM_main'),Jump(labelName)]
                key 'K_RETURN' action [Hide('URM_jump'),Hide('URM_main'),Jump(labelName)]
                textbutton "{urm_notl}Jump{/urm_notl}" style_suffix "buttonPrimary" action [Hide('URM_jump'),Hide('URM_main'),Jump(labelName)]
                null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_jump')

# ==================
# REPLAY JUMP SCREEN
# ==================
screen URM_replay_jump(jumpTo, choiceName=None, dialogTitle='{urm_notl}Next label{/urm_notl}'):
    layer 'x52Overlay'
    style_prefix 'x52URM'
    default errorMessage = None

    use x52URM_Dialog(dialogTitle, Hide('URM_replay_jump'), modal=True, icon='\ue1c4'):
        if choiceName:
            hbox:
                label '{urm_notl}Choice {/urm_notl}'
                text choiceName
        hbox:
            label '[dialogTitle] '
            text jumpTo

        vbox:
            yoffset x52URM.scalePxInt(15)
            spacing x52URM.scalePxInt(15)

            if errorMessage != None:
                use x52URM_messagebar('error', errorMessage)

            vbox:
                text 'Playing the label will {b}not{/b} affect your current gameplay (it starts in replay mode)\nand you will return here after ending the replay (press Alt+M)' text_align .5

            hbox: # Buttons
                xalign 0.5
                spacing x52URM.scalePxInt(20)

                use x52URM_iconButton('\ue1c4', '{u}P{/u}lay', x52URM.URMReplay(jumpTo, Hide('URM_replay_jump'), 'errorMessage'))
                key 'alt_K_p' action x52URM.URMReplay(jumpTo, Hide('URM_replay_jump'), 'errorMessage')
                use x52URM_iconButton('\ue4f8', '{u}R{/u}emember', [Hide('URM_replay_jump'),Show('URM_remember_var', varName=jumpTo, rememberType='label')])
                key 'alt_K_r' action [Hide('URM_replay_jump'),Show('URM_remember_var', varName=jumpTo, rememberType='label')]
                textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_replay_jump')
