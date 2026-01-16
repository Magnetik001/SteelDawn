import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout

import json

import province


class Game(arcade.View):
    def __init__(self):
        super().__init__()

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.all_provinces = arcade.SpriteList()
        self.player_sprite = None

        self.pan_speed = 5.0
        self.keys = {
            arcade.key.W: False,
            arcade.key.S: False,
            arcade.key.A: False,
            arcade.key.D: False,
        }

        self.manager = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

        with open("provinces.json", mode="r", encoding="utf-8") as file:
            data = json.load(file)
            for i in data:
                prov = province.Province(f"images/{i}.png", data[i]["center_x"], data[i]["center_y"], data[i]["color"])
                self.all_provinces.append(prov)

        self.world_camera.position = (self.window.width / 2, self.window.height / 2)

        self.manager = UIManager(self.window)
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=28)
        self.setup_widgets()

        self.anchor_layout.add(self.box_layout, anchor_x="center", anchor_y="top", align_y=-170)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        ...

    def on_hide_view(self):
        if self.manager:
            self.manager.disable()

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

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol in self.keys:
            self.keys[symbol] = True

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in self.keys:
            self.keys[symbol] = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        zoom_factor = 1.1 if scroll_y > 0 else 1 / 1.1
        self.world_camera.zoom *= zoom_factor

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self.all_provinces.draw()

        if self.manager:
            self.gui_camera.use()
            self.manager.draw()