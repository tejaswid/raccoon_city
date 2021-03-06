"""
This script defines the class for the main game.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla
"""

import os
import arcade
from arcade.experimental.lights import Light, LightLayer

from player_sprite import PlayerSprite
from owl_sprite import OwlSprite
from cat_sprite import CatSprite
from racoon_boss_sprite import RacoonBossSprite
from racoon_sprite import RacoonSprite

# Scale sprites up or down
SPRITE_SCALING_PLAYER = 1.0
SPRITE_SCALING_TILES = 1.0

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

# Keep racoon from going too fast
RACOON_MAX_HORIZONTAL_SPEED = 300

# --- Viewport constants
# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 500
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 50

# Ends of the view port = ends of the level
NUM_TILES_LEVEL_ALONG_WIDTH = 150
VIEWPORT_BUFFER = 10    # just a small positive value

# --- Lights
# This is the color used for 'ambient light'.
AMBIENT_COLOR = (200, 200, 200)

# --- Music
SOUNDTRACK_VOLUME = 0.6

# --- Game times
GAME_LENGTH = 46

class GameView(arcade.View):
    """Main Game class."""

    def __init__(self, screen_width, screen_height, sprite_size):
        """Initialize the class."""
        # Init the parent class
        super().__init__()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sprite_size = sprite_size

        # Setup lists for sprites. All sprites shoudl go into one of these lists
        self.player_list: arcade.SpriteList = None
        self.stage_list: arcade.SpriteList = None
        self.bullet_list: arcade.SpriteList = None
        self.items_list: arcade.SpriteList = None
        
        self.sky_list: arcade.SpriteList = None
        self.bkg_back_list: arcade.SpriteList = None
        self.bkg_front_list: arcade.SpriteList = None
        
        self.owl_list: arcade.SpriteList = None
        self.cat_dummy_list: arcade.SpriteList = None
        self.cat_list: arcade.SpriteList = None
        self.racoon_list: arcade.SpriteList = None
        self.racoon_boss_list: arcade.SpriteList = None
        self.game_end_marker_list: arcade.SpriteList = None
        self.timer_bar_list: arcade.SpriteList = None

        # Player sprite
        self.player_sprite: PlayerSprite = None

        # Racoon boss sprite
        self.racoon_boss_sprite: RacoonBossSprite = None

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False

        # Physics engine
        self.physics_engine: arcade.PymunkPhysicsEngine = None

        # Flag for double jump
        self.allow_double_jump: bool = True

        # Set background color - not necessary when using lights
        # arcade.set_background_color(arcade.csscolor.DIM_GRAY)

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
        self.soundtrack: arcade.Sound = arcade.load_sound("resources/sounds/soundtrack.wav")

        self.eat_donut_sound: arcade.Sound = arcade.load_sound("resources/sounds/eatdonut.wav")
        self.heckle_sound: arcade.Sound = arcade.load_sound("resources/sounds/racoon.wav")
        self.bubble_gum_sound: arcade.Sound = arcade.load_sound("resources/sounds/stepinbubblegum.wav")

        # Score
        self.score: int = 0

        # Make the mouse invisible
        self.window.set_mouse_visible(False)

        # Variables for player movement
        self.level_start = VIEWPORT_BUFFER
        self.level_end = NUM_TILES_LEVEL_ALONG_WIDTH * self.sprite_size - self.screen_width - VIEWPORT_BUFFER

        # --- Light related ---
        # List of all the lights
        self.light_layer = None
        # Individual light we move with player, and turn on/off
        self.player_light = None

        # time
        self.game_time_elapsed = 0
        self.timer_bar = None

        self.player_movement_speed = PLAYER_MOVE_FORCE_ON_GROUND

    def setup(self):
        """Set the game up. Call this function to restart the game.
        
        A level ID can be passed to switch between levels.
        """
        # Create lights
        # Create a light layer, used to render things to, then post-process and
        # add lights. This must match the screen size.
        self.light_layer = LightLayer(self.screen_width, self.screen_height)
        # We can also set the background color that will be lit by lights,
        # but in this instance we just want a black background
        self.light_layer.set_background_color(arcade.color.DIM_GRAY)

        # Create a light to follow the player around.
        # We'll position it later, when the player moves.
        # We'll only add it to the light layer when the player turns the light
        # on. We start with the light off.
        radius = 150
        mode = 'soft'
        color = arcade.csscolor.LIGHT_YELLOW
        self.player_light = Light(0, 0, radius, color, mode)

        # create sprite lists
        self.bullet_list = arcade.SpriteList()

        # Read in the tiled map
        map_name = "resources/maps/map.tmx"
        game_map = arcade.tilemap.read_tmx(map_name)

        # Read in the map layers to specific lists
        self.stage_list = arcade.tilemap.process_layer(game_map, 'stage', SPRITE_SCALING_TILES)
        self.items_list = arcade.tilemap.process_layer(game_map, 'items', SPRITE_SCALING_TILES)
        self.sky_list = arcade.tilemap.process_layer(game_map, 'sky', SPRITE_SCALING_TILES)
        self.bkg_back_list = arcade.tilemap.process_layer(game_map, 'bkg_back', SPRITE_SCALING_TILES)
        self.bkg_front_list = arcade.tilemap.process_layer(game_map, 'bkg_front', SPRITE_SCALING_TILES)
        
        # add owls
        self.owl_dummy_list = arcade.tilemap.process_layer(game_map, 'owls', SPRITE_SCALING_TILES)

        owl_dummy_list = arcade.tilemap.process_layer(game_map, 'owls', SPRITE_SCALING_TILES)
        self.owl_list = arcade.SpriteList()
        for owl in owl_dummy_list:
            real_owl = OwlSprite(scale=SPRITE_SCALING_PLAYER)
            real_owl.position = owl.position
            self.owl_list.append(real_owl)

        # add racoon minions
        racoon_dummy_list = arcade.tilemap.process_layer(game_map, 'racoon', SPRITE_SCALING_TILES)
        self.racoon_list = arcade.SpriteList()
        for racoon in racoon_dummy_list:
            real_racoon = RacoonSprite(SPRITE_SCALING_PLAYER, racoon.position)
            real_racoon.position = racoon.position
            self.racoon_list.append(real_racoon)

        # add cats
        self.cat_dummy_list = arcade.tilemap.process_layer(game_map, 'cats', SPRITE_SCALING_TILES)

        self.cat_list = arcade.SpriteList()
        for cat in self.cat_dummy_list:
            realCat = CatSprite(scale=SPRITE_SCALING_PLAYER)
            realCat.position = cat.position
            self.cat_list.append(realCat)

        # --------
        # Player
        # --------
        # Create player sprite
        self.player_sprite = PlayerSprite(scale=SPRITE_SCALING_PLAYER)
        #self.player_sprite = RacoonBossSprite(scale=SPRITE_SCALING_PLAYER)
        
        # Set player location at the centre of the specified grid
        grid_x = 1
        grid_y = 1
        self.player_sprite.center_x = self.sprite_size * grid_x + self.sprite_size / 2
        self.player_sprite.center_y = self.sprite_size * grid_y + self.sprite_size / 2 + 40

        # Add to player sprite list
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        # ------
        # add racoon boss
        # ------
        self.racoon_boss_list = arcade.SpriteList()
        racoon_boss_sprite = RacoonBossSprite(scale=SPRITE_SCALING_PLAYER)
        racoon_boss_sprite.center_x = self.player_sprite.center_x + 500
        racoon_boss_sprite.center_y = 192
        self.racoon_boss_list.append(racoon_boss_sprite)

        # ------
        # add game end marker
        # ------
        self.game_end_marker_list = arcade.tilemap.process_layer(game_map, 'game_end_marker', SPRITE_SCALING_TILES)

        # timer bar
        self.timer_bar = arcade.SpriteSolidColor(1280, 50, arcade.color.LIGHT_GOLDENROD_YELLOW)
        self.timer_bar.center_x = 640
        self.timer_bar.center_y = 64
        self.timer_bar_list = arcade.SpriteList()
        self.timer_bar_list.append(self.timer_bar)

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

        # Owls
        self.physics_engine.add_sprite_list(self.owl_list,
                                            collision_type="owl",
                                            body_type=arcade.PymunkPhysicsEngine.KINEMATIC)

        self.physics_engine.add_collision_handler("player", "owl", post_handler=self.owl_hit_handler)

        # Cats
        self.physics_engine.add_sprite_list(self.cat_list,
                                            collision_type="cat",
                                            body_type=arcade.PymunkPhysicsEngine.KINEMATIC)

        self.physics_engine.add_collision_handler("player", "cat", post_handler=self.cat_hit_handler)

        # racoon minions
        self.physics_engine.add_sprite_list(self.racoon_list,
                                            collision_type="racoon",
                                            body_type=arcade.PymunkPhysicsEngine.DYNAMIC,
                                            moment=arcade.PymunkPhysicsEngine.MOMENT_INF)

        self.physics_engine.add_collision_handler("player", "racoon", post_handler=self.racoon_hit_handler)

        # racoon boss
        self.physics_engine.add_sprite_list(self.racoon_boss_list,
                                            collision_type="racoonboss",
                                            body_type=arcade.PymunkPhysicsEngine.DYNAMIC,
                                            moment=arcade.PymunkPhysicsEngine.MOMENT_INF)
        
        self.physics_engine.add_collision_handler("player", "racoonboss", post_handler=self.racoon_boss_hit_handler)

        # game end marker
        self.physics_engine.add_sprite_list(self.game_end_marker_list,
                                            collision_type="gameend",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC,
                                            moment=arcade.PymunkPhysicsEngine.MOMENT_INF)
        
        self.physics_engine.add_collision_handler("player", "gameend", post_handler=self.gameend_hit_handler)

        self.physics_engine.add_sprite_list(self.timer_bar_list,
                                            collision_type="timerbar",
                                            body_type=arcade.PymunkPhysicsEngine.KINEMATIC,
                                            moment=arcade.PymunkPhysicsEngine.MOMENT_INF)

        self.physics_engine.add_collision_handler("player", "bullet", post_handler=self.bubblegum_hit_handler)

        # Initialize score to zero
        self.score = 0

        # Play the soundtrack
        self.current_player = self.soundtrack.play(SOUNDTRACK_VOLUME, loop=True)

        # Reset the viewport
        arcade.set_viewport(0, self.screen_width - 1, 0, self.screen_height - 1)

        self.count_lagging = 0
        self.start_lagging = False
        self.max_lagging_time = 2

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
        elif key == arcade.key.SPACE:
            # Turn lights on or off
            # We can add/remove lights from the light layer. If they aren't
            # in the light layer, the light is off.
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)

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
        arcade.play_sound(self.eat_donut_sound)
        # Update the score
        self.score += 1
        self.player_movement_speed = PLAYER_MOVE_FORCE_ON_GROUND * 2
        self.start_lagging = True

    def owl_hit_handler(self, player_sprite, owl_sprite, _arbiter, _space, _data):
        """Handle collision between player and owl"""
        # print("player hit owl")
        # Play a sound
        #arcade.play_sound(self.collect_coin_sound)
        # Update the score
        self.score -= 1
        self.trigger_slowdown()

    def cat_hit_handler(self, player_sprite, owl_sprite, _arbiter, _space, _data):
        """Handle collision between player and cat"""
        # print("player hit cat")
        # Play a sound
        #arcade.play_sound(self.collect_coin_sound)
        # Update the score
        self.score -= 1
        self.trigger_slowdown()

    def bubblegum_hit_handler(self, player_sprite, owl_sprite, _arbiter, _space, _data):
        """Handle collision between player and bubblegum"""
        # print("player hit bubblegum")
        # Play a sound
        arcade.play_sound(self.collect_coin_sound)
        # Update the score
        self.score -= 1
        self.trigger_slowdown()

    def racoon_hit_handler(self, player_sprite, racoon_sprite, _arbiter, _space, _data):
        """Handle collision between player and racoon"""
        # print("player hit racoon")
        # Play a sound
        #arcade.play_sound(self.heckle_sound)
        # Update the score
        self.score -= 1
        self.trigger_slowdown()

    def racoon_boss_hit_handler(self, player_sprite, racoon_boss_sprite, _arbiter, _space, _data):
        """Handle collision between player and racoon boss"""
        # print("player hit racoon boss")
        # Play a sound
        #arcade.play_sound(self.collect_coin_sound)
        # Update the score
        self.score -= 1

    def gameend_hit_handler(self, player_sprite, gameend_sprite, _arbiter, _space, _data):
        """Handle collision between player and game end marker"""
        # print("player hit game end")
        game_win_view = GameWinView(self.screen_width, self.screen_height, self.sprite_size)
        self.current_player.pause()
        arcade.play_sound(self.heckle_sound)
        self.window.show_view(game_win_view)
        

    def trigger_slowdown(self):
        self.player_movement_speed = PLAYER_MOVE_FORCE_ON_GROUND * 0.2
        self.start_lagging = True
        # self.game_time_elapsed += 0.5

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
                force = (-self.player_movement_speed, 0)   # apply ground force
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)  # apply air force
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            if is_on_ground:
                force = (self.player_movement_speed, 0)   # apply ground force
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)  # apply air force
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # make owl attack player if it they are close to it
        for owl in self.owl_list:
            if arcade.get_distance_between_sprites(self.player_sprite,owl) < 500:
                #print(arcade.get_distance_between_sprites(self.player_sprite,owl))
                owl.attack_player(self.player_sprite, self.physics_engine, delta_time)

        # make cat attack player if it they are close to it
        for cat in self.cat_list:
            if arcade.get_distance_between_sprites(self.player_sprite,cat) < 250:
                #print(arcade.get_distance_between_sprites(self.player_sprite,cat))
                cat.attack_player(self.player_sprite, self.bullet_list, self.physics_engine, delta_time)

        # wandering racoon code
        for racoon in self.racoon_list:
            if racoon.is_facing_right:
                dist_to_end = (racoon.starting_position[0] + racoon.max_delta_x) - racoon.center_x
                force_val = dist_to_end / (2 * racoon.max_delta_x) * 500 + 4000
                if dist_to_end >= 0:
                    force = (force_val, 0)
                    self.physics_engine.apply_force(racoon, force)
                    self.physics_engine.set_friction(racoon, 0)
                else:
                    racoon.is_facing_right = False
                    self.physics_engine.set_friction(racoon, 1.0)
                    continue
            else:
                dist_to_start = racoon.center_x - (racoon.starting_position[0] - racoon.max_delta_x)
                force_val = dist_to_start / (2 * racoon.max_delta_x) * 500 + 4000
                if dist_to_start >= 0:
                    force = (-force_val, 0)
                    self.physics_engine.apply_force(racoon, force)
                    self.physics_engine.set_friction(racoon, 0)
                else:
                    racoon.is_facing_right = True
                    self.physics_engine.set_friction(racoon, 1.0)
                    continue

        # bullet turns to bubblegum when it hits the floor
        for bullet in self.bullet_list:
            #print("bullet velocity {}".format(bullet.velocity))
            #if bullet.velocity[1] < 0.005 and bullet.velocity[0] < 0.005:
            if self.physics_engine.is_on_ground(bullet):    
                bullet.angle = 0
                bullet.texture = arcade.load_texture(os.path.join("resources/images/cat", "bubblegum.png"))
                self.physics_engine.set_velocity(bullet,(0,0))

        # racoon boss moves to the right and disappears
        for racoon_boss in self.racoon_boss_list:
            if racoon_boss.center_x < 2000:
                self.physics_engine.apply_force(racoon_boss, force)
            if racoon_boss.center_x > 2000 and racoon_boss.center_x < 2500:
                #racoon_boss.position = (17920,racoon_boss.center_y)
                #self.physics_engine.apply_force(racoon_boss, (0,0))
                self.physics_engine.set_position(racoon_boss,(17920,192))
                self.physics_engine.set_velocity(racoon_boss,(0,0))
                self.physics_engine.set_friction(racoon_boss,1.0)

        # Move items in the physics engine
        self.physics_engine.step()

        # Move light along with the player
        self.player_light.position = self.player_sprite.position

        # Trigger game over using these commands as appropriate
        # view = GameOverView()
        # self.window.show_view(view)
        # print(self.racoon_boss_list[0].position)

        self.game_time_elapsed += delta_time
        for tb in self.timer_bar_list:
            self.physics_engine.set_position(tb, (self.view_left + 640 - (self.game_time_elapsed * 1280/GAME_LENGTH), 64))
        if self.game_time_elapsed > GAME_LENGTH:
            self.trigger_gameover()

        if self.start_lagging:
            self.count_lagging += delta_time
            if self.count_lagging > self.max_lagging_time:
                self.start_lagging = False
                self.count_lagging = 0
                self.player_movement_speed = PLAYER_MOVE_FORCE_ON_GROUND

        if self.player_list[0].center_y < 100:
            self.trigger_gameover()


    def on_draw(self):
        """Draw everything to screen."""
        arcade.start_render()
        # Draw the sprite lists
        # Everything that should be affected by lights gets rendered inside this
        # 'with' statement. Nothing is rendered to the screen yet, just the light
        # layer.
        with self.light_layer:
            self.sky_list.draw()
            self.bkg_back_list.draw()
            self.bkg_front_list.draw()
            self.stage_list.draw()
            self.items_list.draw()
            self.player_list.draw()
            self.bullet_list.draw()
            self.owl_list.draw()
            self.cat_list.draw()
            self.racoon_list.draw()
            self.racoon_boss_list.draw()
            self.timer_bar_list.draw()
            

        # Draw the light layer to the screen.
        # This fills the entire screen with the lit version
        # of what we drew into the light layer above.
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        # Draw the score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        #arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
        #               arcade.csscolor.WHITE, 18, font_name=['arial'])

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
                if self.view_left < self.level_start:     # This is just a small positive buffer value
                    # do not scroll left
                    changed_viewport = False
                else:
                    self.view_left -= left_boundary - self.player_sprite.left
                    changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + self.screen_width - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            if self.view_left > self.level_end:
                changed_viewport = False
            else:
                self.view_left += self.player_sprite.right - right_boundary
                changed_viewport = True

        # Scroll up
        # top_boundary = self.view_bottom + self.screen_height - TOP_VIEWPORT_MARGIN
        # if self.player_sprite.top > top_boundary:
        #     self.view_bottom += self.player_sprite.top - top_boundary
        #     changed_viewport = True

        # # Scroll down
        # bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        # if self.player_sprite.bottom < bottom_boundary:
        #     self.view_bottom -= bottom_boundary - self.player_sprite.bottom
        #     changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                self.screen_width + self.view_left,
                                self.view_bottom,
                                self.screen_height + self.view_bottom)

    def trigger_gameover(self):
        "Trigger game over"
        # print("game over")
        game_over_view = GameOverView(self.screen_width, self.screen_height, self.sprite_size)
        self.current_player.pause()
        arcade.play_sound(self.heckle_sound)
        self.window.show_view(game_over_view)


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
        # texture showing the game over screen
        self.texture = arcade.load_texture("resources/images/screens/start_screen.png")

        # Reset the viewport, necessary if we have a scrolling game
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.screen_width - 1, 0, self.screen_height - 1)

    def on_draw(self):
        """Draw this view."""
        arcade.start_render()
        self.texture.draw_sized(self.screen_width / 2, self.screen_height / 2,
                                self.screen_width, self.screen_height)
        #arcade.draw_text("Instructions Screen", self.screen_width / 2, self.screen_height / 2,
        #                 arcade.color.WHITE, font_size=50, anchor_x="center")
        #arcade.draw_text("Press any key to start", self.screen_width / 2, self.screen_height / 2-75,
        #                 arcade.color.WHITE, font_size=20, anchor_x="center")
        #arcade.draw_text("Use arrow keys to move. Space to turn on the torch.", self.screen_width / 2, self.screen_height / 2-150,
        #                 arcade.color.WHITE, font_size=20, anchor_x="center")

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
        
        # texture showing the game over screen
        self.texture = arcade.load_texture("resources/images/screens/game_over_screen.png")

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
    

class GameWinView(arcade.View):

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
        
        # texture showing the game over screen
        self.texture = arcade.load_texture("resources/images/screens/game_win_screen.png")

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
