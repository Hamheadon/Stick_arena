from .LobbyScreen.LobbyScreen import LobbyScreen
from .StartScreen.StartScreen import StartScreen

ss = StartScreen
ls = LobbyScreen
screen_dict = {"ss": {"view": ss,
                      "kv": "screens/StartScreen/StartScreen.kv"},
               "ls": {"view": ls,
                      "kv": "screens/LobbyScreen/LobbyScreen.kv"}}
