import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Racoon"

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 20
GRAVITY = 1

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100


class MainGame(arcade.Window):
    """Main application class."""

    def __init__(self):
        """Initialize the class."""
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set background color here
        arcade.set_background_color(arcade.csscolor.DIM_GRAY)

        # Setup lists for sprites. All sprites shoudl go into one of these lists
        self.item_list = None       # list of pickup items
        self.wall_list = None       # list of all obstacles and immovable objects
        self.player_list = None     # list for the player

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # the physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Load sounds
        # when using :resources:, the sounds are loaded from arcade's library. not the from the current project's library
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def setup(self):
        """Set the game up. Call this function to restart the game."""
        # Initialize the sprite lists.
        # Set use_spatial_hash to True to speed up collision detection. But it slows movement
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)   
        self.item_list = arcade.SpriteList(use_spatial_hash=True)

        # Set the sprite for the player and position it as necessary
        image_source = "resources/images/cop/cop.png"
        self.player_sprite = arcade.Sprite(image_source)
        self.player_sprite.scale = 1.0
        self.player_sprite.center_x = 30
        self.player_sprite.center_y = 155
        self.player_list.append(self.player_sprite)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 800, 105):
            wall = arcade.Sprite("resources/images/objects/floor200x200.png")
            wall.scale = 0.5
            wall.center_x = x
            wall.center_y = 50
            self.wall_list.append(wall)

        # Create blocks at desired locations
        coordinate_list = [[100, 125], [250, 125], [700, 125]]
        for coordinates in coordinate_list:
            wall = arcade.Sprite("resources/images/objects/block50x50.png")
            wall.scale = 1.0
            wall.position = coordinates
            self.wall_list.append(wall)

        # Create items at desired locations
        coordinate_list = [[200, 200], [500, 150], [600, 230]]
        
        for coordinates in coordinate_list:
            coin = arcade.Sprite("resources/images/objects/coin50x100.png")
            coin.scale = 0.5
            coin.position = coordinates
            self.item_list.append(coin)

        # Create a physics engine for the player. tell the engine what objects the player cannot pass through
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)


    def on_draw(self):
        """Render screen."""
        # Clear the screen with the plain background
        arcade.start_render()

        # Draw the sprite lists
        self.wall_list.draw()
        self.item_list.draw()
        self.player_list.draw()


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0


    def on_update(self, delta_time):
        """ Movement and game logic. This function is called 60 times a second """

        # Move the player with the physics engine
        self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """Set up and launch the game."""
    window = MainGame()     # instantiate the main window of the game
    window.setup()          # call the setup function to set the game up
    arcade.run()            # run the game


if __name__ == "__main__":
    main()