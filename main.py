from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager
from screens import *
from screens.screen import screen_dict
from customs import app_pointer

class StickManager(ScreenManager):
    pass


class StickApp(App):

    def build(self):
        self.root = StickManager()
        self.set_current_screen("ss")
        return self.root


    def set_current_screen(self, name: str, first: bool = False, switch: bool = True):
        if not self.root.has_screen(name):
            Builder.load_file(screen_dict[name]["kv"])
            self.root.add_widget(screen_dict[name]["view"]())
        if switch:
            self.root.current = name

    def on_stop(self):
        from extra_functions import server_socket, send_command
        if server_socket:
            send_command("leave")


app_pointer[0] = StickApp(title='Stick Arena')

if __name__ == '__main__':
    app_pointer[0].run()
