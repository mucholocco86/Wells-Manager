
style x52URM_button is x52URM_default:
    background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonBg, x52URM.Theme.colors.buttonBorder)
    hover_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonBgHover, x52URM.Theme.colors.buttonBorder)
    selected_idle_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonBgHover, x52URM.Theme.colors.buttonBorder)
    insensitive_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonBgDisabled, x52URM.Theme.colors.buttonBorderDisabled)
    padding (x52URM.scalePxInt(8), x52URM.scalePxInt(4))
    xminimum None yminimum x52URM.scalePxInt(36)
    xmaximum None ymaximum None

style x52URM_button_text is x52URM_text:
    color x52URM.Theme.colors.buttonText
    insensitive_color x52URM.Theme.colors.buttonTextDisabled
    yalign .5

style x52URM_buttonPrimary is x52URM_button:
    background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonPrimaryBg, x52URM.Theme.colors.buttonPrimaryBorder)
    hover_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonPrimaryBgHover, x52URM.Theme.colors.buttonPrimaryBorder)
    selected_idle_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonPrimaryBgHover, x52URM.Theme.colors.buttonPrimaryBorder)
    insensitive_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonPrimaryBgDisabled, x52URM.Theme.colors.buttonPrimaryBorder)

style x52URM_buttonPrimary_text is x52URM_button_text:
    color x52URM.Theme.colors.buttonPrimaryText
    insensitive_color x52URM.Theme.colors.buttonPrimaryTextDisabled

style x52URM_buttonSecondary is x52URM_button:
    background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSecondaryBg, x52URM.Theme.colors.buttonSecondaryBorder)
    hover_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSecondaryBgHover, x52URM.Theme.colors.buttonSecondaryBorder)
    selected_idle_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSecondaryBgHover, x52URM.Theme.colors.buttonSecondaryBorder)
    insensitive_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSecondaryBgDisabled, x52URM.Theme.colors.buttonSecondaryBorderDisabled)

style x52URM_buttonSecondary_text is x52URM_button_text:
    color x52URM.Theme.colors.buttonSecondaryText
    insensitive_color x52URM.Theme.colors.buttonSecondaryTextDisabled

style x52URM_buttonCancel is x52URM_button:
    background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonCancelBg, x52URM.Theme.colors.buttonCancelBorder)
    hover_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonCancelBgHover, x52URM.Theme.colors.buttonCancelBorder)
    selected_idle_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonCancelBgHover, x52URM.Theme.colors.buttonCancelBorder)
    insensitive_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonCancelBgDisabled, x52URM.Theme.colors.buttonCancelBorderDisabled)

style x52URM_buttonCancel_text is x52URM_button_text:
    color x52URM.Theme.colors.buttonCancelText
    insensitive_color x52URM.Theme.colors.buttonCancelTextDisabled

style x52URM_buttonSuccess is x52URM_button:
    background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSuccessBg, x52URM.Theme.colors.buttonSuccessBorder)
    hover_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSuccessBgHover, x52URM.Theme.colors.buttonSuccessBorder)
    selected_idle_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSuccessBgHover, x52URM.Theme.colors.buttonSuccessBorder)
    insensitive_background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonSuccessBgDisabled, x52URM.Theme.colors.buttonSuccessBorderDisabled)

style x52URM_buttonSuccess_text is x52URM_button_text:
    color x52URM.Theme.colors.buttonSuccessText
    insensitive_color x52URM.Theme.colors.buttonSuccessTextDisabled

style x52URM_icon_button is x52URM_button
style x52URM_icon_button_text is x52URM_button_text:
    font '0x52-URM/framework/MaterialIconsOutlined-Regular.otf'
    hover_font '0x52-URM/framework/MaterialIcons-Regular.ttf'

##############
# ICONBUTTON #
##############
screen x52URM_iconButton(icon, text=None, action=None, xsize=None, sensitive=None, alternate=None):
    style_prefix 'x52URM'

    button:
        xsize xsize
        sensitive sensitive
        action action
        alternate alternate
        if text: # It's a button with text?
            hbox:
                hbox xsize x52URM.scalePxInt(30) yalign .5: # We want this size fixed, to prevent resizing on icon change
                    text icon style_suffix 'icon_button_text'
                if text:
                    text text style_suffix 'button_text' yalign .5
        else: # Icon only button
            text icon style_suffix 'icon_button_text' yalign .5
# We have this screen because in some cases updating the `icon` for `URM_iconbutton` won't work
screen x52URM_checkbox(checked, text, action=None, xsize=None, sensitive=None):
    style_prefix 'x52URM'

    button:
        xsize xsize
        sensitive sensitive
        action action
        hbox:
            hbox xsize x52URM.scalePxInt(30) yalign .5: # We want this size fixed, to prevent resizing on icon change
                if checked:
                    text '\ue834' style_suffix 'icon_button_text' 
                elif checked == False:
                    text '\ue835' style_suffix 'icon_button_text'
                else:
                    text '\ue909' style_suffix 'icon_button_text'
            text text style_suffix 'button_text' yalign .5
# We have this screen because in some cases updating the `icon` for `URM_iconbutton` won't work
screen x52URM_radiobutton(checked, text, action=None, xsize=None, sensitive=None):
    style_prefix 'x52URM'

    button:
        xsize xsize
        sensitive sensitive
        action action
        hbox:
            hbox xsize x52URM.scalePxInt(30) yalign .5: # We want this size fixed, to prevent resizing on icon change
                if checked:
                    text '\ue837' style_suffix 'icon_button_text' 
                else:
                    text '\ue836' style_suffix 'icon_button_text'
            text text style_suffix 'button_text' yalign .5