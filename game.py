import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout
import json
import province


class Game(arcade.View):
    def __init__(self):
        super().__init__()

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.all_provinces = arcade.SpriteList()

        self.pan_speed = 10.0
        self.keys = {key: False for key in (arcade.key.W, arcade.key.S, arcade.key.A, arcade.key.D)}

        self.manager = None
        self.info_box = None
        self.info_label = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

        with open("provinces.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            for name in data:
                prov = province.Province(
                    f"images/{name}.png",
                    data[name]["center_x"],
                    data[name]["center_y"],
                    data[name]["color"],
                    name,
                    data[name]["resource"]
                )
                prov.set_hit_box(prov.texture.hit_box_points)
                self.all_provinces.append(prov)

        self.manager = UIManager()
        self.manager.enable()

        self.info_label = UILabel(
            text="",
            text_color=arcade.color.BLACK,
            font_size=12,
            multiline=True,
            width=250
        )

        self.info_box = UIBoxLayout(vertical=True)
        self.info_box.add(self.info_label)

        self.manager.add(self.info_box.with_space_around(left=10, bottom=10))

        self.info_box.visible = False

    def on_update(self, delta_time: float):
        x, y = self.world_camera.position
        if self.keys[arcade.key.W]:
            y += self.pan_speed
        if self.keys[arcade.key.S]:
            y -= self.pan_speed
        if self.keys[arcade.key.A]:
            x -= self.pan_speed
        if self.keys[arcade.key.D]:
            x += self.pan_speed

        self.world_camera.position = (x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        world_x, world_y, _ = self.world_camera.unproject((x, y))

        for prov in self.all_provinces:
            if prov.collides_with_point((world_x, world_y)):
                text = (
                    f"Province: {prov.name}\n"
                    f"Color: {prov.color}\n"
                    f"Resources: {prov.resource}"
                )
                self.info_label.text = text
                self.info_box.visible = True
                return

        self.info_box.visible = False

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self.all_provinces.draw()

        self.gui_camera.use()
        self.manager.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys[symbol] = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom_factor = 1.1 if scroll_y > 0 else 1 / 1.1
        self.world_camera.zoom *= zoom_factor
