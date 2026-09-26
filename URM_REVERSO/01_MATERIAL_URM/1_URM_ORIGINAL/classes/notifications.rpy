
init 3 python in x52URM:
    _constant = True

    class NotificationsClass(x52NonPicklable):
        def __init__(self):
            self.notifications = []
        
        def add(self, **kwargs):
            notif = Notification(self, **kwargs)
            self.notifications.append(notif)
            renpy.restart_interaction()
            
            if Settings.notificationTimeout:
                def startTimeout():
                    import time
                    time.sleep(Settings.notificationTimeout)
                    self.notifications.remove(notif)
                renpy.invoke_in_thread(startTimeout)
        
        def remove(self, notif):
            if notif in self.notifications:
                self.notifications.remove(notif)
                renpy.restart_interaction()
        
        def clear(self):
            self.notifications = []

    class Notification(x52NonPicklable):
        def __init__(self, notifCls, label, text=None, action=None):
            self.notifCls = notifCls
            self.label = label
            self.text = text
            self.action = action
        
        def close(self):
            self.notifCls.remove(self)
        
        def __call__(self):
            if self.action:
                if isinstance(self.action, list):
                    [action() for action in self.action]
                else:
                    self.action()
            self.close()
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
