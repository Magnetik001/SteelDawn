import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout, UIMessageBox, UIAnchorLayout
import json
import province


class Game(arcade.View):
    def __init__(self, year: int, country: str):
        super().__init__()

        self.year = year
        self.country = country

        print(year, country)

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.all_provinces = arcade.SpriteList()

        self.pan_speed = 20.0
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

    def show_message(self):
        self.message_box = UIMessageBox(
            width=300, height=200,
            message_text=self.prov_name.upper(),
            buttons=("Купить армию", "Закрыть")
        )
        self.message_box.on_action = self.on_message_button
        self.prov_manager.add(self.message_box)
        self.message_box.with_padding(top=20, left=10, right=10, bottom=10)

    def on_message_button(self, button_text):
        if button_text == "Закрыть":
            self.close_message()
        else:
            self.buy_army()

    def buy_army(self):
        pass

    def close_message(self):
        self.message_box.clear()

    def on_show_view(self):
        self.texture = arcade.load_texture("/home/davidenkomi-1/PycharmProjects/SteelDawn/water-background_87394-3060 (1).jpg")


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
                self.all_provinces.append(prov)

        self.manager = UIManager()
        self.manager.enable()

        if self.country == "GER":
            self.world_camera.position = (2544, 2670)

        self.info_label = UILabel(
            text="",
            text_color=arcade.color.BLACK,
            font_size=12,
            multiline=True,
            width=250
        )


        self.info_box = UIBoxLayout(vertical=True)
        self.info_box.add(self.info_label)

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
                self.show_message()
                self.info_box.visible = True

                self.world_camera.position = (prov.center_x, prov.center_y)

                return

        self.info_box.visible = False

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture, arcade.rect.XYWH(1960 // 2, 1080 // 2, 1960, 1080))

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