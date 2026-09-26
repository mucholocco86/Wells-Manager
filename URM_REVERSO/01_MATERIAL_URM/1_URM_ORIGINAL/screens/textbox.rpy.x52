
style URMSay_text is x52URM_text:
    alt None
style URMSay_frame is x52URM_default

style x52URM_textboxConfigBox:
    background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonBgDisabled, x52URM.Theme.colors.buttonPrimaryBgDisabled)
    padding (8, 8)

transform URM_textboxSettingFade:
    on show:
        alpha 0.0
        linear 0.2 alpha 1.0
    on hide:
        alpha 1.0
        linear 0.2 alpha 0.0

screen URM_say(who, what):
    style_prefix 'URMSay'

    vbox:
        xfill True
        yalign 1.0

        if who and x52URM.TextBox.Settings.whoShown:
            frame:
                if x52URM.TextBox.Settings.whoResizeBackground:
                    xsize x52URM.TextBox.whoWidth
                    xalign x52URM.TextBox.Settings.whoPosition
                else:
                    xfill True
                xpadding x52URM.TextBox.whoXPadding
                background x52URM.TextBox.whoBackground
                hbox xsize x52URM.TextBox.whoWidth xalign x52URM.TextBox.Settings.whoPosition:
                    text who id 'who'

        frame:
            if x52URM.TextBox.Settings.whatResizeBackground:
                xsize x52URM.TextBox.textWidth
                xalign x52URM.TextBox.Settings.whatPosition
            else:
                xfill True
            background x52URM.TextBox.whatBackground

            hbox xsize x52URM.TextBox.textWidth xalign x52URM.TextBox.Settings.whatPosition:
                spacing 20
                yminimum x52URM.TextBox.textHeight

                if x52URM.TextBox.Settings.sideImageShown and x52URM.TextBox.Settings.sideImagePos == 'left':
                    add x52URM.TextBox.sideImage

                frame:
                    xsize If(x52URM.TextBox.Settings.sideImageShown, x52URM.TextBox.textWidth-x52URM.TextBox.textHeight, x52URM.TextBox.textWidth)-(x52URM.TextBox.Settings.whatXPadding*2)
                    xpadding x52URM.TextBox.whatXPadding
                    text what id 'what'

                if x52URM.TextBox.Settings.sideImageShown and x52URM.TextBox.Settings.sideImagePos == 'right':
                    add x52URM.TextBox.sideImage


