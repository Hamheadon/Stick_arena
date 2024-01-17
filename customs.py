import json
import random
import sys
import time
from functools import partial
from math import tan, degrees, atan2
from threading import Thread

from kivy.uix.label import Label

from extra_functions import *
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Ellipse, Rotate, PushMatrix, PopMatrix
from kivy.graphics import Line
from kivy.lang import Builder
from kivy.properties import StringProperty, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.core.window import Window

Builder.load_file("Stick.kv")
arrow_keys_configured = [False]
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
        self.clock_vars = {}

    def on_size(self, *args):
        if not self.inited:
            for func in self.on_size_funcs:
                func()
            self.inited = True

    def command_future_clock(self, params: dict):
        """
        fail_msgs: a dict containing fail message-description pairs to display if the clock var is set to something
        else.
        fail_wid: the widget, preferably a label, to display the selected fail message

        :param params: funcs_array, clock_var, completion_var, fail_msgs (optional), fail_wid - same context as fail_msg
        :return:
        """
        self.clock_vars[params["clock_var"]] = [params["completion_var"], "neutral"]

        def clock_subprocess(*args):
            if self.clock_vars[params["clock_var"]][0] == self.clock_vars[params["clock_var"]][1]:
                for func in params["funcs_array"]:
                    func()
                Clock.unschedule(clock_subprocess)
            elif self.clock_vars[params["clock_var"]][1] != "neutral":
                Clock.unschedule(clock_subprocess)
                if "fail_msgs" in params:
                    params["fail_wid"].text = params["fail_msgs"]

            print("Clock sub Still waiting")
        Clock.schedule_interval(clock_subprocess, .2)

    def set_clock_watch_var(self, var, val):
        self.clock_vars[var][1] = val


class SignUpForm(CustomWidget):
    def submit_form(self, *args):
        if self.ids.pwd.text != self.ids.conf_pwd.text:
            self.ids.sign_up_status.text = "The passwords do not match"
        elif not self.ids.username.text:
            self.ids.sign_up_status.text = "Please enter a username!"
        else:
            self.ids.sign_up_status.text = "One second"
            self.command_future_clock({"funcs_array": [lambda: app_pointer[0].set_current_screen("ls")],
                                       "clock_var": "load_status",
                                       "completion_var": "loaded",
                                       "fail_msgs": "Whoops, a non-obvious problem occurred",
                                       "fail_wid": self.ids.sign_up_status})
            Thread(target=self.call_server, daemon=True).start()


    def call_server(self, *args):
        try:
            post_request = send_command(f"job:sign_up,name:{self.ids.username.text},password:{self.ids.pwd.text}",
                                        True, dict)
            if type(post_request) is tuple:
                self.ids.sign_up_status.text = "Successfully signed up!"
                self.set_clock_watch_var("load_status", "loaded")
                app_pointer[0].set_current_screen("ls")
            else:
                self.ids.sign_up_status.text = "The server is inactive right now"
        except Exception as e:
            print(e)
            self.set_clock_watch_var("load_status", "fail")






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


class StickImage(Image):
    pass

class StickScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_active_widget = None
        self.extra_on_size_funcs = []
        self.inited = False
        self.collected_arrow_key_codes = []
        self.config_func = None
        screen_pointers[self.name] = self

    def drop_widget(self, *args):
        def nullify(*args):
            self.remove_widget(self.current_active_widget)
            self.current_active_widget = None
        if self.current_active_widget:
            drop_anim(self.current_active_widget, on_complete=nullify)


    def on_size(self, *args):
        if not self.inited:
            for func in self.extra_on_size_funcs:
                func()
            self.inited = True

    def raise_widget(self, class_name: str, direction="left", *args):
        widget_class = str_to_class(class_name)
        if self.current_active_widget:
            self.drop_widget()
        self.current_active_widget = widget_class(master=self)
        self.add_widget(self.current_active_widget)
        raise_anim(self.current_active_widget)

    def show_arrows_config_prompt(self):
        self.current_active_widget = FloatLayout()
        bg = StickImage(source="assets/mains/wp.jpeg")
        config_msg = Label(text="Press your arrow keys in this order: left, up, right, down",
                           halign="center", valign="center", color=(1, 1, 1, 1))
        self.current_active_widget.add_widget(bg)
        self.current_active_widget.add_widget(config_msg)
        self.add_widget(self.current_active_widget)
        self.config_func = self.arrow_keys_config_listener
        Window.bind(on_key_down=self.config_func)

    def arrow_keys_config_listener(self, *args):
        print("Listening...")
        self.collected_arrow_key_codes.append(args[2])
        self.current_active_widget.children[0].text = random.choice(("And the next...", "Keep going"))

        if len(self.collected_arrow_key_codes) >= 4:
            Window.unbind(on_key_down=self.config_func)
            extra_data["arrow_key_codes"]["left"] = self.collected_arrow_key_codes[0]
            extra_data["arrow_key_codes"]["up"] = self.collected_arrow_key_codes[1]
            extra_data["arrow_key_codes"]["right"] = self.collected_arrow_key_codes[2]
            extra_data["arrow_key_codes"]["down"] = self.collected_arrow_key_codes[3]
            self.drop_widget()
            print("Finished")


