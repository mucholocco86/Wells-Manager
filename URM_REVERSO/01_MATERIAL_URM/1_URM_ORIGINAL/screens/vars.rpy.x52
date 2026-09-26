
# =====================
# VARIABLES MAIN SCREEN
# =====================
screen URM_variables():
    style_prefix "x52URM"
    default movingVarName = None
    default colWidth = [x52URM.scaleX(20), x52URM.scaleX(20), x52URM.scaleX(7), x52URM.scaleX(7), x52URM.scaleX(7), x52URM.scaleX(7)]
    default varPages = x52URM.Pages(len(x52URM.VarsStore.store), itemsPerPage=20)
    default nameSorted = None
    default expandObjectVars = []

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
            
            textbutton '{urm_notl}Variables{/urm_notl}' action SetLocalVariable('expandObjectVars', [])
            for i,var in enumerate(expandObjectVars):
                text '\ue5cc' style_suffix 'icon' yalign .5
                textbutton x52URM.scaleText(var.namePath[-1], 10) substitute False sensitive (i < len(expandObjectVars)-1) action SetLocalVariable('expandObjectVars', expandObjectVars[:i+1])

        null height x52URM.scalePxInt(10)
        frame style_suffix "seperator" ysize x52URM.scalePxInt(2)

        use URM_objectVar(expandObjectVars)

    else:
        python:
            if len(x52URM.VarsStore.store) != varPages.itemCount:
                SetField(varPages, 'itemCount', len(x52URM.VarsStore.store))()

        hbox:
            xfill True
            hbox:
                spacing x52URM.scalePxInt(5)
                if x52URM.URMFiles.file.filename or len(x52URM.VarsStore.store) > 0:
                    text "Remembered variables: "+str(len(x52URM.VarsStore.store)) yalign 0.5
                    textbutton "\ue16c" style_suffix "icon_button" hovered x52URM.Tooltip('Clear variables list') unhovered x52URM.Tooltip() action If(x52URM.VarsStore.store.unsaved, x52URM.Confirm('This will clear the list below, are you sure?', Function(x52URM.VarsStore.clear), title='Clear list'), Function(x52URM.VarsStore.clear))
                else:
                    text "Load a file or add variables using the search option"

            hbox:
                xalign 1.0
                textbutton '\ue03c' style_suffix 'icon_button' hovered x52URM.Tooltip('{urm_notl}Create variable{/urm_notl}') unhovered x52URM.Tooltip() action Show('URM_createVar')
                null width x52URM.scalePxInt(10)
        null height x52URM.scalePxInt(10)
        frame style_suffix "seperator" ysize x52URM.scalePxInt(2)

        if len(x52URM.VarsStore.store) > 0:
            # PAGES
            fixed ysize x52URM.scalePxInt(50):
                hbox xalign .5 yoffset 4 spacing 2:
                    use URM_pages(varPages)

            use URM_tableRow(): # Headers
                hbox xsize colWidth[0]:
                    hbox:
                        label "{urm_notl}Name{/urm_notl}"
                        if nameSorted == 'asc':
                            textbutton '{size=-6}\ue316{/size}' yoffset x52URM.scalePxInt(-4) style_suffix 'icon_textbutton' hovered x52URM.Tooltip('{urm_notl}Sort descending{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.VarsStore.sort, reverse=True),SetLocalVariable('nameSorted', 'desc')]
                        else:
                            textbutton If(nameSorted,'{size=-6}\ue313{/size}','{size=-6}\ue5d7{/size}') yoffset x52URM.scalePxInt(-4) style_suffix 'icon_textbutton' hovered x52URM.Tooltip('{urm_notl}Sort ascending{/urm_notl}') unhovered x52URM.Tooltip() action [Function(x52URM.VarsStore.sort),SetLocalVariable('nameSorted', 'asc')]
                label "{urm_notl}Value{/urm_notl}" xsize colWidth[1]
                hbox xsize colWidth[2]:
                    hbox:
                        label "{urm_notl}Watch{/urm_notl}"
                        textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('Add this variable to the watchpanel\nSo you can easily view and edit it during playing', title='Watch variable')
                hbox xsize colWidth[3]:
                    hbox:
                        if not x52URM.StoreMonitor.isSupported:
                            label "{urm_notl}Freeze{/urm_notl}" text_color '#ff0000'
                            textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('A frozen variable cannot change until you unfreeze it\nYou can only change it through URM\n{color=#ff0000}{b}This feature is not supported on the Ren\'Py version used for this game{/b}{/color}', title='Freeze variable')
                        elif x52URM.StoreMonitor.isAttached:
                            label "{urm_notl}Freeze{/urm_notl}"
                            textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('A frozen variable cannot change until you unfreeze it\nYou can only change it through URM\n{alpha=.8}{size=-5}Use with care. Freezing important variables could break stuff{/size}{/alpha}', title='Freeze variable')
                        else:
                            label "{urm_notl}Freeze{/urm_notl}" text_color '#ff0000'
                            textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('A frozen variable cannot change until you unfreeze it\nYou can only change it through URM\n{color=#ff0000}{b}URM failed to initialize this feature{/b}{/color}', title='Freeze variable')
                hbox xsize colWidth[4]:
                    hbox:
                        if not x52URM.StoreMonitor.isSupported:
                            label "{urm_notl}Monitor{/urm_notl}" text_color '#ff0000'
                            textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('You\'ll receive a notification when this variable changes\n{color=#ff0000}{b}This feature is not supported on the Ren\'Py version used for this game{/b}{/color}', title='Monitor variable')
                        elif x52URM.StoreMonitor.isAttached:
                            label "{urm_notl}Monitor{/urm_notl}"
                            textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('You\'ll receive a notification when this variable changes', title='Monitor variable')
                        else:
                            label "{urm_notl}Monitor{/urm_notl}" text_color '#ff0000'
                            textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('You\'ll receive a notification when this variable changes\n{color=#ff0000}{b}URM failed to initialize this feature{/b}{/color}', title='Monitor variable')
                hbox xsize colWidth[5]:
                    hbox:
                        label "{urm_notl}Ignore{/urm_notl}"
                        textbutton '{size=-6}\uf1c0{/size}' yoffset x52URM.scalePxInt(-8) style_suffix 'icon_textbutton' action x52URM.Confirm('Ignore this variable in path detection {font=0x52-URM/framework/MaterialIcons-Regular.ttf}\ueb80{/font} and/or codeview {font=0x52-URM/framework/MaterialIcons-Regular.ttf}\ue4f3{/font}', title='Ignore variable')

            viewport:
                xfill True
                yfill True
                mousewheel True
                draggable True
                scrollbars "vertical"

                # Results
                use URM_table():
                    for i,(varName,props) in enumerate(list(x52URM.VarsStore.store.items())[varPages.pageStartIndex:varPages.pageEndIndex]):
                        use URM_tableRow(i, True):
                            hbox xsize colWidth[0] yalign .5:
                                if 'name' in props:
                                    text x52URM.scaleText(props['name'], 20) substitute False
                                else:
                                    text x52URM.scaleText(varName, 20) substitute False

                            hbox xsize colWidth[1]:
                                if x52URM.Var(varName).isExpandable:
                                    if len(x52URM.Var(varName).namePath) == 2: # A results we're seeing here could be a subitem/property
                                        textbutton x52URM.Var(varName).getButtonValue(23) substitute False action SetLocalVariable('expandObjectVars', [x52URM.Var(x52URM.Var(varName).namePath[0]), x52URM.Var(varName)])
                                    else:
                                        textbutton x52URM.Var(varName).getButtonValue(23) substitute False action SetLocalVariable('expandObjectVars', [x52URM.Var(varName)])
                                else:
                                    textbutton x52URM.Var(varName).getButtonValue(19) action Show('URM_modify_value', var=x52URM.Var(varName)) substitute False

                            hbox xsize colWidth[2]: # Watch
                                if x52URM.VarsStore.isWatched(varName):
                                    use x52URM_iconButton('\ue8f4', '{urm_notl}Yes{/urm_notl}', action=Function(x52URM.VarsStore.unwatch, varName))
                                else:
                                    use x52URM_iconButton('\ue8f5', '{urm_notl}No{/urm_notl}', action=Show('URM_remember_var', varName=varName, rememberType='watchVar', defaultName=If('name' in props, props['name'], varName)))

                            hbox xsize colWidth[3]: # Freeze
                                if x52URM.VarsStore.isFrozen(varName):
                                    use x52URM_iconButton('\ueb3b', '{urm_notl}Yes{/urm_notl}', action=Function(x52URM.VarsStore.unfreeze, varName), sensitive=If(x52URM.VarsStore.isFreezable(varName), None, False))
                                else:
                                    use x52URM_iconButton('\ue798', '{urm_notl}No{/urm_notl}', action=Function(x52URM.VarsStore.freeze, varName), sensitive=If(x52URM.VarsStore.isFreezable(varName), None, False))

                            hbox xsize colWidth[4]: # Monitor
                                if x52URM.VarsStore.isMonitored(varName):
                                    use x52URM_iconButton('\ue7f4', '{urm_notl}Yes{/urm_notl}', action=Function(x52URM.VarsStore.unmonitor, varName), sensitive=If(x52URM.VarsStore.isMonitorable(varName), None, False))
                                else:
                                    use x52URM_iconButton('\ue7f6', '{urm_notl}No{/urm_notl}', action=Function(x52URM.VarsStore.monitor, varName), sensitive=If(x52URM.VarsStore.isMonitorable(varName), None, False))

                            hbox xsize colWidth[5]: # Ignore
                                hbox spacing 2:
                                    if x52URM.VarsStore.isIgnored(varName, 'path'):
                                        use x52URM_iconButton('\ueb80', action=Function(x52URM.VarsStore.unignore, varName, 'path'))
                                    else:
                                        use x52URM_iconButton('\ue065', action=Function(x52URM.VarsStore.ignore, varName, 'path'))
                                    if x52URM.VarsStore.isIgnored(varName, 'code'):
                                        use x52URM_iconButton('\ue4f3', action=Function(x52URM.VarsStore.unignore, varName, 'code'))
                                    else:
                                        use x52URM_iconButton('\ue86f', action=Function(x52URM.VarsStore.ignore, varName, 'code'))

                            hbox spacing 2:
                                use x52URM_iconButton('\ue3c9', '{urm_notl}Edit{/urm_notl}', action=Show('URM_remember_var', varName=varName, defaultName=If('name' in props, props['name'], varName)))
                                use x52URM_iconButton('\ue872', '{urm_notl}Remove{/urm_notl}', action=x52URM.Confirm('Are you sure you want to remove this variable?', Function(x52URM.VarsStore.forget, varName), title='Remove variable'))
                                if movingVarName:
                                    if movingVarName == varName:
                                        use x52URM_iconButton('\uf230', '{urm_notl}Cancel{/urm_notl}', action=SetLocalVariable('movingVarName', None))
                                    else:
                                        use x52URM_iconButton('\ue55c', '{urm_notl}Before this{/urm_notl}', action=[Function(x52URM.VarsStore.changePos, movingVarName, varName),SetLocalVariable('movingVarName', None)])
                                else:
                                    use x52URM_iconButton('\ue89f', '{urm_notl}Move{/urm_notl}', action=SetLocalVariable('movingVarName', varName))

        else:
            vbox:
                yoffset x52URM.scaleY(1.5)
                xalign 0.5
                label "{urm_notl}There are no remembered variables{/urm_notl}" xalign 0.5

# ===================
# MODIFY VALUE SCREEN
# ===================
screen URM_modify_value(var, allowRemember=False):
    layer 'x52Overlay'
    style_prefix "x52URM"

    default newValue = var.value
    default errorMessage = None
    default valueInput = x52URM.Input(
        text=str(newValue),
        autoFocus=True,
        editable=var.isEditable,
        updateScreenVariable='newValue',
        onEnter=x52URM.SetVarValue(var, onSuccess=Hide('URM_modify_value'), screenErrorVariable='errorMessage', newValue=URMGetScreenVariable('newValue')),
    )

    on "show" action [x52URM.Search.queryInput.Disable(),valueInput.Enable()]

    use x52URM_Dialog(title=If(var.isEditable,'{urm_notl}Modify variable{/urm_notl}','{urm_notl}View variable{/urm_notl}'), closeAction=Hide('URM_modify_value'), modal=True, icon='\ue3c9'):
            vbox xminimum x52URM.scalePxInt(450) # To force a minimum width on the dialog
            label "[var.nameShortened]"
            null height x52URM.scalePxInt(10)

            text "{urm_notl}Value type: [var.varType]{/urm_notl}"
            if var.isExpandable:
                textbutton var.getButtonValue(23) substitute False action [SetField(x52URM.Search, 'expandObjectVars', [var]),x52URM.Open('search')]
            elif var.varType in ['string', 'int', 'float', 'boolean']:
                text "{urm_notl}Value: {/urm_notl}" yalign .5
                if var.varType == 'boolean':
                    textbutton "{urm_notl}[newValue]{/urm_notl}" sensitive var.isEditable action ToggleScreenVariable('newValue', True, False)
                elif var.varType in ['string', 'int', 'float']:
                    vpgrid:
                        cols 1
                        draggable True
                        mousewheel True
                        scrollbars "vertical"

                        button:
                            xminimum x52URM.scalePxInt(450)
                            key_events True
                            sensitive var.isEditable
                            action valueInput.Enable()
                            input value valueInput allow If(var.varType=='string', '', If(var.varType=='float','.0123456789-','0123456789-'))

            if errorMessage != None:
                use x52URM_messagebar('error', errorMessage)

            if allowRemember:
                null height x52URM.scalePxInt(10)
                hbox:
                    align (1.0,1.0)
                    spacing x52URM.scalePxInt(10)

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

            hbox:
                yoffset x52URM.scalePxInt(15)
                align (1.0,1.0)
                spacing x52URM.scalePxInt(10)

                if var.isEditable:
                    if var.varType != 'unsupported' and var.varType in ['string', 'boolean', 'int', 'float']:
                        textbutton "{urm_notl}Change{/urm_notl}" style_suffix "buttonPrimary" action valueInput.onEnter
                    textbutton "{urm_notl}Delete{/urm_notl}" style_suffix 'buttonCancel' align(0.0, 1.0) action [x52URM.Confirm('I hope you know what you\'re doing, are you sure you want to continue?', Function(var.delete), title='{urm_notl}Deleting a variable{/urm_notl}'),Hide('URM_modify_value')]
                    textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_modify_value')
                else:
                    textbutton "{urm_notl}Close{/urm_notl}" action Hide('URM_modify_value')

# ==================
# ADD LIST/DICT ITEM
# ==================
screen URM_add_item(parentVar):
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    default itemVal = ''
    default inputs = x52URM.InputGroup(
        [
            ('itemKey', x52URM.Input(text=If(parentVar.varType=='dict', '', 'auto.'), editable=(parentVar.varType=='dict'))),
            ('itemVal', x52URM.Input(updateScreenVariable='itemVal')),
        ],
        focusFirst=True,
        onSubmit=x52URM.SetVarValue(
            var=parentVar,
            onSuccess=Hide('URM_add_item'),
            screenErrorVariable='errorMessage',
            newValue=URMGetScreenVariable('itemVal'),
            overruleVarType=URMGetScreenVariable('valueTypes', URMGetScreenVariable('valueTypeIndex')),
            operator=If(parentVar.varType=='list', 'append', '='),
            varChildKey=If(parentVar.varType=='dict', x52URM.GetScreenInput('itemKey', 'inputs'), None),
        ),
    )
    default errorMessage = None
    default valueTypes = ['string', 'int', 'float', 'boolean']
    default valueTypeIndex = 0

    on 'show' action [x52URM.Search.queryInput.Disable(),Function(inputs.focus)]
    key 'K_TAB' action inputs.NextInput()
    key 'shift_K_TAB' action inputs.PreviousInput()

    use x52URM_Dialog(title='{urm_notl}Add item{/urm_notl}', closeAction=Hide('URM_add_item'), modal=True, icon='\ue146'):
        label '[parentVar.name]'
        if parentVar.varType=='dict':
            text "{urm_notl}Key:{/urm_notl}"
            button:
                xminimum x52URM.scalePxInt(450)
                key_events True
                action inputs.itemKey.Enable()
                input value inputs.itemKey
            null height x52URM.scalePxInt(10)

        hbox:
            text "{urm_notl}Value type:{/urm_notl} " yalign .5
            textbutton valueTypes[valueTypeIndex] action SetScreenVariable('valueTypeIndex', (valueTypeIndex+1) % len(valueTypes))

        text "{urm_notl}Value:{/urm_notl}"
        if valueTypes[valueTypeIndex] == 'boolean':
            textbutton "[itemVal]" action ToggleScreenVariable('itemVal', True, False)
        else:
            button:
                xminimum x52URM.scalePxInt(450)
                key_events True
                action inputs.itemVal.Enable()
                input value inputs.itemVal

        if errorMessage != None:
            use x52URM_messagebar('error', errorMessage)

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            textbutton "{urm_notl}Add{/urm_notl}" sensitive bool(str(inputs.itemKey)) style_suffix "buttonPrimary" action inputs.onSubmit
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_add_item')

# ============
# REMEMBER VAR
# ============
screen URM_remember_var(varName, rememberType='var', defaultName=None):
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    if rememberType == 'label':
        default submitAction = Function(x52URM.LabelsStore.remember, varName, x52URM.GetScreenInput('displayNameInput'))
    elif rememberType == 'watchVar':
        default submitAction = Function(x52URM.VarsStore.watch, varName, x52URM.GetScreenInput('displayNameInput'))
    else:
        default submitAction = Function(x52URM.VarsStore.remember, varName, x52URM.GetScreenInput('displayNameInput'))

    default displayNameInput = x52URM.Input(text=If(defaultName, defaultName, varName), autoFocus=True, onEnter=[submitAction,Hide('URM_remember_var')])

    on 'show' action [x52URM.Search.queryInput.Disable(),displayNameInput.Enable()]

    use x52URM_Dialog(title=If(rememberType=='label', '{urm_notl}Remember label{/urm_notl}', If(rememberType=='watchVar', '{urm_notl}Watch variable{/urm_notl}', '{urm_notl}Remember variable{/urm_notl}')), closeAction=Hide('URM_remember_var'), modal=True, icon=If(rememberType=='watchVar', '\ue8f4', '\ue862')):
        text "{urm_notl}Enter a name:{/urm_notl}"
        button:
            xminimum x52URM.scalePxInt(450)
            key_events True
            action displayNameInput.Enable()
            input value displayNameInput

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            spacing x52URM.scalePxInt(10)
            if rememberType == 'label':
                use x52URM_iconButton('\ueb8b', action=x52URM.Confirm('Add this label to the labels tab\nSo you can easily find, play and save them', title='Remember label'))
            elif rememberType == 'watchVar':
                use x52URM_iconButton('\ueb8b', action=x52URM.Confirm('Add this variable to the watchpanel\nSo you can easily view and edit it during playing', title='Watch variable'))
            else:
                use x52URM_iconButton('\ueb8b', action=x52URM.Confirm('Add this variable to the variables tab\nSo you can easily find, edit and save them', title='Remember variable'))
            textbutton "{urm_notl}Save{/urm_notl}" style_suffix "buttonPrimary" action [submitAction,Hide('URM_remember_var')]
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_remember_var')

# ===========
# SAVE SCREEN
# ===========
screen URM_save_file():
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    default filenameInput = x52URM.Input(
        text=If(x52URM.URMFiles.file.filename, x52URM.URMFiles.file.filename and x52URM.URMFiles.file.filename[:-4], x52URM.URMFiles.stripSpecialChars(config.name)),
        autoFocus=True,
        onEnter=x52URM.URMFiles.Save(x52URM.GetScreenInput('filenameInput'), Hide('URM_save_file'), 'errorMessage')
    )
    default errorMessage = None

    on 'show' action [x52URM.Search.queryInput.Disable(),filenameInput.Enable()]

    use x52URM_Dialog(title='Save file', closeAction=Hide('URM_save_file'), modal=True, icon='\ue161'):
        text "{urm_notl}Enter a filename:{/urm_notl}"
        button:
            xminimum x52URM.scalePxInt(450)
            key_events True
            action filenameInput.Enable()
            input value filenameInput allow 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123465789-_ '

        if errorMessage != None:
            text errorMessage bold True color "#f42929"

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            spacing x52URM.scalePxInt(10)
            textbutton "\ueb8b" style_suffix "icon_button" yalign .5 action x52URM.Confirm(""".URM files can be shared with anyone and are saved in two locations:\n\n{}\n{}""".format(x52URM.URMFiles.gameDir, x52URM.URMFiles.saveDir or '<Secondary location unavailable in this game>'), title='URM files', promptSubstitution=False)
            textbutton "{urm_notl}Save{/urm_notl}" style_suffix "buttonPrimary" action filenameInput.onEnter
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_save_file')

# ===========
# LOAD SCREEN
# ===========
screen URM_load_file():
    layer 'x52Overlay'
    style_prefix "x52URM"
    default errorMessage = None

    use x52URM_Dialog(title='{urm_notl}Open file{/urm_notl}', closeAction=Hide('URM_load_file'), modal=True, icon='\ue2c7'):
        text '{urm_notl}Select a file to load:{/urm_notl}'
        if len(x52URM.URMFiles.listFiles()) == 0:
            hbox:
                ysize x52URM.scalePxInt(300)
                xsize x52URM.scalePxInt(650)
                vbox align (.5,.5) spacing x52URM.scalePxInt(10):
                    label 'No .urm files found' xalign .5
                    text "Looking for files in:\n{}\n{}".format(x52URM.URMFiles.gameDir, x52URM.URMFiles.saveDir or '')
        else:
            viewport:
                ysize x52URM.scalePxInt(300)
                xsize x52URM.scalePxInt(650)
                draggable True
                mousewheel True
                scrollbars "vertical"
                spacing 2

                vbox spacing 2:
                    for filename,file in x52URM.URMFiles.listFiles().items():
                        hbox spacing 2:
                            button:
                                xfill True right_margin x52URM.scalePxInt(45)
                                action x52URM.URMFiles.Load(filename, Hide('URM_load_file'), 'errorMessage')
                                vbox:
                                    label filename[:-4]
                                    text 'Modified: {}'.format(URMTimeToText(file.mtime))
                                    if file.storeNames:
                                        hbox spacing 2:
                                            if 'vars' in file.storeNames:
                                                text '\uef54' style_suffix 'icon'
                                            if 'watched' in file.storeNames:
                                                text '\ue8f4' style_suffix 'icon'
                                            if 'labels' in file.storeNames:
                                                text '\ue54e' style_suffix 'icon'
                                            if 'replacements' in file.storeNames:
                                                text '\ue560' style_suffix 'icon'
                                            if 'textboxCustomizations' in file.storeNames:
                                                text '\ue0b7' style_suffix 'icon'

                            textbutton '\ue872' xoffset -x52URM.scalePxInt(45) style_suffix 'icon_button' action x52URM.Confirm('Are you sure you want to delete this file? This cannot be undone', x52URM.URMFiles.Delete(file), title='Confirm deletion')

            if errorMessage != None:
                text errorMessage bold True color "#f42929"

# ==================
# VAR CHANGED SCREEN
# ==================
screen URM_var_changed(varName, prevVal):
    layer 'x52Overlay'
    style_prefix "x52URM"
    default var = x52URM.Var(varName)
    default prevValType = x52URM.Var.getValType(prevVal)
    default errorMessage = None

    use x52URM_Dialog(title='{urm_notl}Variable changed{/urm_notl}', closeAction=Hide('URM_var_changed'), modal=True):
        label '{urm_notl}Variable{/urm_notl}'
        text "[var.name]"

        if var.varType != prevValType:
            text "{urm_notl}Type changed from [prevValType] to [var.varType]{/urm_notl}"
        else:
            text "{urm_notl}Type: [var.varType]{/urm_notl}"
        null height x52URM.scalePxInt(10)

        label "{urm_notl}Previous value{/urm_notl}"
        text "{urm_notl}[prevVal]{/urm_notl}"
        null height x52URM.scalePxInt(10)
        label "{urm_notl}New value{/urm_notl}"
        text "{urm_notl}[var.value]{/urm_notl}"

        if errorMessage != None:
            use x52URM_messagebar('error', errorMessage)

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            if var.varType != 'unsupported':
                textbutton "{urm_notl}Change{/urm_notl}" style_suffix "buttonPrimary" action [Show('URM_modify_value', var=var),Hide('URM_var_changed')]
                null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Revert{/urm_notl}" style_suffix 'buttonCancel' align(0.0, 1.0) action x52URM.SetVarValue(var, onSuccess=Hide('URM_var_changed'), screenErrorVariable='errorMessage', newValue=prevVal)
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Close{/urm_notl}" action Hide('URM_var_changed')

screen URM_objectVar(expandObjectVars):
    default objectPages = x52URM.Pages(len(expandObjectVars[-1].children), itemsPerPage=19)
    default colWidth = [x52URM.scaleX(25), x52URM.scaleX(25)]

    python:
        if len(expandObjectVars[-1].children) != objectPages.itemCount:
            SetField(objectPages, 'itemCount', len(expandObjectVars[-1].children))()

    vbox:
        # PAGES
        fixed ysize x52URM.scalePxInt(50):
            hbox xalign .5 yoffset 4 spacing 2:
                use URM_pages(objectPages)
            hbox xalign 1.0 yalign .5:
                text 'Items: {}'.format(len(expandObjectVars[-1].children))
                null width x52URM.scalePxInt(10)

        if expandObjectVars[-1].varType in ['dict','list']:
            use URM_tableRow():
                use x52URM_iconButton('\ue146', '{urm_notl}Add item{/urm_notl}', Show('URM_add_item', parentVar=expandObjectVars[-1]))

        # Headers
        use URM_tableRow():
            hbox xsize colWidth[0]:
                label '{urm_notl}Name{/urm_notl}'
            hbox xsize colWidth[1]:
                label '{urm_notl}Value{/urm_notl}'

        if len(expandObjectVars[-1].children) == 0:
            text '{urm_notl}No items{/urm_notl}' xalign .5 yoffset x52URM.scalePxInt(30)
        else:
            # Results
            viewport:
                xfill True
                yfill True
                mousewheel True
                draggable True
                scrollbars "vertical"

                use URM_table():
                    for i,var in enumerate(expandObjectVars[-1].children[objectPages.pageStartIndex:objectPages.pageEndIndex]):
                        use URM_tableRow(i, True):
                            hbox xsize colWidth[0] yalign .5:
                                text x52URM.scaleText(var.namePath[-1], 23) substitute False
                            hbox xsize colWidth[1] yalign .5:
                                if var.isExpandable:
                                    textbutton var.getButtonValue(23) substitute False action AddToSet(expandObjectVars, var)
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

screen URM_createVar():
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    default itemName = ''
    default itemVal = ''
    default overwrite = False
    default inputs = x52URM.InputGroup(
        [
            ('itemName', x52URM.Input(updateScreenVariable='itemName')),
            ('itemVal', x52URM.Input(updateScreenVariable='itemVal')),
        ],
        focusFirst=True,
        onSubmit=x52URM.CreateVar(
            varName=URMGetScreenVariable('itemName'),
            varVal=URMGetScreenVariable('itemVal'),
            varType=URMGetScreenVariable('valueTypes', URMGetScreenVariable('valueTypeIndex')),
            onSuccess=Hide('URM_createVar'),
            screenErrorVariable='errorMessage',
            overwrite=URMGetScreenVariable('overwrite'),
        ),
    )
    default errorMessage = None
    default valueTypes = ['string', 'int', 'float', 'boolean']
    default valueTypeIndex = 0

    on 'show' action [x52URM.Search.queryInput.Disable(),Function(inputs.focus)]
    key 'K_TAB' action inputs.NextInput()
    key 'shift_K_TAB' action inputs.PreviousInput()

    use x52URM_Dialog(title='{urm_notl}Create variable{/urm_notl}', closeAction=Hide('URM_createVar'), modal=True, icon='\ue146'):
        text "{urm_notl}Name:{/urm_notl}"
        button:
            xminimum x52URM.scalePxInt(450)
            key_events True
            action inputs.itemName.Enable()
            input value inputs.itemName
        null height 2
        use x52URM_checkbox(overwrite, 'Overwrite if exists', ToggleScreenVariable('overwrite', True, False))
        null height x52URM.scalePxInt(10)

        hbox:
            text "{urm_notl}Value type:{/urm_notl} " yalign .5
            textbutton valueTypes[valueTypeIndex] action SetScreenVariable('valueTypeIndex', (valueTypeIndex+1) % len(valueTypes))

        text "{urm_notl}Value:{/urm_notl}"
        if valueTypes[valueTypeIndex] == 'boolean':
            textbutton "[itemVal]" action ToggleScreenVariable('itemVal', True, False)
        else:
            button:
                xminimum x52URM.scalePxInt(450)
                key_events True
                action inputs.itemVal.Enable()
                input value inputs.itemVal

        if errorMessage != None:
            use x52URM_messagebar('error', errorMessage)

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            textbutton "{urm_notl}Add{/urm_notl}" sensitive bool(str(inputs.itemName)) style_suffix "buttonPrimary" action inputs.onSubmit
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_createVar')
