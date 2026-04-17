"""
Game Engine (Game Machine) and In-Memory Database.
Handles physics, player management, and collision detection.
"""
import random
import math
import servidor

class Dados:
    """Manages the global game state and authoritative physics logic."""
    def __init__(self):
        """Initializes game entities and spawning logic."""
        self.state = {
            "ships": {},
            "asteroids": [],
            "lasers": [],
            "winner": None
        }
        # Initial asteroids
        for _ in range(5):
            self.create_asteroid(random.uniform(0, servidor.WIDTH), 
                               random.uniform(0, servidor.HEIGHT), 
                               servidor.ASTEROID_RADIUS_LARGE)

    def create_asteroid(self, x, y, r):
        """Creates an asteroid with a random trajectory at the given location."""
        angle = random.uniform(0, 2 * math.pi)
        self.state["asteroids"].append({
            "x": x, "y": y,
            "vx": math.cos(angle) * servidor.ASTEROID_SPEED,
            "vy": math.sin(angle) * servidor.ASTEROID_SPEED,
            "r": r
        })

    def add_player(self, p_id):
        """Registers a new player and initializes their ship in the center."""
        if p_id not in self.state["ships"]:
            c_idx = len(self.state["ships"]) % len(servidor.PLAYER_COLORS)
            self.state["ships"][p_id] = {
                "player_id": p_id, "x": servidor.WIDTH // 2, "y": servidor.HEIGHT // 2,
                "vx": 0, "vy": 0, "angle": 0, "r": servidor.SHIP_RADIUS,
                "color": servidor.PLAYER_COLORS[c_idx], "score": 0, "alive": True,
                "respawn_timer": 0
            }

    def remove_player(self, p_id):
        """Removes a player from the game state upon disconnection."""
        if p_id in self.state["ships"]:
            del self.state["ships"][p_id]

    def fire_laser(self, ship):
        """Spawns a laser entity in the direction the ship is facing."""
        r = math.radians(ship["angle"])
        self.state["lasers"].append({
            "x": ship["x"] + math.cos(r) * servidor.SHIP_RADIUS,
            "y": ship["y"] + math.sin(r) * servidor.SHIP_RADIUS,
            "vx": math.cos(r) * servidor.LASER_SPEED,
            "vy": math.sin(r) * servidor.LASER_SPEED,
            "r": servidor.LASER_RADIUS,
            "life": servidor.LASER_LIFESPAN,
            "player_id": ship["player_id"]
        })

    def handle_input(self, p_id, keys):
        """Processes player input keys to update ship rotation, thrust, and firing."""
        if self.state.get("winner"):
            return
        
        ship = self.state["ships"].get(p_id)
        if ship and ship["alive"]:
            if "left" in keys: ship["angle"] -= servidor.SHIP_ROTATION_SPEED
            if "right" in keys: ship["angle"] += servidor.SHIP_ROTATION_SPEED
            r = math.radians(ship["angle"])
            if "up" in keys:
                ship["vx"] += math.cos(r) * servidor.SHIP_THRUST
                ship["vy"] += math.sin(r) * servidor.SHIP_THRUST
            if "down" in keys:
                ship["vx"] -= math.cos(r) * (servidor.SHIP_THRUST * 0.5)
                ship["vy"] -= math.sin(r) * (servidor.SHIP_THRUST * 0.5)
            if "fire" in keys:
                self.fire_laser(ship)

    def update(self):
        """Main physics loop: updates all entity positions and resolves collisions."""
        # Update ships
        for p_id, s in self.state["ships"].items():
            if s["alive"]:
                s["x"] += s["vx"]
                s["y"] += s["vy"]
                s["vx"] *= servidor.FRICTION
                s["vy"] *= servidor.FRICTION
                s["x"], s["y"] = servidor.wrap_position(s["x"], s["y"])
                for a in self.state["asteroids"]:
                    if servidor.check_collision(s, a):
                        s["alive"] = False
                        s["score"] = max(0, s["score"] - 50)
                        s["respawn_timer"] = 120
                        break
            else:
                s["respawn_timer"] -= 1
                if s["respawn_timer"] <= 0:
                    s["alive"] = True
                    s["x"], s["y"] = servidor.WIDTH // 2, servidor.HEIGHT // 2
                    s["vx"], s["vy"] = 0, 0
        
        # Update asteroids
        for a in self.state["asteroids"]:
            a["x"] += a["vx"]
            a["y"] += a["vy"]
            a["x"], a["y"] = servidor.wrap_position(a["x"], a["y"])
        
        # Update lasers
        new_lasers = []
        for l in self.state["lasers"]:
            l["x"] += l["vx"]
            l["y"] += l["vy"]
            l["x"], l["y"] = servidor.wrap_position(l["x"], l["y"])
            l["life"] -= 1
            hit = False
            for i, a in enumerate(self.state["asteroids"]):
                if servidor.check_collision(l, a):
                    hit = True
                    if a["r"] == servidor.ASTEROID_RADIUS_LARGE:
                        for _ in range(2): self.create_asteroid(a["x"], a["y"], servidor.ASTEROID_RADIUS_MEDIUM)
                    elif a["r"] == servidor.ASTEROID_RADIUS_MEDIUM:
                        for _ in range(2): self.create_asteroid(a["x"], a["y"], servidor.ASTEROID_RADIUS_SMALL)
                    self.state["asteroids"].pop(i)
                    
                    if l["player_id"] in self.state["ships"]:
                        self.state["ships"][l["player_id"]]["score"] += 10
                        if self.state["ships"][l["player_id"]]["score"] >= servidor.WIN_SCORE:
                            self.state["winner"] = l["player_id"]
                    break
            if not hit and l["life"] > 0:
                new_lasers.append(l)
        
        self.state["lasers"] = new_lasers
        
        if not self.state["asteroids"]:
            for _ in range(3): 
                self.create_asteroid(random.uniform(0, servidor.WIDTH), 
                                   random.uniform(0, servidor.HEIGHT), 
                                   servidor.ASTEROID_RADIUS_LARGE)

    def obter_estado(self):
        """Returns the current snapshot of the game state."""
        return self.state
