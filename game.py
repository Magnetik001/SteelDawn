import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout, UIMessageBox, UIAnchorLayout
import json
import province


class Game(arcade.View):
    def __init__(self, year: int, country: str):
        super().__init__()

        self.army_positions = []
        self.message_opened = False

        self.year = year
        self.country = country

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        with (open("provinces.json", "r", encoding="utf-8") as provinces_file,
            open("countries.json", "r", encoding="utf-8") as countries_file):
            provinces_data = json.load(provinces_file)
            countries_data = json.load(countries_file)
            for i in countries_data:
                if i == self.country:
                    capital = countries_data[i]["capital"]
                    break
            for i in provinces_data:
                if i == capital.lower():
                    self.world_camera.position = (provinces_data[i]["center_x"], provinces_data[i]["center_y"])
                    break

        self.all_provinces = arcade.SpriteList()
        self.background = arcade.SpriteList()
        self.background.append(arcade.Sprite("images\фон.png", center_x=2608, center_y=2432))

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

        # self.country_overview()

    def show_message(self):
        self.message_opened = True

        self.message_box = UIMessageBox(
            width=300, height=200,
            message_text=f"{self.prov_name.upper()}\n{self.prov_resource}",
            buttons=("Купить армию", "Закрыть")
        )
        self.message_box.on_action = self.on_message_button
        self.prov_manager.add(self.message_box)
        self.message_box.with_padding(top=20, left=10, right=10, bottom=10)

    def on_message_button(self, button_text):
        if button_text.action == "Закрыть":
            self.close_message()
        elif button_text.action == "Купить армию":
            self.buy_army()

    def buy_army(self):
        self.message_opened = False
        if self.prov_center not in self.army_positions:
            self.army_positions.append(self.prov_center)
        self.close_message()

    # def country_overview(self):
    #     with (open("provinces.json", "r", encoding="utf-8") as provinces_file,
    #         open("countries.json", "r", encoding="utf-8") as countries_file):
    #         provinces_data = json.load(provinces_file)
    #         countries_data = json.load(countries_file)
    #
    #         for country_name in countries_data:
    #             for prov_name in provinces_data:
    #                 if provinces_data[prov_name]["color"] == countries_data[country_name]["color"]:
    #                     countries_data[country_name]["resources"].append(provinces_data[prov_name]["resource"])
    #                     countries_data[country_name]["provinces"].append(prov_name)
    #
    #     with open("countries.json", "w", encoding="utf-8") as countries_file:
    #         json.dump(countries_data, countries_file, ensure_ascii=False, indent=4)
    #

    def close_message(self):
        self.message_opened = False
        self.message_box.clear()

    def on_country_button_click(self, event):
        with open("countries.json", "r", encoding="utf-8") as countries_file:
            countries_data = json.load(countries_file)
        country_info = countries_data.get(self.country, {})

        provinces_list = ", ".join(country_info.get("provinces", [])) or "Нет провинций"
        resources_list = ", ".join(country_info.get("resources", [])) or "Нет ресурсов"
        stats_text = (
            f"Страна: {self.country}\n"
            f"Год: {self.year}\n"
            f"Провинции: {provinces_list}\n"
            f"Ресурсы: {resources_list}"
        )

        message_box = UIMessageBox(
            width=400,
            height=250,
            message_text=stats_text,
            buttons=("Закрыть",)
        )
        message_box.with_padding(all=15)
        self.manager.add(message_box)

    def on_show_view(self):
        arcade.set_background_color((42, 44, 44))

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

        country_button = arcade.gui.UIFlatButton(text="Статистика", width=120, height=40)
        country_button.on_click = self.on_country_button_click

        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            country_button,
            anchor_x="left",
            anchor_y="top",
            align_x=10,
            align_y=-10
        )
        self.manager.add(anchor_layout)

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

        if self.message_opened == False:
            for prov in self.all_provinces:
                if prov.collides_with_point((world_x, world_y)):
                    self.prov_name = prov.name
                    self.prov_resource = prov.resource
                    self.prov_center = (prov.center_x, prov.center_y)
                    with open("countries.json", "r", encoding="utf-8") as file:
                        data = json.load(file)
                        if self.prov_name in data[self.country]["provinces"]:
                            self.show_message()
                            self.info_box.visible = True
                            self.world_camera.position = (prov.center_x, prov.center_y)

                    return

        self.info_box.visible = False

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self.all_provinces.draw()
        self.background.draw()
        for i in self.army_positions:
            arcade.draw_circle_filled(i[0], i[1], 25, arcade.color.BLUE)

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