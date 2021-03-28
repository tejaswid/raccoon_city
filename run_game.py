import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Racoon"

class MainGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.BLUE_VIOLET)

    def setup(self):
        pass

    def on_draw(self):

        arcade.start_render()


def main():
    window = MainGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()