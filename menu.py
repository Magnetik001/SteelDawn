import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout
import scenarioSelection


class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color((248, 244, 235))

    def on_show_view(self):

        self.manager = UIManager(self.window)
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=30)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout, anchor_x="center", anchor_y="top", align_y=-180)
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

        start_btn = UIFlatButton(
            text="> ПРИСТУПИТЬ К ОПЕРАЦИИ",
            width=520,
            height=36,
            style=button_style
        )
        start_btn.on_click = self.startGame
        self.box_layout.add(start_btn)

    def startGame(self, event):
        self.window.show_view(scenarioSelection.ScenarioSelection())

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "STEEL DAWN",
            self.width // 2,
            self.height - 120,
            (50, 50, 50),
            font_size=56,
            font_name=("Courier New", "Consolas"),
            anchor_x="center",
            bold=False
        )

        arcade.draw_text(
            "ВОЕННО-СТРАТЕГИЧЕСКИЙ СИМУЛЯТОР АЛЬТЕРНАТИВНОЙ ИСТОРИИ",
            self.width // 2,
            self.height - 170,
            (100, 100, 100),
            font_size=18,
            font_name=("Courier New",),
            anchor_x="center"
        )


        arcade.draw_text(
            "ДОПУСК: ГЛАВНОКОМАНДУЮЩИЙ     АРХИВ: ОТДЕЛ ИСТОРИЧЕСКИХ ОПЕРАЦИЙ",
            self.width // 2,
            80,
            (130, 130, 130),
            font_size=14,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_text(
            "ДАННЫЙ СИМУЛЯТОР ЯВЛЯЕТСЯ ИСТОРИЧЕСКИМ ЭКСПЕРИМЕНТОМ. ВСЕ СОБЫТИЯ УСЛОВНЫ.",
            self.width // 2,
            50,
            (150, 150, 150),
            font_size=12,
            font_name=("Courier New",),
            anchor_x="center",
            italic=True
        )

        self.manager.draw()