class Weapon(Image):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.false_pos_hint = [0, 0]
        self.name = name
        self.respawn_time = 15
        self.attacking = False
        self.source = f"assets/mains/{self.name}.png"

    def check_pickup_proximity(self):
        if self.collide_widget(screen_pointers["gs"].player):
            if "trans" not in self.source:
                self.source = "assets/mains/trans.png"
                Clock.schedule_once(self.respawn, self.respawn_time)
                screen_pointers["gs"].player.current_weapon = self
                return True

        return False
    def set_false_pos_hint(self):
        self.false_pos_hint[0] = self.x/self.parent.width
        self.false_pos_hint[1] = self.y / self.parent.height

    def on_size(self, *args):
        self.x = self.false_pos_hint[0] * self.parent.width
        self.y = self.false_pos_hint[1] * self.parent.height

    def fire(self):
        while self.attacking:
            (screen_pointers["ls"].arena_manager.new_data_funcs.
             append(partial(screen_pointers["ls"].arena_manager.check_attack_contact,
                            Window.mouse_pos, weapons_info[self.name]["damage"])))


    def respawn(self, *args):
        self.source = f"assets/mains/{self.name}.png"




class Player(BoxLayout):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.health = 100
        self.inited = False
        self.rotation = None
        self.arena_pos = 0, 0
        self.name = name
        self.speed = 7
        self.current_weapon = Weapon("fist")
        self.source = "assets/mains/sprite.png"
        self.texture_shape = None
        self.size_hint = .11, .22

    def on_size(self, width, height):
        if not self.inited:
            self.bind(pos=self.binding)
            self.inited = True


    def binding(self, *args):
        self.center = self.center
        self.size = self.size

    def pick_up_weapon(self, weapon_name: str):
        self.current_weapon = Weapon(weapon_name)


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
    def __init__(self, map, repeat=True, starting_player: Player = False):
        self.aim_line = None
        self.bind_func = None
        self.is_new = True
        self.map = map
        self.master = None
        self.new_data_funcs = []
        self.own_player = None
        self.players = []
        self.repeat = repeat
        self.rotate_func = self.rotate_player
        self.keyboard_release_func = None
        self.angle = 0
        self.players_scores = {}
        self.current_arena = None
        self.angle = 0

    def check_attack_contact(self, x, y, damage, opp_positions):
        slope = (y - screen_pointers["gs"].player.center_y)/(x - screen_pointers["gs"].player.center_x)


    def set_up_round(self):
        def sub(*args):
            self.master = screen_pointers["gs"]
            self.current_arena = Arena(self, self.map)
            self.master.add_widget(self.current_arena)
            self.current_arena.pos_hint = {"center": (.5, .5)}
        def _spawn(dt):
            for player in self.players:
                self.current_arena.spawn_player(player)

            self.current_arena.spawn_player(app_pointer[0].root.screens[-1].player)
            self.bind_func = self.current_arena.move_player
            self.keyboard_release_func = self.current_arena.stop_movement
            Window.bind(on_key_down=self.bind_func)
            Window.bind(on_key_up=self.keyboard_release_func)
            Window.bind(on_motion=self.rotate_func)




        Clock.schedule_once(sub, .8)
        Clock.schedule_once(_spawn, 1.3)

    def finish_round(self):
        pass

    def listen_for_round_data(self, *args):
        new_data = get_response(server_socket, True, dict)
        for func in self.new_data_funcs:
            func()
            self.new_data_funcs.remove(func)

    def rotate_player(self, *args):
        player = app_pointer[0].root.screens[-1].player.ids.body
        cursor_x, cursor_y = Window.mouse_pos #random screen for tw
        center_x, center_y = player.center

        angle = degrees(atan2(cursor_y - center_y, cursor_x - center_x))
        new_angle = angle - self.angle
        self.angle = angle
        with player.canvas.before:
            PushMatrix()
            if not player.parent.rotation:
                player.parent.rotation = Rotate(angle=new_angle, origin=player.center, axis=(0, 0, 1))
            else:
                player.parent.rotation.angle = new_angle
              #  player.parent.rotation.origin = player.center

        with player.canvas.after:
            PopMatrix()




    def add_player(self, player: Player, is_my_player=False):
        self.players.append(player)
        if is_my_player:
            self.own_player = player
        self.current_arena.spawn_player(player)

