import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout, UIImage
import game

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


class Menu(arcade.View):

    def __init__(self):
        super().__init__()
        arcade.set_background_color(BG)

    def on_show_view(self):
        # Всегда пересоздаём GUI при входе в меню
        self.setup_gui()

    def setup_gui(self):
        # Удаляем старый менеджер, если есть
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

        b1938.on_click = lambda e: self.window.show_view(CountrySelectionView(1938))
        b1941.on_click = lambda e: self.window.show_view(CountrySelectionView(1941))

        self.box.add(b1938)
        self.box.add(b1941)

        self.root.add(self.box, anchor_x="center", anchor_y="center")
        self.manager.add(self.root)

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
            flag_path = f"flags/{country}.png"
            texture = arcade.load_texture(flag_path)
            flag_widget = UIImage(texture=texture, width=120, height=75)

            btn = UIFlatButton(
                text=f"> {country.upper()}",
                width=220,
                height=30,
                style=style
            )
            btn.on_click = lambda e, c=country: self.window.show_view(game.Game(self.year, c))

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