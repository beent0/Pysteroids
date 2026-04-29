"""
Inbound state update receiver.
Listens for periodic game state broadcasts and stores them for the UI loop.
"""
import threading
from middleware.socket_helpers import receive_object

class BroadcastReceiver(threading.Thread):
    """Background thread for receiving JSON game states from the server."""
    def __init__(self, connection, debug=False):
        """Initializes with the server socket and debug flag."""
        super().__init__(daemon=True)
        self.connection = connection
        self.debug = debug
        self.state = {"ships": {}, "asteroids": [], "lasers": [], "winner": None}
        self.lock = threading.Lock()
        self.running = True
        self._last_debug_print = 0

    def run(self):
        """Continuously reads state objects from the broadcast channel."""
        import time
        while self.running:
            try:
                obj = receive_object(self.connection)
                if obj:
                    with self.lock:
                        self.state = obj
                    
                    if self.debug:
                        print(f"DEBUG: Received state: {obj}")
            except:
                if self.running:
                    print("Disconnected from server.")
                break

    def obter_estado(self):
        """Returns a synchronized copy of the latest ships, asteroids, lasers, and winner."""
        with self.lock:
            # Return copies to prevent race conditions in UI loop
            return dict(self.state.get("ships", {})), \
                   list(self.state.get("asteroids", [])), \
                   list(self.state.get("lasers", [])), \
                   self.state.get("winner")
