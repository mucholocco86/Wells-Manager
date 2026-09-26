################################################################################
## MODULE: wells_saveload.rpy (PARTE 1: TELA DE SALVAMENTO EXCLUSIVA)
################################################################################

screen wells_custom_save():
    modal True
    zorder 199 
    tag menu
    add Solid("#000000aa")

    $ current_page_num = int(persistent._file_page) if isinstance(persistent._file_page, (int, float)) or (isinstance(persistent._file_page, basestring if renpy.version_tuple < (8, 0, 0) else str) and persistent._file_page.isdigit()) else 1
    $ wells_prev10_page = current_page_num - 10
    if wells_prev10_page < 1:
        $ wells_prev10_page = 1

    frame:
        xalign 0.5 yalign 0.4
        background Frame("wells/gui/frame_menu.png", 10, 10)
        xsize 1450 ysize 820 padding (50, 40)

        fixed:
            xfill True yfill True

            frame:
                xpos 0 ypos 10
                background Frame("wells/gui/label_frame.png", 10, 10)
                padding (30, 8)
                text "SALVAR" size 32 color "#ff4444"

            hbox:
                xalign 0.5 ypos 10 
                spacing 12

                # Atalho para Salvamento Automático (A)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_auto_idle.png"
                    hover "wells/gui/button/p_auto_hover.png"
                    selected_idle "wells/gui/button/p_auto_hover.png" # Mantém aceso se for a página atual
                    action FilePage("auto")

                # Atalho para Salvamento Rápido (Q)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_quick_idle.png"
                    hover "wells/gui/button/p_quick_hover.png"
                    selected_idle "wells/gui/button/p_quick_hover.png" # Mantém aceso se for a página atual
                    action FilePage("quick")

                # Botão Voltar 10 Páginas (<<<)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_menos10_idle.png"
                    hover "wells/gui/button/p_menos10_hover.png"
                    action FilePage(wells_prev10_page)

                # Botão Voltar 1 Página (<<)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_voltar_idle.png"
                    hover "wells/gui/button/p_voltar_hover.png"
                    action FilePagePrevious()

                # [MANTIDO] Contador de Página Centralizado (Caixa de texto estilizada que mostra o número)
                frame:
                    yalign 0.5
                    background Frame("wells/gui/button/Button-hover.png", 5, 5)
                    padding (20, 8, 20, 8)
                    minimum (70, 55)
                    if persistent._file_page == "auto":
                        text "A" xalign 0.5 yalign 0.5 size 32 color "#2bff00"
                    elif persistent._file_page == "quick":
                        text "Q" xalign 0.5 yalign 0.5 size 32 color "#2bff00"
                    else:
                        text " [persistent._file_page]" xalign 0.5 yalign 0.5 size 32 color "#2bff00"

                # Botão Avançar 1 Página (>>)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_avancar_idle.png"
                    hover "wells/gui/button/p_avancar_hover.png"
                    action FilePageNext()

                # Botão Avançar 10 Páginas (>>>)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_mais10_idle.png"
                    hover "wells/gui/button/p_mais10_hover.png"
                    action FilePage(current_page_num + 10)

            side "c r":
                xalign 0.5 ypos 95 spacing 25 

                vpgrid:
                    id "wells_save_slots_vp"
                    cols 3 rows 5 xspacing 35 yspacing 30 xsize 1250 ysize 565              
                    mousewheel True draggable True arrowkeys True         

                    for slot in range(1, 16):
                        vbox:
                            xysize (360, 262) spacing 5

                            fixed:
                                xysize (360, 230) 

                                button:
                                    xfill True yfill True background Solid("#00000066")
                                    action FileSave(slot)

                                    if FileLoadable(slot):
                                        fixed:
                                            xfill True yfill True
                                            frame:
                                                xfill True yfill True
                                                background Frame(FileScreenshot(slot), 0, 0)
                                    else:
                                        frame:
                                            xfill True yfill True
                                            background Frame("wells/gui/slot_vazio.png", 0, 0)

                                if FileLoadable(slot):
                                    button:
                                        padding (0, 0, 0, 0) xysize (72, 28) 
                                        idle_background Frame("wells/gui/Button-idle.png", 3, 3)
                                        hover_background Frame("wells/gui/Button-hover.png", 3, 3)
                                        action FileDelete(slot) 
                                        text _("Delete") xalign 0.5 yalign 0.5 size 20 hover_color "#2bff00"

                            if FileLoadable(slot):
                                text FileTime(slot, format=_("{#file_time}%d.%m.%Y - %H:%M"), empty=_("Vazio")) xalign 0.5 size 22 color "#2bff00"
                            else:
                                text "Vazio" xalign 0.5 size 22 color "#ffffff"

                vbar:
                    value YScrollValue("wells_save_slots_vp")
                    top_bar Frame("wells/gui/vertical_cheia.png", 0, 0)   
                    bottom_bar Frame("wells/gui/vertical_vazia.png", 0, 0) 
                    thumb Frame("wells/gui/v_pino.png", 10, 0) xsize 20                                               

        button:
            padding (0, 0, 0, 0) xysize (180, 45) xalign 0.5 yalign 0.985 
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action [Hide("wells_custom_save")]
            text _("Voltar") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"

