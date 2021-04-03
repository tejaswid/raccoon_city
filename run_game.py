"""
This is the code for the game ..... developed for pyweek31.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla
"""
import os
import arcade

from game_view import InstructionsView

# Title of the game
global SCREEN_TITLE
SCREEN_TITLE = "Racoon"

# How big are our image tiles?
global SPRITE_IMAGE_SIZE
SPRITE_IMAGE_SIZE = 128

# Scale sprites up or down
global SPRITE_SCALING_PLAYER
SPRITE_SCALING_PLAYER = 1.0
global SPRITE_SCALING_TILES
SPRITE_SCALING_TILES = 1.0

# Scaled sprite size for tiles
global SPRITE_SIZE
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# Size of grid to show on screen, in number of tiles
NUM_TILES_ALONG_WIDTH = 10
NUM_TILES_ALONG_HEIGHT = 7

# Size of screen to show, in pixels
global SCREEN_WIDTH
SCREEN_WIDTH = SPRITE_SIZE * NUM_TILES_ALONG_WIDTH      # 1280
global SCREEN_HEIGHT
SCREEN_HEIGHT = SPRITE_SIZE * NUM_TILES_ALONG_HEIGHT    # 768


def main():
    """Call main function."""
    # instantiate a window for the game
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    # create the starting view
    starting_view = InstructionsView(SCREEN_WIDTH, SCREEN_HEIGHT, SPRITE_SIZE)
    # show the view in the window
    window.show_view(starting_view)
    # run the game
    arcade.run()


if __name__ == "__main__":
    main()