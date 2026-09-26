################################################################################
## WELLS FRAMEWORK — SISTEMA UNIVERSAL DE ESCOLHAS
##
## Este arquivo controla apenas a tela "choice".
## Os valores usados aqui ficam em persistent e são ajustados pelo
## wells_screen_control.rpy.
################################################################################

init 999 screen choice(items):
    style_prefix "choice"

    # ========================================================================
    # SLOT 0 — PASS-THROUGH / COMPATIBILIDADE
    # Mantém a estrutura visual do jogo hospedeiro, mas aplica os controles
    # universais do Wells para posição, tamanho, espaçamento e largura.
    # ========================================================================
    if persistent.wells_choice_slot == 0:

        vbox:
            xalign (persistent.wells_choice_xpos if persistent.wells_choice_xpos is not None else 0.5)
            yalign (persistent.wells_choice_ypos if persistent.wells_choice_ypos is not None else 0.5)
            spacing (persistent.wells_choice_spacing if persistent.wells_choice_spacing is not None else gui.choice_spacing)

            for i in items:

                # Compatibilidade com Choice objects do Ren'Py e com entradas
                # em formato de tupla usadas por alguns jogos/mods.
                python:
                    if hasattr(i, "caption"):
                        caption = i.caption
                        action = i.action
                    else:
                        caption = i[0]
                        action = i[1]

                if action:
                    button:
                        action action
                        style "wells_choice_button"

                        xminimum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)
                        xmaximum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)

                        text caption:
                            style "wells_choice_text"
                            size (persistent.wells_choice_size if persistent.wells_choice_size is not None else gui.choice_button_text_size)
                            xalign 0.5
                            text_align 0.5

                else:
                    text caption style "wells_choice_text"

    # ========================================================================
    # SLOT 1 — PERSONALIZAÇÃO MANUAL
    # Usa o estilo choice_vbox do jogo/framework, mantendo os mesmos controles
    # universais de posição, tamanho, espaçamento e largura.
    # ========================================================================
    else:

        vbox:
            style "choice_vbox"
            xalign (persistent.wells_choice_xpos if persistent.wells_choice_xpos is not None else 0.5)
            yalign (persistent.wells_choice_ypos if persistent.wells_choice_ypos is not None else 0.5)
            spacing (persistent.wells_choice_spacing if persistent.wells_choice_spacing is not None else gui.choice_spacing)

            for i in items:

                # Mesmo tratamento de compatibilidade do Slot 0.
                python:
                    if hasattr(i, "caption"):
                        caption = i.caption
                        action = i.action
                    else:
                        caption = i[0]
                        action = i[1]

                textbutton caption:
                    action action
                    text_size (persistent.wells_choice_size if persistent.wells_choice_size is not None else gui.choice_button_text_size)
                    xalign 0.5
                    text_align 0.5
                    xminimum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)
                    xmaximum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)
