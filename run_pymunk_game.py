"""
This is the code for the game ..... developed for pyweek31.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla

"""
import os
import arcade

# Title of the game
SCREEN_TITLE = "Racoon"

# How big are our image tiles?
SPRITE_IMAGE_SIZE = 128

# Scale sprites up or down
SPRITE_SCALING_PLAYER = 1.0
SPRITE_SCALING_TILES = 1.0

# Scaled sprite size for tiles
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# Size of grid to show on screen, in number of tiles
NUM_TILES_ALONG_WIDTH = 10
NUM_TILES_ALONG_HEIGHT = 6

# Size of screen to show, in pixels
SCREEN_WIDTH = SPRITE_SIZE * NUM_TILES_ALONG_WIDTH      # 1280
SCREEN_HEIGHT = SPRITE_SIZE * NUM_TILES_ALONG_HEIGHT    # 768

# --- Physics forces. Higher number, faster accelerating.
# Gravity
GRAVITY = 1500

# Damping - Factor of speed kept in 1 second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

# Friction between objects, 0.0=ice, 1.0=rubber
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.0

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 900

# Strength of a jump
PLAYER_JUMP_IMPULSE = 1800
PLAYER_DOUBLEJUMP_IMPULSE_SCALING = 0.6 

# --- Animation constants.
# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 20

# --- Viewport constants
# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 50

# Ends of the view port = ends of the level
NUM_TILES_LEVEL_ALONG_WIDTH = 100
VIEWPORT_BUFFER = 10    # just a small positive value
LEVEL_LEFT_END = VIEWPORT_BUFFER
LEVEL_RIGHT_END = NUM_TILES_LEVEL_ALONG_WIDTH * SPRITE_SIZE - SCREEN_WIDTH - VIEWPORT_BUFFER

