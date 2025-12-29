import arcade
import menu

class GameWindow(arcade.Window):
    def __init__(self, width=1280, height=720, title="Стальной рассвет"):
        super().__init__(width, height, title)
        self.width = width
        self.height = height

    def setup(self):
        self.show_view(menu.Menu())

if __name__ == "__main__":
    window = GameWindow()
    window.setup()
    arcade.run()