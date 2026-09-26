################################################################################
## 2. SCREEN MENU PRINCIPAL (CENTRALIZADO)
################################################################################

screen wells_menu_language():
    modal True
    zorder 200
    tag menu
    add Solid("#00000080") 

    frame:
        xalign 0.5 yalign 0.4
        background Frame("wells/gui/frame_menu.png", 10, 10)

        # --- LÓGICA DE RESOLUÇÃO E MOBILE ---
        if config.screen_width == 1920:
            if renpy.variant("small"):
                xsize 1600 ysize 950 padding (60, 50)
            else:
                xsize 1450 ysize 820 padding (50, 40)
        else:
            xsize 1150 ysize 700 padding (40, 35)

        vbox:
            xfill True
            spacing 25

            frame:
                xpos 670
                xanchor 0.5
                ypos 15
                background Frame("wells/gui/label_frame.png", 0, 0)
                padding (10, 10)

                label _("Wells Framework"):
                        text_size 48 
                        text_color "#ff4444"

            hbox:
                xalign 0.5 spacing 60 

# --- COLUNA 1: SISTEMA (FONTES) ---
                vbox:
                    xsize 420 spacing 15 
                    ypos 20
                    xanchor 0.5
                    xpos 160

                    label _("FONTS"):
                        xalign 0.3
                        text_size 26 
                        text_color "#347bff"
                        padding (25, 6)
                        background Frame("wells/gui/label_frame.png", 10, 10)

                    frame:
                        xsize 380 ysize 220 background Solid("#00000066")
                        
                        side "c r":
                            spacing 10 
                            
                            viewport:
                                id "vp_fonts" mousewheel True draggable True
                                vbox spacing 8 xfill True:
                                    for fonte in listar_fontes():
                                        $ f_path = "wells/fonts/" + fonte
                                        textbutton fonte:
                                            action [SetField(persistent, "font_escolhida", f_path), Preference("font transform", "wells_custom")]
                                            text_font f_path text_size 24
                                            text_selected_color "#2bff00"
                                            text_hover_color "#ff0000"
                                            selected (persistent.font_escolhida == f_path)

                            vbar:
                                value YScrollValue("vp_fonts")
                                top_bar Frame("wells/gui/vertical_cheia.png", 0, 0)   
                                bottom_bar Frame("wells/gui/vertical_vazia.png", 0, 0) 
                                thumb Frame("wells/gui/v_pino.png", 10, 10)             
                                xsize 20                                               

                    # --- BOTÃO REINICIAR UNIVERSAL DE FONTES ---
                    button:
                        padding (0, 0, 0, 0)
                        xysize (180, 45)
                        xpos 150 ypos 6 xanchor 0.5
                        idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                        hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                        # [CORREÇÃO] Define a escolha como None e desliga o transformador para restaurar a fonte original do jogo
                        action [SetField(persistent, "font_escolhida", None), Preference("font transform", None)] 
                        text _("Reiniciar Font") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"

                # --- COLUNA 2: TODOS OS SLIDERS (CONTROLES) ---
                vbox:
                    xsize 420 spacing 10 
                    ypos 20
                    xanchor 0.5
                    xpos 290

                    label _("SOUNDS"):
                        xalign 0.5 
                        text_size 26 
                        text_color "#347bff"
                        padding (25, 6)
                        background Frame("wells/gui/label_frame.png", 10, 10)

                    vbox spacing 4:

                        label _("Music"):
                            xalign 0.5 
                            text_size 24 
                            text_color "#2cf1ff"
                            padding (15, 4)
                            background Frame("wells/gui/label_frame.png", 10, 10)

                        bar:
                            value Preference("music volume") 
                            xsize 400 ysize 25
                            idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                            hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                            idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                            hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                            thumb "wells/gui/pino.png"
                            thumb_shadow None
                            thumb_offset 1

                        label _("SFX"):
                            xalign 0.5 
                            text_size 24 
                            text_color "#2cf1ff"
                            padding (15, 4)
                            background Frame("wells/gui/label_frame.png", 10, 10)

                        bar:
                            value Preference("sound volume") 
                            xsize 400 ysize 25
                            idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                            hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                            idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                            hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                            thumb "wells/gui/pino.png"
                            thumb_shadow None
                            thumb_offset 1

                        label _("Voice"):
                            xalign 0.5 
                            text_size 24 
                            text_color "#2cf1ff"
                            padding (15, 4)
                            background Frame("wells/gui/label_frame.png", 10, 10)

                        bar:
                            value Preference("voice volume") 
                            xsize 400 ysize 25
                            idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                            hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                            idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                            hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                            thumb "wells/gui/pino.png"
                            thumb_shadow None
                            thumb_offset 1

                    vbox spacing 10:

                        button:
                            padding (0, 0, 0, 0)
                            xysize (180, 45)
                            xpos 200 ypos 25 xanchor 0.5
                            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                            action Preference("all mute", "toggle")
                            text _("MUTE") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"

        button:
            padding (0, 0, 0, 0)
            xysize (180, 45)
            xpos 290 ypos 675 xanchor 0.5
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action [Show("idioma_seletor"), Hide("wells_menu_language")]
            text _("Idiomas") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"

        button:
            padding (0, 0, 0, 0)
            xysize (180, 45)
            xpos 480 ypos 675 xanchor 0.5
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action [Show("menu_performance"), Hide("wells_menu_language")]
            text _("Performance") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"

        button:
            padding (0, 0, 0, 0)
            xysize (180, 45)
            xpos 670 ypos 675 xanchor 0.5  # Este é o centro real exato do painel (1450 / 2)
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action [Show("dialogue_adjusts"), Hide("wells_menu_language")]
            text _("Diálogo") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"

        button:
            padding (0, 0, 0, 0)
            xysize (180, 45)
            xpos 1050 ypos 675 xanchor 0.5
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action [Hide("wells_menu_language")]
            text _("Fechar") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"