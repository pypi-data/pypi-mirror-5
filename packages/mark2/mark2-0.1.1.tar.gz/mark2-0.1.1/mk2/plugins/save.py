from mk2.plugins import Plugin
from mk2.events import Hook


class Save(Plugin):
    warn_message = "WARNING: saving map in {delay}."
    message      = "MAP IS SAVING."
    
    def setup(self):
        self.register(self.save, Hook, public=True, name='save', doc='save the map')
    
    def warn(self, delay):
        self.send_format("say %s" % self.warn_message, parseColors=True, delay=delay)
    
    def save(self, event):
        action = self.save_real
        if event.args:
            warn_length, action = self.action_chain(event.args, self.warn, action)
        action()
        event.handled = True

    def save_real(self):
        if self.message:
            self.send('say %s' % self.message, parseColors=True)
        self.send('save-all')
    
