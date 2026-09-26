
screen URM_snapshots():
    style_prefix "x52URM"
    default comparingSnapshotName = None
    default colWidth = [x52URM.scaleX(20), x52URM.scaleX(12), x52URM.scaleX(60)]
    default comparing = None
    default snapshotsPages = x52URM.Pages(len(x52URM.Snapshots.snapshotNames), itemsPerPage=20)

    python:
        if len(x52URM.Snapshots.snapshotNames) != snapshotsPages.itemCount:
            SetField(snapshotsPages, 'itemCount', len(x52URM.Snapshots.snapshotNames))()

    hbox:
        spacing x52URM.scalePxInt(5)
        if comparing:
            use x52URM_iconButton('\ue5c4', '{urm_notl}Back{/urm_notl}', action=SetLocalVariable('comparing', None))
            if len(comparing) > 1:
                text 'Comparing "{}" with "{}"'.format(comparing[0], comparing[1]) yalign .5
            else:
                text 'Comparing "{}" with "{}"'.format(comparing[0], 'Current variables') yalign .5
        else:
            use x52URM_iconButton('\ue439', '{urm_notl}Create{/urm_notl}', action=Show('URM_snapshot_create'))
    frame style_suffix "seperator" ysize x52URM.scalePxInt(2) yoffset x52URM.scalePxInt(5)

    if comparing:
        if len(comparing) > 1:
            use URM_snapshots_comparison(comparing[0], comparing[1])
        else:
            use URM_snapshots_comparison(comparing[0])
    
    elif len(x52URM.Snapshots.snapshotNames) > 0:
        null height x52URM.scalePxInt(10)

        # PAGES
        fixed ysize x52URM.scalePxInt(50):
            hbox xalign .5 yoffset 4 spacing 2:
                use URM_pages(snapshotsPages)
            hbox xalign 1.0 yalign .5:
                text 'Snapshots: {}'.format(len(x52URM.Snapshots.snapshotNames))
                null width x52URM.scalePxInt(10)

        use URM_tableRow(): # Headers
            label "{urm_notl}Name{/urm_notl}" xsize colWidth[0]
            label "{urm_notl}Creation time{/urm_notl}" xsize colWidth[1]

        viewport:
            xfill True
            yfill True
            mousewheel True
            draggable True
            scrollbars "vertical"

            # Results
            use URM_table():
                for i,name in enumerate(x52URM.Snapshots.snapshotNames[snapshotsPages.pageStartIndex:snapshotsPages.pageEndIndex]):
                    use URM_tableRow(i, True):
                        hbox xsize colWidth[0] yalign .5:
                            text x52URM.scaleText(name, 18) substitute False

                        hbox xsize colWidth[1] yalign .5:
                            text x52URM.Snapshots.getSnapshotTime(name)

                        hbox xsize colWidth[2]:
                            hbox spacing 2:
                                if comparingSnapshotName: # Trying to compare?
                                    if comparingSnapshotName == name:
                                        use x52URM_iconButton('\uf230', '{urm_notl}Cancel{/urm_notl}', action=SetLocalVariable('comparingSnapshotName', None))
                                    else:
                                        use x52URM_iconButton('\ueb7d', '{urm_notl}Compare{/urm_notl}', action=[SetLocalVariable('comparing', [comparingSnapshotName,name]),SetLocalVariable('comparingSnapshotName', None)])
                                else:
                                    use x52URM_iconButton('\ue8f2', '{urm_notl}Show changes{/urm_notl}', SetLocalVariable('comparing', [name]))
                                    use x52URM_iconButton('\ueb7d', '{urm_notl}Compare with...{/urm_notl}', sensitive=(len(x52URM.Snapshots.snapshotNames) > 1), action=SetLocalVariable('comparingSnapshotName', name))
                                    use x52URM_iconButton('\ue872', '{urm_notl}Remove{/urm_notl}', x52URM.Confirm('Are you sure you want to remove this snapshot?', Function(x52URM.Snapshots.delete, name), title='{urm_notl}Remove snapshot{/urm_notl}'))

    else:
        vbox:
            yoffset x52URM.scaleY(1.5)
            xalign 0.5
            label "{urm_notl}There are no snapshots yet{/urm_notl}" xalign 0.5
            null height x52URM.scalePxInt(15)
            text "Here you can create snapshots of all current variables and later use them to list all changed variables" xalign .5
            text "(snapshots can be compared to current variables or other snapshots)" xalign .5
            text "Note: Snapshots will be lost when closing the game" style_suffix 'text_small' xalign .5 yoffset x52URM.scalePxInt(10)