################################################################################
## MODULE: wells_saveload.rpy (PARTE 2: TELA DE CARREGAMENTO EXCLUSIVA)
################################################################################

screen wells_custom_load():
    modal True
    zorder 199 
    tag menu
    add Solid("#000000aa")

    $ current_page_num = int(persistent._file_page) if isinstance(persistent._file_page, (int, float)) or (isinstance(persistent._file_page, basestring if renpy.version_tuple < (8, 0, 0) else str) and persistent._file_page.isdigit()) else 1
    $ wells_prev10_page = current_page_num - 10
    if wells_prev10_page < 1:
        $ wells_prev10_page = 1

    frame:
        xalign 0.5 yalign 0.4
        background Frame("wells/gui/frame_menu.png", 10, 10)
        xsize 1450 ysize 820 padding (50, 40)

        fixed:
            xfill True yfill True

            frame:
                xpos 0 ypos 10
                background Frame("wells/gui/label_frame.png", 10, 10)
                padding (30, 8)
                text "CARREGAR" size 32 color "#ff4444"

            hbox:
                xalign 0.5 ypos 10 
                spacing 12

                # Atalho para Salvamento Automático (A)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_auto_idle.png"
                    hover "wells/gui/button/p_auto_hover.png"
                    selected_idle "wells/gui/button/p_auto_hover.png" # Mantém aceso se for a página atual
                    action FilePage("auto")

                # Atalho para Salvamento Rápido (Q)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_quick_idle.png"
                    hover "wells/gui/button/p_quick_hover.png"
                    selected_idle "wells/gui/button/p_quick_hover.png" # Mantém aceso se for a página atual
                    action FilePage("quick")

                # Botão Voltar 10 Páginas (<<<)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_menos10_idle.png"
                    hover "wells/gui/button/p_menos10_hover.png"
                    action FilePage(wells_prev10_page)

                # Botão Voltar 1 Página (<<)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_voltar_idle.png"
                    hover "wells/gui/button/p_voltar_hover.png"
                    action FilePagePrevious()

                # [MANTIDO] Contador de Página Centralizado (Caixa de texto estilizada que mostra o número)
                frame:
                    yalign 0.5
                    background Frame("wells/gui/button/Button-hover.png", 5, 5)
                    padding (20, 8, 20, 8)
                    minimum (70, 55)
                    if persistent._file_page == "auto":
                        text "A" xalign 0.5 yalign 0.5 size 32 color "#2bff00"
                    elif persistent._file_page == "quick":
                        text "Q" xalign 0.5 yalign 0.5 size 32 color "#2bff00"
                    else:
                        text " [persistent._file_page]" xalign 0.5 yalign 0.5 size 32 color "#2bff00"

                # Botão Avançar 1 Página (>>)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_avancar_idle.png"
                    hover "wells/gui/button/p_avancar_hover.png"
                    action FilePageNext()

                # Botão Avançar 10 Páginas (>>>)
                imagebutton:
                    yalign 0.5
                    idle "wells/gui/button/p_mais10_idle.png"
                    hover "wells/gui/button/p_mais10_hover.png"
                    action FilePage(current_page_num + 10)

            side "c r":
                xalign 0.5 ypos 95 spacing 25 

                vpgrid:
                    id "wells_load_slots_vp"
                    cols 3 rows 5 xspacing 35 yspacing 30 xsize 1250 ysize 565              
                    mousewheel True draggable True arrowkeys True         

                    for slot in range(1, 16):
                        vbox:
                            xysize (360, 262) spacing 5

                            fixed:
                                xysize (360, 230) 

                                button:
                                    xfill True yfill True background Solid("#00000066")
                                    action FileLoad(slot)

                                    if FileLoadable(slot):
                                        fixed:
                                            xfill True yfill True
                                            frame:
                                                xfill True yfill True
                                                background Frame(FileScreenshot(slot), 0, 0)
                                    else:
                                        frame:
                                            xfill True yfill True
                                            background Frame("wells/gui/slot_vazio.png", 0, 0)

                                if FileLoadable(slot):
                                    button:
                                        padding (0, 0, 0, 0) xysize (72, 28) 
                                        idle_background Frame("wells/gui/Button-idle.png", 3, 3)
                                        hover_background Frame("wells/gui/Button-hover.png", 3, 3)
                                        action FileDelete(slot) 
                                        text _("Delete") xalign 0.5 yalign 0.5 size 20 hover_color "#2bff00"

                            if FileLoadable(slot):
                                text FileTime(slot, format=_("{#file_time}%d.%m.%Y - %H:%M"), empty=_("Vazio")) xalign 0.5 size 22 color "#2bff00"
                            else:
                                text "Vazio" xalign 0.5 size 22 color "#ffffff"

                vbar:
                    value YScrollValue("wells_load_slots_vp")
                    top_bar Frame("wells/gui/vertical_cheia.png", 0, 0)   
                    bottom_bar Frame("wells/gui/vertical_vazia.png", 0, 0) 
                    thumb Frame("wells/gui/v_pino.png", 10, 0) xsize 20                                               

        button:
            padding (0, 0, 0, 0) xysize (180, 45) xalign 0.5 yalign 0.985 
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action [Hide("wells_custom_load")]
            text _("Voltar") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"
