import arcade

import menu

class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 500, "Steel Dawn")

    def setup(self):
        self.show_view(menu.Menu())

if __name__ == "__main__":
    window = MainWindow()
    window.setup()
    arcade.run()