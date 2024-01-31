import json
import random
import sys
import time
import traceback
from functools import partial
from math import tan, degrees, atan2
from threading import Thread, Lock

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

class StartPageForm(CustomWidget):
    def __init__(self, master, post_success_msg="Welcome", post_failure_msg="Something went wrong", **kwargs):
        super().__init__(master, **kwargs)
        self.post_success_msg = post_success_msg
        self.post_failure_msg = post_failure_msg

    def primary_validations_satisfied(self, *args):
        if not self.ids.username.text:
            self.ids.login_status.text = "Please enter a username!"
            return False
        elif not self.ids.pwd.text:
            self.ids.login_status.text = "Please enter a password!"
            return False
        return True

    def prepare_server_clock_vars(self):
        self.command_future_clock({"funcs_array": [lambda: screen_pointers["ss"].do_login_setups()],
                                   "clock_var": "load_status",
                                   "completion_var": "loaded",
                                   "fail_msgs": "Whoops, a non-obvious problem occurred",
                                   "fail_wid": self.ids.form_status})
        Thread(target=self.call_server, daemon=True).start()

    def call_server(self):
        pass

    def submit_form(self):
        pass

class HealthBar(BoxLayout):
    pass

class LoginForm(StartPageForm):

    def call_server(self, *args):
        self.ids.form_status.text = "One sec..."

        try:
            post_request = send_command(f"job:sign_in,name:{self.ids.username.text},password:{self.ids.pwd.text}",
                                        True, dict)
            if type(post_request) is tuple:
                if post_request[1]["status"] == "success":
                    self.ids.form_status.text = post_request[1]["success_message"]
                    self.set_clock_watch_var("load_status", "loaded")
                else:
                    self.ids.form_status.text = post_request[1]["fail_message"]

            else:
                self.ids.form_status.text = "The server is inactive right now"
        except Exception as e:
            print(f"Excepting {traceback.format_exc()}")
            self.set_clock_watch_var("load_status", "fail")

    def submit_form(self):
        if not self.primary_validations_satisfied():
            return
        self.prepare_server_clock_vars()


class SignUpForm(StartPageForm):
    def submit_form(self, *args):
        if not self.primary_validations_satisfied():
            return
        elif self.ids.pwd.text != self.ids.conf_pwd.text:
            self.ids.form_status.text = "The passwords do not match"

        else:
            self.ids.form_status.text = "One second"
            self.prepare_server_clock_vars()


    def call_server(self, *args):

        try:
            post_request = send_command(f"job:sign_up,name:{self.ids.username.text},password:{self.ids.pwd.text}",
                                        True, dict)
            if type(post_request) is tuple:
                if post_request[1]["status"] == "success":
                    self.ids.form_status.text = post_request[1]["success_message"]
                    self.set_clock_watch_var("load_status", "loaded")
                else:
                    self.ids.form_status.text = post_request[1]["fail_message"]

            else:
                self.ids.form_status.text = "The server is inactive right now"
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
        if (self.collide_widget(screen_pointers["gs"].player) and not
        self.name == screen_pointers["gs"].player.current_weapon.name):
            if "trans" not in self.source:
                self.source = "assets/mains/trans.png"
                Clock.schedule_once(self.respawn, self.respawn_time)
                screen_pointers["gs"].player.current_weapon = self
                # screen_pointers["gs"].player.ids.body.source = f"assets/anims/{self.name}.gif"
                return True

        return False

    def set_false_pos_hint(self):
        self.false_pos_hint[0] = self.x / self.parent.width
        self.false_pos_hint[1] = self.y / self.parent.height

    def set_motion_events(self):
        if self.name != "fist":
            screen_pointers["gs"].player.ids.body.source = f"assets/anims/moving_{self.name}.gif"

    def stop_motion_events(self):
        if self.name != "fist":
            screen_pointers["gs"].player.ids.body.source = f"assets/anims/{self.name}.gif"

    def on_size(self, *args):
        self.x = self.false_pos_hint[0] * self.parent.width
        self.y = self.false_pos_hint[1] * self.parent.height

    def cease_fire(self, *args):
        self.attacking = False

    def fire(self):
        if not self.attacking:
            self.attacking = True
            Thread(target=self._fire).start()

    def _fire(self, *args):
        while self.attacking:
            (screen_pointers["ls"].arena_manager.new_data_funcs.
             insert(0, partial(screen_pointers["ls"].arena_manager.check_attack_contact,
                               Window.mouse_pos, weapons_info[self.name]["damage"])))
            screen_pointers["ls"].arena_manager.check_attack_contact(*Window.mouse_pos,
                                                                     weapons_info[self.name]["damage"])
            time.sleep(weapons_info[self.name]["rate"])

    def respawn(self, *args):
        self.source = f"assets/mains/{self.name}.png"


