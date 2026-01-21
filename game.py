import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout, UIMessageBox, UIFlatButton, UIAnchorLayout
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

        self.pan_speed = 20.0
        self.keys = {key: False for key in (arcade.key.W,
                                            arcade.key.S,
                                            arcade.key.A,
                                            arcade.key.D)}

        self.dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        self.manager = None
        self.current_message_box = None

        self.min_zoom = 0.3
        self.max_zoom = 3.0

        self.country_overview()

    def country_overview(self):
        with (open("provinces.json", "r", encoding="utf-8") as provinces_file,
            open("countries.json", "r", encoding="utf-8") as countries_file):
            provinces_data = json.load(provinces_file)
            countries_data = json.load(countries_file)

            for country_name in countries_data:
                for prov_name in provinces_data:
                    if provinces_data[prov_name]["color"] == countries_data[country_name]["color"]:
                        countries_data[country_name]["resources"].append(provinces_data[prov_name]["resource"])
                        countries_data[country_name]["provinces"].append(prov_name)

        with open("countries.json", "w", encoding="utf-8") as countries_file:
            json.dump(countries_data, countries_file, ensure_ascii=False, indent=4)


    def show_prov_without_army(self):
        self.message_opened = True
        self.current_message_box = UIMessageBox(
            width=300,
            height=200,
            message_text=f"{self.prov_name.upper()}\n{self.prov_resource}",
            buttons=("Купить армию", "Закрыть")
        )
        self.current_message_box.on_action = self.on_message_button_without_army
        self.manager.add(self.current_message_box)

    def show_prov_with_army(self):
        self.message_opened = True
        self.current_message_box = UIMessageBox(
            width=300,
            height=200,
            message_text=f"{self.prov_name.upper()}\n{self.prov_resource}",
            buttons=("Переместить армию", "Закрыть")
        )
        self.current_message_box.on_action = self.on_message_button_with_army
        self.manager.add(self.current_message_box)

    def on_message_button_without_army(self, event):
        action = event.action
        if action == "Закрыть":
            self.close_message()
        elif action == "Купить армию":
            self.buy_army()
            self.close_message()

    def on_message_button_with_army(self, event):
        action = event.action
        if action == "Закрыть":
            self.close_message()
        elif action == "Переместить армию":
            self.move_army()
            self.close_message()

    def buy_army(self):
        if self.prov_center not in self.army_positions:
            self.army_positions.append(self.prov_center)

    def move_army(self):
        if self.prov_center not in self.army_positions:
            self.army_positions.append(self.prov_center)

    def close_message(self):
        if self.current_message_box:
            self.current_message_box.clear()
            self.current_message_box = None
        self.message_opened = False

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
        message_box.on_action = lambda e: message_box.clear()
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

        country_button = UIFlatButton(text="Статистика", width=120, height=40)
        country_button.on_click = self.on_country_button_click

        anchor_layout = UIAnchorLayout()
        anchor_layout.add(
            country_button,
            anchor_x="left",
            anchor_y="top",
            align_x=10,
            align_y=-10
        )
        self.manager.add(anchor_layout)

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
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.dragging = True
            self.last_mouse_x = x
            self.last_mouse_y = y
            return

        if self.message_opened:
            return

        world_x, world_y, _ = self.world_camera.unproject((x, y))
        for prov in self.all_provinces:
            if prov.collides_with_point((world_x, world_y)):
                self.prov_name = prov.name
                self.prov_resource = prov.resource
                self.prov_center = (prov.center_x, prov.center_y)

                with open("countries.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if self.prov_name in data.get(self.country, {}).get("provinces", []):
                        if self.prov_center in self.army_positions:
                            self.show_prov_with_army()
                        else:
                            self.show_prov_without_army()
                        self.world_camera.position = self.clamp_camera(
                            prov.center_x, prov.center_y
                        )
                        return

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self.background.draw()
        self.all_provinces.draw()
        for pos in self.army_positions:
            arcade.draw_circle_filled(pos[0], pos[1], 25, arcade.color.BLUE)

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