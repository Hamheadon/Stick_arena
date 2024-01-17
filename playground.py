from kivy.app import App
from kivy.graphics import PushMatrix, Rotate, PopMatrix
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget

Builder.load_string('''
<TestKV>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: self.angle
            axis: (0, 0, 1)
            origin: self.center
    canvas.after:
        PopMatrix
''')
class TestKV(Image):
    angle = NumericProperty(0)

    def __init__(self, x, **kwargs):
        super(TestKV, self).__init__(**kwargs)
        self.x = x
        self.angle = 45

    def on_touch_down(self, touch):
        self.angle += 20
        self.x += 10

class TestPY(Image):
    def __init__(self, **kwargs):
        super(TestPY, self).__init__(**kwargs)
        # self.x = x -- not necessary, x is a property and will be handled by super()
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()
            self.rot.angle = 45
            self.rot.origin = self.center
            self.rot.axis = (0, 0, 1)
        with self.canvas.after:
            PopMatrix()

    def on_touch_down(self, touch):
        self.x += 10
        self.rot.origin = self.center  # center has changed; update here or bind instead
        self.rot.angle += 20


class MainWidget(Widget):
    #this is the main widget that contains the game.

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.all_sprites = []

        self.k = TestKV(source="myTestImage.bmp", x=10)
        self.add_widget(self.k)

        self.p = TestPY(source="myTestImage.bmp", x=200)
        self.add_widget(self.p)


class TheApp(App):

    def build(self):
        parent = Widget()
        app = MainWidget()
        parent.add_widget(app)

        return parent

if __name__ == '__main__':
    TheApp().run()
