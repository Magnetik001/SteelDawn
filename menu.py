import arcade


class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        self.setup()


    def setup(self):
        self.texture = arcade.load_texture("images/backgrounds/menu_bg1.png")

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height))
