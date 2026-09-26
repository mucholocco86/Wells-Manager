
init 999 python in x52URM:
    _constant = True

    class ExceptionHandler(x52NonPicklable):
        def __init__(self):
            if hasattr(renpy.config, 'exception_handler'):
                self._m1_ExceptionHandler__originalCustomHandler = renpy.config.exception_handler
                renpy.config.exception_handler = self._m1_ExceptionHandler__createHandler()
        
        def _m1_ExceptionHandler__createHandler(self):
            def handler(short, full, traceback_fn):
                
                try:
                    f = renpy.os.open(traceback_fn, renpy.os.O_WRONLY | renpy.os.O_APPEND)
                    renpy.os.write(f, '0x52 URM {}'.format(version)) 
                    renpy.os.close(f)
                except Exception as e:
                    print('0x52: Failed to write to traceback file: {}'.format(e))
                
                if self._m1_ExceptionHandler__originalCustomHandler:
                    return self._m1_ExceptionHandler__originalCustomHandler(short, full, traceback_fn)
                else:
                    return False
            
            return handler


    ExceptionHandler()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
