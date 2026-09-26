################################################################################
## WELLS FRAMEWORK — SISTEMA UNIVERSAL DE ESCOLHAS CONECTADO AO MOTOR WF
################################################################################

init 999 screen choice(items):
    style_prefix "choice"

    # Aciona o processamento da árvore de escolhas baseado no SDK real
    $ mapa_wf_atual = WFWalkthrough.processar_menu_atual()

    # ========================================================================
    # SLOT 0 — PASS-THROUGH / COMPATIBILIDADE + INTEGRAÇÃO WF
    # ========================================================================
    if persistent.wells_choice_slot == 0:

        vbox:
            xalign (persistent.wells_choice_xpos if persistent.wells_choice_xpos is not None else 0.5)
            yalign (persistent.wells_choice_ypos if persistent.wells_choice_ypos is not None else 0.5)
            spacing (persistent.wells_choice_spacing if persistent.wells_choice_spacing is not None else gui.choice_spacing)

            for idx_atual, i in enumerate(items):

                python:
                    if hasattr(i, "caption"):
                        caption = i.caption
                        action = i.action
                    else:
                        caption = i[0]
                        action = i[1]

                    # Resgata o objeto WFChoice construído pela engenharia de dados
                    exibicao_guia = "➔ Avança para a história..."
                    if mapa_wf_atual and idx_atual in mapa_wf_atual:
                        escolha_wf = mapa_wf_atual[idx_atual]
                        if escolha_wf.code != "Nenhuma alteração de estado detectada.":
                            exibicao_guia = "➔ " + escolha_wf.code
                        else:
                            exibicao_guia = "➔ " + escolha_wf.jumpTo

                if action:
                    button:
                        # INTERVENÇÃO HISTÓRICA: O botão agora chama o método Action() do Wells,
                        # que desativa o rollback_is_fixed e aciona o ChoiceReturn nativo de forma limpa!
                        action (escolha_wf.Action if (mapa_wf_atual and idx_atual in mapa_wf_atual) else action)
                        style "wells_choice_button"

                        xminimum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)
                        xmaximum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)

                        vbox:
                            xalign 0.5
                            yalign 0.5
                            spacing 8
                            
                            text caption:
                                style "wells_choice_text"
                                size (persistent.wells_choice_size if persistent.wells_choice_size is not None else gui.choice_button_text_size)
                                xalign 0.5
                                text_align 0.5
                                
                            frame:
                                xalign 0.5
                                background Frame(Flatten(Solid("#000000a0")), 0, 0)
                                padding (12, 4, 12, 4)
                                
                                text "[exibicao_guia]":
                                    style "wells_choice_text"
                                    size (persistent.wells_choice_size - 4 if persistent.wells_choice_size is not None else gui.choice_button_text_size - 4)
                                    color "#00ff00" 
                                    xalign 0.5
                                    text_align 0.5
                else:
                    text caption style "wells_choice_text"

    # ========================================================================
    # SLOT 1 — PERSONALIZAÇÃO MANUAL + INTEGRAÇÃO WF
    # ========================================================================
    else:

        vbox:
            style "choice_vbox"
            xalign (persistent.wells_choice_xpos if persistent.wells_choice_xpos is not None else 0.5)
            yalign (persistent.wells_choice_ypos if persistent.wells_choice_ypos is not None else 0.5)
            spacing (persistent.wells_choice_spacing if persistent.wells_choice_spacing is not None else gui.choice_spacing)

            for idx_atual, i in enumerate(items):

                python:
                    if hasattr(i, "caption"):
                        caption = i.caption
                        action = i.action
                    else:
                        caption = i[0]
                        action = i[1]
                        
                    exibicao_guia = "➔ Avança para a história..."
                    if mapa_wf_atual and idx_atual in mapa_wf_atual:
                        escolha_wf = mapa_wf_atual[idx_atual]
                        if escolha_wf.code != "Nenhuma alteração de estado detectada.":
                            exibicao_guia = "➔ " + escolha_wf.code
                        else:
                            exibicao_guia = "➔ " + escolha_wf.jumpTo

                vbox:
                    xalign 0.5
                    
                    textbutton caption:
                        action (escolha_wf.Action if (mapa_wf_atual and idx_atual in mapa_wf_atual) else action)
                        text_size (persistent.wells_choice_size if persistent.wells_choice_size is not None else gui.choice_button_text_size)
                        xalign 0.5
                        text_align 0.5
                        xminimum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)
                        xmaximum (persistent.wells_choice_width if persistent.wells_choice_width is not None else 920)

                    frame:
                        xalign 0.5
                        background Frame(Flatten(Solid("#000000a0")), 0, 0)
                        padding (10, 4, 10, 4)
                        
                        text "[exibicao_guia]":
                            size (persistent.wells_choice_size - 6 if persistent.wells_choice_size is not None else gui.choice_button_text_size - 6)
                            color "#00ff00"
                            xalign 0.5
                            text_align 0.5