class PlayerSprite(arcade.Sprite):
    """Player Sprite."""
    def __init__(self):
        """Initialize the class."""
        # Let parent initialize
        super().__init__()

        # Set our scale
        self.scale = SPRITE_SCALING_PLAYER

        # Load textures for idle standing
        resource_path = "resources/images/cop"
        self.idle_texture_pair = arcade.load_texture_pair(os.path.join(resource_path, "cop_idle.png"))
        self.jump_texture_pair = arcade.load_texture_pair(os.path.join(resource_path, "cop_jump.png"))
        self.fall_texture_pair = arcade.load_texture_pair(os.path.join(resource_path, "cop_fall.png"))

        # Load textures for walking
        self.walk_textures = []
        self.num_walk_textures = 3
        for i in range(self.num_walk_textures):
            texture = arcade.load_texture_pair(os.path.join(resource_path, f"cop_{i}.png"))
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Index of our current texture
        self.cur_texture = 0

        # How far have we traveled horizontally since changing the texture
        self.x_odometer = 0

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Handle being moved by the pymunk engine.

        :param physics_engine: The physics engine
        :type physics_engine: arcade.PymunkPhysicsEngine
        :param dx: amount moved along x direction
        :type dx: float
        :param dy: amount moved along y direction
        :type dy: float
        :param d_angle: angle moved
        :type d_angle: float
        """
        # Figure out if we need to face left or right
        if dx < -DEAD_ZONE and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx

        # Jumping animation
        if not is_on_ground:
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return

        # Idle animation
        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Have we moved far enough to change the texture?
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:

            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_texture += 1
            if self.cur_texture >= self.num_walk_textures:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]


class GameWindow(arcade.Window):
    """Main Game Window class."""

    def __init__(self, width, height, title):
        """Initialize the class.

        :param width: Width of the window in pixels
        :type width: int
        :param height: Height of the window in pixels
        :type height: int
        :param title: Name of the window
        :type title: str
        """
        # Init the parent class
        super().__init__(width, height, title)

        # Setup lists for sprites. All sprites shoudl go into one of these lists
        self.player_list: arcade.SpriteList = None
        self.stage_list: arcade.SpriteList = None
        self.bullet_list: arcade.SpriteList = None
        self.items_list: arcade.SpriteList = None
        self.bkg_list: arcade.SpriteList = None

        # Player sprite
        self.player_sprite: PlayerSprite = None

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False

        # Physics engine
        self.physics_engine: arcade.PymunkPhysicsEngine = None

        # Flag for double jump
        self.allow_double_jump: bool = True

        # Set background color
        arcade.set_background_color(arcade.csscolor.DIM_GRAY)

        # Viewport variables
        self.view_left: int = 0
        self.view_bottom: int = 0
        self.view_is_just_started: bool = True

        # Sounds
        # when using :resources:, the sounds are loaded from arcade's library. not the from the current project's library
        self.collect_coin_sound: arcade.Sound = arcade.load_sound("resources/sounds/coin1.wav")
        self.jump_sound: arcade.Sound = arcade.load_sound("resources/sounds/jump3.wav")
        self.double_jump_sound: arcade.Sound = arcade.load_sound("resources/sounds/jump4.wav")
        self.game_start_sound: arcade.Sound = arcade.load_sound("resources/sounds/secret2.wav")

        # Score
        self.score: int = 0

    def setup(self):
        """Set the game up. Call this function to restart the game.
        
        A level ID can be passed to switch between levels.
        """
        # create sprite lists
        self.bullet_list = arcade.SpriteList()
        self.bkg_list = arcade.SpriteList()

        # Read in the tiled map
        map_name = "resources/maps/map.tmx"
        game_map = arcade.tilemap.read_tmx(map_name)

        # Read in the map layers to specific lists
        self.stage_list = arcade.tilemap.process_layer(game_map, 'stage', SPRITE_SCALING_TILES)
        self.items_list = arcade.tilemap.process_layer(game_map, 'items', SPRITE_SCALING_TILES)

        # --------
        # Player
        # --------
        # Create player sprite
        self.player_sprite = PlayerSprite()
        # Set player location at the centre of the specified grid
        grid_x = 1
        grid_y = 1
        self.player_sprite.center_x = SPRITE_SIZE * grid_x + SPRITE_SIZE / 2
        self.player_sprite.center_y = SPRITE_SIZE * grid_y + SPRITE_SIZE / 2
        # Add to player sprite list
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        # setup the physics engine
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=damping,
                                                         gravity=gravity)

        # ------------------------------------
        # Add sprites to the physics engine
        # ------------------------------------
        # Player. 
        # Setting the moment to PymunkPhysicsEngine.MOMENT_INF prevents it from rotating.
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
        # Stage.
        # Setting the body type to PymunkPhysicsEngine.STATIC
        # Movable objects that respond to forces are PymunkPhysicsEngine.DYNAMIC
        # PymunkPhysicsEngine.KINEMATIC objects will move, but are assumed to be
        # repositioned by code and don't respond to physics forces.
        # Dynamic is default.
        self.physics_engine.add_sprite_list(self.stage_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        # Items.
        self.physics_engine.add_sprite_list(self.items_list,
                                            friction=DYNAMIC_ITEM_FRICTION,
                                            collision_type="item")  
        self.physics_engine.add_collision_handler("player", "item", post_handler=self.item_hit_handler)

        # Initialize score to zero
        self.score = 0

        # Play a game start sound - helps load sounds faster
        arcade.play_sound(self.game_start_sound)

    def on_key_press(self, key, modifiers):
        """Handle a key press.

        :param key: The key that is pressed
        :type key: int
        :param modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
        pressed during this event. See :ref:`keyboard_modifiers`.
        :type modifiers: int
        """
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite):
                self.allow_double_jump = True
                arcade.play_sound(self.jump_sound)
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
            else:
                if self.allow_double_jump:
                    self.allow_double_jump = False
                    arcade.play_sound(self.double_jump_sound)
                    impulse = (0, PLAYER_JUMP_IMPULSE * PLAYER_DOUBLEJUMP_IMPULSE_SCALING)
                    self.physics_engine.apply_impulse(self.player_sprite, impulse)

    def on_key_release(self, key, modifiers):
        """Handle a key release.

        :param key: The key that is released
        :type key: int
        :param modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
        pressed during this event. See :ref:`keyboard_modifiers`.
        :type modifiers: int
        """
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def item_hit_handler(self, player_sprite, item_sprite, _arbiter, _space, _data):
            """Handle collision between player and item"""
            item_sprite.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Update the score
            self.score += 1

    def on_update(self, delta_time):
        """Update positions and game logic. This function is called 60 times a second.

        :param delta_time: Time interval since the last time the function was called in seconds.
        :type delta_time: float
        """
        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        
        # Update player forces based on keys pressed
        if self.left_pressed and not self.right_pressed:
            # Create a force to the left. Apply it.
            if is_on_ground:
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)   # apply ground force
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)  # apply air force
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            if is_on_ground:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)   # apply ground force
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)  # apply air force
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # Move items in the physics engine
        self.physics_engine.step()

    def on_draw(self):
        """Draw everything to screen."""
        arcade.start_render()
        # Draw the sprite lists
        self.bkg_list.draw()
        self.stage_list.draw()
        self.items_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()

        # Draw the score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

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


def main():
    """Call main function."""
    # instantiate the main window of the game
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    # call the setup function to set the game up
    window.setup()
    # run the game
    arcade.run()


if __name__ == "__main__":
    main()