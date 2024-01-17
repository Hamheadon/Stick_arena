from customs import *


class GameScreen(StickScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = None
