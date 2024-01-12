from customs import *

class StartScreen(StickScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not arrow_keys_configured[0]:
            self.extra_on_size_funcs.append(self.show_arrows_config_prompt)