screen URM_snapshots_comparison(old, new=None):
    style_prefix "x52URM"

    default changes = x52URM.Snapshots.findChanges(old, new)
    default comparisonColWidth = [x52URM.scaleX(20), x52URM.scaleX(20), x52URM.scaleX(20)]
    default comparisonPages = x52URM.Pages(len(changes), itemsPerPage=21)
    default compareDict = None
    default compareList = None

    if compareDict:
        hbox yoffset x52URM.scalePxInt(6):
            spacing x52URM.scalePxInt(5)
            use x52URM_iconButton('\ue5c4', '{urm_notl}Back{/urm_notl}', action=SetLocalVariable('compareDict', None))
            text 'Comparing variable "{}"'.format(compareDict['old'].name) yalign .5
        frame style_suffix "seperator" ysize x52URM.scalePxInt(2) yoffset x52URM.scalePxInt(6)
        use URM_snapshots_dictCompare(compareDict)

    elif compareList:
        hbox yoffset x52URM.scalePxInt(6):
            spacing x52URM.scalePxInt(5)
            use x52URM_iconButton('\ue5c4', '{urm_notl}Back{/urm_notl}', action=SetLocalVariable('compareList', None))
            text 'Comparing variable "{}"'.format(compareList['old'].name) yalign .5
        frame style_suffix "seperator" ysize x52URM.scalePxInt(2) yoffset x52URM.scalePxInt(6)
        use URM_snapshots_listCompare(compareList)

    elif len(changes) == 0:
        label "No changes were found" xalign 0.5 yoffset x52URM.scaleY(1.5)

    else:
        # PAGES
        fixed ysize x52URM.scalePxInt(50):
            hbox xalign .5 yoffset 4 spacing 2:
                use URM_pages(comparisonPages)
            hbox xalign 1.0 yalign .5:
                text 'Changes: {}'.format(len(changes))

        use URM_tableRow(): # Headers
            label "{urm_notl}Name{/urm_notl}" xsize comparisonColWidth[0]
            label "{urm_notl}Previous{/urm_notl}" xsize comparisonColWidth[1]
            label "{urm_notl}New{/urm_notl}" xsize comparisonColWidth[2]

        viewport:
            xfill True
            yfill True
            mousewheel True
            draggable True
            scrollbars "vertical"

            # Results
            use URM_table():
                for var in changes[comparisonPages.pageStartIndex:comparisonPages.pageEndIndex]:
                    use URM_tableRow():
                        hbox xsize comparisonColWidth[0] yalign .5:
                            text x52URM.scaleText(var['old'].name, 18) substitute False

                        hbox xsize comparisonColWidth[1] yalign .5:
                            textbutton var['old'].getButtonValue(17) substitute False action Show('URM_modify_value', var=var['old'])

                        hbox xsize comparisonColWidth[2] yalign .5:
                            textbutton var['new'].getButtonValue(17) substitute False action Show('URM_modify_value', var=var['new'])

                        hbox:
                            hbox spacing 2:
                                # Remember
                                if x52URM.VarsStore.has(var['new'].name):
                                    use x52URM_iconButton('\ue4f8', '{urm_notl}Forget{/urm_notl}', Function(x52URM.VarsStore.forget, var['new'].name))
                                else:
                                    use x52URM_iconButton('\ue862', '{urm_notl}Remember{/urm_notl}', Show('URM_remember_var', varName=var['new'].name))
                                # Watch
                                if x52URM.VarsStore.isWatched(var['new'].name):
                                    use x52URM_iconButton('\ue8f5', '{urm_notl}Unwatch{/urm_notl}', Function(x52URM.VarsStore.unwatch, var['new'].name))
                                else:
                                    use x52URM_iconButton('\ue8f4', '{urm_notl}Watch{/urm_notl}', Show('URM_remember_var', varName=var['new'].name, rememberType='watchVar'))
                                # List changes
                                if var['old'].varType == 'dict' and var['new'].varType == 'dict':
                                    use x52URM_iconButton('\ue8f2', '{urm_notl}Show changes{/urm_notl}', SetLocalVariable('compareDict', var))
                                elif var['old'].varType == 'list' and var['new'].varType == 'list':
                                    use x52URM_iconButton('\ue8f2', '{urm_notl}Show changes{/urm_notl}', SetLocalVariable('compareList', var))

