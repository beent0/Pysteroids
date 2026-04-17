"""
Periodic game state broadcaster.
Drives the game loop at 60 FPS and pushes state updates to all connected clients.
"""
import threading
import time
import json
import servidor
from common.socket_helpers import send_object

class ThreadBroadcast(threading.Thread):
    """Background thread that handles physics updates and periodic state distribution."""
    def __init__(self, lista_clientes, dados):
        """Initializes with shared client list and game data."""
        super().__init__(daemon=True)
        self.lista_clientes = lista_clientes
        self.dados = dados
        self.running = True

    def run(self):
        """Drives the 60Hz physics clock and performs TCP broadcasts."""
        print("ThreadBroadcast (60 FPS) active")
        while self.running:
            try:
                # Update game logic at 60 FPS
                self.dados.update()
                
                # Broadcast state to all clients
                state = self.dados.obter_estado()
                # Deep copy via JSON to avoid race conditions during iteration
                state_copy = json.loads(json.dumps(state))
                
                clientes = self.lista_clientes.obter_lista()
                for addr, conn in clientes.items():
                    try:
                        send_object(conn, state_copy)
                    except:
                        self.lista_clientes.remover(addr)
                
                time.sleep(1.0 / servidor.FPS)
            except Exception as e:
                print(f"Broadcast Error: {e}")
                continue
