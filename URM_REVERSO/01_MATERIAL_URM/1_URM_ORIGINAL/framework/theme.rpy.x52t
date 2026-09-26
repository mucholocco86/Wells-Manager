
transform x52URM_fadeinout:
    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on hide:
        linear 0.3 alpha 0.0

style x52URM_default is default:
    background None
    hover_background None
    selected_background None
    selected_hover_background None
    insensitive_background None

    xalign .0 yalign .0
    xpadding 0 ypadding 0
    xmargin 0 ymargin 0
    spacing 0 line_spacing 0

style x52URM_text is x52URM_default:
    font '0x52-URM/framework/Roboto-Regular.ttf'
    color x52URM.Theme.text
    size x52URM.scalePxInt(24)
    text_align 0.0
    outlines []
    alt ''

style x52URM_label is x52URM_default
style x52URM_label_text is x52URM_text:
    bold True

style x52URM_icon is x52URM_text:
    font '0x52-URM/framework/MaterialIconsOutlined-Regular.otf'

style x52URM_iconSolid is x52URM_icon:
    font '0x52-URM/framework/MaterialIcons-Regular.ttf'

style x52URM_overlay:
    background x52URM.Theme.colorAlpha(x52URM.Theme.background, 0.4)

style x52URM_frame is x52URM_default:
    background Solid(x52URM.Theme.background)
    padding (x52URM.scalePxInt(7), x52URM.scalePxInt(5))

style x52URM_vscrollbar:
    xsize x52URM.scalePxInt(15)
    ysize None # Prevent fixed height
    left_bar Solid(x52URM.Theme.colors.scrollBg)
    right_bar Solid(x52URM.Theme.colors.scrollBg)
    thumb Solid(x52URM.Theme.colors.scrollThumb)
    hover_thumb Solid(x52URM.Theme.colors.scrollThumbHover)
    unscrollable 'hide'

# We cannot inherit `x52URM_vscrollbar`, because it will invert the scrollbar for some reason
style x52URM_vbar:
    xsize x52URM.scalePxInt(15)
    left_bar Solid(x52URM.Theme.colors.scrollBg)
    right_bar Solid(x52URM.Theme.colors.scrollBg)
    thumb Solid(x52URM.Theme.colors.scrollThumb)
    hover_thumb Solid(x52URM.Theme.colors.scrollThumbHover)
    unscrollable 'hide'