screen URM_textboxCustomizations():
    style_prefix "x52URM"
    default colWidth = [x52URM.scaleX(20), x52URM.scaleX(60)]
    default textboxPages = x52URM.Pages(len(x52URM.TextBox.Settings.store), itemsPerPage=20)

    hbox:
        spacing x52URM.scalePxInt(5)
        use x52URM_iconButton('\ue266', '{urm_notl}Add{/urm_notl}', action=Function(x52URM.TextBox.openCustomizer, beforeOpenAction=Hide('URM_main'), afterCloseAction=x52URM.Open()))
        use x52URM_checkbox(checked=x52URM.TextBox.enabled, text='{urm_notl}Enabled{/urm_notl}', action=ToggleField(x52URM.TextBox, 'enabled', True, False))
        if not x52URM.TextBox.enabled:
            text 'Custom textboxes are currently disabled, settings will not have any effect' yalign .5
    null height x52URM.scalePxInt(10)
    frame style_suffix "seperator" ysize x52URM.scalePxInt(2)

    if len(x52URM.TextBox.Settings.store) > 0:
        # PAGES
        fixed ysize x52URM.scalePxInt(50):
            hbox xalign .5 yoffset 4 spacing 2:
                use URM_pages(textboxPages)
            hbox xalign 1.0 yalign .5:
                text 'Customizations: {}'.format(len(x52URM.TextBox.Settings.store))
                null width x52URM.scalePxInt(10)

        use URM_tableRow(): # Headers
            label "{urm_notl}Character{/urm_notl}" xsize colWidth[0]

        viewport:
            xfill True
            yfill True
            mousewheel True
            draggable True
            scrollbars "vertical"

            # Results
            use URM_table():
                for i,charVarName in enumerate(list(x52URM.TextBox.Settings.store.keys())[textboxPages.pageStartIndex:textboxPages.pageEndIndex]):
                    use URM_tableRow(i, True):
                        hbox xsize colWidth[0] yalign .5:
                            if charVarName == 'None':
                                text '{urm_notl}Any{/urm_notl}'
                            elif x52URM.Characters.getByVarName(charVarName):
                                text x52URM.scaleText(x52URM.Characters.getByVarName(charVarName).fullName, 18)
                            else:
                                text x52URM.scaleText(charVarName, 18)

                        hbox xsize colWidth[1]:
                            hbox spacing 2:
                                use x52URM_iconButton('\ue3c9', '{urm_notl}Edit{/urm_notl}', action=Function(x52URM.TextBox.openCustomizer, charVarName=charVarName, beforeOpenAction=Hide('URM_main'), afterCloseAction=x52URM.Open()))
                                use x52URM_iconButton('\ue872', '{urm_notl}Remove{/urm_notl}', x52URM.Confirm('Are you sure you want to remove this customization?', Function(x52URM.TextBox.Settings.remove, charVarName), title='Remove textbox customization'))
    
    else:
        vbox:
            yoffset x52URM.scaleY(1.5)
            xalign 0.5
            label "{urm_notl}There are no customizations yet{/urm_notl}" xalign 0.5
            null height x52URM.scalePxInt(15)
            text "Here you can customize the textbox for each or all characters" xalign .5
            text "Use the add button a the left top to start customizing" xalign .5