screen URM_snapshots_dictCompare(compareVar):
    style_prefix "x52URM"

    default dictChanges = x52URM.Snapshots.findDictChanges(compareVar['old'].value, compareVar['new'].value)
    default dictComparisonColWidth = [x52URM.scaleX(20), x52URM.scaleX(20), x52URM.scaleX(20)]
    default dictComparisonPages = x52URM.Pages(len(dictChanges), itemsPerPage=20)

    if len(dictChanges) == 0:
        label "No changes were found" xalign 0.5 yoffset x52URM.scaleY(1.5)
    
    else:
        # PAGES
        fixed ysize x52URM.scalePxInt(50):
            hbox xalign .5 yoffset 4 spacing 2:
                use URM_pages(dictComparisonPages)
            hbox xalign 1.0 yalign .5:
                text 'Changes: {}'.format(len(dictChanges))
                null width x52URM.scalePxInt(10)

        use URM_tableRow(): # Headers
            label "{urm_notl}Name{/urm_notl}" xsize dictComparisonColWidth[0]
            label "{urm_notl}Previous{/urm_notl}" xsize dictComparisonColWidth[1]
            label "{urm_notl}New{/urm_notl}" xsize dictComparisonColWidth[2]

        viewport:
            xfill True
            yfill True
            mousewheel True
            draggable True
            scrollbars "vertical"
            spacing x52URM.scalePxInt(10)

            # Results
            use URM_table():
                for var in dictChanges[dictComparisonPages.pageStartIndex:dictComparisonPages.pageEndIndex]:
                    use URM_tableRow():
                        hbox xsize dictComparisonColWidth[0] yalign .5:
                            text x52URM.scaleText(var['old'].name, 18) substitute False

                        hbox xsize dictComparisonColWidth[1] yalign .5:
                            textbutton var['old'].getButtonValue(17) substitute False action Show('URM_modify_value', var=var['old'])

                        hbox xsize dictComparisonColWidth[2] yalign .5:
                            textbutton var['new'].getButtonValue(17) substitute False action NullAction()

screen URM_snapshots_listCompare(compareVar):
    style_prefix "x52URM"

    default listChanges = x52URM.Snapshots.findListChanges(compareVar['old'].value, compareVar['new'].value)
    default listComparisonColWidth = [x52URM.scaleX(15), x52URM.scaleX(70)]
    default listComparisonPages = x52URM.Pages(len(listChanges), itemsPerPage=20)

    if len(listChanges) == 0:
        label "{urm_notl}No changes were found{/urm_notl}" xalign 0.5 yoffset x52URM.scaleY(1.5)
    
    else:
        # PAGES
        fixed ysize x52URM.scalePxInt(50):
            hbox xalign .5 yoffset 4 spacing 2:
                use URM_pages(listComparisonPages)
            hbox xalign 1.0 yalign .5:
                text 'Changes: {}'.format(len(listChanges))

        use URM_tableRow(): # Headers
            label "{urm_notl}Added/Remove{/urm_notl}" xsize listComparisonColWidth[0]
            label "{urm_notl}Value{/urm_notl}" xsize listComparisonColWidth[1]

        viewport:
            xfill True
            yfill True
            mousewheel True
            draggable True
            scrollbars "vertical"

            # Results
            use URM_table():
                for change in listChanges[listComparisonPages.pageStartIndex:listComparisonPages.pageEndIndex]:
                    use URM_tableRow():
                        hbox xsize listComparisonColWidth[0]:
                            text change['type']

                        hbox xsize listComparisonColWidth[1]:
                            text x52URM.scaleText(str(change['val']), 68) substitute False


screen URM_snapshot_create():
    layer 'x52Overlay'
    style_prefix "x52URM"

    default submitAction = Function(x52URM.Snapshots.create, name=x52URM.GetScreenInput('nameInput'))
    default nameInput = x52URM.Input(autoFocus=True, onEnter=[submitAction,Hide('URM_snapshot_create')])

    use x52URM_Dialog(title='{urm_notl}Create snapshot{/urm_notl}', closeAction=Hide('URM_snapshot_create'), modal=True, icon='\ue439'):
        text "Enter a name:"
        button:
            xminimum x52URM.scalePxInt(450)
            key_events True
            action nameInput.Enable()
            input value nameInput

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            textbutton "{urm_notl}Create{/urm_notl}" style_suffix "buttonPrimary" action [submitAction,Hide('URM_snapshot_create')]
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_snapshot_create')

