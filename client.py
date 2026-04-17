import socket
import sys
import uuid
import json
import pygame
import math
import threading
from common import *

class Client:
    def __init__(self, ip="127.0.0.1"):
        self.p_id = str(uuid.uuid4())[:8]
        self.ip = ip
        self.state = {"ships": {}, "asteroids": [], "lasers": []}
        self.lock = threading.Lock()
        
        # TCP Connection
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, PORT))
        
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Asteroids DESTROIED - {self.p_id}")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        
        # Start receiver thread (calc_7 style)
        threading.Thread(target=self.receive_state, daemon=True).start()
        
        # Register
        self.send_cmd({"type": "connect", "player_id": self.p_id})

    def send_cmd(self, data):
        # We use a lock for sending because the receiver thread is on the same socket
        # Note: In calc_7 this was risky, but here we synchronize
        with self.lock:
            send_object(self.conn, data)
            # We don't wait for ACK here to keep game loop fast, 
            # or the server sends an ACK we must consume.
            # But the receiver thread is busy consuming EVERYTHING.
            # This is the "destroied" part: collisions are likely.
            pass

    def receive_state(self):
        while True:
            try:
                obj = receive_object(self.conn)
                if obj and "status" not in obj: # Ignore ACKs, take states
                    self.state = obj
            except:
                break

    def handle_input(self):
        keys = pygame.key.get_pressed()
        cmd_keys = []
        if keys[pygame.K_LEFT]: cmd_keys.append("left")
        if keys[pygame.K_RIGHT]: cmd_keys.append("right")
        if keys[pygame.K_UP]: cmd_keys.append("up")
        if keys[pygame.K_DOWN]: cmd_keys.append("down")
        
        if cmd_keys:
            self.send_cmd({
                "type": "input",
                "player_id": self.p_id,
                "keys": cmd_keys
            })
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.send_cmd({
                        "type": "input",
                        "player_id": self.p_id,
                        "keys": ["fire"]
                    })
        return True

    def draw(self):
        self.screen.fill(BLACK)
        for a in self.state["asteroids"]:
            pygame.draw.circle(self.screen, WHITE, (int(a["x"]), int(a["y"])), int(a["r"]), 2)
        for l in self.state["lasers"]:
            pygame.draw.circle(self.screen, YELLOW, (int(l["x"]), int(l["y"])), int(l["r"]))
        for p_id, s in self.state["ships"].items():
            if s["alive"]:
                r = math.radians(s["angle"])
                p1 = (s["x"] + math.cos(r) * s["r"], s["y"] + math.sin(r) * s["r"])
                p2 = (s["x"] + math.cos(r + 2.5) * s["r"], s["y"] + math.sin(r + 2.5) * s["r"])
                p3 = (s["x"] + math.cos(r - 2.5) * s["r"], s["y"] + math.sin(r - 2.5) * s["r"])
                color = s["color"]
                if p_id == self.p_id:
                    pygame.draw.polygon(self.screen, color, [p1, p2, p3])
                else:
                    pygame.draw.polygon(self.screen, color, [p1, p2, p3], 2)
        score_text = ""
        if self.p_id in self.state["ships"]:
            score_text = f"Score: {self.state['ships'][self.p_id]['score']}"
        img = self.font.render(score_text, True, WHITE)
        self.screen.blit(img, (10, 10))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    ip = "127.0.0.1"
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    Client(ip).run()
