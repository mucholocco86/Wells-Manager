
style x52URM_progressBar_back:
    background x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonBg, x52URM.Theme.colors.buttonBorder)
    padding (2, 2)

style x52URM_progressBar_back_translucent is x52URM_progressBar_back:
    background Transform(x52URM.Theme.getButtonBg(x52URM.Theme.colors.buttonBg, x52URM.Theme.colors.buttonBorder), alpha=.3)

style x52URM_progressBar_fore:
    background x52URM.Theme.secondary
    yfill True

style x52URM_progressBar_fore_translucent is x52URM_progressBar_fore:
    background Transform(x52URM.Theme.secondary, alpha=.3)

screen URM_progress():
    default hovered = False

    drag:
        draggable True
        if x52URM.Settings.progressPosition:
            pos x52URM.Settings.progressPosition
        else:
            align (.5,.5)
        dragged x52URM.progressDragged
        hovered SetLocalVariable('hovered', True)
        unhovered SetLocalVariable('hovered', False)

        use URM_progressBar(translucent=not hovered)

screen URM_progressBar(translucent=False):
    style_prefix 'x52URM'

    python:
        barWidth = x52URM.min(x52URM.max(250, x52URM.ProgressBar.textWidth), x52URM.scaleX(75))+x52URM.scalePxInt(18)

    frame:
        style_suffix If(translucent, 'progressBar_back_translucent', 'progressBar_back')
        xysize (int(barWidth)+4, x52URM.scalePxInt(40))
        frame style_suffix If(translucent, 'progressBar_fore_translucent', 'progressBar_fore') xsize int(barWidth*(x52URM.ProgressBar.percentage/100))
        text x52URM.ProgressBar.text yalign .5 xalign .5