class Arena(FloatLayout):
    def __init__(self, master, dimensions_path, *args, **kwargs):
        # pos_hint will always be .5, .5 to center
        super().__init__()
        self.dimensions = dimensions_path
        self.kivy_thread_instructions = []
        self.master = master
        self.weapons = []
        self.arena_pieces = []
        self.arena_grid = GridLayout()
        self.blocking_pieces = []
        self.pressed_btns = []
        self.arena_info = None
        self.inited = False
        self.player_trace_line = None
        self.collision_equation: str = ""
        #TODO find size_hint from uniform length of dim_strings(width) and length of DS array(height)

    def set_up_dims(self):
        self.size_hint = .15, .15
        self.pos_hint = {"center": (.5, .5)}
        self.add_widget(self.arena_grid)
        initial_size_hint_y = self.size_hint_y
        with open("maps.json", "r") as dimensions_file:
            self.arena_info = json.load(dimensions_file)[self.dimensions]

        self.arena_grid.size_hint = 1, 1
        derived_rows = len(self.arena_info['dimensions'][0].split(","))

        self.arena_grid.cols = derived_rows
        self.size_hint_x *= self.arena_grid.cols
        for i in self.arena_info["dimensions"]:
            stripped = i.replace("\n", "")
            piece_row = stripped.split(",")
            for piece_name in piece_row:
                if piece_name == "0":
                    self.arena_grid.add_widget(StickImage(source=f"assets/mains/trans.png"))
                else:
                    self.arena_grid.add_widget(StickImage(source=f"assets/{self.dimensions}/{piece_name}.png"))
            self.size_hint_y += initial_size_hint_y


        def set_center(dt):
            self.arena_grid.center = self.center

        Clock.schedule_once(set_center, .1)
    def spawn_player(self, player):

        spawn_point = self.arena_info["spawn_positions"][0]
        spawn_pos = list(self.arena_grid.children[spawn_point].pos)
        self.pos_hint = {"center": (.5, .5)}
        self.parent.add_widget(player)
        player.pos = spawn_pos
        for key, val in self.arena_info["weapon_positions"].items():
            wep_spawn_pos = list(self.arena_grid.children[int(key)].center)
            weapon = Weapon(val, pos=(wep_spawn_pos),
                            size_hint=(.1, .1))
            self.parent.add_widget(weapon)
            weapon.set_false_pos_hint()
            self.weapons.append(weapon)


    def movement_tracker(self, code, *args):
        while self.pressed_btns:
            def serve_main_thread():
                self.parent.player.rotation.origin = self.parent.player.center

            if extra_data["arrow_key_codes"]["left"] in self.pressed_btns:
                if self.parent.player.x >= self.arena_grid.x:
                    #self.arena_grid.x += self.parent.player.speed
                    for weapon in self.weapons:
                        weapon.x += self.parent.player.speed

                    screen_pointers["gs"].player.x -= self.parent.player.speed


            if extra_data["arrow_key_codes"]["up"] in self.pressed_btns:
                if self.parent.player.y + self.parent.player.height <= self.arena_grid.y + self.arena_grid.height:
                    #self.arena_grid.y -= self.parent.player.speed
                    for weapon in self.weapons:
                        weapon.y -= self.parent.player.speed

                    screen_pointers["gs"].player.y += self.parent.player.speed

            if extra_data["arrow_key_codes"]["right"] in self.pressed_btns:
                if self.parent.player.x + self.parent.player.width <= self.arena_grid.x + self.arena_grid.width:
                    #self.arena_grid.x -= self.parent.player.speed
                    for weapon in self.weapons:
                        weapon.x -= self.parent.player.speed
                    screen_pointers["gs"].player.x += self.parent.player.speed


            if extra_data["arrow_key_codes"]["down"] in self.pressed_btns:
                if self.parent.player.y >= self.arena_grid.y:
                    #self.arena_grid.y += self.parent.player.speed
                    for weapon in self.weapons:
                        weapon.y += self.parent.player.speed
                    screen_pointers["gs"].player.y -= self.parent.player.speed

            #self.kivy_thread_instructions.append(serve_main_thread)

            for weapon in self.weapons:
                weapon.set_false_pos_hint()
                if weapon.check_pickup_proximity():
                    break

            time.sleep(FPS)

    def move_on_kivy_thread(self, *args):
        has_executed_one = False
        if has_executed_one and not self.kivy_thread_instructions:
            Clock.unschedule(self.move_on_kivy_thread)


    def move_player(self, *args):
        code = args[2]
        if code in self.pressed_btns:
            return
        if not self.pressed_btns:
            self.pressed_btns.append(code)
            movement_thread = Thread(target=self.movement_tracker, daemon=True, args=(code,))
            movement_thread.start()
            Clock.schedule_interval(self.move_on_kivy_thread, FPS)

        else:
            self.pressed_btns.append(code)

    def stop_movement(self, instance, keyboard, code):
        self.pressed_btns.remove(code)



    def on_size(self, *args):
        if not self.inited:
            self.set_up_dims()
            self.inited = True





    def check_collision(self):
        def _check_collision(*args):
            points = self.parent.player_trace_line.points
            slope = (points[3] - points[1])/(points[2] - points[0])
            y_intercept = points[1] - (slope * points[0])
            self.collision_equation = f""

        Thread(target=_check_collision).start()

x = ArenaPiece("assets/hq/hq48.png")

print(x.config)
