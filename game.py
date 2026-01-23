import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout, UIMessageBox, UIFlatButton, UIAnchorLayout
import json
from collections import Counter

import province


class Game(arcade.View):
    def __init__(self, year: int, country: str):
        super().__init__()

        self.year = year
        self.country = country

        self.army_positions = []
        self.all_provinces = arcade.SpriteList()
        self.background = arcade.SpriteList()

        bg = arcade.Sprite("images/backgrounds/map.png")
        bg.center_x = bg.width // 2
        bg.center_y = bg.height // 2
        self.background.append(bg)
        bg_sprite = self.background[0]
        self.map_width = bg_sprite.width
        self.map_height = bg_sprite.height
        self.map_center_x = bg_sprite.center_x
        self.map_center_y = bg_sprite.center_y

        self.manager = None
        self.message_box = None
        self.province_panel = False

        self.dragging = False

        self.last_mouse_x = 0
        self.last_mouse_y = 0

        self.min_zoom = 0.3
        self.max_zoom = 3.0

        self.pan_speed = 20.0
        self.keys = {key: False for key in (arcade.key.W,
                                            arcade.key.S,
                                            arcade.key.A,
                                            arcade.key.D)}

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        with open("provinces.json", "r", encoding="utf-8") as provinces_file, \
             open("countries.json", "r", encoding="utf-8") as countries_file:
            provinces_data = json.load(provinces_file)
            countries_data = json.load(countries_file)

            capital = countries_data[self.country]["capital"]
            cap_key = capital.lower()
            if cap_key in provinces_data:
                self.world_camera.position = (
                    provinces_data[cap_key]["center_x"],
                    provinces_data[cap_key]["center_y"]
                )

    #     self.country_overview()
    #
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

    def on_show_view(self):
        arcade.set_background_color((42, 44, 44))

        with open("provinces.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            for name in data:
                prov = province.Province(
                    f"images/provinces/{name}.png",
                    data[name]["center_x"],
                    data[name]["center_y"],
                    data[name]["color"],
                    name,
                    data[name]["resource"]
                )
                self.all_provinces.append(prov)

        self.manager = UIManager()
        self.manager.enable()

        self.country_button = UIFlatButton(text="Статистика", width=130, height=50)
        self.country_button.on_click = lambda e: self.country_statistic_panel()

        self.country_button_container = UIAnchorLayout()
        self.country_button_container.add(
            self.country_button,
            anchor_x="left",
            anchor_y="top",
            align_x=10,
            align_y=-10
        )
        self.manager.add(self.country_button_container)

        self.economics_button = UIFlatButton(text="Экономика", width=130, height=50)
        self.economics_button.on_click = lambda e: self.economic_panel()

        self.economics_button_container = UIAnchorLayout()
        self.economics_button_container.add(
            self.economics_button,
            anchor_x="left",
            anchor_y="top",
            align_x=150,
            align_y=-10
        )

        self.manager.add(self.economics_button_container)

        self.tech_button = UIFlatButton(text="Технологии", width=130, height=50)
        self.tech_button.on_click = lambda e: self.new_turn()

        self.tech_button_container = UIAnchorLayout()
        self.tech_button_container.add(
            self.tech_button,
            anchor_x="left",
            anchor_y="top",
            align_x=290,
            align_y=-10
        )

        self.manager.add(self.tech_button_container)

        self.new_turn_button = UIFlatButton(text="Новый ход", width=150, height=75)
        self.new_turn_button.on_click = lambda e: self.new_turn()

        self.new_turn_button_container = UIAnchorLayout()
        self.new_turn_button_container.add(
            self.new_turn_button,
            anchor_x="right",
            anchor_y="bottom",
            align_x=-25,
            align_y=25
        )

        self.manager.add(self.new_turn_button_container)

        self.exit_button = UIFlatButton(text="Выход", width=150, height=50)
        self.exit_button.on_click = lambda e: self.new_turn()

        self.exit_button_container = UIAnchorLayout()
        self.exit_button_container.add(
            self.exit_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-10,
            align_y=-10
        )

        self.manager.add(self.exit_button_container)

    def show_province_panel(self, has_army: bool):
        if self.province_panel:
            return

        self.province_panel = True

        panel = UIBoxLayout(vertical=True, space_between=12)
        panel.with_padding(top=15, bottom=15, left=15, right=15)
        panel.with_background(color=(32, 35, 40, 220))
        panel.style = {
            "border_color": (90, 95, 105),
            "border_width": 2
        }

        title = UILabel(text=self.prov_name.upper(), width=280, align="left")
        title.style = {
            "normal": {
                "font_size": 18,
                "text_color": arcade.color.WHITE
            }
        }

        divider1 = UILabel(text="─" * 30)
        divider1.style = {
            "normal": {
                "text_color": (120, 120, 120)
            }
        }

        resource_label = UILabel(text=f"Ресурс: {self.prov_resource}", width=280, align="left")
        resource_label.style = {
            "normal":
                {"text_color": (200, 200, 200)
                 }
        }

        army_status = "присутствует" if has_army else "отсутствует"
        army_label = UILabel(text=f"Армия: {army_status}", width=280, align="left")
        army_label.style = {
            "normal": {
                "text_color": (160, 160, 160)
            }
        }

        divider2 = UILabel(text="─" * 30)
        divider2.style = divider1.style

        if has_army:
            button_text = "Переместить армию"
            on_click_action = self.move_army
        else:
            button_text = "Купить армию"
            on_click_action = self.buy_army

        action_button = UIFlatButton(text=button_text, width=260, height=40)
        action_button.on_click = lambda e: on_click_action()

        close_button = UIFlatButton(text="Закрыть", width=260, height=36)
        close_button.on_click = lambda e: self.close_province_message()

        for widget in [title, divider1, resource_label, army_label, divider2, action_button, close_button]:
            panel.add(widget)

        anchor = UIAnchorLayout()
        anchor.add(
            panel,
            anchor_x="left",
            anchor_y="bottom",
            align_x=15,
            align_y=15
        )

        self.message_box = anchor
        self.manager.add(anchor)

    def country_statistic_panel(self):
        self.country_panel_opened = True
        self.manager.remove(self.country_button_container)
        self.manager.remove(self.economics_button_container)
        self.manager.remove(self.tech_button_container)

        with open("countries.json", mode="r", encoding="UTF-8") as file:
            data = json.load(file)
            provinces = data[self.country]["provinces"]
            resources = dict(Counter(data[self.country]["resources"]))

        del resources["-"]
        resources_str = str(resources).replace(",", ";").replace("'", "")[1:-1]

        panel = UIBoxLayout(vertical=True, space_between=10)
        panel.with_padding(top=14, bottom=14, left=16, right=16)
        panel.with_background(color=(28, 30, 34, 230))
        panel.style = {
            "border_color": (85, 90, 100),
            "border_width": 2
        }

        title = UILabel(
            text=self.country.upper(),
            width=300,
            align="left"
        )
        title.style = {
            "normal": {
                "font_size": 20,
                "text_color": (240, 240, 240)
            }
        }

        divider1 = UILabel("─" * 34)
        divider1.style = {
            "normal": {
                "text_color": (120, 120, 120)
            }
        }

        resource_label = UILabel(resources_str)
        resource_label.style = {
            "normal": {
                "font_size": 20,
                "text_color": (240, 240, 240)
            }
        }

        divider2 = UILabel("─" * 34)
        divider2.style = {
            "normal": {
                "text_color": (120, 120, 120)
            }
        }

        panel.add(title)
        panel.add(divider1)
        panel.add(resource_label)
        panel.add(divider2)

        current_line = []
        current_length = 0
        for prov in provinces:
            prov_len = len(prov)
            added_length = prov_len + (2 if current_line else 0)
            if current_length + added_length > 60 and current_line:
                line_text = ", ".join(current_line)
                label = UILabel(text=line_text, width=280, align="left")
                label.style = {
                    "normal": {
                        "font_size": 20,
                        "text_color": (240, 240, 240)
                    }
                }
                panel.add(label)
                current_line = [prov]
                current_length = prov_len
            else:
                current_line.append(prov)
                current_length += added_length

        if current_line:
            line_text = ", ".join(current_line)
            label = UILabel(text=line_text, width=280, align="left")
            label.style = {
                "normal": {
                    "font_size": 20,
                    "text_color": (240, 240, 240)
                }
            }
            panel.add(label)

        divider3 = UILabel("─" * 34)
        divider3.style = {
            "normal": {
                "text_color": (120, 120, 120)
            }
        }

        close_button = UIFlatButton(text="Закрыть", width=280, height=36)
        close_button.on_click = lambda e: self.close_country_statistic_message()

        panel.add(divider3)
        panel.add(close_button)

        anchor = UIAnchorLayout()
        anchor.add(
            panel,
            anchor_x="left",
            anchor_y="top",
            align_x=15,
            align_y=-15
        )

        self.country_panel = anchor
        self.manager.add(anchor)

    def economic_panel(self):
        self.country_panel_opened = True
        self.manager.remove(self.country_button_container)
        self.manager.remove(self.economics_button_container)
        self.manager.remove(self.tech_button_container)

        panel = UIBoxLayout(vertical=True, space_between=10)
        panel.with_padding(top=14, bottom=14, left=16, right=16)
        panel.with_background(color=(28, 30, 34, 230))
        panel.style = {
            "border_color": (85, 90, 100),
            "border_width": 2
        }

        text1 = UILabel("На складах:")
        text1.style = {
            "normal": {
                "font_size": 20,
                "text_color": (240, 240, 240)
            }
        }

        panel.add(text1)

        with open("countries.json", mode="r", encoding="utf-8") as file:
            data = json.load(file)
            wheat = data[self.country]["wheat"]
            metal = data[self.country]["metal"]
            wood = data[self.country]["wood"]
            coal = data[self.country]["coal"]
            oil = data[self.country]["oil"]


        wheat_label = UILabel(text=f"Пшеница: {str(wheat)}", align="left")
        metal_label = UILabel(text=f"Металл: {str(metal)}", align="left")
        wood_label = UILabel(text=f"Дерево: {str(wood)}", align="left")
        coal_label = UILabel(text=f"Уголь: {str(coal)}", align="left")
        oil_label = UILabel(text=f"Нефть: {str(oil)}", align="left")

        for i in wheat_label, metal_label, wood_label, coal_label, oil_label:
            panel.add(i)


        anchor = UIAnchorLayout()
        anchor.add(
            panel,
            anchor_x="left",
            anchor_y="top",
            align_x=15,
            align_y=-15
        )

        self.economics_panel = anchor
        self.manager.add(anchor)

    def new_turn(self):
        ...

    def buy_army(self):
        if self.prov_center not in self.army_positions:
            self.army_positions.append(self.prov_center)

    def move_army(self):
        if self.prov_center not in self.army_positions:
            self.army_positions.append(self.prov_center)

    def close_province_message(self):
        if self.message_box is not None and self.manager:
            self.manager.remove(self.message_box)
            self.message_box = None
        self.province_panel = False

    def close_country_statistic_message(self):
        if self.country_panel is not None and self.manager:
            self.manager.remove(self.country_panel)
            self.country_panel = None
        self.manager.add(self.country_button_container)
        self.manager.add(self.economics_button_container)
        self.manager.add(self.tech_button_container)
        self.country_panel_opened = False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.dragging = True
            self.last_mouse_x = x
            self.last_mouse_y = y
            self.manager.on_mouse_press(x, y, button, modifiers)
            return

        world_x, world_y, _ = self.world_camera.unproject((x, y))

        for prov in self.all_provinces:
            if prov.collides_with_point((world_x, world_y)):
                with open("countries.json", "r", encoding="utf-8") as file:
                    data = json.load(file)

                    if prov.name not in data[self.country]["provinces"]:
                        return

                self.prov_name = prov.name
                self.prov_resource = prov.resource
                self.prov_center = (prov.center_x, prov.center_y)

                self.close_province_message()
                has_army = self.prov_center in self.army_positions
                self.show_province_panel(has_army=has_army)
                return

        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys[symbol] = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom_factor = 1.1 if scroll_y > 0 else 1 / 1.1
        new_zoom = self.world_camera.zoom * zoom_factor

        min_zoom_x = self.window.width / self.map_width
        min_zoom_y = self.window.height / self.map_height
        safe_min_zoom = max(min_zoom_x, min_zoom_y, self.min_zoom)

        self.world_camera.zoom = max(safe_min_zoom, min(self.max_zoom, new_zoom))

        cx, cy = self.world_camera.position
        cx, cy = self.clamp_camera(cx, cy)
        self.world_camera.position = (cx, cy)

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.dragging:
            return

        zoom = self.world_camera.zoom
        cam_x, cam_y = self.world_camera.position
        cam_x -= dx / zoom
        cam_y -= dy / zoom
        cam_x, cam_y = self.clamp_camera(cam_x, cam_y)
        self.world_camera.position = (cam_x, cam_y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.dragging = False

    def clamp_camera(self, x, y):
        zoom = self.world_camera.zoom

        half_w = (self.window.width / zoom) / 2
        half_h = (self.window.height / zoom) / 2

        left = half_w
        right = self.map_width - half_w
        bottom = half_h
        top = self.map_height - half_h

        x = max(left, min(right, x))
        y = max(bottom, min(top, y))

        return x, y

    def on_update(self, delta_time: float):
        if self.dragging:
            return

        x, y = self.world_camera.position

        if self.keys[arcade.key.W]:
            y += self.pan_speed
        if self.keys[arcade.key.S]:
            y -= self.pan_speed
        if self.keys[arcade.key.A]:
            x -= self.pan_speed
        if self.keys[arcade.key.D]:
            x += self.pan_speed

        x, y = self.clamp_camera(x, y)
        self.world_camera.position = (x, y)

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self.background.draw()
        self.all_provinces.draw()
        for pos in self.army_positions:
            arcade.draw_circle_filled(pos[0], pos[1], 25, arcade.color.BLUE)

        self.gui_camera.use()
        self.manager.draw()
