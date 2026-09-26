
# init python:
#     def codeViewTest():
#         renpy.show_screen('URM_CodeView', """
# boolVar = True
# numberVar = 1337
# stringVar = 'str'

# if var in ['test'] and 'test' in var: pass
# if is not var: pass
# if var >= 1 or var <= 1: pass
# if var < 1 and var > 1: pass
# if 1 >= var or not 1 <= var: pass
# if 1 < gina_sx and 1 > gina_af: pass

# var += 1
# var = 1 + var + 1
# var -= 1
# var = 1 - var - 1
# var *= 1
# var = 1 * var * 1
# var /= 1
# var = 1 / var / 1
# var %= 1
# var = 1 % var % 1
# var ^= 1
# var = 1 ^ var ^ 1
# var &= 1
# var = 1 & var & 1
# var |= 1
# var = 1 | var | 1
# var != 1
# obj.prop = 1

# test(var1)
# test(var1, var2)
# test(var1, var2, var3)
# test(var1, var2, var3, var4)

# class ExampleClass(ParentClass):
#     def __init__(self):
#         self.__testDict = {'key': 'val'}

#     def test(self):
#         return self.__testDict['key']

#     def test2(self, var): # Some comment
#         if var == 'test':
#             return True
#         elif 'no test' == var:
#             return False
#         elif 'not equal' != var:
#             pass
#         else:
#             return var
#         """)

# label codeViewTest(*args, **kwargs):
#     menu:
#         "Python block":
#             python:
#                 if gina_sx > 50: # Test
#                     gina_af += 10
#                 elif gina_sx < 50:
#                     gina_af += 15

#                 if 'test' in seenLabels:
#                     renpy.jump('codeViewTest')
#         "Ren'Py code" if 1 == 1:
#             if gina_sx > 50: # Test
#                 $ gina_af += 10
#             elif gina_sx < 50:
#                 $ gina_af += 15
#             else:
#                 $ gina_af += 25

#             jump codeViewTest
#         "Ren'Py call with args":
#             call codeViewTest ('arg1', arg2=2)
#             $ gina_af += 10
#         "Ren'Py call w/o args":
#             call codeViewTest
#             $ gina_af += 10
#         "Ren'Py methods":
#             python:
#                 renpy.restart_interaction()
#                 ui.reset()
#                 renpy.play('someaudio.mp3')
#                 # renpy.jump('codeViewTest')
#         "Call/Show screen":
#             call screen URM_CodeView('test')
#             show screen URM_CodeView
#             $ gina_af += 10
#             hide screen URM_CodeView
#         "Conditional dialogue":
#             if 1 == 1:
#                 "0x52" "Some dialogue"
#                 "0x52" "Some more"
#             else:
#                 "0x52" "Another dialogue"
#                 "0x52" "And some more again"
#             "0x52" "This is always there"
#         "Dialogue only":
#             "0x52" "Some dialogue"
#             "0x52" "Some more"
#     "We're done!"
#     jump codeViewTest

screen URM_CodeView(code, title='{urm_notl}Codeview{/urm_notl}', icon='\ue86f', details=None, detailsTitle=None):
    layer 'x52Overlay'
    style_prefix 'x52URM'
    default colorized = x52URM.CodeView.colorize(code)

    use x52URM_Dialog(title, Hide('URM_CodeView'), icon=icon, backgroundColor=x52URM.CodeView.colors['background'], details=details, detailsTitle=detailsTitle):
        vpgrid: # We need a vpgrid, because a viewport takes up all available height
            cols 1
            draggable True
            mousewheel True
            scrollbars "vertical"
            ymaximum x52URM.scaleY(60)

            text colorized size x52URM.scalePxInt(22) substitute False
