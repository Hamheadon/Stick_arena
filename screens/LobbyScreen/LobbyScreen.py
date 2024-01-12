from customs import *

class LobbyScreen(StickScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arena_manager = None

    def config(self):
        print(app_pointer[0].root.screens)

    def start_game(self, *args):
        app_pointer[0].set_current_screen("gs")
        app_pointer[0].root.screens[-1].player = Player(name="hammed")
        self.arena_manager = RoundManager("hamsterdam")
        self.arena_manager.set_up_round()