class Player(BoxLayout):
    def __init__(self, name, personal=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.health = 100
        self.inited = False
        self.personal = personal
        self.rotation = None
        self.arena_pos = 0, 0
        self.name = name
        self.speed = 7
        self.current_weapon = Weapon("fist")
        self.source = "assets/mains/sprite.png"
        self.texture_shape = None
        self.size_hint = .11, .16
        self.false_pos_hint = [0, 0]

    def on_size(self, width, height):
        if not self.inited:
            self.bind(pos=self.binding)
            self.set_false_pos_hint()
            self.inited = True
       # self.size = .09 * width, .13 * height

        if not self.personal:
            self.x = self.false_pos_hint[0] * self.parent.width
            self.y = self.false_pos_hint[1] * self.parent.height


    def binding(self, *args):
        self.center = self.center
        self.size = self.size

    def set_false_pos_hint(self, *args):
        self.false_pos_hint[0] = self.x / self.parent.width
        self.false_pos_hint[1] = self.y / self.parent.height
    def get_shot_by(self, name):
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
            # Window.bind(on_motion=self.check_collision)
            self.inited = True


class RoundManager:
    def __init__(self, map, repeat=True, starting_player: Player = False):
        self.aim_line = None
        self.bind_func = None
        self.is_new = True
        self.map = map
        self.master = None
        self.model_player_size = None
        self.new_data_funcs = []
        self.own_player = None
        self.players = []
        self.repeat = repeat
        self.rotate_func = self.rotate_player
        self.server_data = {}
        self.keyboard_release_func = None
        self.angle = 0
        self.players_scores = {}
        self.current_arena = None
        self.angle = 0

    def check_attack_contact(self, x, y, damage):
        # y = mx + b

        slope = (y - screen_pointers["gs"].player.center_y) / (x - screen_pointers["gs"].player.center_x)
        print(f"Slope is {slope}")
        b = y - slope * x
        players_in_range = []
        player = self.current_arena.dummy_player

        for x_pos in range(int(player.x), int(player.x + screen_pointers["gs"].player.width)):
            # find slope's y and see if it is in player's y range
            if player.y <= int(x_pos * slope + b) <= player.y + player.height:
                print("...and HIT!")
                break


    def set_up_round(self):
        def sub(*args):
            self.master = screen_pointers["gs"]
            self.current_arena = Arena(self, self.map)
            self.master.add_widget(self.current_arena)
            self.master.health_bar = HealthBar()
            self.master.add_widget(self.master.health_bar)
            # self.current_arena.pos_hint = {"center": (.5, .5)}

        def _spawn(dt):
            for player in self.players:
                self.current_arena.spawn_player(player)

            self.current_arena.spawn_player(app_pointer[0].root.screens[-1].player)
            self.model_player_size = screen_pointers["gs"].player.size
            self.current_arena.spawn_player(self.current_arena.dummy_player, False, True)
            model_hint_y = self.model_player_size[1] / self.current_arena.height
            model_hint_x = self.model_player_size[0] / self.current_arena.width
            self.current_arena.dummy_player.size = model_hint_y, model_hint_x

            self.bind_func = self.current_arena.move_player
            self.keyboard_release_func = self.current_arena.stop_movement
            Window.bind(on_key_down=self.bind_func)
            Window.bind(on_key_up=self.keyboard_release_func)
            Window.bind(on_motion=self.rotate_func)

        Clock.schedule_once(sub, .8)
        Clock.schedule_once(_spawn, 1.5)

    def finish_round(self):
        pass

    def listen_for_round_data(self, *args):
        new_data = get_response(server_socket, True, dict)
        for func in self.new_data_funcs[::-1]:
            func()
            self.new_data_funcs.remove(func)

    def rotate_player(self, *args):
        player = app_pointer[0].root.screens[-1].player.ids.body
        cursor_x, cursor_y = Window.mouse_pos  # random screen for tw
        center_x, center_y = player.center

        angle = degrees(atan2(cursor_y - center_y, cursor_x - center_x))
        new_angle = angle - self.angle
        self.angle = angle
        with player.canvas.before:
            PushMatrix()
            player.parent.rotation = Rotate(angle=new_angle, origin=player.center, axis=(0, 0, 1))

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
        self.dummy_player = Player("Dam")
        self.kivy_thread_instructions = []
        self.master: RoundManager = master
        self.spawned_once = False
        self.weapons = []
        self.arena_pieces = []
        self.arena_grid = GridLayout(pos_hint={"center": (.5, .5)})
        self.blocking_pieces = []
        self.pressed_btns = []
        self.arena_info = None
        self.inited = False
        self.player_trace_line = None
        self.collision_equation: str = ""
        self.lock = Lock()
        # TODO find size_hint from uniform length of dim_strings(width) and length of DS array(height)

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

    def spawn_player(self, player, personal=True, new=True):

        spawn_point = self.arena_info["spawn_positions"][0]
        spawn_pos = list(self.arena_grid.children[spawn_point].center)
        if personal:
            player.pos_hint = {"center": (.5, .5)}
            self.center = spawn_pos
            if new:
                self.parent.add_widget(player)

        else:
            if new:
                self.parent.add_widget(player)
            player.center = spawn_pos[0], spawn_pos[1]
            print(player.parent)
            print("hey", player.pos_hint)

        if not self.spawned_once:
            for key, val in self.arena_info["weapon_positions"].items():
                wep_spawn_pos = list(self.arena_grid.children[int(key)].center)
                weapon = Weapon(val, pos=(wep_spawn_pos),
                                size_hint=(.1, .1))
                self.parent.add_widget(weapon)
                weapon.set_false_pos_hint()
                self.weapons.append(weapon)

            self.spawned_once = True

    def movement_tracker(self, code, *args):
        while self.pressed_btns:
            self.lock.acquire()

            def serve_main_thread():
                self.parent.player.rotation.origin = self.parent.player.center

            x = self.center[0]
            y = self.center[1]
            if 44 in self.pressed_btns:
                self.parent.player.current_weapon.fire()

            if extra_data["arrow_key_codes"]["left"] in self.pressed_btns:
                if self.parent.player.x >= self.arena_grid.x:
                    x += self.parent.player.speed
                    self.dummy_player.x += self.parent.player.speed
                    x_hint = x / Window.width
                    y_hint = self.pos_hint["center"][1]
                    self.pos_hint["center"] = (x_hint, y_hint)
                    # self.x += self.parent.player.speed
                    for weapon in self.weapons:
                        weapon.x += self.parent.player.speed

                    # screen_pointers["gs"].player.x -= self.parent.player.speed

            if extra_data["arrow_key_codes"]["up"] in self.pressed_btns:
                if self.parent.player.y + self.parent.player.height <= self.arena_grid.y + self.arena_grid.height:
                    y -= self.parent.player.speed
                    self.dummy_player.y -= self.parent.player.speed
                    y_hint = y / Window.height
                    x_hint = self.pos_hint["center"][0]
                    self.pos_hint["center"] = (x_hint, y_hint)
                    for weapon in self.weapons:
                        weapon.y -= self.parent.player.speed

                # screen_pointers["gs"].player.y += self.parent.player.speed

            if extra_data["arrow_key_codes"]["right"] in self.pressed_btns:
                if self.parent.player.x + self.parent.player.width <= self.arena_grid.x + self.arena_grid.width:
                    x -= self.parent.player.speed
                    self.dummy_player.x -= self.parent.player.speed
                    x_hint = x / Window.width
                    y_hint = self.pos_hint["center"][1]
                    self.pos_hint["center"] = (x_hint, y_hint)
                    for weapon in self.weapons:
                        weapon.x -= self.parent.player.speed
                    # screen_pointers["gs"].player.x += self.parent.player.speed

            if extra_data["arrow_key_codes"]["down"] in self.pressed_btns:
                if self.parent.player.y >= self.arena_grid.y:
                    y += self.parent.player.speed
                    self.dummy_player.y += self.parent.player.speed
                    y_hint = y / Window.height
                    x_hint = self.pos_hint["center"][0]
                    self.pos_hint["center"] = (x_hint, y_hint)
                    for weapon in self.weapons:
                        weapon.y += self.parent.player.speed
                    # screen_pointers["gs"].player.y -= self.parent.player.speed

            # self.kivy_thread_instructions.append(serve_main_thread)
            for player in self.master.players:
                player["sprite"].set_false_pos_hint()
            self.dummy_player.set_false_pos_hint()
            for weapon in self.weapons:
                weapon.set_false_pos_hint()
                if weapon.check_pickup_proximity():
                    break
            self.lock.release()
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
            if code in extra_data["arrow_key_codes"].values() or code == 44:
                self.pressed_btns.append(code)
            movement_thread = Thread(target=self.movement_tracker, daemon=True, args=(code,))
            movement_thread.start()
            self.parent.player.current_weapon.set_motion_events()
            # Clock.schedule_interval(self.move_on_kivy_thread, FPS)

        elif code in extra_data["arrow_key_codes"].values() or code == 44:
            self.pressed_btns.append(code)

    def stop_movement(self, instance, keyboard, code):
        self.pressed_btns.remove(code)
        if code == 44:
            self.parent.player.current_weapon.cease_fire()
        if not self.pressed_btns:
            self.parent.player.current_weapon.stop_motion_events()

    def on_size(self, *args):
        if not self.inited:
            self.set_up_dims()
            self.inited = True

    def check_collision(self):
        def _check_collision(*args):
            points = self.parent.player_trace_line.points
            slope = (points[3] - points[1]) / (points[2] - points[0])
            y_intercept = points[1] - (slope * points[0])
            self.collision_equation = f""

        Thread(target=_check_collision).start()


x = ArenaPiece("assets/hq/hq48.png")

print(x.config)
