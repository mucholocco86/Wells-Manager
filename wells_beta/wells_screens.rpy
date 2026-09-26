################################################################################
## WELLS FRAMEWORK — SAY / MULTIPLE SAY — BASE LIMPA
## Um único sistema universal de diálogo + Incubus para diálogo múltiplo.
################################################################################

init 999 screen say(who, what, multiple=None):
    # Escala: 1280/1920 usam a base; acima de 1920 cresce até 1.50.
    $ wells_scale = float(config.screen_width) / 1920.0
    if wells_scale < 1.0:
        $ wells_scale = 1.0
    elif wells_scale > 1.50:
        $ wells_scale = 1.50

    $ wells_box_width = int(persistent.wells_textbox_width * wells_scale)
    if wells_box_width > int(config.screen_width * 0.92):
        $ wells_box_width = int(config.screen_width * 0.92)
    if wells_box_width < 100:
        $ wells_box_width = 100

    $ wells_dialogue_size = int((persistent.pref_text_size_dialogue or 28) * wells_scale)
    if wells_dialogue_size < 12:
        $ wells_dialogue_size = 12

    $ wells_name_size = int((persistent.pref_text_size_label or 30) * wells_scale)
    if wells_name_size < 12:
        $ wells_name_size = 12

    $ wells_line = int((persistent.wells_line_spacing or 5) * wells_scale)
    $ wells_y = int((persistent.wells_dialogue_y_offset or 0) + ((persistent.wells_textbox_y - 1.0) * config.screen_height))

    $ wells_opacity = float(persistent.wells_textbox_opacity)
    if wells_opacity < 0.0:
        $ wells_opacity = 0.0
    elif wells_opacity > 1.0:
        $ wells_opacity = 1.0
    $ wells_bg_alpha = int(wells_opacity * 255.0)

    $ wells_pad_x = int(45 * wells_scale)
    $ wells_pad_top = int(14 * wells_scale)
    $ wells_pad_bottom = int(20 * wells_scale)
    $ wells_name_gap = int((persistent.wells_name_dialogue_spacing if persistent.wells_name_dialogue_spacing is not None else 0) * wells_scale)
    $ wells_content_width = wells_box_width - (wells_pad_x * 2)
    if wells_content_width < 100:
        $ wells_content_width = 100

    window id "window":
        xalign persistent.wells_textbox_x
        yalign 1.0
        yoffset wells_y
        xanchor 0.5
        xsize wells_box_width
        background Solid("#000000%02x" % wells_bg_alpha)
        padding (wells_pad_x, wells_pad_top, wells_pad_x, wells_pad_bottom)

        vbox:
            xpos 0
            xsize wells_content_width
            spacing wells_name_gap

            if who is not None:
                text who id "who":
                    style "default"
                    xpos 0
                    xalign 0.0
                    xsize wells_content_width
                    text_align 0.0
                    size wells_name_size
                    color "#FFFFFF"
                    if persistent.wells_force_outline:
                        outlines [(absolute(2), "#000000", 0, 0)]

            text what id "what":
                style "default"
                xpos 0
                xalign 0.0
                xsize wells_content_width
                text_align 0.0
                line_spacing wells_line
                size wells_dialogue_size
                color "#FFFFFF"
                if persistent.wells_force_outline:
                    outlines [(absolute(2), "#000000", 0, 0)]

    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0
        use quick_menu()


#################################################################################
## MULTIPLE SAY — INCUBUS / ÚNICO LAYOUT
#################################################################################

