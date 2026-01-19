import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout
import game
import style

COUNTRIES_BY_YEAR = {
    1938: [
        "Германия", "СССР", "Великобритания", "Франция", "Италия",
        "Польша", "Чехословакия", "Испания", "Турция", "Швеция",
        "Румыния", "Венгрия", "Югославия", "Греция", "Бельгия",
        "Нидерланды", "Дания", "Норвегия", "Финляндия", "Португалия",
        "Швейцария", "Ирландия", "Болгария", "Австрия", "Литва",
        "Латвия", "Эстония"
    ],
    1941: [
        "Германия", "СССР", "Великобритания", "Италия", "Словакия",
        "Франция Виши", "Свободная Франция", "Хорватия",
        "Венгрия", "Румыния", "Болгария", "Финляндия",
        "Швеция", "Швейцария", "Португалия", "Испания", "Турция",
        "Ирландия"
    ]
}


class Menu(arcade.View):

    def __init__(self):
        super().__init__()
        arcade.set_background_color((248, 244, 235))
        self.selected_year = None

    def on_show_view(self):
        self.manager = UIManager(self.window)
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=30)

        btn_1938 = UIFlatButton(
            text="> 1938 г.",
            width=520,
            height=36,
            style=style.button_style
        )
        btn_1938.on_click = lambda e: self.select_year(1938)
        self.box_layout.add(btn_1938)

        btn_1941 = UIFlatButton(
            text="> 1941 г.",
            width=520,
            height=36,
            style=style.button_style
        )
        btn_1941.on_click = lambda e: self.select_year(1941)
        self.box_layout.add(btn_1938)
        self.box_layout.add(btn_1941)

        self.anchor_layout.add(self.box_layout, anchor_x="center", anchor_y="top", align_y=-180)
        self.manager.add(self.anchor_layout)

    def select_year(self, year):
        self.selected_year = year
        country_view = CountrySelectionView(year)
        self.window.show_view(country_view)


    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "STEEL DAWN",
            self.window.width // 2,
            self.window.height - 120,
            (50, 50, 50),
            font_size=56,
            font_name=("Courier New", "Consolas"),
            anchor_x="center",
            bold=False
        )

        arcade.draw_text(
            "ВОЕННО-СТРАТЕГИЧЕСКИЙ СИМУЛЯТОР АЛЬТЕРНАТИВНОЙ ИСТОРИИ",
            self.window.width // 2,
            self.window.height - 170,
            (100, 100, 100),
            font_size=18,
            font_name=("Courier New",),
            anchor_x="center"
        )


        arcade.draw_text(
            "ДОПУСК: ГЛАВНОКОМАНДУЮЩИЙ     АРХИВ: ОТДЕЛ ИСТОРИЧЕСКИХ ОПЕРАЦИЙ",
            self.window.width // 2,
            80,
            (130, 130, 130),
            font_size=14,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_text(
            "«Steel Dawn» — альтернативная история. Все сценарии вымышлены.",
            self.window.width // 2,
            50,
            (150, 150, 150),
            font_size=12,
            font_name=("Courier New",),
            anchor_x="center",
            italic=True
        )

        self.manager.draw()


class CountrySelectionView(arcade.View):

    def __init__(self, year):
        super().__init__()
        self.year = year
        self.countries = COUNTRIES_BY_YEAR.get(year, [])
        arcade.set_background_color((248, 244, 235))

    def on_show_view(self):
        self.manager = UIManager(self.window)
        self.manager.enable()

        self.main_box = UIBoxLayout(vertical=True, space_between=10)


        for country in self.countries:
            btn = UIFlatButton(
                text=f"> {country.upper()}",
                width=480,
                height=32,
                style=style.country_button_style
            )
            btn.on_click = lambda e, c=country: self.startGame(c)
            self.main_box.add(btn)

        back_btn = UIFlatButton(
            text="< НАЗАД",
            width=300,
            height=28,
            style=style.back_style
        )
        back_btn.on_click = lambda e: self.window.show_view(Menu())
        self.main_box.add(back_btn)

        self.anchor = UIAnchorLayout()
        self.anchor.add(self.main_box, anchor_x="center", anchor_y="top", align_y=-100)
        self.manager.add(self.anchor)


    def on_hide_view(self):
        self.manager.disable()

    def startGame(self, event):
        self.window.show_view(game.Game(self.year, event))

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            f"{self.year}",
            self.window.width // 2,
            self.window.height - 40,
            (200, 200, 200),
            font_size=34,
            font_name=("Courier New", "Consolas"),
            anchor_x="center",
            bold=True
        )

        arcade.draw_text(
            "ДОПУСК: ГЛАВНОКОМАНДУЮЩИЙ     АРХИВ: ОТДЕЛ ИСТОРИЧЕСКИХ ОПЕРАЦИЙ",
            self.window.width // 2,
            40,
            (130, 130, 130),
            font_size=14,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_text(
            "ОПЕРАТИВНЫЙ СПИСОК НАЦИЙ",
            self.width // 6,
            self.height - 110,
            (50, 50, 50),
            font_size=30,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_text(
            "Выберите страну для ведения операции",
            self.width // 6,
            self.height - 150,
            (100, 100, 100),
            font_size=18,
            font_name=("Courier New",),
            anchor_x="center"
        )

        arcade.draw_line(
            start_x=self.width // 6 - 220,
            start_y=self.height - 170,
            end_x=self.width // 6 + 220,
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
