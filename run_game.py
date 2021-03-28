import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Racoon"

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


    def on_draw(self):
        """Render screen."""
        # Clear the screen with the plain background
        arcade.start_render()

        # Draw the sprite lists
        self.wall_list.draw()
        self.item_list.draw()
        self.player_list.draw()

def main():
    """Set up and launch the game."""
    window = MainGame()     # instantiate the main window of the game
    window.setup()          # call the setup function to set the game up
    arcade.run()            # run the game


if __name__ == "__main__":
    main()