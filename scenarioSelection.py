import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout
import countrySelection


class ScenarioSelection(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show_view(self):
        arcade.set_background_color((248, 244, 235))

        self.manager = UIManager(self.window)
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=30)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout, anchor_x="center", anchor_y="top", align_y=-160)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        button_style = {
            "normal": {
                "bg": (248, 244, 235, 0),
                "font_color": (40, 40, 40),
                "font_name": ("Courier New", "Consolas", "monospace"),
                "font_size": 20,
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

        btn_1939 = UIFlatButton(
            text="> Вторжение в Польшу (сентябрь 1939)",
            width=680,
            height=36,
            style=button_style
        )
        btn_1939.on_click = self.startGame
        self.box_layout.add(btn_1939)

        btn_1941 = UIFlatButton(
            text="> Операция «Барбаросса» (июнь 1941)",
            width=680,
            height=36,
            style=button_style
        )
        btn_1941.on_click = self.startGame
        self.box_layout.add(btn_1941)

    def startGame(self, event):
        self.window.show_view(countrySelection.CountrySelection())

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "ВОЕННО-ИСТОРИЧЕСКИЙ АРХИВ",
            self.width // 2,
            self.height - 80,
            (60, 60, 60),
            font_size=32,
            font_name=("Courier New", "Consolas"),
            anchor_x="center",
            bold=False
        )

        arcade.draw_text(
            "ИНДЕКС: SD-1939 / SD-1941     ДОПУСК: УТВЕРЖДЁН",
            self.width // 2,
            self.height - 120,
            (100, 100, 100),
            font_size=18,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_line(
            start_x=self.width // 2 - 250,
            start_y=self.height - 140,
            end_x=self.width // 2 + 250,
            end_y=self.height - 140,
            color=(180, 180, 180),
            line_width=1
        )

        arcade.draw_text(
            "«Steel Dawn» — альтернативная история. Все сценарии вымышлены.",
            self.width // 2,
            50,
            (140, 140, 140),
            font_size=14,
            font_name=("Courier New",),
            anchor_x="center",
            italic=True
        )

        self.manager.draw()