
screen URM_gamesaves():
    style_prefix 'x52URM'
    default slotRegEx = '([0-9]+|quick)-([0-9]+)'

    hbox:
        vbox xsize x52URM.scaleX(22.8):
            hbox xsize x52URM.scaleX(22.8):
                label '{urm_notl}Quick resume{/urm_notl}' yalign .5
                textbutton "\ueb8b" style_suffix "icon_button" xalign 1.0 hovered x52URM.Tooltip("Explain quick resume") unhovered x52URM.Tooltip() action x52URM.Confirm("""The game will immediately load this save after starting the game\nThis skips the title screen and menu, you're directly back in the game\n\n{b}IMPORTANT:{/b} This save will be deleted after it has been loaded""", title='Quick resume')
            use URM_gamesaves_button('_reload-1')

            null height x52URM.scalePxInt(10)

            label '{urm_notl}Newest save{/urm_notl}'
            use URM_gamesaves_button(renpy.newest_slot(slotRegEx))

        null width x52URM.scalePxInt(10)
        frame style_suffix "vseperator" xsize x52URM.scalePxInt(2)
        null width x52URM.scalePxInt(10)

        vbox:
            fixed ysize x52URM.scalePxInt(45):
                hbox:
                    text x52URM.Gamesaves.pageName yalign .5 substitute False style_suffix 'label_text'
                    null width x52URM.scalePxInt(10)
                    textbutton "\ue9a2" style_suffix "icon_button" xalign 1.0 hovered x52URM.Tooltip("{urm_notl}Rename page{/urm_notl}") unhovered x52URM.Tooltip() action Show('URM_gamesaves_pagename')

                # PAGES
                hbox xalign 1.0:
                    textbutton "\ue5dc" style_suffix 'icon_button' sensitive (x52URM.Gamesaves.page != 1) action SetField(x52URM.Gamesaves, 'page', 1) yalign .5 hovered x52URM.Tooltip('Go to first page') unhovered x52URM.Tooltip()
                    textbutton "\ue408" style_suffix 'icon_button' sensitive (x52URM.Gamesaves.page != x52URM.Gamesaves.prevPage) action SetField(x52URM.Gamesaves, 'page', x52URM.Gamesaves.prevPage) yalign .5 hovered x52URM.Tooltip('Go to previous page') unhovered x52URM.Tooltip()

                    textbutton 'A' sensitive ('auto' != x52URM.Gamesaves.page) action SetField(x52URM.Gamesaves, 'page', 'auto') hovered x52URM.Tooltip('Go to auto save page') unhovered x52URM.Tooltip()
                    textbutton 'Q' sensitive ('quick' != x52URM.Gamesaves.page) action SetField(x52URM.Gamesaves, 'page', 'quick') hovered x52URM.Tooltip('Go to quick save page') unhovered x52URM.Tooltip()
                    for page in x52URM.Gamesaves.pageRange:
                        textbutton If(page<10, '0[page]', '[page]') sensitive (page != x52URM.Gamesaves.page) action SetField(x52URM.Gamesaves, 'page', page)

                    textbutton "\ue409" style_suffix 'icon_button' action SetField(x52URM.Gamesaves, 'page', x52URM.Gamesaves.nextPage) yalign .5 hovered x52URM.Tooltip('Go to next page') unhovered x52URM.Tooltip()
                    textbutton "\uf045" style_suffix 'icon_button' action Show('URM_gamesaves_pagenumber') yalign .5 hovered x52URM.Tooltip('Enter page number') unhovered x52URM.Tooltip()

            frame style_suffix "seperator" ysize x52URM.scalePxInt(2)
            null height x52URM.scalePxInt(10)
            
            vpgrid:
                xfill True yfill True
                cols 3
                mousewheel True
                draggable True
                scrollbars "vertical"
                spacing x52URM.scalePxInt(10)

                for position in range(1,10):
                    use URM_gamesaves_button('{}-{}'.format(x52URM.Gamesaves.page, position))


screen URM_gamesaves_button(slot):
    default thumbnailScale = 22.8

    vbox:
        button:
            style_suffix 'thumbnailButton'
            xsize x52URM.scaleX(thumbnailScale) ysize x52URM.scaleY(thumbnailScale)
            if renpy.can_load(slot):
                action Function(x52URM.Gamesaves.load, slot)
                add x52URM.GameSavesClass.SlotScreenshot(slot) xalign .5 yalign .5
                label x52URM.Gamesaves.slotTime(slot) xalign .5 text_outlines [(absolute(2), x52URM.Theme.background, 0, 0)]
                text x52URM.Gamesaves.slotName(slot) xalign .5 yalign 1.0 substitute False text_align .5 outlines [(absolute(2), x52URM.Theme.background, 0, 0)]
            else:
                action Function(x52URM.Gamesaves.save, slot)
                text 'Empty' xalign .5 yalign .5

        null height 2
        hbox xsize x52URM.scaleX(thumbnailScale):
            hbox spacing 2:
                textbutton "\ue2c7" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Load game{/urm_notl}') unhovered x52URM.Tooltip() action If(renpy.can_load(slot), Function(x52URM.Gamesaves.load, slot), None)
                textbutton "\ue161" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Save game{/urm_notl}') unhovered x52URM.Tooltip() action Function(x52URM.Gamesaves.save, slot)

            hbox xalign 1.0 spacing 2:
                textbutton "\ue89f" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Move save{/urm_notl}') unhovered x52URM.Tooltip() action If(renpy.can_load(slot), Function(x52URM.Gamesaves.move, slot), None)
                textbutton "\ue173" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Copy save{/urm_notl}') unhovered x52URM.Tooltip() action If(renpy.can_load(slot), Function(x52URM.Gamesaves.copy, slot), None)
                textbutton "\ue872" style_suffix "icon_button" hovered x52URM.Tooltip('{urm_notl}Delete save{/urm_notl}') unhovered x52URM.Tooltip() action If(renpy.can_load(slot), Function(x52URM.Gamesaves.delete, slot), None)


