import socket
import threading
import time
import math
import random
import json
from common import *

class Server:
    def __init__(self):
        self.state = {"ships": {}, "asteroids": [], "lasers": []}
        self.clients = {} # addr: connection
        self.lock = threading.RLock()
        for _ in range(5):
            self.create_asteroid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), ASTEROID_RADIUS_LARGE)

    def create_asteroid(self, x, y, r):
        angle = random.uniform(0, 2 * math.pi)
        with self.lock:
            self.state["asteroids"].append({
                "x": x, "y": y,
                "vx": math.cos(angle) * ASTEROID_SPEED,
                "vy": math.sin(angle) * ASTEROID_SPEED,
                "r": r
            })

    def fire_laser(self, ship):
        r = math.radians(ship["angle"])
        with self.lock:
            self.state["lasers"].append({
                "x": ship["x"] + math.cos(r) * SHIP_RADIUS,
                "y": ship["y"] + math.sin(r) * SHIP_RADIUS,
                "vx": math.cos(r) * LASER_SPEED,
                "vy": math.sin(r) * LASER_SPEED,
                "r": LASER_RADIUS,
                "life": LASER_LIFESPAN,
                "player_id": ship["player_id"]
            })

    def handle_input(self, p_id, keys):
        with self.lock:
            ship = self.state["ships"].get(p_id)
            if ship and ship["alive"]:
                if "left" in keys: ship["angle"] -= SHIP_ROTATION_SPEED
                if "right" in keys: ship["angle"] += SHIP_ROTATION_SPEED
                r = math.radians(ship["angle"])
                if "up" in keys:
                    ship["vx"] += math.cos(r) * SHIP_THRUST
                    ship["vy"] += math.sin(r) * SHIP_THRUST
                if "down" in keys:
                    ship["vx"] -= math.cos(r) * (SHIP_THRUST * 0.5)
                    ship["vy"] -= math.sin(r) * (SHIP_THRUST * 0.5)
                if "fire" in keys:
                    self.fire_laser(ship)

    def update(self):
        with self.lock:
            # Update ships
            for p_id, s in self.state["ships"].items():
                if s["alive"]:
                    s["x"] += s["vx"]
                    s["y"] += s["vy"]
                    s["vx"] *= FRICTION
                    s["vy"] *= FRICTION
                    s["x"], s["y"] = wrap_position(s["x"], s["y"])
                    for a in self.state["asteroids"]:
                        if check_collision(s, a):
                            s["alive"] = False
                            s["score"] = 0
                            s["respawn_timer"] = 120
                            break
                else:
                    s["respawn_timer"] -= 1
                    if s["respawn_timer"] <= 0:
                        s["alive"] = True
                        s["x"], s["y"] = WIDTH // 2, HEIGHT // 2
                        s["vx"], s["vy"] = 0, 0
            
            # Update asteroids
            for a in self.state["asteroids"]:
                a["x"] += a["vx"]
                a["y"] += a["vy"]
                a["x"], a["y"] = wrap_position(a["x"], a["y"])
            
            # Update lasers
            new_lasers = []
            for l in self.state["lasers"]:
                l["x"] += l["vx"]
                l["y"] += l["vy"]
                l["x"], l["y"] = wrap_position(l["x"], l["y"])
                l["life"] -= 1
                hit = False
                for i, a in enumerate(self.state["asteroids"]):
                    if check_collision(l, a):
                        hit = True
                        if a["r"] == ASTEROID_RADIUS_LARGE:
                            for _ in range(2): self.create_asteroid(a["x"], a["y"], ASTEROID_RADIUS_MEDIUM)
                        elif a["r"] == ASTEROID_RADIUS_MEDIUM:
                            for _ in range(2): self.create_asteroid(a["x"], a["y"], ASTEROID_RADIUS_SMALL)
                        self.state["asteroids"].pop(i)
                        if l["player_id"] in self.state["ships"]:
                            self.state["ships"][l["player_id"]]["score"] += 10
                        break
                if not hit and l["life"] > 0:
                    new_lasers.append(l)
            self.state["lasers"] = new_lasers
            if not self.state["asteroids"]:
                for _ in range(3): self.create_asteroid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), ASTEROID_RADIUS_LARGE)

    def broadcast(self):
        while True:
            time.sleep(1.0/FPS)
            self.update()
            with self.lock:
                state_copy = json.loads(json.dumps(self.state))
                for addr, conn in list(self.clients.items()):
                    try:
                        send_object(conn, state_copy)
                    except:
                        print(f"Client {addr} disconnected")
                        del self.clients[addr]

    def handle_client(self, conn, addr):
        try:
            while True:
                msg = receive_object(conn)
                if not msg: break
                
                if msg["type"] == "connect":
                    p_id = msg["player_id"]
                    print(f"[{p_id}] Conectando...")
                    with self.lock:
                        if p_id not in self.state["ships"]:
                            c_idx = len(self.state["ships"]) % len(PLAYER_COLORS)
                            self.state["ships"][p_id] = {
                                "player_id": p_id, "x": WIDTH // 2, "y": HEIGHT // 2,
                                "vx": 0, "vy": 0, "angle": 0, "r": SHIP_RADIUS,
                                "color": PLAYER_COLORS[c_idx], "score": 0, "alive": True,
                                "respawn_timer": 0
                            }
                    # REMOVED send_object(conn, {"status": "ok"}) to prevent interleaving
                elif msg["type"] == "input":
                    p_id = msg["player_id"]
                    keys = msg["keys"]
                    print(f"[{p_id}] Comando: {keys}")
                    self.handle_input(p_id, keys)
                    # REMOVED send_object(conn, {"status": "ok"})
        except:
            pass
        finally:
            with self.lock:
                if addr in self.clients: del self.clients[addr]
            conn.close()

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', PORT))
        s.listen(5)
        print(f"TCP Server started on port {PORT}")
        threading.Thread(target=self.broadcast, daemon=True).start()
        while True:
            conn, addr = s.accept()
            with self.lock:
                self.clients[addr] = conn
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    Server().run()
