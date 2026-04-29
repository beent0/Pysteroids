# Network
PORT = 5555
INT_SIZE = 8

# Screen
WIDTH = 800
HEIGHT = 600
FPS = 1

# Entities
SHIP_RADIUS = 15
SHIP_ROTATION_SPEED = 5
SHIP_THRUST = 0.2
FRICTION = 0.98

LASER_SPEED = 10
LASER_RADIUS = 2
LASER_LIFESPAN = 60

ASTEROID_RADIUS_LARGE = 40
ASTEROID_RADIUS_MEDIUM = 20
ASTEROID_RADIUS_SMALL = 10
ASTEROID_SPEED = 2

WIN_SCORE = 500

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PLAYER_COLORS = [RED, GREEN, BLUE, YELLOW]

def wrap_position(x, y):
    return x % WIDTH, y % HEIGHT

def check_collision(obj1, obj2):
    import math
    dx = obj1['x'] - obj2['x']
    dy = obj1['y'] - obj2['y']
    dist = math.sqrt(dx*dx + dy*dy)
    return dist < (obj1['r'] + obj2['r'])