screen URM_textboxCustomizer(charVarName=None):
    layer 'x52Overlay'
    style_prefix "x52URM"
    modal True

    on 'show' action Function(x52URM.TextBox.Settings.enableTemp, charVarName=charVarName)

    use x52URM_Dialog(title='{urm_notl}Textbox customizer{/urm_notl}', closeAction=Function(x52URM.TextBox.closeCustomizer), icon='\ue0b7'):
        vpgrid: # We need a vpgrid, because a viewport takes up all available height
            cols 1
            draggable True
            mousewheel True
            scrollbars "vertical"
            
            vbox spacing x52URM.scalePxInt(10):
                hbox spacing x52URM.scalePxInt(10):
                    # Character picker
                    vbox:
                        hbox:
                            text '\ue87c' style_suffix 'icon'
                            label '{urm_notl}Character{/urm_notl}'
                        hbox spacing 2:
                            if x52URM.TextBox.previewCharacter == x52URM.TextBox.demoCharacter:
                                text '{urm_notl}Any{/urm_notl}' yalign .5
                            elif x52URM.Characters.getByVarName(x52URM.TextBox.previewCharacterVarName):
                                text '{} ({})'.format(x52URM.Characters.getByVarName(x52URM.TextBox.previewCharacterVarName).displayName, x52URM.Characters.getByVarName(x52URM.TextBox.previewCharacterVarName).varName) substitute False yalign .5
                            else:
                                text str(x52URM.TextBox.previewCharacterVarName) yalign .5
                            textbutton '\ue3c9' style_suffix 'icon_button' action Show('URM_textboxCharacterPicker')
                            textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox, 'previewCharacter', None) sensitive (x52URM.TextBox.previewCharacter != x52URM.TextBox.demoCharacter)
                            textbutton '\ueb8b' style_suffix 'icon_button' action x52URM.Confirm('Select a character to apply the customization to.\n"Any" is applied to any character that doensn\'t have it\'s own customizations.', title='{urm_notl}Character selection{/urm_notl}')

                    vbox:
                        label 'Mode'
                        hbox:
                            textbutton If(x52URM.TextBox.Settings.customSayScreen, '{urm_notl}Full{/urm_notl}', '{urm_notl}Light{/urm_notl}') action ToggleField(x52URM.TextBox.Settings, 'customSayScreen', True, False)
                            textbutton '\ueb8b' style_suffix 'icon_button' action x52URM.Confirm('{b}Full{/b} = Use a fully customizable textbox\n{b}Light{/b} = Use the original textbox (some customization may not work)', title='{urm_notl}Textbox mode{/urm_notl}') yalign .5

                # Namebox settings
                vbox:
                    hbox:
                        text '\ue0b7' style_suffix 'icon'
                        label '{urm_notl}Namebox{/urm_notl}'
                        if x52URM.TextBox.Settings.customSayScreen:
                            use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoShown, text='{urm_notl}Enabled{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoShown', True, False))
                        
                    showif not x52URM.TextBox.Settings.customSayScreen or x52URM.TextBox.Settings.whoShown:
                        hbox spacing x52URM.scalePxInt(15) at URM_textboxSettingFade:
                            vbox:
                                text '{urm_notl}Text{/urm_notl}'
                                frame style_suffix 'textboxConfigBox':
                                    has vbox
                                    hbox spacing x52URM.scalePxInt(10):
                                        vbox spacing 2:
                                            hbox: # Bold
                                                use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoBold, text='{urm_notl}Bold{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoBold', True, False))
                                                textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoBold', None) sensitive isinstance(x52URM.TextBox.Settings.whoBold, bool) yalign .5
                                            hbox: # Italic
                                                use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoItalic, text='{urm_notl}Italic{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoItalic', True, False))
                                                textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoItalic', None) sensitive isinstance(x52URM.TextBox.Settings.whoItalic, bool) yalign .5
                                            hbox: # Color
                                                use x52URM_iconButton('\ue40a', '{urm_notl}Color{/urm_notl}', Show('URM_colorpicker', callback=x52URM.TextBoxSettingCallback('whoColor'), onClose=Hide('URM_colorpicker'), defaultColor=x52URM.TextBox.Settings.whoColor))
                                                if x52URM.TextBox.Settings.whoColor:
                                                    frame yalign .5:
                                                        background x52URM.TextBox.Settings.whoColor
                                                        text ''
                                                textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoColor', None) sensitive bool(x52URM.TextBox.Settings.whoColor) yalign .5
                                        vbox spacing 2:
                                            if x52URM.TextBox.Settings.customSayScreen:
                                                text '{size=-4}{urm_notl}Alignment{/urm_notl}{/size}'
                                                hbox: # Alignment
                                                    textbutton '\ue236' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoXAlign', 0.0)
                                                    textbutton '\ue234' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoXAlign', 0.5)
                                                    textbutton '\ue237' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoXAlign', 1.0)
                                            text '{size=-4}{urm_notl}Size{/urm_notl}{/size}'
                                            hbox: # Size
                                                textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoSize', x52URM.max(x52URM.TextBox.Settings.whoSize-2, 12))
                                                text '[x52URM.TextBox.Settings.whoSize]' yalign .5
                                                textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoSize', x52URM.min(x52URM.TextBox.Settings.whoSize+2, 100))
                                                textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoSize', x52URM.TextBoxSettings.defaultValues['whoSize'])
                                    hbox spacing x52URM.scalePxInt(5): # Change font
                                        use x52URM_iconButton('\ue165', '{urm_notl}Font{/urm_notl}', action=Show('URM_textboxFontPicker', settingName='whoFont', defaultSelected=x52URM.TextBox.Settings.whoFont))
                                        if not x52URM.TextBox.Settings.customSayScreen:
                                            textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoFont', None) sensitive (x52URM.TextBox.Settings.whoFont != None) yalign .5
                                        if x52URM.TextBox.Settings.customSayScreen or x52URM.TextBox.Settings.whoFont != None:
                                            text (x52URM.TextBox.Settings.whoFont or list(x52URM.TextBoxSettings.fontOptions.keys())[0]) font x52URM.TextBox.whoFont yalign .5

                            vbox:
                                text '{urm_notl}Border{/urm_notl}'
                                frame style_suffix 'textboxConfigBox':
                                    has vbox
                                    spacing 2
                                    use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoOutlinesEnabled, text='{urm_notl}Enabled{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoOutlinesEnabled', True, False))
                                    hbox: # Color
                                        use x52URM_iconButton('\ue40a', '{urm_notl}Color{/urm_notl}', Show('URM_colorpicker', callback=x52URM.TextBoxSettingCallback('whoOutlinesColor'), onClose=Hide('URM_colorpicker'), defaultColor=x52URM.TextBox.Settings.whoOutlinesColor))
                                        if x52URM.TextBox.Settings.whoOutlinesColor:
                                            frame yalign .5:
                                                background x52URM.TextBox.Settings.whoOutlinesColor
                                                text ''
                                    text '{size=-4}{urm_notl}Size{/urm_notl}{/size}'
                                    hbox: # Size
                                        textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoOutlinesWidth', x52URM.max(x52URM.TextBox.Settings.whoOutlinesWidth-1, 1))
                                        text '[x52URM.TextBox.Settings.whoOutlinesWidth]' yalign .5
                                        textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoOutlinesWidth', x52URM.min(x52URM.TextBox.Settings.whoOutlinesWidth+1, 10))
                                        textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoOutlinesWidth', x52URM.TextBoxSettings.defaultValues['whoOutlinesWidth'])

                            showif x52URM.TextBox.Settings.customSayScreen:
                                vbox at URM_textboxSettingFade:
                                    text '{urm_notl}Background{/urm_notl}'
                                    frame style_suffix 'textboxConfigBox':
                                        has vbox
                                        spacing 2
                                        use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoBackgroundEnabled, text='{urm_notl}Enabled{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoBackgroundEnabled', True, False))
                                        hbox: # Color
                                            use x52URM_iconButton('\ue40a', '{urm_notl}Color{/urm_notl}', Show('URM_colorpicker', callback=x52URM.TextBoxSettingCallback('whoBackground'), onClose=Hide('URM_colorpicker'), defaultColor=x52URM.TextBox.Settings.whoBackground))
                                            frame yalign .5:
                                                background x52URM.TextBox.Settings.whoBackground
                                                text ''
                                        use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoBackgroundGradient, text='{urm_notl}Gradient{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoBackgroundGradient', True, False))
                                        hbox: # Character color
                                            use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoBackgroundCharacterColor, text='{urm_notl}Character color{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoBackgroundCharacterColor', True, False))
                                            textbutton '\ueb8b' style_suffix 'icon_button' action x52URM.Confirm('Use the character\'s name color (when available)\n{size=-5}{alpha=.9}Note: This still uses the transparency/alpha from the color you\'ve set{/alpha}{/size}', title='Character color') yalign .5

                            showif x52URM.TextBox.Settings.customSayScreen:
                                vbox at URM_textboxSettingFade:
                                    text '{urm_notl}Size/position{/urm_notl}'
                                    frame style_suffix 'textboxConfigBox':
                                        has vbox
                                        spacing 2
                                        vbox:
                                            text '{size=-4}{urm_notl}Height{/urm_notl}{/size}'
                                            hbox: # Height
                                                textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoHeight', x52URM.max(x52URM.TextBox.Settings.whoHeight-10, 50))
                                                text '[x52URM.TextBox.Settings.whoHeight]' yalign .5
                                                textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoHeight', x52URM.min(x52URM.TextBox.Settings.whoHeight+10, 450))
                                                textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoHeight', x52URM.TextBoxSettings.defaultValues['whoHeight'])
                                        vbox:
                                            text '{size=-4}{urm_notl}Width{/urm_notl}{/size}'
                                            hbox: # Width
                                                textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoWidth', x52URM.max(x52URM.TextBox.Settings.whoWidth-5, 40))
                                                text '[x52URM.TextBox.Settings.whoWidth]%' yalign .5
                                                textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoWidth', x52URM.min(x52URM.TextBox.Settings.whoWidth+5, 100))
                                                textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoWidth', x52URM.TextBoxSettings.defaultValues['whoWidth'])
                                        vbox:
                                            text '{size=-4}{urm_notl}Position{/urm_notl}{/size}'
                                            hbox: # Position
                                                textbutton '\ue5c4' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoPosition', x52URM.max(x52URM.TextBox.Settings.whoPosition-0.05, 0.0))
                                                text '{}%'.format(int(x52URM.TextBox.Settings.whoPosition*100)) yalign .5
                                                textbutton '\ue5c8' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoPosition', x52URM.min(x52URM.TextBox.Settings.whoPosition+0.05, 1.0))
                                                textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whoPosition', x52URM.TextBoxSettings.defaultValues['whoPosition'])
                                        use x52URM_checkbox(checked=x52URM.TextBox.Settings.whoResizeBackground, text='{urm_notl}Resize background{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whoResizeBackground', True, False))

                # Textbox settings
                vbox:
                    hbox:
                        text '\uf086' style_suffix 'icon'
                        label 'Text'

                    hbox spacing x52URM.scalePxInt(15):
                        vbox:
                            text '{urm_notl}Text{/urm_notl}'
                            frame style_suffix 'textboxConfigBox':
                                has vbox
                                spacing 2
                                hbox spacing x52URM.scalePxInt(10):
                                    vbox spacing 2:
                                        hbox: # Bold
                                            use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatBold, text='{urm_notl}Bold{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatBold', True, False))
                                            textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatBold', None) sensitive isinstance(x52URM.TextBox.Settings.whatBold, bool) yalign .5
                                        hbox: # Italic
                                            use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatItalic, text='{urm_notl}Italic{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatItalic', True, False))
                                            textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatItalic', None) sensitive isinstance(x52URM.TextBox.Settings.whatItalic, bool) yalign .5
                                        hbox: # Color
                                            use x52URM_iconButton('\ue40a', '{urm_notl}Color{/urm_notl}', Show('URM_colorpicker', callback=x52URM.TextBoxSettingCallback('whatColor'), onClose=Hide('URM_colorpicker'), defaultColor=x52URM.TextBox.Settings.whatColor))
                                            if x52URM.TextBox.Settings.whatColor:
                                                frame yalign .5:
                                                    background x52URM.TextBox.Settings.whatColor
                                                    text ''
                                            textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatColor', None) sensitive bool(x52URM.TextBox.Settings.whatColor) yalign .5
                                    vbox spacing 2:
                                        if x52URM.TextBox.Settings.customSayScreen:
                                            text '{size=-4}{urm_notl}Alignment{/urm_notl}{/size}'
                                            hbox: # Alignment
                                                textbutton '\ue236' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatAlign', 0.0)
                                                textbutton '\ue234' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatAlign', 0.5)
                                                textbutton '\ue237' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatAlign', 1.0)
                                        text '{size=-4}{urm_notl}Size{/urm_notl}{/size}'
                                        hbox: # Size
                                            textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatSize', x52URM.max(x52URM.TextBox.Settings.whatSize-2, 12))
                                            text '[x52URM.TextBox.Settings.whatSize]' yalign .5
                                            textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatSize', x52URM.min(x52URM.TextBox.Settings.whatSize+2, 100))
                                            textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatSize', x52URM.TextBoxSettings.defaultValues['whatSize'])
                                hbox: # Character color
                                    use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatColorFromCharacter, text='{urm_notl}Character color{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatColorFromCharacter', True, False))
                                    textbutton '\ueb8b' style_suffix 'icon_button' action x52URM.Confirm('Use the character\'s name color (when available)\n{size=-5}{alpha=.9}Note: This still uses the transparency/alpha from the color you\'ve set{/alpha}{/size}', title='Character color') yalign .5
                                hbox spacing x52URM.scalePxInt(5): # Change font
                                    use x52URM_iconButton('\ue165', '{urm_notl}Font{/urm_notl}', action=Show('URM_textboxFontPicker', settingName='whatFont', defaultSelected=x52URM.TextBox.Settings.whatFont))
                                    if not x52URM.TextBox.Settings.customSayScreen:
                                        textbutton '\ue872' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatFont', None) sensitive (x52URM.TextBox.Settings.whatFont != None) yalign .5
                                    if x52URM.TextBox.Settings.customSayScreen or x52URM.TextBox.Settings.whatFont != None:
                                        text (x52URM.TextBox.Settings.whatFont or list(x52URM.TextBoxSettings.fontOptions.keys())[0]) font x52URM.TextBox.whatFont yalign .5
                        
                        vbox:
                            text '{urm_notl}Border{/urm_notl}'
                            frame style_suffix 'textboxConfigBox':
                                has vbox
                                spacing 2
                                use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatOutlinesEnabled, text='{urm_notl}Enabled{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatOutlinesEnabled', True, False))
                                hbox: # Color
                                    use x52URM_iconButton('\ue40a', '{urm_notl}Color{/urm_notl}', Show('URM_colorpicker', callback=x52URM.TextBoxSettingCallback('whatOutlinesColor'), onClose=Hide('URM_colorpicker'), defaultColor=x52URM.TextBox.Settings.whatOutlinesColor))
                                    if x52URM.TextBox.Settings.whatOutlinesColor:
                                        frame yalign .5:
                                            background x52URM.TextBox.Settings.whatOutlinesColor
                                            text ''
                                text '{size=-4}{urm_notl}Size{/urm_notl}{/size}'
                                hbox: # Size
                                    textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatOutlinesWidth', x52URM.max(x52URM.TextBox.Settings.whatOutlinesWidth-1, 1))
                                    text '[x52URM.TextBox.Settings.whatOutlinesWidth]' yalign .5
                                    textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatOutlinesWidth', x52URM.min(x52URM.TextBox.Settings.whatOutlinesWidth+1, 10))
                                    textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatOutlinesWidth', x52URM.TextBoxSettings.defaultValues['whatOutlinesWidth'])
                        
                        showif x52URM.TextBox.Settings.customSayScreen:
                            vbox at URM_textboxSettingFade:
                                text '{urm_notl}Background{/urm_notl}'
                                frame style_suffix 'textboxConfigBox':
                                    has vbox
                                    spacing 2
                                    use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatBackgroundEnabled, text='{urm_notl}Enabled{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatBackgroundEnabled', True, False))
                                    hbox: # Color
                                        use x52URM_iconButton('\ue40a', '{urm_notl}Color{/urm_notl}', Show('URM_colorpicker', callback=x52URM.TextBoxSettingCallback('whatBackground'), onClose=Hide('URM_colorpicker'), defaultColor=x52URM.TextBox.Settings.whatBackground))
                                        frame yalign .5:
                                            background Solid(x52URM.TextBox.Settings.whatBackground)
                                            text ''
                                    use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatBackgroundGradient, text='{urm_notl}Gradient{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatBackgroundGradient', True, False))
                                    hbox: # Character color
                                        use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatBackgroundCharacterColor, text='{urm_notl}Character color{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatBackgroundCharacterColor', True, False))
                                        textbutton '\ueb8b' style_suffix 'icon_button' action x52URM.Confirm('Use the character\'s name color (when available)\n{size=-5}{alpha=.9}Note: This still uses the transparency/alpha from the color you\'ve set{/alpha}{/size}', title='Character color') yalign .5

                        showif x52URM.TextBox.Settings.customSayScreen:
                            vbox at URM_textboxSettingFade:
                                text '{urm_notl}Size/position{/urm_notl}'
                                frame style_suffix 'textboxConfigBox':
                                    has vbox
                                    spacing 2
                                    vbox:
                                        text '{size=-4}{urm_notl}Height{/urm_notl}{/size}'
                                        hbox: # Height
                                            textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatHeight', x52URM.max(x52URM.TextBox.Settings.whatHeight-10, 50))
                                            text '[x52URM.TextBox.Settings.whatHeight]' yalign .5
                                            textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatHeight', x52URM.min(x52URM.TextBox.Settings.whatHeight+10, 450))
                                            textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatHeight', x52URM.TextBoxSettings.defaultValues['whatHeight'])
                                    vbox:
                                        text '{size=-4}{urm_notl}Width{/urm_notl}{/size}'
                                        hbox: # Width
                                            textbutton '\ue15b' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatWidth', x52URM.max(x52URM.TextBox.Settings.whatWidth-5, 40))
                                            text '[x52URM.TextBox.Settings.whatWidth]%' yalign .5
                                            textbutton '\ue145' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatWidth', x52URM.min(x52URM.TextBox.Settings.whatWidth+5, 100))
                                            textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatWidth', x52URM.TextBoxSettings.defaultValues['whatWidth'])
                                    vbox:
                                        text '{size=-4}{urm_notl}Position{/urm_notl}{/size}'
                                        hbox: # Position
                                            textbutton '\ue5c4' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatPosition', x52URM.max(x52URM.TextBox.Settings.whatPosition-0.05, 0.0))
                                            text '{}%'.format(int(x52URM.TextBox.Settings.whatPosition*100)) yalign .5
                                            textbutton '\ue5c8' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatPosition', x52URM.min(x52URM.TextBox.Settings.whatPosition+0.05, 1.0))
                                            textbutton '\uf053' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'whatPosition', x52URM.TextBoxSettings.defaultValues['whatPosition'])
                                    use x52URM_checkbox(checked=x52URM.TextBox.Settings.whatResizeBackground, text='{urm_notl}Resize background{/urm_notl}', action=ToggleField(x52URM.TextBox.Settings, 'whatResizeBackground', True, False))

                # Sideimage settings
                showif x52URM.TextBox.Settings.customSayScreen:
                    vbox at URM_textboxSettingFade:
                        hbox:
                            text '\ue416' style_suffix 'icon'
                            label '{urm_notl}Side image{/urm_notl}'
                            use x52URM_checkbox(checked=x52URM.TextBox.Settings.sideImageShown, text='Enabled', action=ToggleField(x52URM.TextBox.Settings, 'sideImageShown', True, False))
                        
                        showif x52URM.TextBox.Settings.sideImageShown:
                            hbox at URM_textboxSettingFade:
                                text '{urm_notl}Position: {/urm_notl}' yalign .5
                                hbox:
                                    textbutton '\ue00d' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'sideImagePos', 'left')
                                    textbutton '\ue010' style_suffix 'icon_button' action SetField(x52URM.TextBox.Settings, 'sideImagePos', 'right')

        hbox:
            xalign 1.0
            spacing x52URM.scalePxInt(10)
            yoffset x52URM.scalePxInt(10)

            use x52URM_iconButton('\ueb8b', '{urm_notl}Help{/urm_notl}', Show('URM_textboxCustomizerHelp'))
            use x52URM_iconButton('\ue8f4', '{urm_notl}Preview{/urm_notl}', Jump('URM_textboxCustomizer'))
            use x52URM_iconButton('\ue86c', '{urm_notl}Apply{/urm_notl}', Function(x52URM.TextBox.closeCustomizer, save=True))
            use x52URM_iconButton('\uf230', '{urm_notl}Cancel{/urm_notl}', Function(x52URM.TextBox.closeCustomizer))


