
# ==================
# SEARCH MAIN SCREEN
# ==================
screen URM_search():
    style_prefix "x52URM"
    default colWidth = [x52URM.scaleX(25), x52URM.scaleX(25)]
    default searchPages = x52URM.Pages(len(x52URM.Search.results), itemsPerPage=20)
    default nameSorted = None
    default expandObjectVars = []

    python:
        if x52URM.Search.expandObjectVars:
            SetLocalVariable('expandObjectVars', x52URM.Search.expandObjectVars)()
            x52URM.Search.expandObjectVars = None

    if len(expandObjectVars):
        default xadj = ui.adjustment() # Used to auto scoll to the end

        python:
            if xadj.value == xadj.range:
                xadj.value = float('inf')

        viewport:
            xfill True ysize x52URM.scalePxInt(38)
            mousewheel 'horizontal'
            draggable True
            xadjustment xadj
            has hbox
            spacing 2
            
            textbutton 'Results' action SetLocalVariable('expandObjectVars', [])
            for i,var in enumerate(expandObjectVars):
                text '\ue5cc' style_suffix 'icon' yalign .5
                textbutton x52URM.scaleText(var.namePath[-1], 10) substitute False sensitive (i < len(expandObjectVars)-1) action SetLocalVariable('expandObjectVars', expandObjectVars[:i+1])

        null height x52URM.scalePxInt(10)
        frame style_suffix "seperator" ysize x52URM.scalePxInt(2)

        use URM_objectVar(expandObjectVars)

    else:
        python:
            if len(x52URM.Search.results) != searchPages.itemCount:
                SetField(searchPages, 'itemCount', len(x52URM.Search.results))()

        hbox:
            xfill True
            hbox:
                spacing 5
                text "Search: " yalign .5
                hbox yalign .5:
                    button:
                        xminimum x52URM.scalePxInt(250)
                        key_events True
                        action x52URM.Search.queryInput.Enable()
                        input value x52URM.Search.queryInput
                text " in " yalign .5
                textbutton "[x52URM.Search.searchType]" yalign .5 selected False action [Show('URM_search_options'),x52URM.Search.queryInput.Disable()]
                textbutton "{urm_notl}Search{/urm_notl}" style_suffix "buttonPrimary" yalign .5 action Function(x52URM.Search.doSearch)
                textbutton "{urm_notl}Reset{/urm_notl}" yalign .5 action Function(x52URM.Search.resetSearch)

                if x52URM.Search.searchType == 'labels':
                    text 'Last seen: [x52URM.Search.lastLabel]' yalign 0.5
                    if renpy.has_label(x52URM.Search.lastLabel):
                        if not x52URM.LabelsStore.has(x52URM.Search.lastLabel):
                            textbutton "\ue609" style_suffix "icon_button" yalign 0.5 hovered x52URM.Tooltip('Remember label') unhovered x52URM.Tooltip() action Show('URM_remember_var', varName=x52URM.Search.lastLabel, rememberType='label')
                        textbutton "\ue1c4" style_suffix "icon_button" yalign 0.5 hovered x52URM.Tooltip('Replay label') unhovered x52URM.Tooltip() action Show('URM_replay', labelName=x52URM.Search.lastLabel)

            hbox xalign 1.0 yalign .5 spacing 2:
                textbutton '{urm_notl}R{/urm_notl}' style_suffix If(x52URM.Settings.searchRecursive, 'buttonSuccess', 'buttonCancel') selected False hovered x52URM.Tooltip(If(x52URM.Settings.searchRecursive, 'Recursive search enabled', 'Recursive search disabled')) unhovered x52URM.Tooltip() action ToggleField(x52URM.Settings, 'searchRecursive', True, False) text_xalign .5 xsize x52URM.scalePxInt(36)
                textbutton '{urm_notl}P{/urm_notl}' style_suffix If(x52URM.Settings.searchPersistent, 'buttonSuccess', 'buttonCancel') selected False hovered x52URM.Tooltip(If(x52URM.Settings.searchPersistent, 'Persistent variables search enabled', 'Persistent variables search disabled')) unhovered x52URM.Tooltip() action ToggleField(x52URM.Settings, 'searchPersistent', True, False) text_xalign .5 xsize x52URM.scalePxInt(36)
                textbutton '{urm_notl}O{/urm_notl}' style_suffix If(x52URM.Settings.searchObjects, 'buttonSuccess', 'buttonCancel') selected False hovered x52URM.Tooltip(If(x52URM.Settings.searchObjects, 'Object search enabled', 'Object search disabled')) unhovered x52URM.Tooltip() action ToggleField(x52URM.Settings, 'searchObjects', True, False) text_xalign .5 xsize x52URM.scalePxInt(36)
                textbutton '{urm_notl}W{/urm_notl}' style_suffix If(x52URM.Settings.useWildcardSearch, 'buttonSuccess', 'buttonCancel') selected False hovered x52URM.Tooltip(If(x52URM.Settings.useWildcardSearch, 'Wildcard search enabled', 'Wildcard search disabled')) unhovered x52URM.Tooltip() action ToggleField(x52URM.Settings, 'useWildcardSearch', True, False) text_xalign .5 xsize x52URM.scalePxInt(36)
                textbutton '{urm_notl}U{/urm_notl}' style_suffix If(x52URM.Settings.showUnsupportedVariables, 'buttonSuccess', 'buttonCancel') selected False tooltip If(x52URM.Settings.showUnsupportedVariables, 'Showing unsupported vars', 'Hiding unsupported vars') action ToggleField(x52URM.Settings, 'showUnsupportedVariables', True, False)
                textbutton '{urm_notl}I{/urm_notl}' style_suffix If(x52URM.Settings.searchInternalVars, 'buttonSuccess', 'buttonCancel') selected False hovered x52URM.Tooltip(If(x52URM.Settings.searchInternalVars, 'Showing internal variables', 'Hiding internal variables')) unhovered x52URM.Tooltip() action ToggleField(x52URM.Settings, 'searchInternalVars', True, False) text_xalign .5 xsize x52URM.scalePxInt(36)
                null width x52URM.scalePxInt(10)
                
        null height x52URM.scalePxInt(10)
        frame style_suffix "seperator" ysize x52URM.scalePxInt(2)

        if len(x52URM.Search.results) > 0:
            # PAGES
            fixed ysize x52URM.scalePxInt(50):
                hbox xalign .5 yoffset 4 spacing 2:
                    use URM_pages(searchPages)
                hbox xalign 1.0 yalign .5:
                    text 'Results: {}'.format(len(x52URM.Search.results))
                    null width x52URM.scalePxInt(10)

            # Headers
            use URM_tableRow():
                hbox xsize colWidth[0]:
                    hbox:
                        label '{urm_notl}Name{/urm_notl}'
                        if nameSorted == 'asc':
                            textbutton '{size=-6}\ue316{/size}' yoffset x52URM.scalePxInt(-4) style_suffix 'icon_textbutton' hovered x52URM.Tooltip('{urm_notl}Sort descending{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.Search.sort, reverse=True),SetLocalVariable('nameSorted', 'desc')]
                        else:
                            textbutton If(nameSorted,'{size=-6}\ue313{/size}','{size=-6}\ue5d7{/size}') yoffset x52URM.scalePxInt(-4) style_suffix 'icon_textbutton' hovered x52URM.Tooltip('{urm_notl}Sort ascending{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.Search.sort),SetLocalVariable('nameSorted', 'asc')]
                hbox xsize colWidth[1]:
                    label If(x52URM.Search.searchType=='labels', '{urm_notl}Replay{/urm_notl}', '{urm_notl}Value{/urm_notl}')

            # Results
            viewport:
                xfill True
                yfill True
                mousewheel True
                draggable True
                scrollbars "vertical"

                use URM_table():
                    for i,var in enumerate(x52URM.Search.results[searchPages.pageStartIndex:searchPages.pageEndIndex]):
                        use URM_tableRow(i, True):
                            if x52URM.Search.searchType == 'labels': # Are we searching labels?
                                hbox xsize colWidth[0] yalign .5:
                                    text x52URM.scaleText(var.name, 23) substitute False
                                hbox spacing 2 yalign .5:
                                    use x52URM_iconButton('\ue1c4', '{urm_notl}Play{/urm_notl}', Show('URM_replay', labelName=var.name))
                                    use x52URM_iconButton('\ue163', '{urm_notl}Jump{/urm_notl}', Show('URM_jump', labelName=var.name))
                                    # Remember
                                    if x52URM.LabelsStore.has(var.name):
                                        use x52URM_iconButton('\ue4f8', '{urm_notl}Forget{/urm_notl}', Function(x52URM.LabelsStore.forget, var.name))
                                    else:
                                        use x52URM_iconButton('\ue862', '{urm_notl}Remember{/urm_notl}', Show('URM_remember_var', varName=var.name, rememberType='label'))

                            else: # We are searching variables
                                hbox xsize colWidth[0] yalign .5:
                                    text x52URM.scaleText(var.name, 23) substitute False
                                hbox xsize colWidth[1] yalign .5:
                                    if var.isExpandable:
                                        if len(var.namePath) == 2: # A results we're seeing here could be a subitem/property
                                            textbutton var.getButtonValue(23) substitute False action SetLocalVariable('expandObjectVars', [x52URM.Var(var.namePath[0]), var])
                                        else:
                                            textbutton var.getButtonValue(23) substitute False action SetLocalVariable('expandObjectVars', [var])
                                    else:
                                        textbutton var.getButtonValue(23) substitute False action Show('URM_modify_value', var=var)
                                hbox spacing 2 yalign .5:
                                    # Remember
                                    if x52URM.VarsStore.has(var.name):
                                        use x52URM_iconButton('\ue4f8', '{urm_notl}Forget{/urm_notl}', Function(x52URM.VarsStore.forget, var.name))
                                    else:
                                        use x52URM_iconButton('\ue862', '{urm_notl}Remember{/urm_notl}', Show('URM_remember_var', varName=var.name))
                                    # Watch
                                    if x52URM.VarsStore.isWatched(var.name):
                                        use x52URM_iconButton('\ue8f5', '{urm_notl}Unwatch{/urm_notl}', Function(x52URM.VarsStore.unwatch, var.name))
                                    else:
                                        use x52URM_iconButton('\ue8f4', '{urm_notl}Watch{/urm_notl}', Show('URM_remember_var', varName=var.name, rememberType='watchVar'))

        else: # No results
            vbox:
                yoffset x52URM.scaleY(1.5)
                xalign 0.5

                label "{urm_notl}No results{/urm_notl}" xalign 0.5
                if x52URM.Search.searchRecursive:
                    null height x52URM.scalePxInt(10)
                    text "You're currently doing a recursive search, use the reset button to start over" xalign 0.5
                    text "This means you're searching your previous results instead of everything" xalign 0.5 size 16

# =====================
# SEARCH OPTIONS SCREEN
# =====================
screen URM_search_options():
    layer 'x52Overlay'
    style_prefix "x52URM"

    use x52URM_Dialog('Search options', closeAction=Hide('URM_search_options'), modal=True, icon='\ue8b6'):
        text '{urm_notl}Search type:{/urm_notl}'
        vbox spacing 2:
            use x52URM_radiobutton(checked=(x52URM.Search.searchType=='variable names'), text='{urm_notl}Variable names{/urm_notl}', action=[SetField(x52URM.Search, 'searchType', 'variable names'),Hide('URM_search_options')])
            use x52URM_radiobutton(checked=(x52URM.Search.searchType=='values'), text='{urm_notl}Values{/urm_notl}', action=[SetField(x52URM.Search, 'searchType', 'values'),Hide('URM_search_options')])
            use x52URM_radiobutton(checked=(x52URM.Search.searchType=='labels'), text='{urm_notl}Labels/Scenes{/urm_notl}', action=[SetField(x52URM.Search, 'searchType', 'labels'),Hide('URM_search_options')])

        null height 20
        text 'Other options:'
        vbox spacing 2:
            hbox:
                use x52URM_checkbox(checked=x52URM.Settings.searchRecursive, text='Use recursive search', action=ToggleField(x52URM.Settings, 'searchRecursive', True, False))
                textbutton "\ueb8b" style_suffix "icon_button" yalign .5 hovered x52URM.Tooltip("Explain resursive search") unhovered x52URM.Tooltip() action x52URM.Confirm("""Enabling this feature means you'll search previous results until you reset\n\nExample:\nYou search for value {b}51{/b}, but get a lot of results\nWhen you know the value changed to (for example) {b}52{/b}, search for {b}52{/b}\nRecursive search will show all previous {b}51{/b} values that changed to {b}52{/b}""", title='Recursive search')
            hbox:
                use x52URM_checkbox(checked=x52URM.Settings.searchPersistent, text='Search in persistents', action=ToggleField(x52URM.Settings, 'searchPersistent', True, False))
                textbutton "\ueb8b" style_suffix "icon_button" yalign .5 hovered x52URM.Tooltip("Explain persistents") unhovered x52URM.Tooltip() action x52URM.Confirm("""Persistent variables are variables outside your save\n\nThose will stay the same regardless of the save you load,\nor even when you start a new game""", title='Persistent variables')
            hbox:
                use x52URM_checkbox(checked=x52URM.Settings.searchObjects, text='Search in objects/lists/dicts', action=ToggleField(x52URM.Settings, 'searchObjects', True, False))
                textbutton "\ueb8b" style_suffix "icon_button" yalign .5 hovered x52URM.Tooltip("Explain object search") unhovered x52URM.Tooltip() action x52URM.Confirm("""Objects, lists and dicts are essentually variables that contain variables\n\nFor example the object {b}player{/b} could contain the variable {b}name{/b}\nWhich is diplayed as {b}player.name{/b}""", title='search objects')
            hbox:
                use x52URM_checkbox(checked=x52URM.Settings.useWildcardSearch, text='Use wildcard search', action=ToggleField(x52URM.Settings, 'useWildcardSearch', True, False))
                textbutton "\ueb8b" style_suffix "icon_button" yalign .5 hovered x52URM.Tooltip("Explain wildcard search") unhovered x52URM.Tooltip() action x52URM.Confirm("""Enabling this feature means results will exactly match the value you've entered. {b}Unless{/b} you use a wilcard.\n\nThere are 2 types of wildcards:\n{b}*{/b} : Will match any character\n{b}?{/b} : Matches any single character\n\nExample:\n{b}0x52{/b} will only match exactly {b}0x52{/b}\n{b}*0x52*{/b} will also match {b}Hi, I'm 0x52! Who are you?{/b}\n{b}0*52{/b} will match {b}0x52{/b}, {b}0xxx52{/b} and {b}052{/b}\n{b}0?52{/b} will match {b}0x52{/b}, but will NOT match {b}0xxx52{/b} or {b}052{/b}""", title='Wildcard search')
            hbox:
                use x52URM_checkbox(checked=x52URM.Settings.showUnsupportedVariables, text='Show unsupported variables', action=ToggleField(x52URM.Settings, 'showUnsupportedVariables', True, False))
                textbutton "\ueb8b" style_suffix "icon_button" yalign .5 tooltip "Explain unsupported variables" action x52URM.Confirm("""Show variables that URM cannot modify""", title='Unsupported variables')
