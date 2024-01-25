from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window


class KeyBindingApp(App):
    def build(self):
        self.label = Label(text="Press a key", font_size=30)
        # Bind the on_key_down event
        Window.bind(on_key_down=self.on_key_down)
        return self.label

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        self.label.text = f"Key down: {text} | Keycode: {keycode}"

    def unbind_key_event(self):
        # Unbind the on_key_down event for the on_key_down method
        Window.unbind(on_key_down=self.on_key_down)


if __name__ == '__main__':
    app = KeyBindingApp()
    app.run()
    # Unbind the key event when the application is about to exit
    app.unbind_key_event()
