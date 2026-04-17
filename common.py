import math
import json

# screen
WIDTH = 800
HEIGHT = 600
FPS = 60

# networking constants
PORT = 5555
INT_SIZE = 8

# entities
SHIP_RADIUS = 15
SHIP_ROTATION_SPEED = 5
SHIP_THRUST = 0.2
FRICTION = 0.98

LASER_SPEED = 10
LASER_RADIUS = 2
LASER_LIFESPAN = 60 # frames

ASTEROID_RADIUS_LARGE = 40
ASTEROID_RADIUS_MEDIUM = 20
ASTEROID_RADIUS_SMALL = 10
ASTEROID_SPEED = 2

# colors
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
    dx = obj1['x'] - obj2['x']
    dy = obj1['y'] - obj2['y']
    dist = math.sqrt(dx*dx + dy*dy)
    return dist < (obj1['r'] + obj2['r'])

# Raw socket helpers
def send_int(connection, value: int):
    connection.sendall(value.to_bytes(INT_SIZE, byteorder="big", signed=True))

def receive_int(connection):
    data = b""
    while len(data) < INT_SIZE:
        chunk = connection.recv(INT_SIZE - len(data))
        if not chunk: return None
        data += chunk
    return int.from_bytes(data, byteorder='big', signed=True)

def send_object(connection, obj):
    data = json.dumps(obj).encode('utf-8')
    size = len(data)
    send_int(connection, size)
    connection.sendall(data)

def receive_object(connection):
    size = receive_int(connection)
    if size is None: return None
    data = b""
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk: break
        data += chunk
    return json.loads(data.decode('utf-8'))