screen URM_gamesaves_selectslot(defaultPage, defaultPosition, callback, confirmButtonText='{urm_notl}OK{/urm_notl}'):
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    default inputs = x52URM.InputGroup([
            ('page', x52URM.Input(text=defaultPage)),
            ('position', x52URM.Input(text=defaultPosition)),
        ],
        focusFirst=True,
        onSubmit=[Function(callback, x52URM.GetScreenInput('page', 'inputs'), x52URM.GetScreenInput('position', 'inputs')),Hide('URM_gamesaves_selectslot')],
    )

    key 'K_TAB' action inputs.NextInput()
    key 'shift_K_TAB' action inputs.PreviousInput()

    use x52URM_Dialog(title='{urm_notl}Select save slot{/urm_notl}', closeAction=Hide('URM_gamesaves_selectslot'), modal=True, icon='\ue161'):
        text "Page:"
        button:
            xminimum x52URM.scalePxInt(450)
            key_events True
            action inputs.page.Enable()
            input value inputs.page allow '0123456789'

        text "Position:"
        button:
            xminimum x52URM.scalePxInt(450)
            key_events True
            action inputs.position.Enable()
            input value inputs.position allow '123456789' length 1

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            textbutton confirmButtonText style_suffix "buttonPrimary" action inputs.onSubmit
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_gamesaves_selectslot')


screen URM_gamesaves_pagenumber():
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    default pageInput = x52URM.Input(text=str(x52URM.Gamesaves.page), autoFocus=True, onEnter=[x52URM.Gamesaves.SetPage(x52URM.GetScreenInput('pageInput')),Hide('URM_gamesaves_pagenumber')])

    use x52URM_Dialog(title='{urm_notl}Enter a page number{/urm_notl}', closeAction=Hide('URM_gamesaves_pagenumber'), modal=True, icon='\uf045'):
        text "Page:"
        button:
            xminimum x52URM.scalePxInt(350)
            key_events True
            action pageInput.Enable()
            input value pageInput allow '0123456789'

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            textbutton '{urm_notl}Open{/urm_notl}' style_suffix "buttonPrimary" action pageInput.onEnter
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_gamesaves_pagenumber')


screen URM_gamesaves_pagename():
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    default pageNameInput = x52URM.Input(text=x52URM.Gamesaves.pageName, autoFocus=True, onEnter=[x52URM.Gamesaves.SetPageName(x52URM.GetScreenInput('pageNameInput')),Hide('URM_gamesaves_pagename')])

    use x52URM_Dialog(title='{urm_notl}Change page name{/urm_notl}', closeAction=Hide('URM_gamesaves_pagename'), modal=True, icon='\ue9a2'):
        text "{urm_notl}Page name:{/urm_notl}"
        button:
            xminimum x52URM.scalePxInt(350)
            key_events True
            action pageNameInput.Enable()
            input value pageNameInput length 50

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            textbutton '{urm_notl}Change{/urm_notl}' style_suffix "buttonPrimary" action pageNameInput.onEnter
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_gamesaves_pagename')

screen URM_gamesaves_savename(callback):
    layer 'x52Overlay'
    style_prefix "x52URM"
    
    default inputSaveName = x52URM.Input(autoFocus=True, onEnter=[Function(callback, x52URM.GetScreenInput('inputSaveName')),Hide('URM_gamesaves_savename')])

    use x52URM_Dialog(title='{urm_notl}Save description{/urm_notl}', closeAction=Hide('URM_gamesaves_savename'), modal=True, icon='\ue161'):
        text "{urm_notl}Save name:{/urm_notl}"
        button:
            xminimum x52URM.scalePxInt(350)
            key_events True
            action inputSaveName.Enable()
            input value inputSaveName length 150

        hbox:
            yoffset x52URM.scalePxInt(15)
            align (1.0,1.0)
            textbutton '{urm_notl}Save{/urm_notl}' style_suffix "buttonPrimary" action inputSaveName.onEnter
            null width x52URM.scalePxInt(10)
            textbutton "{urm_notl}Cancel{/urm_notl}" action Hide('URM_gamesaves_savename')
