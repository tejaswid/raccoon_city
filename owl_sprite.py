"""
This script defines the class for the owl sprite.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla
"""

import os
import arcade

# --- Animation constants.
# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.05

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 20

class OwlSprite(arcade.Sprite):
    """Class for Owl."""

    def __init__(self, scale):
        """Initialize the class."""
        # Let parent initialize
        super().__init__()

        # Set our scale
        self.scale = scale

        # Load textures 
        resource_path = "resources/images/owl"
        self.idle_texture = arcade.load_texture(os.path.join(resource_path, "owl_idle.png"))
        self.fly_texture = arcade.load_texture(os.path.join(resource_path, "owl_fly.png"))

        # Set the initial texture
        self.texture = self.idle_texture

        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Index of our current texture
        self.cur_texture = 0

        # Is the sprite cloe to the player?
        self.is_close_to_player = False

        # Has the owl started attacking?
        self.is_attacking = False
        self.attack_steps = 100

        self.owl_flying_sound: arcade.Sound = arcade.load_sound("resources/sounds/owlflying.wav")
    
    def attack_player(self, player, physics_engine, delta_time):

        if self.is_attacking is False:
            self.is_attacking = True
            self.texture = self.fly_texture
            attack_direction = player.position - self.position
            attack_direction = attack_direction / arcade.get_distance_between_sprites(self,player)
            self.change_x = attack_direction[0] * 2
            self.change_y = attack_direction[1] * 2
            velocity = (self.change_x*1/delta_time, self.change_y*1/delta_time)
            physics_engine.set_velocity(self,velocity)
            #print("i am attacking player at", player.position)
        self.attack_steps -= 1
        #print("attack steps {}, velocity {}".format(self.attack_steps, self.velocity))
        if self.attack_steps < 0:
            #self.is_attacking = False
            self.attack_steps = 5
            self.change_x = 0
            self.change_y = 0
            velocity = (self.change_x*1/delta_time, self.change_y*1/delta_time)
            physics_engine.set_velocity(self,velocity)
            #arcade.play_sound(self.owl_flying_sound)
            

        
