import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout
import game

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

COUNTRIES_BY_YEAR = {
    1938: [
        "Германия", "СССР", "Великобритания", "Франция", "Италия",
        "Польша", "Чехословакия", "Испания", "Турция", "Швеция",
        "Румыния", "Венгрия", "Югославия", "Греция"
    ],
    1941: [
        "Германия", "СССР", "Великобритания", "Италия",
        "Венгрия", "Румыния", "Финляндия"
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
        self.manager = UIManager(self.window)
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
            text="НАЧАТЬ КАМПАНИЮ 1938",
            width=520,
            height=56,
            style=style
        )
        b1941 = UIFlatButton(
            text="НАЧАТЬ КАМПАНИЮ 1941",
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
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 150,
            DARK,
            72,
            anchor_x="center",
            font_name=("Courier New",)
        )

        arcade.draw_text(
            "ВОЕННО-СТРАТЕГИЧЕСКИЙ СИМУЛЯТОР АЛЬТЕРНАТИВНОЙ ИСТОРИИ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 220,
            MID,
            20,
            anchor_x="center",
            font_name=("Courier New",)
        )

        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - 350,
            right=SCREEN_WIDTH // 2 + 350,
            top=SCREEN_HEIGHT // 2 + 160,
            bottom=SCREEN_HEIGHT // 2 - 160,
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
        self.manager = UIManager(self.window)
        self.manager.enable()

        self.root = UIAnchorLayout()
        self.box = UIBoxLayout(vertical=True, space_between=12)

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

        for c in self.countries:
            b = UIFlatButton(
                text=f"> {c.upper()}",
                width=640,
                height=36,
                style=style
            )
            b.on_click = lambda e, country=c: self.window.show_view(game.Game(self.year, country))
            self.box.add(b)

        back = UIFlatButton(
            text="< ВЕРНУТЬСЯ",
            width=300,
            height=34,
            style=style
        )

        back.on_click = lambda e: self.window.show_view(Menu())
        self.box.add(back)

        self.root.add(self.box, anchor_x="center", anchor_y="center")
        self.manager.add(self.root)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            str(self.year),
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 80,
            (200, 200, 200),
            46,
            anchor_x="center",
            font_name=("Courier New",),
            bold=True
        )

        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - 410,
            right=SCREEN_WIDTH // 2 + 410,
            top=SCREEN_HEIGHT // 2 + 390,
            bottom=SCREEN_HEIGHT // 2 - 390,
            color=(180, 180, 180),
            border_width=1
        )

        self.manager.draw()
