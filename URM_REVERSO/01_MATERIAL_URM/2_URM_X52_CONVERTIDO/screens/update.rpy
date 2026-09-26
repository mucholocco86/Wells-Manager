
screen URM_update(isNotification=False):
    layer 'x52Overlay'
    style_prefix 'x52URM'

    on 'show' action If(x52URM.API.updates==None, Function(x52URM.API.fetchUpdate, renpy.restart_interaction, renpy.restart_interaction), None)

    use x52URM_Dialog('Update URM', closeAction=Hide('URM_update'), modal=True, icon='\ue923'):
        if isNotification:
            label '{urm_notl}Update available!{/urm_notl}'

        hbox:
            text '{urm_notl}Your version: {/urm_notl}'
            label "[x52URM.version]"
        hbox:
            text '{urm_notl}Latest version: {/urm_notl}' yalign .5
            label x52URM.API.updateAvailable or 'N/A' yalign .5
            if x52URM.API.updateAvailable:
                null width 5
                use x52URM_iconButton('\uf090', '{urm_notl}Install{/urm_notl}', action=[Hide('URM_main'),Hide('URM_update'),Show('URM_performupdate')])
                if isNotification: # Add options to skip version
                    null width x52URM.scalePxInt(10)
                    use x52URM_iconButton('\ue044', '{urm_notl}Skip this version{/urm_notl}', action=[SetField(x52URM.Settings, 'skipUpdate', x52URM.API.updateAvailable),Hide('URM_update')])

        label '{urm_notl}Changelog{/urm_notl}' yoffset 2
        frame style_suffix "seperator" ysize x52URM.scalePxInt(2) xsize x52URM.scalePxInt(650)
        null height x52URM.scalePxInt(10)
        viewport:
            ysize x52URM.scalePxInt(250) xsize x52URM.scalePxInt(650)
            draggable True
            mousewheel True
            scrollbars "vertical"
            
            vbox:
                if x52URM.API.updates != None:
                    if x52URM.API.updateAvailable:
                        for update in x52URM.API.updates: # Changelog version
                            hbox:
                                label update['versionName']
                                if update['channel'] == 'beta':
                                    text ' (beta)'
                                text ' '+update['createdAt'].split('T')[0]
                            text update['changelog'] substitute False
                            null height 10
                    else:
                        text '{urm_notl}No update available{/urm_notl}'
                elif x52URM.API.latestError:
                    use x52URM_messagebar('error', x52URM.API.latestError, substitute=False)
                else:
                    text '{urm_notl}Fetching update information...{/urm_notl}'


screen URM_performupdate():
    layer 'x52Overlay'
    style_prefix 'x52URM'

    on 'show' action Function(x52URM.API.performUpdate, x52URM.Settings.updateChannel, URMFunctionWithArgs(renpy.restart_interaction), URMFunctionWithArgs(renpy.restart_interaction))

    use x52URM_Dialog('{urm_notl}Performing update{/urm_notl}', modal=True, icon='\uf001'):
        vbox xminimum x52URM.scalePxInt(450) spacing 20:
            if x52URM.API.isUpdating:
                text '{urm_notl}Installing update...{/urm_notl}' align (.5,.5)
            elif x52URM.API.latestError:
                use x52URM_messagebar('error', x52URM.API.latestError, substitute=False)
                textbutton '{urm_notl}Close{/urm_notl}' xalign .5 action Hide('URM_performupdate')
            else:
                label '{urm_notl}Update completed{/urm_notl}' xalign .5
                textbutton '{urm_notl}Apply update{/urm_notl}' xalign .5 action [Hide('URM_performupdate'),Hide('URM_main'),Function(renpy.reload_script)]
