from .GameScreen.GameScreen import GameScreen
from .LobbyScreen.LobbyScreen import LobbyScreen
from .StartScreen.StartScreen import StartScreen

ss = StartScreen
ls = LobbyScreen
gs = GameScreen
screen_dict = {"ss": {"view": ss,
                      "kv": "screens/StartScreen/StartScreen.kv"},
               "ls": {"view": ls,
                      "kv": "screens/LobbyScreen/LobbyScreen.kv"},
               "gs": {"view": gs,
                      "kv": "screens/GameScreen/GameScreen.kv"}}
