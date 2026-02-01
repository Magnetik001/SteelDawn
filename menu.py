import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout, UIImage

import game
from save_manager import has_save

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

COUNTRIES_BY_YEAR = {
    1938: [
        "Германия", "СССР", "Британия", "Франция", "Италия",
        "Польша", "Чехословакия", "Испания", "Турция", "Швеция",
        "Румыния", "Венгрия", "Югославия", "Греция", "Бельгия",
        "Нидерланды", "Дания", "Норвегия", "Финляндия", "Португалия",
        "Швейцария", "Ирландия", "Болгария", "Австрия", "Литва",
        "Латвия", "Эстония"
    ],
    1941: [
        "Германия", "СССР", "Британия", "Италия", "Словакия",
        "Франция Виши", "Свободная Франция", "Хорватия",
        "Венгрия", "Румыния", "Болгария", "Финляндия",
        "Швеция", "Швейцария", "Португалия", "Испания", "Турция",
        "Ирландия"
    ]
}

BG = (242, 238, 228)
DARK = (40, 40, 40)
MID = (110, 110, 110)


class Plane(arcade.Sprite):
    def __init__(self, center_y, speed):
        super().__init__()

        self.sp = speed

        if self.sp is True:
            self.speed = 300
        else:
            self.speed = 600
        self.center_x = SCREEN_WIDTH
        self.center_y = center_y

        self.scale = 1.0
        self.health = 100

        self.walk_textures = []
        for i in range(1, 3):
            texture = arcade.load_texture(f"images/самолет {i}.png")
            self.walk_textures.append(texture)

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1

    def update_animation(self, delta_time: float = 1 / 120):
        self.texture_change_time += delta_time
        if self.texture_change_time >= self.texture_change_delay:
            self.texture_change_time = 0
            self.current_texture += 1
            if self.current_texture >= len(self.walk_textures):
                self.current_texture = 0
            self.texture = self.walk_textures[self.current_texture]

    def update(self, delta_time):
        if self.center_x < 0:
            self.remove_from_sprite_lists()

        if self.sp is True:
            self.center_x -= 100 * delta_time
            return

        self.center_x -= 200 * delta_time


class Cloud(arcade.Sprite):
    def __init__(self, centre_y, reverse=False):
        super().__init__()

        self.reverse = reverse

        self.scale = 1.0
        self.health = 100

        self.idle_texture = arcade.load_texture("images/туча 3.png")
        self.texture = self.idle_texture

        if self.reverse is True:
            self.center_x = SCREEN_WIDTH
            self.speed = 375
        else:
            self.center_x = 0
            self.speed = 200
        self.center_y = centre_y

    def update(self, delta_time):
        if self.center_x > SCREEN_WIDTH + 200 and not self.reverse:
            self.remove_from_sprite_lists()

        if self.center_x < 0 and self.reverse:
            self.remove_from_sprite_lists()

        if self.reverse:
            self.center_x -= 150 * delta_time
        else:
            self.center_x += 50 * delta_time


