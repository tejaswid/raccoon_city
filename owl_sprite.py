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
        self.fly_texture = arcade.load_texture(os.path.join(resource_path, "owl_fly.png")

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
    
    def attack_player(self, player):
        print("i am attacking player at" player.position)
        
