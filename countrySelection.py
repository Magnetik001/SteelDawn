import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout

import game


class CountrySelection(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color((248, 244, 235))

    def on_show_view(self):
        self.manager = UIManager(self.window)
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=28)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout, anchor_x="center", anchor_y="top", align_y=-170)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        button_style = {
            "normal": {
                "bg": (248, 244, 235, 0),
                "font_color": (40, 40, 40),
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

        de_btn = UIFlatButton(
            text="> DEU: Третий рейх — Ось",
            width=600,
            height=36,
            style=button_style
        )
        de_btn.on_click = self.startGame
        self.box_layout.add(de_btn)

        su_btn = UIFlatButton(
            text="> URS: Советский Союз — Союзники",
            width=600,
            height=36,
            style=button_style
        )
        su_btn.on_click = self.startGame
        self.box_layout.add(su_btn)

    def startGame(self, event):
        self.window.show_view(game.Game())

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "ОПЕРАТИВНЫЙ СПИСОК НАЦИЙ",
            self.width // 2,
            self.height - 110,
            (50, 50, 50),
            font_size=30,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_text(
            "Выберите сторону для ведения операции",
            self.width // 2,
            self.height - 150,
            (100, 100, 100),
            font_size=18,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_line(
            start_x=self.width // 2 - 220,
            start_y=self.height - 170,
            end_x=self.width // 2 + 220,
            end_y=self.height - 170,
            color=(180, 180, 180),
            line_width=1
        )

        arcade.draw_text(
            "КОДЫ НАЦИЙ СООТВЕТСТВУЮТ СТАНДАРТУ MIL-STD-1008",
            self.width // 2,
            60,
            (140, 140, 140),
            font_size=13,
            font_name=("Courier New",),
            anchor_x="center",
            italic=True
        )

        self.manager.draw()