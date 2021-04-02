"""
This script defines the classes for different screens.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla
"""

import arcade
from game_view import GameView

class InstructionsView(arcade.View):
    """Instruction View class."""

    def __init__(self, screen_width, screen_height, sprite_size):
        """Initialize the class.

        :param screen_width: screen width in pixels
        :type screen_width: int
        :param screen_height: screen height in pixels
        :type screen_height: int
        :param sprite_size: size of a sprite in pixels
        :type sprite_size: int
        """
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sprite_size = sprite_size

    def on_show(self):
        """Show once when we run this view."""
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.screen_width - 1, 0, self.screen_height - 1)

    def on_draw(self):
        """Draw this view."""
        arcade.start_render()
        arcade.draw_text("Instructions Screen", self.screen_width / 2, self.screen_height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Press any key to start", self.screen_width / 2, self.screen_height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        """Handle a key press. 

        When any key is pressed this view switches to the main game.
        :param key: The key that is pressed
        :type key: int
        :param modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
        pressed during this event. See :ref:`keyboard_modifiers`.
        :type modifiers: int
        """
        game_view = GameView(self.screen_width, self.screen_height, self.sprite_size)
        game_view.setup()
        self.window.show_view(game_view)


class GameOverView(arcade.View):

    def __init__(self, screen_width, screen_height, sprite_size):
        """Initialize the class.

        :param screen_width: screen width in pixels
        :type screen_width: int
        :param screen_height: screen height in pixels
        :type screen_height: int
        :param sprite_size: size of a sprite in pixels
        :type sprite_size: int
        """
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sprite_size = sprite_size
        
        # tecture showing the game over screen
        self.texture = arcade.load_texture("resources/images/screens/game_over.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.screen_width - 1, 0, self.screen_height - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        self.texture.draw_sized(self.screen_width / 2, self.screen_height / 2,
                                self.screen_width, self.screen_height)

    def on_key_press(self, key, modifiers):
        """Handle a key press. 

        When any key is pressed this view switches to the main game.
        :param key: The key that is pressed
        :type key: int
        :param modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
        pressed during this event. See :ref:`keyboard_modifiers`.
        :type modifiers: int
        """
        if key == arcade.key.R:
            game_view = GameView(self.screen_width, self.screen_height, self.sprite_size)
            game_view.setup()
            self.window.show_view(game_view)
    