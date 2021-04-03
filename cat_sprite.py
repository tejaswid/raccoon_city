"""
This script defines the class for the cat sprite.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla
"""

import os
import arcade
import math

# --- Animation constants.
# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.05

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 20

class CatSprite(arcade.Sprite):
    """Class for Cat."""

    def __init__(self, scale):
        """Initialize the class."""
        # Let parent initialize
        super().__init__()

        # Set our scale
        self.scale = scale

        # Load textures 
        resource_path = "resources/images/cat"
        self.idle_texture = arcade.load_texture(os.path.join(resource_path, "cat_idle.png"))
        self.fly_texture = arcade.load_texture(os.path.join(resource_path, "cat_idle.png"))

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
        self.has_attacked = False
        self.attack_steps = 100
    
    def attack_player(self, player, bullet_list, physics_engine, delta_time):
        if self.has_attacked is False:
            # shoot a bubblegum
            start_x = self.center_x
            start_y = self.center_y
            
            bullet = arcade.SpriteSolidColor(20, 5, arcade.color.PINK_SHERBET)
            bullet.position = self.position
            

            dest_x = (self.center_x + player.center_x) / 2
            dest_y = self.center_y - self.height/2

            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            size = max(self.width, self.height) / 2

            bullet.center_x += size * math.cos(angle)
            bullet.center_y += size * math.sin(angle)

            bullet.angle = math.degrees(angle)

            bullet_gravity = (0, -300)

            physics_engine.add_sprite(bullet,
                                       mass=0.1,
                                       damping=1.0,
                                       friction=0.6,
                                       collision_type="bullet",
                                       gravity=bullet_gravity,
                                       elasticity=0.9)

            force = (4500, 0)
            physics_engine.apply_force(bullet, force)
            physics_engine.set_velocity(bullet,(0.01,0.01))
            bullet_list.append(bullet)

        self.has_attacked = True
                    

        