screen URM_textboxCustomizerHelp():
    layer 'x52Overlay'
    style_prefix "x52URM"

    use x52URM_Dialog(title='{urm_notl}Textbox customizer{/urm_notl}', closeAction=Hide('URM_textboxCustomizerHelp'), modal=True, icon='\ue88e'):
        text 'This feature enabled you to customize the textbox displaying the game\'s dialogue.\nWhen changing settings, some will show immediately and for some you\'ll have to press the Preview button.'
        null height x52URM.scalePxInt(10)
        label '{urm_notl}Legend{/urm_notl}'
        hbox:
            text '\ue872' style_suffix 'icon'
            text 'Erase the value (use the game\'s value)'
        hbox:
            text '\uf053' style_suffix 'icon'
            text 'Reset value (back to initial value)'
        hbox:
            text '\ue909' style_suffix 'icon'
            text 'Using the game\'s value'
        hbox:
            text '\ue834' style_suffix 'icon'
            text '{urm_notl}Enabled{/urm_notl}'
        hbox:
            text '\ue835' style_suffix 'icon'
            text '{urm_notl}Disabled{/urm_notl}'


screen URM_textboxCharacterPicker():
    layer 'x52Overlay'
    style_prefix "x52URM"
    default charFilterInput = x52URM.Input(autoFocus=True)

    use x52URM_Dialog(title='Found '+str(len(x52URM.Characters.all))+' characters', closeAction=Hide('URM_textboxCharacterPicker'), modal=True, icon='\ue853'):
        text '{urm_notl}Selecter a character{/urm_notl}'

        hbox:
            spacing 5
            text "{urm_notl}Filter: {/urm_notl}" yalign .5
            button:
                xminimum x52URM.scalePxInt(350)
                key_events True
                action charFilterInput.Enable()
                input value charFilterInput

        viewport:
            ysize x52URM.scalePxInt(250)
            xsize x52URM.scalePxInt(450)
            draggable True
            mousewheel True
            scrollbars "vertical"

            vbox:
                for char in x52URM.Characters.all:
                    if char.match(str(charFilterInput)):
                        textbutton char.fullName substitute False xfill True action [Hide('URM_textboxCharacterPicker'),SetField(x52URM.TextBox, 'previewCharacter', char.varName)]