class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(BG)

        self.cloud_list = None
        self.plane_list = None

    def on_show_view(self):
        self.animation_ = 0
        self.setup_gui()

    def setup_gui(self):
        if hasattr(self, 'manager'):
            self.manager.disable()

        self.manager = UIManager()
        self.manager.enable()

        self.root = UIAnchorLayout()
        self.box = UIBoxLayout(vertical=True, space_between=30)

        style = {
            "normal": {
                "font_name": ("Courier New",),
                "font_size": 26,
                "font_color": DARK,
                "bg": (0, 0, 0, 0),
                "border": 0
            },
            "hover": {
                "font_color": (0, 0, 0),
                "bg": (220, 215, 205, 160)
            },
            "press": {
                "font_color": (0, 0, 0),
                "bg": (210, 205, 195, 180)
            }
        }

        if has_save():
            b_continue = UIFlatButton(
                text="> ПРОДОЛЖИТЬ ИГРУ",
                width=520,
                height=56,
                style=style
            )
            b_continue.on_click = lambda e: self._load_saved_game()
            self.box.add(b_continue)

        b1938 = UIFlatButton(
            text="> НАЧАТЬ КАМПАНИЮ 1938",
            width=520,
            height=56,
            style=style
        )
        b1941 = UIFlatButton(
            text="> НАЧАТЬ КАМПАНИЮ 1941",
            width=520,
            height=56,
            style=style
        )

        b_exit = UIFlatButton(
            x=10,
            y=10,
            text="Выход",
            width=250,
            height=75,
            style=style
        )

        b_donttouch = UIFlatButton(
            x=10,
            y=self.window.height - 100,
            text="Не нажимай!",
            width=250,
            height=75,
            style=style
        )

        b1938.on_click = lambda e: self.window.show_view(CountrySelectionView(1938))
        b1941.on_click = lambda e: self.window.show_view(CountrySelectionView(1941))
        b_exit.on_click = lambda e: arcade.exit()
        b_donttouch.on_click = lambda e: self.animation()

        self.box.add(b1938)
        self.box.add(b1941)

        self.root.add(self.box, anchor_x="center", anchor_y="center")
        self.manager.add(self.root)
        self.manager.add(b_exit)
        self.manager.add(b_donttouch)

        b_stats = UIFlatButton(
            text="Статистика",
            width=250,
            height=75,
            style=style
        )
        b_stats.on_click = lambda e: self.window.show_view(StatisticsView())

        stats_anchor = UIAnchorLayout()
        stats_anchor.add(
            b_stats,
            anchor_x="right",
            anchor_y="bottom",
            align_x=-10,
            align_y=10
        )
        self.manager.add(stats_anchor)

    def animation(self):
        self.animation_ += 1
        if self.animation_ == 1:
            self.plane_list = arcade.SpriteList()
            self.cloud_list = arcade.SpriteList()

            for i in range(5):
                speed = (i % 2 == 0)
                plane = Plane(SCREEN_HEIGHT // 6 * i, speed)
                self.plane_list.append(plane)

            for i in range(6):
                rev = (i % 2 == 0)
                cloud = Cloud(SCREEN_HEIGHT // 7 * i, rev)
                self.cloud_list.append(cloud)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "STEEL DAWN",
            self.window.width // 2,
            self.window.height - 150,
            DARK,
            72,
            anchor_x="center",
            font_name=("Courier New",)
        )

        arcade.draw_text(
            "ВОЕННО-СТРАТЕГИЧЕСКИЙ СИМУЛЯТОР АЛЬТЕРНАТИВНОЙ ИСТОРИИ",
            self.window.width // 2,
            self.window.height - 220,
            MID,
            20,
            anchor_x="center",
            font_name=("Courier New",)
        )

        arcade.draw_lrbt_rectangle_outline(
            left=self.window.width // 2 - 300,
            right=self.window.width // 2 + 300,
            top=self.window.height // 2 + 110,
            bottom=self.window.height // 2 - 110,
            color=(180, 180, 180),
            border_width=1
        )

        self.manager.draw()
        if self.cloud_list is not None and self.plane_list is not None:
            self.cloud_list.draw()
            self.plane_list.draw()

    def on_update(self, delta_time):
        if self.animation_ % 2 != 0:
            self.cloud_list.update()
            self.plane_list.update()
            for plane in self.plane_list:
                plane.update_animation()

            if len(self.plane_list) < 5:
                for i in range(5):
                    speed = (i % 2 == 0)
                    plane = Plane(SCREEN_HEIGHT // 6 * i, speed)
                    self.plane_list.append(plane)

            if len(self.cloud_list) < 6:
                for i in range(6):
                    rev = (i % 2 == 0)
                    cloud = Cloud(SCREEN_HEIGHT // 7 * i, rev)
                    self.cloud_list.append(cloud)

    def _load_saved_game(self):
        from save_manager import load_game, apply_save_to_game
        import game as game_module

        save_data = load_game()
        if not save_data:
            return

        g = game_module.Game(save_data["year"], save_data["country"], is_new_game=False)
        g._pending_save_data = save_data
        self.window.show_view(g)


class CountrySelectionView(arcade.View):
    def __init__(self, year):
        super().__init__()
        self.year = year
        self.countries = COUNTRIES_BY_YEAR.get(year, [])
        arcade.set_background_color(BG)

    def on_show_view(self):
        self.setup_gui()

    def setup_gui(self):
        self.manager = UIManager()
        self.manager.enable()

        style = {
            "normal": {
                "font_name": ("Courier New",),
                "font_size": 18,
                "font_color": DARK,
                "bg": (0, 0, 0, 0),
                "border": 0
            },
            "hover": {
                "font_color": (0, 0, 0),
                "bg": (220, 215, 205, 160)
            },
            "press": {
                "font_color": (0, 0, 0),
                "bg": (210, 205, 195, 180)
            }
        }

        num_cols = 6
        columns = [UIBoxLayout(vertical=True, space_between=10) for _ in range(num_cols)]

        for i, country in enumerate(self.countries):
            flag_path = f"images/flags/{country}.png"
            texture = arcade.load_texture(flag_path)
            flag_widget = UIImage(texture=texture, width=120, height=75)

            btn = UIFlatButton(
                text=f"> {country.upper()}",
                width=220,
                height=30,
                style=style
            )
            btn.on_click = lambda e, c=country: self.window.show_view(
                game.Game(self.year, c, is_new_game=True)
            )

            country_block = UIBoxLayout(vertical=True, space_between=5)
            country_block.add(flag_widget)
            country_block.add(btn)

            columns[i % num_cols].add(country_block)

        cols_row = UIBoxLayout(vertical=False, space_between=5, align="top")
        for col in columns:
            cols_row.add(col)

        back_button = UIFlatButton(
            text="< НАЗАД",
            width=200,
            height=30,
            style=style
        )
        back_button.on_click = lambda e: self.window.show_view(Menu())

        root = UIAnchorLayout()
        root.add(cols_row, anchor_x="center", anchor_y="top", align_y=-130)
        root.add(back_button, anchor_x="left", anchor_y="top", align_x=20, align_y=-20)

        self.manager.add(root)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            str(self.year),
            self.window.width // 2,
            self.window.height - 80,
            (200, 200, 200),
            46,
            anchor_x="center",
            font_name=("Courier New",),
            bold=True
        )
        self.manager.draw()


class StatisticsView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(BG)
        self.stats = None

    def on_show_view(self):
        from stats_manager import get_stats
        self.stats = get_stats()
        self.setup_gui()

    def setup_gui(self):
        self.manager = UIManager()
        self.manager.enable()

        style = {
            "normal": {
                "font_name": ("Courier New",),
                "font_size": 26,
                "font_color": DARK,
                "bg": (0, 0, 0, 0),
                "border": 0
            },
            "hover": {
                "font_color": (0, 0, 0),
                "bg": (220, 215, 205, 160)
            },
            "press": {
                "font_color": (0, 0, 0),
                "bg": (210, 205, 195, 180)
            }
        }

        back_button = UIFlatButton(
            text="Назад",
            width=250,
            height=75,
            style=style
        )
        back_button.on_click = lambda e: self.window.show_view(Menu())

        back_anchor = UIAnchorLayout()
        back_anchor.add(
            back_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-10,
            align_y=-10
        )
        self.manager.add(back_anchor)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "СТАТИСТИКА ИГРОКА",
            self.window.width // 2,
            self.window.height - 120,
            DARK,
            48,
            anchor_x="center",
            font_name=("Courier New",),
            bold=True
        )

        arcade.draw_text(
            "Накоплено за все сессии игры",
            self.window.width // 2,
            self.window.height - 180,
            MID,
            24,
            anchor_x="center",
            font_name=("Courier New",)
        )

        stats_y = self.window.height - 280
        line_height = 60

        arcade.draw_text(
            f"Всего ходов: {self.stats['turns']}",
            self.window.width // 2,
            stats_y,
            DARK,
            36,
            anchor_x="center",
            font_name=("Courier New",)
        )

        arcade.draw_text(
            f"Заказано подкреплений: {self.stats['reinforcements']}",
            self.window.width // 2,
            stats_y - line_height,
            DARK,
            36,
            anchor_x="center",
            font_name=("Courier New",)
        )

        arcade.draw_text(
            f"Захвачено провинций: {self.stats['conquered']}",
            self.window.width // 2,
            stats_y - line_height * 2,
            DARK,
            36,
            anchor_x="center",
            font_name=("Courier New",)
        )

        arcade.draw_text(
            f"Последнее обновление: {self.stats['last_update'] or 'никогда'}",
            self.window.width // 2,
            stats_y - line_height * 3 - 40,
            (130, 130, 130),
            20,
            anchor_x="center",
            font_name=("Courier New",),
            italic=True
        )

        arcade.draw_lrbt_rectangle_outline(
            left=self.window.width // 2 - 400,
            right=self.window.width // 2 + 400,
            top=self.window.height // 2 + 150,
            bottom=self.window.height // 2 - 150,
            color=(180, 180, 180),
            border_width=1
        )

        self.manager.draw()