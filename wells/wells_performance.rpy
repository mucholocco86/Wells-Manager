################################################################################
## 5. SCREEN PERFORMANCE
################################################################################

screen menu_performance():
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

                label _("PERFORMANCE"):
                        text_size 48 
                        text_color "#ff4444"

            hbox:
                xalign 0.5 spacing 60 
                vbox:
                    spacing 15 xfill True
                    hbox:
                        xpos 670
                        ypos 25
                        xanchor 0.5
                        spacing 40

                        # --- COLUNA: PERFORMANCE (configuração) ---
                        vbox:
                            xsize 400 spacing 12

                            vbox:
                                spacing 6 xfill True

                                # --- SUBTÍTULO VIDEO PERFORMANCE COM MOLDURA ---
                                frame:
                                    xalign 0.5
                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                    padding (15, 2)
                                    text "VIDEO PERFORMANCE" size 24 color "#2cf1ff" xalign 0.5

                                $ current_fps = "30 FPS" if preferences.gl_framerate == 30 else "60 FPS"
                                textbutton "Limit FPS: [current_fps]":
                                    xalign 0.5
                                    action Function(toggle_power_save)
                                    text_hover_color "#2bff00"
                                    text_size 28
                                    text_color  "#cacaca"

                                $ gl_ps_status = "ON" if preferences.gl_powersave else "OFF"
                                textbutton "Economia de energia: [gl_ps_status]":
                                    xalign 0.5
                                    action Preference("gl powersave", "toggle")
                                    text_hover_color "#2bff00"
                                    text_size 28
                                    text_color  "#adabab"

                            vbox:
                                spacing 6 xfill True

                                # --- SUBTÍTULO RENDERIZAÇÃO COM MOLDURA ---
                                frame:
                                    xalign 0.5
                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                    padding (15, 2)
                                    text "RENDERIZAÇÃO DE VÍDEO" size 22 color "#2cf1ff" xalign 0.5

                                $ hw_label = "Hardware (GPU)" if persistent.use_hw_video else "Software (CPU)"
                                textbutton "Decoding: [hw_label]":
                                    xalign 0.5
                                    action [ToggleField(persistent, "use_hw_video"), Notify("Restart game to apply changes")]
                                    text_hover_color "#2bff00"
                                    text_size 28

                                text "Use se você vir uma tela preta." size 24 color "#949494" xalign 0.5

        button:
            padding (0, 0, 0, 0)
            xysize (180, 45)
            xpos 670 ypos 675 xanchor 0.5
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action Show("wells_menu_language")
            text _("Voltar") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"