init 999 screen multiple_say(who, what, multiple):

    $ wells_scale = float(config.screen_width) / 1920.0

    if wells_scale < 1.0:
        $ wells_scale = 1.0
    elif wells_scale > 1.50:
        $ wells_scale = 1.50


    # Ren'Py normalmente envia:
    # multiple = (bloco_atual, total_de_blocos)

    $ wells_block = multiple[0] if (isinstance(multiple, (tuple, list)) and len(multiple) > 0) else (int(multiple) if multiple is not None else 1)

    $ wells_total_blocks = multiple[1] if (isinstance(multiple, (tuple, list)) and len(multiple) > 1) else wells_block


    if wells_block < 1:
        $ wells_block = 1

    if wells_total_blocks < 1:
        $ wells_total_blocks = 1


    # --------------------------------------------------------------------------
    # TAMANHO
    # --------------------------------------------------------------------------

    $ wells_box_width = int(persistent.wells_multiple_width * wells_scale)

    if wells_box_width > int(config.screen_width * 0.92):
        $ wells_box_width = int(config.screen_width * 0.92)

    if wells_box_width < 300:
        $ wells_box_width = 300


    $ wells_dialogue_size = int((persistent.wells_multiple_text_size or 23) * wells_scale)

    if wells_dialogue_size < 12:
        $ wells_dialogue_size = 12


    $ wells_name_size = int((persistent.pref_text_size_label or 30) * wells_scale)

    if wells_name_size < 12:
        $ wells_name_size = 12


    $ wells_line = int((persistent.wells_line_spacing or 5) * wells_scale)


    # --------------------------------------------------------------------------
    # POSIÇÃO BASE DA CAIXA NORMAL
    # --------------------------------------------------------------------------

    $ wells_base_y = int(
        (persistent.wells_dialogue_y_offset or 0)
        + ((persistent.wells_textbox_y - 1.0) * config.screen_height)
    )


    # --------------------------------------------------------------------------
    # OPACIDADE
    # --------------------------------------------------------------------------

    $ wells_opacity = float(persistent.wells_textbox_opacity)

    if wells_opacity < 0.0:
        $ wells_opacity = 0.0
    elif wells_opacity > 1.0:
        $ wells_opacity = 1.0


    # --------------------------------------------------------------------------
    # MULTI X
    # --------------------------------------------------------------------------

    $ wells_multi_x = int(
        float(persistent.wells_multiple_x) * config.screen_width
    )


    # --------------------------------------------------------------------------
    # MULTI Y
    #
    # Move TODO o conjunto para cima/baixo.
    # --------------------------------------------------------------------------

    $ wells_multi_y = int(
        persistent.wells_multiple_y or 0
    )


    # --------------------------------------------------------------------------
    # MULTI V STEP
    #
    # Controla somente a distância entre os blocos.
    # --------------------------------------------------------------------------

    $ wells_multi_step = int(
        float(persistent.wells_multiple_stack_step) * wells_scale
    )


    # --------------------------------------------------------------------------
    # POSIÇÃO DO BLOCO
    #
    # O grupo inteiro é centralizado em torno de wells_multi_y.
    #
    # Exemplo com 2 blocos:
    #
    # Multi V Step = 250
    #
    #       BLOCO 1
    #          |
    #        250 px
    #          |
    #       BLOCO 2
    #
    # Ao alterar Multi Y, os dois sobem/descem juntos.
    # Ao alterar Multi V Step, os dois se afastam/aproximam.
    # --------------------------------------------------------------------------

    $ wells_multi_stack_offset = int(
        ((wells_total_blocks - 1) * wells_multi_step) / 2.0
    )

    $ wells_multi_block_offset = int(
        (wells_block - 1) * wells_multi_step
    )

    $ wells_multi_position_y = int(
        wells_base_y
        - wells_multi_stack_offset
        + wells_multi_block_offset
        + wells_multi_y
    )


    # --------------------------------------------------------------------------
    # CAIXA
    # --------------------------------------------------------------------------

    window id "window":
        style "default"

        xanchor 0.5
        xpos wells_multi_x

        yalign 1.0
        yoffset wells_multi_position_y


        frame:
            background Transform(
                "wells/gui/textbox_multiple_frame.png",
                alpha=wells_opacity
            )

            xsize wells_box_width

            padding (
                int(45 * wells_scale),
                int(18 * wells_scale),
                int(45 * wells_scale),
                int(18 * wells_scale)
            )


            vbox:
                xfill True
                spacing int(1 * wells_scale)


                if who is not None:

                    window:
                        id "namebox"

                        style "namebox_multiple_wells_1920"

                        background Frame(
                            "wells/gui/namebox_multiple.png",
                            3,
                            3
                        )

                        xalign 0.0


                        text who id "who":
                            size wells_name_size
                            xalign 0.0

                            if persistent.wells_force_outline:
                                outlines [
                                    (absolute(2), "#000000", 0, 0)
                                ]


                text what id "what":

                    xfill True

                    size wells_dialogue_size

                    line_spacing wells_line

                    xalign 0.0


                    if persistent.wells_force_outline:
                        outlines [
                            (absolute(2), "#000000", 0, 0)
                        ]


    # --------------------------------------------------------------------------
    # SIDE IMAGE / QUICK MENU
    # --------------------------------------------------------------------------

    if not renpy.variant("small"):

        add SideImage() xalign 0.0 yalign 1.0

        use quick_menu()