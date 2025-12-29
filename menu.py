import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UIFlatButton
import random

class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        self.setup()

        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        flat_button = UIFlatButton(text="Плоская Кнопка", width=200, height=50, color=arcade.color.BLUE)
        flat_button.on_click = lambda event: print("Flat клик!")  # Не только лямбду, конечно
        self.box_layout.add(flat_button)

    def setup(self):
        num = random.randint(1, 2)
        self.texture = arcade.load_texture(f"images/backgrounds/menu_bg{num}.png")

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.texture,
            arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        )