import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout, UIAnchorLayout, UIFlatButton
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

        self.prov_manager = UIManager()
        self.prov_manager.enable()

        self.prov_anchor_layout = UIAnchorLayout()
        self.prov_box_layout = UIBoxLayout(vertical=True, space_between=10)
        self.prov_anchor_layout.add(self.prov_box_layout, anchor_x="center", anchor_y="top", align_y=-550, align_x=-600)
        self.prov_manager.add(self.prov_anchor_layout)

    def setup_prov_widgets(self):
        button_style = {
            "normal": {
                "bg": (40, 40, 40, 200),
                "font_color": (240, 240, 240),
                "font_name": ("Courier New", "Consolas", "monospace"),
                "font_size": 24,
                "border": 0,
            },
            "hover": {
                "font_color": (20, 20, 20),
                "bg": (235, 230, 220, 100),
            },
            "press": {
                "font_color": (0, 0, 0),
            },
        }
        self.prov_name_text = UILabel(
            text=self.prov_name.upper(),
            font_size=36,
            text_color=(40, 40, 40),
            font_name=("Courier New", "Consolas", "monospace")
        )
        self.prov_box_layout.add(self.prov_name_text)
    
        self.buy_army_btn = UIFlatButton(
            text="Создать армию в этой провинции",
            width=600,
            height=36,
            style=button_style
        )
        self.buy_army_btn.on_click = self.buy_army
        self.prov_box_layout.add(self.buy_army_btn)
    
        self.close_prov_btn = UIFlatButton(
            text="Закрыть",
            width=600,
            height=36,
            style=button_style
        )
        self.close_prov_btn.on_click = self.close_prov_widgets
        self.prov_box_layout.add(self.close_prov_btn)

    def buy_army(self, event):
        pass

    def close_prov_widgets(self, event):
        self.prov_box_layout.remove(self.close_prov_btn)
        self.prov_box_layout.remove(self.buy_army_btn)
        self.prov_box_layout.remove(self.prov_name_text)

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
                self.prov_name = prov.name
                self.info_box.visible = True
                self.setup_prov_widgets()
                return

        self.info_box.visible = False

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self.all_provinces.draw()

        self.gui_camera.use()
        self.manager.draw()
        self.prov_manager.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys[symbol] = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom_factor = 1.1 if scroll_y > 0 else 1 / 1.1
        self.world_camera.zoom *= zoom_factor
