"""
This script defines the class for the racoon sprite.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla
"""

import os
import arcade
from arcade import physics_engines

# --- Animation constants.
# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.05

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 25

class RacoonSprite(arcade.Sprite):
    """Class for Racoon."""

    def __init__(self, scale, starting_position):
        """Initialize the class."""
        # Let parent initialize
        super().__init__()

        # Set our scale
        self.scale = scale

        # Load textures 
        resource_path = "resources/images/racoon"
        self.idle_texture = arcade.load_texture(os.path.join(resource_path, "racoon_0.png"))
        self.fly_texture = arcade.load_texture(os.path.join(resource_path, "racoon_0.png"))

        # Load textures for walking
        self.walk_textures = []
        self.num_walk_textures = 4
        for i in range(self.num_walk_textures):
            texture = arcade.load_texture_pair(os.path.join(resource_path, f"racoon_{i}.png"))
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture

        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

        # Default to face-right
        self.is_facing_right = True

        # Index of our current texture
        self.cur_texture = 0

        # save the starting position of the racoon
        self.starting_position = starting_position

        # max movement offset along x direction
        self.max_delta_x = 300

        # max velocity
        self.pymunk.max_horizontal_velocity = 100

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

        self.x_odometer += dx

        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:

            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_texture += 1
            if self.cur_texture >= self.num_walk_textures:
                self.cur_texture = 0
            if self.is_facing_right:
                self.texture = self.walk_textures[self.cur_texture][0]
            else:
                self.texture = self.walk_textures[self.cur_texture][1]

    def switch_texture(self):
        if self.is_facing_right:
            # switch to left texture
            self.texture = self.walk_textures[self.cur_texture][1]
        else:
            # switch to right texture
            self.texture = self.walk_textures[self.cur_texture][0]
