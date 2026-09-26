
screen URM_colorpicker(callback, onClose, defaultColor=None):
    layer 'x52Overlay'
    style_prefix "x52URM"
    modal True

    default colorPicker = x52URM.ColorPicker(defaultColor)
    default colorPresets = [(0, 0, 0), (12, 19, 79), (29, 38, 125), (92, 70, 156), (212, 173, 252), (255, 255, 255)]

    use x52URM_Dialog(title='{urm_notl}Colorpicker{/urm_notl}', closeAction=onClose, icon='\ue40a'):
        label '{urm_notl}Current:{/urm_notl}'
        frame xsize x52URM.scalePxInt(230) ysize 30:
            background Solid(colorPicker.hex)
            text ''

        null height x52URM.scalePxInt(5)

        hbox: # Color presents
            spacing 3
            for preset in colorPresets:
                imagebutton:
                    idle Solid(Color((preset[0], preset[1], preset[2], 175)))
                    hover Solid(Color(preset))
                    xsize 20 ysize 20
                    action SetField(colorPicker, 'rgba', preset)

        null height x52URM.scalePxInt(10)

        hbox ysize x52URM.scalePxInt(250) xsize x52URM.scalePxInt(230):
            vbox:
                text "{urm_notl}R{/urm_notl}" xalign .5 color '#ffadad' size 34 outlines [(2, '#222', 0, 0)]
                vbar xoffset 4:
                    value FieldValue(colorPicker, 'r', 255, step=1)
            vbox:
                text "{urm_notl}G{/urm_notl}" xalign .5 color '#adffad' size 34 outlines [(2, '#222', 0, 0)]
                vbar xoffset 4:
                    value FieldValue(colorPicker, 'g', 255, step=1)
            vbox:
                text "{urm_notl}B{/urm_notl}" xalign .5 color '#3572ff' size 34 outlines [(2, '#222', 0, 0)]
                vbar xoffset 4:
                    value FieldValue(colorPicker, 'b', 255, step=1)
            vbox:
                text "{urm_notl}A{/urm_notl}" xalign .5 size 34 outlines [(2, '#222', 0, 0)]
                vbar xoffset 4:
                    value FieldValue(colorPicker, 'a', 1.0, step=.1)

        hbox yoffset 10:
            textbutton '{urm_notl}Apply{/urm_notl}' action [Function(callback, colorPicker.hex), onClose]
            textbutton '{urm_notl}Cancel{/urm_notl}' action onClose

screen URM_table(spacing=2):
    vbox:
        spacing spacing
        transclude

style x52URM_tableRow is x52URM_default
style x52URM_tableRow_odd is x52URM_tableRow:
    background Solid(
        x52URM.Theme.colorAlpha(
            If(x52URM.Theme.isLightColor(x52URM.Theme.background),
                x52URM.Theme.backgroundDarker,
                x52URM.Theme.backgroundLighter,
            ),
            .5)
        )

screen URM_tableRow(rowIndex=0, fill=False):
    frame:
        style If(rowIndex % 2 == 0,'x52URM_tableRow','x52URM_tableRow_odd')
        xfill fill
        hbox:
            yminimum x52URM.scalePxInt(36)+x52URM.scalePxInt(4) # Button height + padding
            spacing 4
            transclude
