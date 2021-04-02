"""
This is the code for the game ..... developed for pyweek31.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla

"""

import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Racoon"

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 15
PLAYER_JUMP_SPEED = 20
GRAVITY = 1

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

# Ends of the view port = ends of the level
VIEWPORT_BUFFER = 10    # just a small positive value
LEVEL_LEFT_END = VIEWPORT_BUFFER
LEVEL_RIGHT_END = 12800 - SCREEN_WIDTH - VIEWPORT_BUFFER


# scaling for different objects
TILE_SCALING = 1.0

# How should different layers move wrt player speed
SKY_SPEED_SCALING = 0.2

class MainGame(arcade.Window):
    """Main application class."""

    def __init__(self):
        """Initialize the class."""
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set background color here
        arcade.set_background_color(arcade.csscolor.DIM_GRAY)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Setup lists for sprites. All sprites shoudl go into one of these lists
        self.items_list = None       # list of pickup items
        self.stage_list = None      # list of all stage objects - platform, blocks, walls
        self.player_list = None     # list for the player
        self.bkg_list = None

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

        # keep track of score
        self.score = 0

        # boolean to know if the game just started
        self.view_is_just_started = True

    def setup(self):
        """Set the game up. Call this function to restart the game."""
        # Initialize the sprite lists.
        # Set use_spatial_hash to True to speed up collision detection. But it slows movement
        self.player_list = arcade.SpriteList()
        self.stage_list = arcade.SpriteList(use_spatial_hash=True)   
        self.items_list = arcade.SpriteList(use_spatial_hash=True)
        self.bkg_list = arcade.SpriteList()

        # Set the sprite for the player and position it as necessary
        image_source = "resources/images/cop/cop.png"
        self.player_sprite = arcade.Sprite(image_source)
        self.player_sprite.scale = 1.0
        self.player_sprite.center_x = 100       # where to place the centre of the sprite along horizontal
        self.player_sprite.center_y = 155       # where to place the centre of the sprite along vertical
        self.player_list.append(self.player_sprite)

        # ------------------------------------------
        # Load the map created by the tile editor
        # ------------------------------------------
        # --> Name of map file to load
        map_name = "resources/map/map.tmx"
        
        # --> Nmae of the layers
        stage_layer_name = 'stage'      # layer with platform / blocks / walls
        items_layer_name = 'items'      # layer with pickup items
        sky_layer_name = 'sky'          # layer with sky
        moving_blocks_layer_name = 'obstacles'
        # --> Read in the tiled map
        game_map = arcade.tilemap.read_tmx(map_name)

        # --> Load the platforms
        self.stage_list = arcade.tilemap.process_layer(map_object=game_map,
                                                      layer_name=stage_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        self.items_list = arcade.tilemap.process_layer(map_object=game_map,
                                                      layer_name=items_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)   

        moving_blocks_list = arcade.tilemap.process_layer(map_object=game_map,
                                                      layer_name=moving_blocks_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)                                                       
        for sprite in moving_blocks_list:
            self.stage_list.append(sprite)

        # # Create the ground
        # # This shows using a loop to place multiple sprites horizontally
        # for x in range(0, 800, 105):
        #     wall = arcade.Sprite("resources/images/objects/floor200x200.png")
        #     wall.scale = 0.5
        #     wall.center_x = x
        #     wall.center_y = 50
        #     self.stage_list.append(wall)

        # # Create blocks at desired locations
        # coordinate_list = [[100, 125], [250, 125], [700, 125]]
        # for coordinates in coordinate_list:
        #     wall = arcade.Sprite("resources/images/objects/block50x50.png")
        #     wall.scale = 1.0
        #     wall.position = coordinates
        #     self.stage_list.append(wall)

        bkg = arcade.Sprite("resources/images/backgrounds/bkg1_1920x1080.png")
        bkg.scale = 1
        bkg.center_x = SCREEN_WIDTH / 2
        bkg.center_y = SCREEN_HEIGHT / 2
        self.bkg_list.append(bkg)

        # self.bkg_list = arcade.tilemap.process_layer(map_object=game_map,
        #                                              layer_name=sky_layer_name,
        #                                              scaling=TILE_SCALING,
        #                                              use_spatial_hash=False) 



        # Create a physics engine for the player. tell the engine what objects the player cannot pass through
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.stage_list,
                                                             GRAVITY)

        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Initialize score to zero
        self.score = 0

    def on_draw(self):
        """Render screen."""
        # Clear the screen with the plain background
        arcade.start_render()

        # Draw the sprite lists
        self.bkg_list.draw()
        self.stage_list.draw()
        self.items_list.draw()
        self.player_list.draw()
        

        # Draw the score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

    def process_keychange(self):
        """Change player state when a key is pressed."""
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0


    def on_key_press(self, key, modifiers):
        """Call whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()


    def on_key_release(self, key, modifiers):
        """Call when the user releases a key."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        self.process_keychange()

    def on_update(self, delta_time):
        """Update positions and game logic. This function is called 60 times a second."""
        # Move the player with the physics engine
        self.physics_engine.update()

        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        # check collision with items
        item_hit_list = arcade.check_for_collision_with_list(self.player_sprite,self.items_list)

        # Loop through each item we hit (if any) and remove it
        for item in item_hit_list:
            # Remove the item
            item.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Update the score
            self.score += 1

        # Update moving blocks
        self.stage_list.update()

        # change direction in which the moving objects move, only movable objects have 
        # boundary_... and change_... properties defined
        for obstacle in self.stage_list:
            # left - right inversion
            if obstacle.boundary_left and obstacle.left < obstacle.boundary_left and obstacle.change_x < 0:
                obstacle.change_x *= -1
            if obstacle.boundary_right and obstacle.right > obstacle.boundary_right and obstacle.change_x > 0:
                obstacle.change_x *= -1

            # top-bottom inversion
            if obstacle.boundary_top and obstacle.top > obstacle.boundary_top and obstacle.change_y > 0:
                obstacle.change_y *= -1
            if obstacle.boundary_bottom and obstacle.bottom < obstacle.boundary_bottom and obstacle.change_y < 0:
                obstacle.change_y *= -1


        # --- Manage Scrolling ---

        # Track if we need to change the viewport
        changed_viewport = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        # Start scrolling left only after the player crosses the left boundary
        # for the first time. Until then keep the view.left to 0
        if self.view_is_just_started:
            if self.player_sprite.left > left_boundary:
                self.view_is_just_started = False
        else:
            if self.player_sprite.left < left_boundary:
                # if we reach the start of the game, stop scrolling left
                if self.view_left < LEVEL_LEFT_END:     # This is just a small positive buffer value
                    # do not scroll left
                    changed_viewport = False
                else:
                    self.view_left -= left_boundary - self.player_sprite.left
                    changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            if self.view_left > LEVEL_RIGHT_END:
                changed_viewport = False
            else:
                self.view_left += self.player_sprite.right - right_boundary
                changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

        # scroll the background sprite slowly
        if self.player_sprite.left > LEVEL_LEFT_END and self.player_sprite.right < LEVEL_RIGHT_END:
            self.bkg_list[0].center_x -= self.player_sprite.change_x * SKY_SPEED_SCALING

def main():
    """Set up and launch the game."""
    window = MainGame()     # instantiate the main window of the game
    window.setup()          # call the setup function to set the game up
    arcade.run()            # run the game


if __name__ == "__main__":
    main()