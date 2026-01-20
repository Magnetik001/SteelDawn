import arcade
import arcade.gui
import style
import menu
import game

class Message(arcade.View):
    def __init__(self, prov, resourse, year):
        super().__init__()
        self.prov_name = prov.name
        self.year = year
        self.prov_resource = resourse
        arcade.set_background_color((129, 127, 104))

    def on_show_view(self):
        self.manager = arcade.gui.UIManager(self.window)
        self.manager.enable()

        self.anchor_layout = arcade.gui.UIAnchorLayout()
        self.box_layout = arcade.gui.UIBoxLayout(vertical=True, space_between=30)

        text_label = arcade.gui.UITextArea(width=600, height=400,
                                           text=f"{self.prov_name.upper()}\n{self.prov_resource}",
                                           text_color=arcade.color.BLACK, font_size=44)
        self.box_layout.add(text_label)

        buy_button = arcade.gui.UIFlatButton(
            text="Создать армию (потратить что-то там)",
            width=900,
            height=100,
            style=style.dark_button_style)
        close_button = arcade.gui.UIFlatButton(
            text="Закрыть",
            width=900,
            height=100,
            style=style.dark_button_style)

        buy_button.on_click = self.buy_army

        close_button.on_click = self.close_message

        # Обернем кнопки в HorizontalLayout для отображения в линию
        button_layout = arcade.gui.UIBoxLayout(horizontal=True)
        button_layout.add(buy_button)
        button_layout.add(close_button)

        self.box_layout.add(button_layout)
        self.anchor_layout.add(self.box_layout, anchor_x="center", anchor_y="top", align_y=-100)
        self.manager.add(self.anchor_layout)


    def close_message(self):
        self.window.show_view(game.Game(self.year, event))

    def buy_army(self):
        pass


    def on_draw(self):
        self.clear()
        self.manager.draw()