################################################################################
## WELLS FRAMEWORK — DIALOGUE CONTROLS / BASE LIMPA
################################################################################

screen dialogue_adjusts():
    modal True
    zorder 200
    tag menu
    add Solid("#00000080")

    $ wells_name_pct = int(persistent.pref_text_size_label or 30)
    $ wells_dialogue_pct = int(persistent.pref_text_size_dialogue or 28)
    $ wells_x_pct = int((persistent.wells_textbox_x or 0.5) * 100)
    $ wells_y_pct = int((persistent.wells_textbox_y or 1.0) * 100)
    $ wells_width_value = int(persistent.wells_textbox_width or 1450)
    $ wells_opacity_pct = int((persistent.wells_textbox_opacity if persistent.wells_textbox_opacity is not None else 0.75) * 100)
    $ wells_multiple_x_pct = int((persistent.wells_multiple_x or 0.5) * 100)
    $ wells_multiple_width_value = int(persistent.wells_multiple_width or 600)
    $ wells_step_value = int(persistent.wells_multiple_stack_step or 310)
    $ wells_name_adjust_value = int(persistent.wells_name_size_offset or 2)
    $ wells_gap_value = int(persistent.wells_name_dialogue_spacing if persistent.wells_name_dialogue_spacing is not None else 0)
    $ wells_multiple_y_value = int(persistent.wells_multiple_y or 0)
    $ wells_choice_width_value = int(persistent.wells_choice_width or 920)
    $ wells_choice_x_pct = int((persistent.wells_choice_xpos or 0.5) * 100)
    $ wells_choice_y_pct = int((persistent.wells_choice_ypos or 0.5) * 100)

    frame:
        xalign 0.5
        yalign 0.4
        background Frame("wells/gui/frame_menu.png", 10, 10)
        xsize 1450
        ysize 820
        padding (50, 40)

        vbox:
            xfill True
            spacing 15

            frame:
                xpos 670
                xanchor 0.5
                ypos 15
                background Frame("wells/gui/label_frame.png", 0, 0)
                padding (10, 10)
                label _("DIALOGUE MENU"):
                    text_size 42
                    text_color "#ff4444"

            frame:
                xpos 120
                ypos 60
                xsize 760
                ysize 400
                background None
                padding (10, 10, 10, 10)

                side "c r":
                    xalign 0.5
                    ypos 0
                    spacing 15

                    viewport:
                        id "wells_painel_controles_vp"
                        mousewheel True
                        draggable True
                        arrowkeys True
                        xsize 720
                        ysize 380

                        vbox:
                            spacing 18
                            xsize 680

                            frame:
                                xsize 700
                                background Frame("wells/gui/frame_control.png", 10, 10)
                                padding (12, 12)

                                vbox:
                                    spacing 8
                                    xfill True

                                    frame:
                                        xalign 0.5
                                        background Frame("wells/gui/label_frame.png", 10, 10)
                                        padding (12, 4)
                                        label _("DIALOGUE"):
                                            text_size 26
                                            text_color "#ff4444"

                                    hbox:
                                        spacing 18
                                        xfill True

                                        vbox:
                                            spacing 10
                                            xsize 315

                                            vbox spacing 4:
                                                label "Name Size: [wells_name_pct]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "pref_text_size_label", range=60, offset=12, step=1)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            vbox spacing 4:
                                                label "Textbox X: [wells_x_pct]%":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_textbox_x", range=1.0, step=0.01)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            vbox spacing 4:
                                                label "Textbox Width: [wells_width_value]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_textbox_width", range=1800, offset=300, step=10)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            vbox spacing 4:
                                                label "Line Spacing: [persistent.wells_line_spacing]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_line_spacing", range=50, step=1)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            vbox spacing 4:
                                                label "DIalogue Adjust: [wells_name_adjust_value]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_name_size_offset", range=10, offset=-10, step=1)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            # CHOICE X

                                        vbox:
                                            spacing 10
                                            xsize 315

                                            vbox spacing 4:
                                                label "Text Size: [wells_dialogue_pct]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "pref_text_size_dialogue", range=60, offset=12, step=1)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            vbox spacing 4:
                                                label "Textbox Y: [wells_y_pct]%":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_textbox_y", range=1.0, step=0.01)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            vbox spacing 4:
                                                label "Textbox Opacity: [wells_opacity_pct]%":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_textbox_opacity", range=1.0, step=0.01)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                            vbox spacing 4:
                                                label "Name ↕ Dialogue: [wells_gap_value]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_name_dialogue_spacing", range=200, offset=-100, step=1)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                            frame:
                                xsize 700
                                background Frame("wells/gui/frame_control.png", 10, 10)
                                padding (12, 12)

                                vbox:
                                    spacing 8
                                    xfill True

                                    frame:
                                        xalign 0.5
                                        background Frame("wells/gui/label_frame.png", 10, 10)
                                        padding (12, 4)
                                        label _("MULTIPLE DIALOGUE"):
                                            text_size 26
                                            text_color "#ff4444"

                                    hbox:
                                        spacing 18
                                        xfill True

                                        vbox:
                                            spacing 10
                                            xsize 315

                                            vbox spacing 4:
                                                label "Multi X: [wells_multiple_x_pct]%":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)

                                                bar:
                                                    value FieldValue(persistent, "wells_multiple_x", range=1.0, step=0.01)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                        vbox:
                                            spacing 14
                                            yalign 0.0
                                            xsize 330

                                            # CHOICE Y

                                            vbox spacing 4:
                                                label "Multi Width: [wells_multiple_width_value]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_multiple_width", range=1400, offset=300, step=10)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                    hbox:
                                        spacing 18
                                        xfill True

                                        vbox:
                                            spacing 10
                                            xsize 315

                                            vbox spacing 4:
                                                label "Multi Y: [wells_multiple_y_value]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_multiple_y", range=600, offset=-300, step=5)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1
                                        vbox:
                                            spacing 10
                                            xsize 315

                                            vbox spacing 4:
                                                label "Multi V Step: [wells_step_value]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_multiple_stack_step", range=600, offset=100, step=5)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                            frame:
                                xsize 700
                                background Frame("wells/gui/frame_control.png", 10, 10)
                                padding (12, 12)

                                vbox:
                                    spacing 8
                                    xfill True

                                    frame:
                                        xalign 0.5
                                        background Frame("wells/gui/label_frame.png", 10, 10)
                                        padding (12, 4)
                                        label _("CHOICES"):
                                            text_size 26
                                            text_color "#ff4444"

                                    hbox:
                                        spacing 18
                                        xfill True

                                        vbox:
                                            spacing 10
                                            xsize 315

                                            vbox spacing 4:
                                                label "Choice X: [wells_choice_x_pct]%":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_choice_xpos", range=1.0, step=0.01)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1
                                            # CHOICE WIDTH

                                            vbox spacing 4:
                                                label "Choice Width: [wells_choice_width_value]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_choice_width", range=1500, offset=300, step=10)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                                        vbox:
                                            spacing 10
                                            xsize 315

                                            vbox spacing 4:
                                                label "Choice Y: [wells_choice_y_pct]%":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_choice_ypos", range=1.0, step=0.01)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1
                                            # CHOICE SPACING

                                            vbox spacing 4:
                                                label "Choice Spacing: [persistent.wells_choice_spacing]":
                                                    text_size 24
                                                    text_color "#2cf1ff"
                                                    padding (15, 2)
                                                    background Frame("wells/gui/label_frame.png", 10, 10)
                                                bar:
                                                    value FieldValue(persistent, "wells_choice_spacing", range=100, step=1)
                                                    xsize 320
                                                    ysize 25
                                                    xalign 0.5
                                                    idle_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    hover_right_bar Frame("wells/gui/barra_vazia.png", 5, 5)
                                                    idle_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    hover_left_bar Frame("wells/gui/barra_cheia.png", 5, 5)
                                                    thumb "wells/gui/pino.png"
                                                    thumb_shadow None
                                                    thumb_offset 1

                    vbar:
                        value YScrollValue("wells_painel_controles_vp")
                        top_bar Frame("wells/gui/vertical_cheia.png", 0, 0)
                        bottom_bar Frame("wells/gui/vertical_vazia.png", 0, 0)
                        thumb Frame("wells/gui/v_pino_wsc.png", 10, 10)
                        xsize 12

            vbox:
                spacing 8
                xpos 920
                ypos -300
                xsize 186

                vbox:
                    spacing 8

                    button:
                        padding (0, 0, 0, 0)
                        xysize (180, 42)
                        idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                        hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                        action Preference("skip", "toggle")
                        if preferences.skip_unseen:
                            text _("Pular Texto") xalign 0.5 yalign 0.5 size 20 color "#39ff14" hover_color "#00f3ff"
                        else:
                            text _("Pular Texto") xalign 0.5 yalign 0.5 size 20 color "#FFFFFF" hover_color "#2bff00"
                    button:
                        padding (0, 0, 0, 0)
                        xysize (180, 42)
                        idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                        hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                        action Preference("after choices", "toggle")
                        if preferences.skip_after_choices:
                            text _("Após Escolhas") xalign 0.5 yalign 0.5 size 20 color "#39ff14" hover_color "#00f3ff"
                        else:
                            text _("Após Escolhas") xalign 0.5 yalign 0.5 size 20 color "#FFFFFF" hover_color "#2bff00"

                    button:
                        padding (0, 0, 0, 0)
                        xysize (180, 42)
                        idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                        hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                        action Preference("transitions", "toggle")
                        if preferences.transitions == 2:
                            text _("Transições") xalign 0.5 yalign 0.5 size 20 color "#FFFFFF" hover_color "#00f3ff"
                        else:
                            text _("Transições") xalign 0.5 yalign 0.5 size 20 color "#39ff14" hover_color "#2bff00"

                    button:
                        padding (0, 0, 0, 0)
                        xysize (180, 42)
                        idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                        hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                        action ToggleField(persistent, "wells_force_outline")

                        if persistent.wells_force_outline:
                            text "CONTORNO" xalign 0.5 yalign 0.5 size 18 color "#39ff14" hover_color "#00f3ff"
                        else:
                            text "CONTORNO" xalign 0.5 yalign 0.5 size 18 color "#FFFFFF" hover_color "#2bff00"

                    button:
                        padding (0, 0, 0, 0)
                        xysize (180, 42)
                        idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                        hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                        action If(persistent.wells_choice_slot == 0, SetField(persistent, "wells_choice_slot", 1), SetField(persistent, "wells_choice_slot", 0))
                        if persistent.wells_choice_slot == 0:
                            text "Choices: 0" xalign 0.5 yalign 0.5 size 18 color "#00f3ff" hover_color "#2bff00"
                        else:
                            text "Choices: 1" xalign 0.5 yalign 0.5 size 18 color "#39ff14" hover_color "#00f3ff"

                    button:
                        xysize (180, 42)
                        idle_background Frame("wells/gui/Button-idle.png", 5, 5)
                        hover_background Frame("wells/gui/Button-hover.png", 5, 5)
                        action Function(restore_wells_defaults)
                        text _("Reset Wells") xalign 0.5 yalign 0.5 size 20 hover_color "#2bff00"

        button:
            xysize (180, 45)
            xpos 670
            ypos 675
            xanchor 0.5
            idle_background Frame("wells/gui/Button-idle.png", 5, 5)
            hover_background Frame("wells/gui/Button-hover.png", 5, 5)
            action Show("wells_menu_language")
            text _("Voltar") xalign 0.5 yalign 0.5 size 22 hover_color "#2bff00"
