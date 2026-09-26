################################################################################
## 3. SCREEN IDIOMA SELETOR
################################################################################

screen idioma_seletor():
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

                label _("LANGUAGE SELECTOR"):
                        text_size 48 
                        text_color "#ff4444"

            vbox:
                xalign 0.5
                yalign 0.5
                spacing 15

                if renpy.variant("small"):
                    xsize 400 
                else:
                    xsize 380

                label _("TRANSLATION"):
                    xalign 0.5 
                    text_size 26 
                    text_color "#347bff"
                    padding (25, 6)
                    background Frame("wells/gui/label_frame.png", 10, 10)

                vbox:
                    xalign 0.5
                    spacing 6
                    style_prefix "radio"
                    
                    frame:
                        xsize 380 ysize 280 background Solid("#0000004f")
                        
                        side "c r":
                            spacing 10 
                            
                            viewport:
                                id "vp_tl" mousewheel True draggable True
                                vbox spacing 8 xfill True:
                                    $ langs = get_all_languages()
                                    for lang in langs:
                                        textbutton "[lang]".capitalize():
                                            action Language(None if lang=="Default" else lang)
                                            text_idle_color "#ffffff"
                                            text_hover_color "#ff0000"
                                            text_selected_idle_color "#2bff00"
                                            text_selected_hover_color "#2bff00"
                                            text_size 26
                                            xalign 0.5

                            vbar:
                                value YScrollValue("vp_tl")
                                top_bar Frame("wells/gui/vertical_cheia.png", 0, 0)   
                                bottom_bar Frame("wells/gui/vertical_vazia.png", 0, 0) 
                                thumb Frame("wells/gui/v_pino.png", 0, 0)             
                                xsize 20                                               

        button:
            padding (0, 0, 0, 0)
            xysize (180, 45)
            xpos 670 ypos 675 xanchor 0.5  
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action Show("wells_menu_language")
            text _("Voltar") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"
