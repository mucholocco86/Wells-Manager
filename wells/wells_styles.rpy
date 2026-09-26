################################################################################
## WELLS FRAMEWORK — STYLES / BASE LIMPA
################################################################################

init -1 style wells_menu_slider_label is pref_label
init -1 style wells_menu_slider_label_text is label_text
init -1 style wells_menu_slider_slider is gui_slider
init -1 style wells_menu_slider_button is gui_button
init -1 style wells_menu_slider_button_text is gui_button_text
init -1 style wells_menu_slider_pref_vbox is pref_vbox
init -1 style wells_menu_check_button_text is button_text
init -1 style wells_menu_radio_button_text is button_text

init -1 style wells_menu_quick_button:
    padding (10, 4, 10, 4)

init -1 style wells_menu_quick_button_text:
    size 22
    color "#FFFFFF"
    outlines [(1, "#000000", 0, 0)]
    hover_color "#2bff00"

init -1 style wells_menu_quick_text is wells_menu_quick_button_text:
    size 22

if not renpy.variant("small"):
    init -1 style wells_menu_slider_label_text:
        size 28
    init -1 style wells_menu_check_button_text:
        size 28
    init -1 style wells_menu_radio_button_text:
        size 28
    init -1 style wells_menu_slider_slider:
        xsize 400
    init -1 style wells_menu_slider_button:
        yalign 0.5
        left_margin 15
    init -1 style wells_menu_slider_button_text:
        size 18
        font "wells/fonts/Roboto-Regular.ttf"
    init -1 style wells_menu_slider_vbox:
        xsize 675

init -1 style wells_choice_button is default:
    idle_background Frame("wells/gui/styles/wells_choices_idle.png", 35, 10, 35, 10)
    hover_background Frame("wells/gui/styles/wells_choices_hover.png", 35, 10, 35, 10)
    padding (40, 12, 40, 12)
    xalign 0.5
    yalign 0.5

init -1 style wells_choice_text is default:
    font "wells/fonts/cabin-regular.ttf"
    color "#e7e2e2"
    hover_color "#e7e2e2"
    size 28
    outlines [(absolute(2), "#212121", 0, 0)]

init -1 style namebox_multiple_wells_1920 is default
init -1 style namebox_multiple_wells_1920:
    xpos 400
    xanchor 0.5
    xsize None
    ypos -80
    ysize None
    background Frame("wells/gui/namebox_multiple.png", wells_namebox_borders, tile=False, xalign=0.0)
    padding wells_namebox_borders.padding

init -1 style game_menu_outer_frame:
    bottom_padding 30
    top_padding 120
    background Image("wells/gui/frame.png")

init -501 screen input(prompt):
    style_prefix "input"
    window:
        if renpy.variant("small"):
            yalign 0.2
        text prompt style "input_prompt"
        input id "input"

init -1 style input_prompt is default
