from customs import *

class LobbyScreen(StickScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arena_manager = None

    def config(self):
        print(app_pointer[0].root.screens)

    def start_game(self, *args):
        app_pointer[0].set_current_screen("gs")
        self.arena_manager = RoundManager("hamster_arena.txt")
        self.arena_manager.set_up_round()