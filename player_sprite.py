"""
This script defines the class for the player sprite.

Developers: DemonCyborg, Taterstew, pillitoka, ballipilla
"""

import os
import arcade

# --- Animation constants.
# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0#0.05

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 20

class PlayerSprite(arcade.Sprite):
    """Player Sprite."""
    def __init__(self, scale):
        """Initialize the class."""
        # Let parent initialize
        super().__init__()

        # Set our scale
        self.scale = scale

        # Load textures for idle standing
        resource_path = "resources/images/cop"
        self.idle_texture_pair = arcade.load_texture_pair(os.path.join(resource_path, "cop_idle.png"))
        self.jump_texture_pair = arcade.load_texture_pair(os.path.join(resource_path, "cop_idle.png"))
        self.fall_texture_pair = arcade.load_texture_pair(os.path.join(resource_path, "cop_idle.png"))

        self.collision_shape = arcade.load_texture(os.path.join(resource_path, "cop_collision.png"))

        # Load textures for walking
        self.walk_textures = []
        self.num_walk_textures = 10
        for i in range(self.num_walk_textures):
            texture = arcade.load_texture_pair(os.path.join(resource_path, f"cop_{i}.png"))
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the custom ellipse shape.
        #self.hit_box = self.collision_shape.hit_box_points
        self.hit_box = [[-44.0, -56.0], [-11.0, -89.0], [0, -90], [10.0, -89.0], [43.0, -56.0], [43.0, 61.0], [10.0, 94.0], [-11.0, 94.0], [-44.0, 61.0]]
        # print(self.get_points())
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
            self.cur_texture = 0
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
