"""
Main Pygame UI and input controller.
Handles the graphics window, user events, and sends move/fire commands.
"""
import socket
import sys
import uuid
import json
import pygame
import math
import signal
import cliente
from common.socket_helpers import send_object
from cliente.broadcast_receiver import BroadcastReceiver

class Interface:
    """The main game 'view' that renders the state and captures inputs."""
    def __init__(self, ip=cliente.SERVER_ADDRESS, debug=False):
        """Initializes Pygame, connects to the server, and starts the receiver thread."""
        self.p_id = str(uuid.uuid4())[:8]
        self.ip = ip
        self.debug = debug
        self.running = True
        
        # TCP Connection
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.ip, cliente.PORT))
        except Exception as e:
            print(f"Error connecting to server: {e}")
            sys.exit(1)
        
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((cliente.WIDTH, cliente.HEIGHT))
        pygame.display.set_caption(f"Asteroids RawTCP - {self.p_id}")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        
        # Start receiver thread (calc_7 pattern)
        self.receiver = BroadcastReceiver(self.conn, debug=self.debug)
        self.receiver.start()
        
        # Signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Register
        self.send_cmd({"type": "connect", "player_id": self.p_id})
        
        if self.debug:
            print(f"[DEBUG] Registered with ID: {self.p_id}")

    def signal_handler(self, sig, frame):
        """Handles Ctrl+C to ensure a graceful disconnect."""
        print("\n[CLIENT] Interrupted. Disconnecting...")
        self.disconnect()

    def disconnect(self):
        """Stops threads, sends disconnect message, and closes the window."""
        if not self.running: return
        self.running = False
        self.receiver.running = False
        try:
            self.send_cmd({"type": "disconnect", "player_id": self.p_id})
            self.conn.close()
        except:
            pass
        pygame.quit()
        sys.exit(0)

    def send_cmd(self, data):
        """Sends a JSON command object to the server."""
        try:
            if self.debug:
                print(f"OUT: {json.dumps(data)}")
            send_object(self.conn, data)
        except Exception as e:
            if self.running:
                print(f"Error sending command: {e}")

    def handle_input(self):
        """Polls Pygame events and key states to send input commands."""
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
                self.disconnect()
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
        """Renders the latest game entities received from the server."""
        self.screen.fill(cliente.BLACK)
        
        ships, asteroids, lasers, winner = self.receiver.obter_estado()

        for a in asteroids:
            pygame.draw.circle(self.screen, cliente.WHITE, (int(a["x"]), int(a["y"])), int(a["r"]), 2)
        for l in lasers:
            pygame.draw.circle(self.screen, cliente.YELLOW, (int(l["x"]), int(l["y"])), int(l["r"]))
        
        for p_id, s in ships.items():
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
        if self.p_id in ships:
            score_text = f"Score: {ships[self.p_id]['score']}"
        img = self.font.render(score_text, True, cliente.WHITE)
        self.screen.blit(img, (10, 10))

        if winner:
            win_text = f"GAME OVER - WINNER: {winner}"
            win_img = self.font.render(win_text, True, cliente.RED)
            self.screen.blit(win_img, (cliente.WIDTH // 2 - 150, cliente.HEIGHT // 2))

        pygame.display.flip()

    def execute(self):
        """Starts the game loop and maintains 60 FPS."""
        while self.running:
            if not self.handle_input():
                break
            self.draw()
            self.clock.tick(cliente.FPS)
        self.disconnect()
