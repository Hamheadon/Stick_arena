from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from screens import *
from screens.screen import screen_dict


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


app = StickApp(title='Stick Arena')

if __name__ == '__main__':
    app.run()
