import arcade
from arcade.gui import UIManager, UILabel, UIBoxLayout, UIMessageBox, UIFlatButton, UIAnchorLayout
from arcade.particles import FadeParticle, Emitter, EmitBurst
import json
from collections import Counter
import random

import province
import menu


class Game(arcade.View):
    def __init__(self, year: int, country: str, is_new_game: bool = True):
        super().__init__()

        self.moving = False
        self.prov_center = ""
        self.moving_army = False
        self.prov_name = ""

        self.year = year
        self.country = country

        self.army_positions = {}
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

        self.province_panel_opened = False
        self.country_panel_opened = False
        self.economics_panel_opened = False

        self.province_panel = None
        self.country_panel = None
        self.economics_panel = None
        self.moving_anchor = None

        self.dragging = False

        self.turn = 0

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

        with open(f"provinces{self.year}.json", "r", encoding="utf-8") as provinces_file, \
             open(f"countries{self.year}.json", "r", encoding="utf-8") as countries_file:
            provinces_data = json.load(provinces_file)
            countries_data = json.load(countries_file)

            capital = countries_data[self.country]["capital"]
            cap_key = capital.lower()
            if cap_key in provinces_data:
                self.world_camera.position = (
                    provinces_data[cap_key]["center_x"],
                    provinces_data[cap_key]["center_y"]
                )

        self.particle_emitters = []
        self._init_particle_textures()
        if is_new_game:
            self.overview()

        self._pending_save_data = None

    def overview(self):
        # with (open(f"provinces{self.year}.json", "r", encoding="utf-8") as provinces_file,
        #     open(f"countries{self.year}.json", "r", encoding="utf-8") as countries_file):
        #     provinces_data = json.load(provinces_file)
        #     countries_data = json.load(countries_file)
        #
        #     for country_name in countries_data:
        #         for prov_name in provinces_data:
        #             if provinces_data[prov_name]["color"] == countries_data[country_name]["color"]:
        #                 countries_data[country_name]["resources"].append(provinces_data[prov_name]["resource"])
        #                 countries_data[country_name]["provinces"].append(prov_name)
        #
        # with open(f"countries{self.year}.json", "w", encoding="utf-8") as countries_file:
        #     json.dump(countries_data, countries_file, ensure_ascii=False, indent=4)

        with (open(f"provinces{self.year}.json", "r", encoding="utf-8") as f,
              open(f"countries{self.year}.json", "r", encoding="utf-8") as c):
            province_data = json.load(f)
            countries_data = json.load(c)

        for province in province_data.values():
            province["level"] = 1

        for country in countries_data.values():
            country["wheat"] = 0
            country["metal"] = 0
            country["wood"] = 0
            country["coal"] = 0
            country["oil"] = 0

        with (open(f"provinces{self.year}.json", "w", encoding="utf-8") as f,
              open(f"countries{self.year}.json", "w", encoding="utf-8") as c):
            json.dump(province_data, f, ensure_ascii=False, indent=4)
            json.dump(countries_data, c, ensure_ascii=False, indent=4)

    def _init_particle_textures(self):
        self.victory_spark_textures = [
            arcade.make_soft_circle_texture(10, arcade.color.GOLD),
            arcade.make_soft_circle_texture(10, arcade.color.ORANGE_RED),
            arcade.make_soft_circle_texture(10, arcade.color.DARK_ORANGE),
            arcade.make_soft_circle_texture(10, arcade.color.SUNRAY),
        ]
        self.smoke_texture = arcade.make_soft_circle_texture(25, arcade.color.LIGHT_GRAY, 255, 80)
        self.flash_texture = arcade.make_soft_circle_texture(15, arcade.color.WHITE, 255, 120)

    def create_conquest_particles(self, x: float, y: float, conquering_color: tuple):
        explosion = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(70),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(self.victory_spark_textures),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 8.0),
                lifetime=random.uniform(0.7, 1.3),
                start_alpha=255,
                end_alpha=0,
                scale=random.uniform(0.4, 0.8),
                mutation_callback=lambda p: (
                    setattr(p, 'change_y', p.change_y - 0.08),
                    setattr(p, 'change_x', p.change_x * 0.94),
                    setattr(p, 'change_y', p.change_y * 0.94)
                ),
            ),
        )

        flash = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(15),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=self.flash_texture,
                change_xy=(0, 0),
                lifetime=0.3,
                start_alpha=220,
                end_alpha=0,
                scale=random.uniform(1.2, 2.0),
            ),
        )

        smoke = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(25),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=self.smoke_texture,
                change_xy=(random.uniform(-0.8, 0.8), random.uniform(1.0, 2.5)),
                lifetime=random.uniform(2.0, 3.0),
                start_alpha=180,
                end_alpha=0,
                scale=random.uniform(0.6, 1.0),
                mutation_callback=lambda p: (
                    setattr(p, 'scale', p.scale),
                    setattr(p, 'alpha', max(0, p.alpha - 2.0))
                ),
            ),
        )

        color_sparks = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(40),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=arcade.make_soft_circle_texture(
                    8,
                    (conquering_color[0], conquering_color[1], conquering_color[2])
                ),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 6.0),
                lifetime=random.uniform(0.9, 1.6),
                start_alpha=240,
                end_alpha=30,
                scale=random.uniform(0.3, 0.6),
                mutation_callback=lambda p: (
                    setattr(p, 'change_y', p.change_y - 0.04),
                    setattr(p, 'scale', p.scale)
                ),
            ),
        )

        self.particle_emitters.extend([explosion, flash, smoke, color_sparks])

    def on_show_view(self):
        arcade.set_background_color((42, 44, 44))

        with open(f"provinces{self.year}.json", "r", encoding="utf-8") as file:
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
        self.exit_button.on_click = lambda e: self.exit()

        self.exit_button_container = UIAnchorLayout()
        self.exit_button_container.add(
            self.exit_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-10,
            align_y=-10
        )

        self.manager.add(self.exit_button_container)

        self.turn_label = UILabel(
            text=f"Ход: {self.turn}",
            font_size=18,
            text_color=(220, 220, 220),
            bold=True
        )
        turn_label_container = UIAnchorLayout()
        turn_label_container.add(
            self.turn_label,
            anchor_x="right",
            anchor_y="top",
            align_x=-20,
            align_y=-75
        )
        self.manager.add(turn_label_container)

        if self._pending_save_data is not None:
            from save_manager import apply_save_to_game
            apply_save_to_game(self, self._pending_save_data)
            self._pending_save_data = None

    def show_province_panel(self, has_army: bool):
        self.province_panel_opened = True

        self.panel = UIBoxLayout(vertical=True, space_between=12)
        self.panel.with_padding(top=15, bottom=15, left=15, right=15)
        self.panel.with_background(color=(32, 35, 40, 220))

        title = UILabel(text=self.prov_name.upper(), width=280, align="left")

        divider1 = UILabel(text="─" * 30)

        resource_label = UILabel(text=f"Ресурс: {self.prov_resource}", width=280, align="left")

        army_status = "присутствует" if has_army else "отсутствует"
        army_label = UILabel(text=f"Армия: {army_status}", width=280, align="left")

        divider2 = UILabel(text="─" * 30)

        with open(f"provinces{self.year}.json", mode="r", encoding="utf-8") as provinces_file:
            data = json.load(provinces_file)
            level = str(data[self.prov_name]["level"])

        row = UIBoxLayout(vertical=False, space_between=10)

        level_label = UILabel(text=f"Уровень провинции: {level}", width=280, align="left")
        level_button = UIFlatButton(text="+", width=35, height=35)
        level_button.on_click = lambda e: self.level_up()

        row.add(level_label)
        row.add(level_button)

        divider3 = UILabel(text="─" * 30)

        if has_army:
            button_text = "Переместить армию"
            on_click_action = self.move_army
        else:
            button_text = "Тренировать войска"
            on_click_action = self.buy_army

        action_button = UIFlatButton(text=button_text, width=260, height=40)
        action_button.on_click = lambda e: on_click_action()

        close_button = UIFlatButton(text="Закрыть", width=260, height=36)
        close_button.on_click = lambda e: self.close_province_message()

        for widget in [title, divider1, resource_label, army_label, divider2, row, divider3, action_button, close_button]:
            self.panel.add(widget)

        anchor = UIAnchorLayout()
        anchor.add(
            self.panel,
            anchor_x="left",
            anchor_y="bottom",
            align_x=15,
            align_y=15
        )

        self.province_panel = anchor
        self.manager.add(anchor)

    def country_statistic_panel(self):
        self.country_panel_opened = True
        self.manager.remove(self.country_button_container)
        self.manager.remove(self.economics_button_container)
        self.manager.remove(self.tech_button_container)

        with open(f"countries{self.year}.json", mode="r", encoding="UTF-8") as file:
            data = json.load(file)
            provinces = data[self.country]["provinces"]
            resources = dict(Counter(data[self.country]["resources"]))

        del resources["-"]
        resources_str = str(resources).replace(",", ";").replace("'", "")[1:-1]

        panel = UIBoxLayout(vertical=True, space_between=10)
        panel.with_padding(top=14, bottom=14, left=16, right=16)
        panel.with_background(color=(28, 30, 34, 230))

        title = UILabel(
            text=self.country.upper(),
            width=300,
            align="left"
        )
        panel.add(title)

        divider1 = UILabel("─" * 34)
        panel.add(divider1)

        resource_label = UILabel(resources_str)
        panel.add(resource_label)

        divider2 = UILabel("─" * 34)
        panel.add(divider2)

        current_line = []
        current_length = 0
        for prov in provinces:
            prov_len = len(prov)
            added_length = prov_len + (2 if current_line else 0)
            if current_length + added_length > 60 and current_line:
                line_text = ", ".join(current_line)
                label = UILabel(text=line_text, width=280, align="left")
                panel.add(label)
                current_line = [prov]
                current_length = prov_len
            else:
                current_line.append(prov)
                current_length += added_length

        if current_line:
            line_text = ", ".join(current_line)
            label = UILabel(text=line_text, width=280, align="left")
            panel.add(label)

        divider3 = UILabel("─" * 34)
        panel.add(divider3)

        close_button = UIFlatButton(text="Закрыть", width=280, height=36)
        close_button.on_click = lambda e: self.close_top_message(self.country_panel, self.country_panel_opened)

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
        self.economics_panel_opened = True
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
        panel.add(text1)

        with open(f"countries{self.year}.json", mode="r", encoding="utf-8") as file:
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

        divider1 = UILabel("─" * 34)
        panel.add(divider1)

        text2 = UILabel(text="Провинции с ресурсами:", align="left")
        panel.add(text2)

        with open(f"countries{self.year}.json", mode="r", encoding="utf-8") as file:
            data = json.load(file)
            for i in range(len(data[self.country]["resources"])):
                if data[self.country]["resources"][i] != "-":
                    row = UIBoxLayout(vertical=False, space_between=10)

                    prov_name = data[self.country]["provinces"][i]
                    resource = data[self.country]["resources"][i]

                    prov_label = UILabel(
                        text=f"{prov_name} - {resource}",
                        align="left",
                        width=200
                    )

                    action_button = UIFlatButton(
                        text="▶",
                        width=35,
                        height=35
                    )

                    action_button.on_click = (
                        lambda e, name=prov_name: self.go_to_province(name)
                    )

                    row.add(prov_label)
                    row.add(action_button)
                    panel.add(row)

        divider1 = UILabel("─" * 34)
        panel.add(divider1)

        close_button = UIFlatButton(text="Закрыть", width=280, height=36)
        close_button.on_click = lambda e: self.close_top_message(self.economics_panel, self.economics_panel_opened)

        panel.add(close_button)

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

    def show_victory_window(self):
        self.manager.clear()

        with open(f"countries{self.year}.json", encoding="utf-8") as f:
            data = json.load(f)[self.country]

        panel = UIBoxLayout(vertical=True, space_between=12)
        panel.with_padding(top=20, bottom=20, left=25, right=25)
        panel.with_background(color=(25, 28, 32, 240))

        title = UILabel(
            text="ПОБЕДА",
            font_size=28,
            align="center",
            text_color=(220, 220, 220)
        )
        panel.add(title)

        country_label = UILabel(
            text=f"Страна: {self.country}",
            align="left"
        )

        turn_label = UILabel(
            text=f"Ходов сыграно: {self.turn}",
            align="left"
        )

        divider = UILabel("─" * 36)

        res_label = UILabel("Ресурсы:", align="left")

        resources = [
            f"Пшеница: {data['wheat']}",
            f"Металл: {data['metal']}",
            f"Дерево: {data['wood']}",
            f"Уголь: {data['coal']}",
            f"Нефть: {data['oil']}"
        ]

        panel.add(res_label)
        for r in resources:
            panel.add(UILabel(text=r, align="left"))

        panel.add(divider)

        exit_button = UIFlatButton(
            text="Выйти в меню",
            width=240,
            height=45
        )
        exit_button.on_click = lambda e: self.exit()

        panel.add(country_label)
        panel.add(turn_label)
        panel.add(divider)
        panel.add(exit_button)

        anchor = UIAnchorLayout()
        anchor.add(
            panel,
            anchor_x="center",
            anchor_y="center"
        )

        self.manager.add(anchor)

    def show_loser_window(self):
        self.manager.clear()

        with open(f"countries{self.year}.json", encoding="utf-8") as f:
            data = json.load(f)[self.country]

        panel = UIBoxLayout(vertical=True, space_between=12)
        panel.with_padding(top=20, bottom=20, left=25, right=25)
        panel.with_background(color=(25, 28, 32, 240))

        title = UILabel(
            text="ПОРАЖЕНИЕ",
            font_size=28,
            align="center",
            text_color=(220, 220, 220)
        )
        panel.add(title)

        country_label = UILabel(
            text=f"Страна: {self.country}",
            align="left"
        )

        turn_label = UILabel(
            text=f"Вы потратили слишком много времени: {self.turn}",
            align="left"
        )

        divider = UILabel("─" * 36)

        panel.add(divider)

        exit_button = UIFlatButton(
            text="Выйти в меню",
            width=240,
            height=45
        )
        exit_button.on_click = lambda e: self.exit()

        panel.add(country_label)
        panel.add(turn_label)
        panel.add(divider)
        panel.add(exit_button)

        anchor = UIAnchorLayout()
        anchor.add(
            panel,
            anchor_x="center",
            anchor_y="center"
        )

        self.manager.add(anchor)

    def exit(self):
        from save_manager import save_game
        save_game(self)
        self.window.show_view(menu.Menu())

    def level_up(self):
        with (open(f"provinces{self.year}.json", mode="r", encoding="utf-8") as prov_file,
              open(f'countries{self.year}.json', mode="r", encoding="utf-8") as country_file):
            prov_data = json.load(prov_file)
            country_data = json.load(country_file)
            if (country_data[self.country]["wood"] >= 2 and country_data[self.country]["coal"] >= 2 and
                    prov_data[self.prov_name]["level"] != 5):
                country_data[self.country]["wood"] -= 2
                country_data[self.country]["coal"] -= 2
                prov_data[self.prov_name]["level"] += 1

        with open(f"provinces{self.year}.json", mode="w", encoding="utf-8") as prov_file, \
            open(f"countries{self.year}.json", mode="w", encoding="utf-8") as country_file:
            json.dump(prov_data, prov_file, indent=4, ensure_ascii=False)
            json.dump(country_data, country_file, indent=4, ensure_ascii=False)

    def go_to_province(self, name):
        self.close_province_message()
        self.prov_name = name
        with open(f"provinces{self.year}.json", mode="r", encoding="utf-8") as file:
            data = json.load(file)
            self.prov_center = (data[name]["center_x"], data[name]["center_y"])
            self.prov_resource = data[name]["resource"]
            self.world_camera.position = self.prov_center
            if self.prov_center in self.army_positions.keys():
                has_army = True
            else:
                has_army = False
            self.show_province_panel(has_army)

    def new_turn(self):
        with open(f"countries{self.year}.json", mode="r", encoding="utf-8") as country_file,\
            open(f"provinces{self.year}.json", mode="r", encoding="utf-8") as provinces_file:
            country_data = json.load(country_file)
            provinces_data = json.load(provinces_file)

            for prov in country_data[self.country]["provinces"]:
                level = provinces_data[prov]["level"]
                if provinces_data[prov]["resource"] == "Пшеница":
                    country_data[self.country]["wheat"] += level
                elif provinces_data[prov]["resource"] == "Металл":
                    country_data[self.country]["metal"] += level
                elif provinces_data[prov]["resource"] == "Дерево":
                    country_data[self.country]["wood"] += level
                elif provinces_data[prov]["resource"] == "Уголь":
                    country_data[self.country]["coal"] += level
                elif provinces_data[prov]["resource"] == "Нефть":
                    country_data[self.country]["oil"] += level

            if country_data[self.country]["wheat"] >= len(self.army_positions):
                country_data[self.country]["wheat"] -= len(self.army_positions)
            else:
                country_data[self.country]["wheat"] = 0

            if country_data[self.country]["oil"] >= len(self.army_positions):
                country_data[self.country]["oil"] -= len(self.army_positions)
            else:
                country_data[self.country]["oil"] = 0

        with open(f"countries{self.year}.json", mode="w", encoding="utf-8") as file:
            json.dump(country_data, file, ensure_ascii=False, indent=4)

        for i in self.army_positions.keys():
            self.army_positions[i] = 0

        self.turn += 1

        if hasattr(self, 'turn_label') and self.turn_label:
            self.turn_label.text = f"Ход: {self.turn}"

        self.result = 0
        for i in self.all_provinces:
            if i.color.r == country_data[self.country]["color"][0] and \
                i.color.g == country_data[self.country]["color"][1] and \
                i.color.b == country_data[self.country]["color"][2]:
                self.result += 1
        if self.result >= 150:
            self.show_victory_window()
        elif self.turn == 50:
            self.show_loser_window()

        self.close_help()

    def buy_army(self):
        if self.prov_center not in self.army_positions.keys():
            with open(f"countries{self.year}.json", mode="r", encoding="utf-8") as file:
                data = json.load(file)
                if data[self.country]["wheat"] - 1 >= 0 and data[self.country]["metal"] - 1 >= 0:
                    self.army_positions[self.prov_center] = 0
                    data[self.country]["wheat"] -= 1
                    data[self.country]["metal"] -= 1

                    with open(f"countries{self.year}.json", mode="w", encoding="utf-8") as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)

    def move_army(self):
        self.moving = True
        choice = UILabel(text="Выберите провинцию", text_color=(40, 40, 40), width=300)
        panel = UIBoxLayout(vertical=True, space_between=10)
        panel.with_padding(top=14, bottom=14, left=16, right=16)
        panel.with_background(color=(250, 250, 250, 230))
        panel.add(choice)
        self.move_anchor = UIAnchorLayout()
        self.move_anchor.add(
            panel,
            anchor_x="left",
            anchor_y="top",
            align_x=15,
            align_y=-450
        )
        self.manager.add(self.move_anchor)

    def moving_to(self):
        if self.prov_center not in self.army_positions.keys():
            with (open(f"countries{self.year}.json", mode="r", encoding="utf-8") as file):
                data = json.load(file)
                if data[self.country]["wheat"] > 0 and data[self.country]["metal"] > 0 and self.army_positions[
                    self.last_prov_centre] == 0:
                    if abs(self.prov_center[0] - self.last_prov_centre[0]) <= 300 and abs(
                            self.prov_center[1] - self.last_prov_centre[1]) <= 300:

                        self.army_positions[self.prov_center] = 1
                        while self.last_prov_centre in self.army_positions:
                            del self.army_positions[self.last_prov_centre]

                        data[self.country]["wheat"] -= 1
                        data[self.country]["metal"] -= 1

                        with open(f"countries{self.year}.json", mode="w", encoding="utf-8") as file:
                            json.dump(data, file, ensure_ascii=False, indent=4)

                        with open(f"countries{self.year}.json", mode="r", encoding="utf-8") as country_file:
                            country_data = json.load(country_file)
                            conquering_color = country_data[self.country]["color"]

                            for i in self.all_provinces:
                                if i.name == self.prov_name:
                                    if i.color.r != conquering_color[0] or i.color.g != conquering_color[1] or i.color.b != conquering_color[2]:
                                        i.color = conquering_color
                                        self.create_conquest_particles(i.center_x, i.center_y, conquering_color)
                                    break

                elif not(data[self.country]["wheat"] > 0 and data[self.country]["metal"] > 0):
                    choice = UILabel(text="Не хватает ресурсов!", text_color=(40, 40, 40), width=300)
                    panel = UIBoxLayout(vertical=True, space_between=10)
                    panel.with_padding(top=14, bottom=14, left=16, right=16)
                    panel.with_background(color=(250, 250, 250, 230))
                    panel.add(choice)
                    self.moving_anchor = UIAnchorLayout()
                    self.moving_anchor.add(
                        panel,
                        anchor_x="left",
                        anchor_y="top",
                        align_x=15,
                        align_y=-650
                    )
                    self.manager.add(self.moving_anchor)

                elif not(self.army_positions[self.last_prov_centre] == 0):
                    choice = UILabel(text="Эта армия уже ходила!", text_color=(40, 40, 40), width=300)
                    panel = UIBoxLayout(vertical=True, space_between=10)
                    panel.with_padding(top=14, bottom=14, left=16, right=16)
                    panel.with_background(color=(250, 250, 250, 230))
                    panel.add(choice)
                    self.moving_anchor = UIAnchorLayout()
                    self.moving_anchor.add(
                        panel,
                        anchor_x="left",
                        anchor_y="top",
                        align_x=15,
                        align_y=-650
                    )
                    self.manager.add(self.moving_anchor)
                else:
                    print(data[self.country]["wheat"] > 0, data[self.country]["metal"] > 0, self.army_positions[self.last_prov_centre] == 0)
            self.moving = False

    def close_help(self):
        if self.moving_anchor is not None and self.manager:
            self.manager.remove(self.moving_anchor)
            self.moving_anchor = None

    def close_province_message(self):
        if self.province_panel is not None and self.manager:
            self.manager.remove(self.province_panel)
            self.province_panel = None
        self.province_panel_opened = False

    def close_top_message(self, panel, flag):
        if panel is not None and self.manager:
            self.manager.remove(panel)
            panel = None
        self.manager.add(self.country_button_container)
        self.manager.add(self.economics_button_container)
        self.manager.add(self.tech_button_container)
        self.flag = False

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

                self.last_prov_name = self.prov_name
                self.last_prov_centre = self.prov_center

                self.prov_name = prov.name
                self.prov_resource = prov.resource
                self.prov_center = (prov.center_x, prov.center_y)

                with open(f"countries{self.year}.json", "r", encoding="utf-8") as country_file:
                    country_data = json.load(country_file)

                    for i in self.all_provinces:
                        if i.name == prov.name:
                            prov_color = [i.color.r, i.color.g, i.color.b]
                            break

                    if prov_color == country_data[self.country]["color"]:

                        self.close_province_message()
                        has_army = self.prov_center in self.army_positions.keys()
                        self.show_province_panel(has_army)

                if self.moving:
                    self.manager.remove(self.move_anchor)
                    self.moving_to()

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

        emitters_to_remove = []
        for emitter in self.particle_emitters:
            emitter.update(delta_time)
            if emitter.can_reap():
                emitters_to_remove.append(emitter)

        for emitter in emitters_to_remove:
            self.particle_emitters.remove(emitter)

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self.background.draw()
        self.all_provinces.draw()
        for pos in self.army_positions:
            self.helmet = arcade.Sprite("images/шлем зеленый 3.png", scale=2)
            self.helmet.center_x = pos[0]
            self.helmet.center_y = pos[1]
            self.helmet_list = arcade.SpriteList()
            self.helmet_list.append(self.helmet)
            self.helmet_list.draw()

        for emitter in self.particle_emitters:
            emitter.draw()

        self.gui_camera.use()
        self.manager.draw()
