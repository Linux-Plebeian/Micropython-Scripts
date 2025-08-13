import ssd1306
import machine
import math
import time
from machine import Pin, I2C
import sys
btn_left = Pin(16, Pin.IN, Pin.PULL_DOWN)
btn_forward = Pin(18, Pin.IN, Pin.PULL_DOWN)
btn_right = Pin(21, Pin.IN, Pin.PULL_DOWN)

# Screen dimensions
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# Map dimensions
MAP_WIDTH = 16
MAP_HEIGHT = 8

# Simple map (1 = wall, 0 = empty)
game_map = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,1,0,1,0,0,0,0,1,0,1,0,0,0,0],
    [1,0,1,0,1,1,1,1,0,1,0,1,0,1,1,1],
    [1,0,1,0,1,0,0,0,0,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,1,0,1,0,1,0,0,0,1],
    [1,0,1,0,1,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# Player variables
player_x = 1.5
player_y = 1.5
player_angle = 0.0
ticks = 0
# Raycasting parameters
FOV = math.pi / 3  # 60 degrees field of view
HALF_FOV = FOV / 2
NUM_RAYS = SCREEN_WIDTH // 4  # Cast fewer rays for performance
MAX_DEPTH = 8
DELTA_ANGLE = FOV / NUM_RAYS

def cast_ray(angle):
    """Cast a single ray and return distance to wall"""
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    
    # Start from player position
    x, y = player_x, player_y
    
    # Step size for ray marching
    dx = cos_a * 0.04
    dy = sin_a * 0.04
    
    # March along the ray
    for i in range(int(MAX_DEPTH / 0.04)):
        x += dx
        y += dy
        
        # Check bounds
        map_x = int(x)
        map_y = int(y)
        
        if (map_x < 0 or map_x >= MAP_WIDTH or 
            map_y < 0 or map_y >= MAP_HEIGHT or
            game_map[map_y][map_x] == 1):
            # Hit a wall or boundary
            distance = math.sqrt((x - player_x)**2 + (y - player_y)**2)
            return distance
    
    return MAX_DEPTH

def render_frame(display):

    display.fill(0)
    
    # Store wall heights for wireframe drawing
    wall_heights = []
    
    # Cast rays to get wall distances
    for i in range(NUM_RAYS):
        # Calculate ray angle
        ray_angle = player_angle - HALF_FOV + i * DELTA_ANGLE
        
        # Cast ray
        distance = cast_ray(ray_angle)
        
        # Remove fisheye effect
        distance *= math.cos(player_angle - ray_angle)
        
        if distance > 0:
            wall_height = min(SCREEN_HEIGHT, int(SCREEN_HEIGHT / distance))
        else:
            wall_height = SCREEN_HEIGHT
        
        wall_heights.append(wall_height)
    
    # Draw wireframe - only draw top and bottom edges of walls
    for i in range(NUM_RAYS):
        wall_height = wall_heights[i]
        wall_top = (SCREEN_HEIGHT - wall_height) // 4
        wall_bottom = wall_top + wall_height
        
        x_pos = i * 4
        if x_pos < SCREEN_WIDTH:
            # Draw top edge of wall
            if wall_top >= 0 and wall_top < SCREEN_HEIGHT:
                display.pixel(x_pos, wall_top, 1)
                if x_pos + 1 < SCREEN_WIDTH:
                    display.pixel(x_pos + 1, wall_top, 1)
            
            # Draw bottom edge of wall
            if wall_bottom >= 0 and wall_bottom < SCREEN_HEIGHT:
                display.pixel(x_pos, wall_bottom, 1)
                if x_pos + 1 < SCREEN_WIDTH:
                    display.pixel(x_pos + 1, wall_bottom, 1)
    
    # Draw vertical connecting lines at regular intervals for structure
    for i in range(1, NUM_RAYS):  # Every 8th ray
        wall_height = wall_heights[i]
        wall_top = (SCREEN_HEIGHT - wall_height) // 4
        wall_bottom = wall_top + wall_height
        
        x_pos = i * 4
        if x_pos < SCREEN_WIDTH:
            # Draw vertical line connecting top and bottom
            for y in range(max(0, wall_top), min(SCREEN_HEIGHT, wall_bottom + 1), 3):

                display.pixel(x_pos, y, 1)

def handle_input(display):
    """Handle button presses"""
    global player_angle, player_x, player_y,ticks
    
    # Turn left
    if  btn_left.value():
        ticks = 0
        player_angle -= 0.1
        if player_angle < 0:
            player_angle += 2 * math.pi
    
    # Turn right  
    if  btn_right.value():
        ticks = 0
        player_angle += 0.1
        if player_angle >= 4 * math.pi:
            player_angle -= 4 * math.pi
    
    # Move forward
    if  btn_forward.value():
        ticks = 0
        # Calculate new position
        new_x = player_x + math.cos(player_angle) * 0.2
        new_y = player_y + math.sin(player_angle) * 0.2
        
        # Check collision
        map_x = int(new_x)
        map_y = int(new_y)
        
        if (map_x >= 0 and map_x < MAP_WIDTH and 
            map_y >= 0 and map_y < MAP_HEIGHT and
            game_map[map_y][map_x] == 0):
            player_x = new_x
            player_y = new_y

def main(display):
    """Main game loop"""
    print("Starting raycaster...")
    print("Controls:")
    print("- Button on pin 2: Turn left")
    print("- Button on pin 4: Turn right") 
    print("- Button on pin 5: Move forward")
    
    while True:
        global ticks
        ticks +=1
        # Handle input
        handle_input(display)
        
        # Render frame
        render_frame(display)
        
        
        # Update display
        display.show()
        
        # Small delay to prevent overwhelming the display
        time.sleep_ms(0)
        if ticks > 30:
            sys.exit()