screen URM_textboxFontPicker(settingName, defaultSelected=None):
    layer 'x52Overlay'
    style_prefix "x52URM"
    default selectedFont = (defaultSelected or list(x52URM.TextBoxSettings.fontOptions.keys())[0])
    default fontSize = 30
    
    use x52URM_Dialog(title='{urm_notl}Pick a font{/urm_notl}', closeAction=Hide('URM_textboxFontPicker'), modal=True, icon='\ue165'):
        hbox spacing x52URM.scalePxInt(20):
            vbox:
                label '{urm_notl}Available fonts{/urm_notl}'
                for name,fontFile in x52URM.TextBoxSettings.fontOptions.items():
                    if renpy.loadable(fontFile):
                        textbutton name text_font fontFile action SetScreenVariable('selectedFont', name)

            vbox:
                label '{urm_notl}Preview{/urm_notl}'
                hbox:
                    text '{urm_notl}Fontsize: [fontSize]{/urm_notl}' yalign .5
                    textbutton '\ue15b' style_suffix 'icon_button' action SetScreenVariable('fontSize', x52URM.max(fontSize-2, 12))
                    textbutton '\ue145' style_suffix 'icon_button' action SetScreenVariable('fontSize', x52URM.min(fontSize+2, 60))
                null height x52URM.scalePxInt(20)
                text "Here's some example text to show you this font." font x52URM.TextBoxSettings.fontOptions[selectedFont] size fontSize
                text "And also some bold text to show." bold True font x52URM.TextBoxSettings.fontOptions[selectedFont] size fontSize
                text "Also some italic while we're at it" italic True font x52URM.TextBoxSettings.fontOptions[selectedFont] size fontSize

        hbox:
            spacing x52URM.scalePxInt(10)
            xalign 1.0
            use x52URM_iconButton('\ue86c', '{urm_notl}Select{/urm_notl}', action=[SetField(x52URM.TextBox.Settings, settingName, selectedFont),Hide('URM_textboxFontPicker')])
            use x52URM_iconButton('\uf230', '{urm_notl}Cancel{/urm_notl}', action=Hide('URM_textboxFontPicker'))


label URM_textboxCustomizer(charVarName=None):
    show screen URM_textboxCustomizer (charVarName)
    x52URM.TextBox.previewCharacter "Here's some text for testing purposes...\nAlso another line of text to fill up this space"
    return

label URM_textboxCustomizer_return:
    return
