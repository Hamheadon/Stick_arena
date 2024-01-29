from customs import *

class StartScreen(StickScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not arrow_keys_configured[0]:
            self.extra_on_size_funcs.append(self.show_arrows_config_prompt)

    def do_login_setups(self, *args):
        app_pointer[0].set_current_screen("ls")
        Thread(target=get_response,  args=(server_socket, True, dict, screen_pointers["ls"], "lobby_data"),
               daemon=True).start()
        Clock.schedule_interval(screen_pointers["ls"].update_data_ui, 2)