
style x52URM_seperator is x52URM_default:
    background x52URM.Theme.primary
    ysize 2
style x52URM_vseperator is x52URM_default:
    background x52URM.Theme.primary
    xsize 2

style x52URM_text_small is x52URM_text:
    size x52URM.scalePxInt(20)
style x52URM_description is x52URM_text_small:
    color x52URM.Theme.textTranslucent140

style x52URM_icon_textbutton is x52URM_icon_button:
    background None
    hover_background None
    selected_idle_background None
    insensitive_background None
    padding (0,0)
style x52URM_icon_textbutton_text is x52URM_icon_button_text

style x52URM_header_text is x52URM_label_text:
    color x52URM.Theme.secondary
    outlines [(absolute(1), x52URM.Theme.secondaryDarker, absolute(1), absolute(1)),(absolute(1), x52URM.Theme.secondaryLighter, absolute(-1), absolute(-1))]
    size x52URM.scalePxInt(28)

style x52URM_thumbnailButton is x52URM_button:
    padding (2, 2)

style x52URM_hbox is x52URM_default
style x52URM_vbox is x52URM_default  
style x52URM_vpgrid is x52URM_default

style x52URM_input is x52URM_button_text
