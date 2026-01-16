import arcade
from arcade.gui import UIManager, UIFlatButton, UIAnchorLayout, UIBoxLayout
import game

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
    """Первый экран: выбор 1938 или 1941 года"""

    def __init__(self):
        super().__init__()
        arcade.set_background_color((248, 244, 235))
        self.selected_year = None

    def on_show_view(self):
        self.manager = UIManager(self.window)
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=30)

        # Стиль кнопок - ВАШ ТОЧНЫЙ СТИЛЬ
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

        # Кнопка 1938
        btn_1938 = UIFlatButton(
            text="> 1938 - ЗА ЧАС ДО СОБЫТИЙ",
            width=520,
            height=36,
            style=button_style
        )
        btn_1938.on_click = lambda e: self.select_year(1938)
        self.box_layout.add(btn_1938)

        # Кнопка 1941
        btn_1941 = UIFlatButton(
            text="> 1941 - ВСЕ НА ВОСТОК!!!",
            width=520,
            height=36,
            style=button_style
        )
        btn_1941.on_click = lambda e: self.select_year(1941)
        self.box_layout.add(btn_1938)
        self.box_layout.add(btn_1941)

        self.anchor_layout.add(self.box_layout, anchor_x="center", anchor_y="top", align_y=-180)
        self.manager.add(self.anchor_layout)

    def select_year(self, year):
        """Переходим к выбору страны для выбранного года"""
        self.selected_year = year
        country_view = CountrySelectionView(year)
        self.window.show_view(country_view)


    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        # ВАШ ТОЧНЫЙ ТЕКСТ С ЗАГОЛОВКАМИ
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


# ВЫБОР СТРАНЫ
class CountrySelectionView(arcade.View):
    """Второй экран: выбор страны для выбранного года"""

    def __init__(self, year):
        super().__init__()
        self.year = year
        self.countries = COUNTRIES_BY_YEAR.get(year, [])
        arcade.set_background_color((248, 244, 235))

    def on_show_view(self):
        self.manager = UIManager(self.window)
        self.manager.enable()

        # Создаем основной контейнер с прокруткой
        self.main_box = UIBoxLayout(vertical=True, space_between=10)

        # Заголовок
        title_style = {
            "normal": {
                "bg": (248, 244, 235, 0),
                "font_color": (60, 60, 60),
                "font_name": ("Courier New", "Consolas", "monospace"),
                "font_size": 20,
                "border": 0,
            }
        }


        # Стиль кнопок стран (ВАШ СТИЛЬ)
        country_button_style = {
            "normal": {
                "bg": (248, 244, 235, 0),
                "font_color": (40, 40, 40),
                "font_name": ("Courier New", "Consolas", "monospace"),
                "font_size": 18,
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

        # Создаем кнопки для всех стран
        for country in self.countries:
            btn = UIFlatButton(
                text=f"> {country.upper()}",
                width=480,
                height=32,
                style=country_button_style
            )
            btn.on_click = lambda e, c=country: self.startGame(c)
            self.main_box.add(btn)

        # Кнопка возврата
        back_style = {
            "normal": {
                "bg": (248, 244, 235, 0),
                "font_color": (100, 100, 100),
                "font_name": ("Courier New", "Consolas", "monospace"),
                "font_size": 16,
                "border": 0,
            },
            "hover": {
                "font_color": (70, 70, 70),
                "bg": (235, 230, 220, 80),
            }
        }

        back_btn = UIFlatButton(
            text="< НАЗАД",
            width=300,
            height=28,
            style=back_style
        )
        back_btn.on_click = lambda e: self.window.show_view(Menu())
        self.main_box.add(back_btn)

        # Размещаем по центру
        self.anchor = UIAnchorLayout()
        self.anchor.add(self.main_box, anchor_x="center", anchor_y="top", align_y=-100)
        self.manager.add(self.anchor)


    def on_hide_view(self):
        self.manager.disable()

    def startGame(self, event):
        self.window.show_view(game.Game())

    def on_draw(self):
        self.clear()

        # Фоновый текст (как в оригинале)
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


def main():
    window = arcade.Window(1024, 768, "STEEL DAWN")
    start_view = Menu()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
