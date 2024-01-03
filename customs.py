import sys
from threading import Thread
from extra_functions import *
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Ellipse
from kivy.graphics import Line
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

Builder.load_file("Stick.kv")

arena_piece_configs = {"hq48.png": (0, 0)}


premade_arena_piece_meta = {}



def drop_anim(wid, direction="down", on_complete=None, *args):
    if direction == "down":
        new_hint = {"center": (.5, -1)}
    elif direction == "up":
        new_hint = {"center": (.5, 1)}
    elif direction == "left":
        new_hint = {"center": (-1, .5)}
    elif direction == "right":
        new_hint = {"center": (1, .5)}
    else:
        print("Invalid direction")
        return
    anim = Animation(pos_hint=new_hint, duration=.7)
    anim.bind(on_complete=on_complete)
    anim.start(wid)

def raise_anim(wid, *args):
    anim = Animation(pos_hint={"center": (.5, .5)}, duration=.8)
    anim.start(wid)

def str_to_class(class_name):
    class_obj = getattr(sys.modules[__name__], class_name)
    return class_obj

class StickInput(TextInput):
    hint_msg = StringProperty("")

    def __init__(self, hint_msg=None, **kwargs):
        super().__init__(**kwargs)
        if hint_msg:
            self.hint_msg = hint_msg
        self.hint_text = self.hint_msg

class CustomWidget(BoxLayout):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.inited = False
        self.master = master
        self.on_size_funcs = []

    def on_size(self, *args):
        if not self.inited:
            for func in self.on_size_funcs:
                func()
            self.inited = True


class SignUpForm(CustomWidget):
    def submit_form(self, *args):
        if self.ids.pwd.text != self.ids.conf_pwd.text:
            self.ids.sign_up_status.text = "The passwords do not match"
        elif not self.ids.username.text:
            self.ids.sign_up_status.text = "Please enter a username!"
        else:
            self.ids.sign_up_status.text = "One second"
            Thread(target=self.call_server, daemon=True).start()

    def call_server(self, *args):
        post_request = send_command(f"job:sign_up,name:{self.ids.username.text},password:{self.ids.pwd.text}",
                                    True, dict)
        if type(post_request) is tuple:
            self.ids.sign_up_status.text = "Successfully signed up!"
        else:
            self.ids.sign_up_status.text = "The server is inactive right now"






class StickButton(Button):
    master = None
    release_func = None
    def __init__(self, master=None, release_func=None, **kwargs):
        super().__init__(**kwargs)
        if master:
            self.master = master
        if release_func:
            self.release_func = release_func
        if self.master:
            self.bind(on_release=self.on_release)
        self.on_release = self.secure_release

    def secure_release(self, *args):
        if self.master:
            if self.master.current_active_widget:
                return
        self.release_func()

    def on_release(self, *args):
        if self.master.current_active_widget:
            return
        print("releasing")
        super().on_release()
class StickScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_active_widget = None

    def drop_widget(self, *args):
        def nullify(*args):
            self.current_active_widget = None
        if self.current_active_widget:
            drop_anim(self.current_active_widget, on_complete=nullify)

    def raise_widget(self, class_name: str, direction="left", *args):
        widget_class = str_to_class(class_name)
        if self.current_active_widget:
            self.drop_widget()
        self.current_active_widget = widget_class(master=self)
        self.add_widget(self.current_active_widget)
        raise_anim(self.current_active_widget)




class Player(Ellipse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.health = 100
        self.arena_pos = 0, 0
        self.speed = 5

    def on_size(self, width, height):
        self.size = (width * .08, height * .08)

    def move(self):
        pass


class ArenaPiece(FloatLayout):
    source = StringProperty("")

    def __init__(self, source: str, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.config = arena_piece_configs[self.source.split("/")[-1]]
        self.inited = False


    def on_size(self, *args):
        if not self.inited:
            #Window.bind(on_motion=self.check_collision)
            self.inited = True


class RoundManager:
    def __init__(self, map):
        self.map = map
        self.players = []
        self.players_scores = {}

    def set_up_round(self):
        pass


    def finish_round(self):
        pass

class Arena(GridLayout, CustomWidget):
    def __init__(self, dimensions, *args, **kwargs):
        # pos_hint will always be .5, .5 to center
        super().__init__()
        self.dimension_strings = dimensions
        self.cols = len(self.dimension_strings)
        self.arena_pieces = []
        self.blocking_pieces = []
        self.player_trace_line = None
        self.collision_equation: str = ""
        #TODO find size_hint from uniform length of dim_strings(width) and length of DS array(height)

    def set_up_dims(self):
        pass

    def check_collision(self):
        def _check_collision(*args):
            points = self.parent.player_trace_line.points
            slope = (points[3] - points[1])/(points[2] - points[0])
            y_intercept = points[1] - (slope * points[0])
            self.collision_equation = f""

        Thread(target=_check_collision).start()

x = ArenaPiece("assets/hq/hq48.png")

print(x.config)
