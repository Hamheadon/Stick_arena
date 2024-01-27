from customs import *

class LobbyScreen(StickScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arena_manager = None
        self.lobby_data = {}
        self.game_names = []

    def config(self):
        print(app_pointer[0].root.screens)

    def join_game(self, *args):
        pass

    def update_data_ui(self, *args):
        self.ids.games_list.clear_widgets()
        names = list(self.lobby_data["games"].keys())
        names.sort()
        for name in names:
            self.ids.games_list.add_widget(Button(text=name, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1)))



    def start_game(self, *args):
        app_pointer[0].set_current_screen("gs")
        app_pointer[0].root.screens[-1].player = Player(name="hammed", personal=True)
        self.arena_manager = RoundManager("hamsterdam")
        self.arena_manager.set_up_round()