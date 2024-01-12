from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window


class MultiKeyApp(App):
    def build(self):
        self.label = Label(text="Press two keys simultaneously", font_size=20)
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        return self.label

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        self.label.text = f"Keys down: {text} | Modifiers: {keycode}"
        print(f"Keys down: {text} and keycode: {keycode}")

    def on_key_up(self, instance, keyboard, keycode):
        print(f"keycode: {keycode}")
        self.label.text = "Press two keys simultaneously"


if __name__ == '__main__':
    MultiKeyApp().run()
