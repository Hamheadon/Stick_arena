from kivy.app import App
from kivy.graphics import Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput



class MyTextInput(TextInput):
    def on_focus(self, instance, value):
        if value:  # When TextInput is focused
            self.hint_text = ''  # Clear hint_text


class MyApp(App):
    def build(self):
        b = BoxLayout(orientation='vertical')
        text_input = MyTextInput(hint_text='Enter text...')
        b.add_widget(text_input)
        b.add_widget(Button(text='Click'))
        return b


if __name__ == '__main__':
    MyApp().run()