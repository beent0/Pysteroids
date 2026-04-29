"""
Individual client command handler.
Reads move and fire inputs from a specific client and updates the shared game state.
"""
import threading
from middleware.socket_helpers import receive_object

class ProcessaCliente(threading.Thread):
    """Thread responsible for processing incoming messages (Unicast) from a single client."""
    def __init__(self, connection, address, lista_clientes, dados):
        """Stores the socket connection and shared data pointers."""
        super().__init__(daemon=True)
        self.connection = connection
        self.address = address
        self.lista_clientes = lista_clientes
        self.dados = dados
        self.p_id = None

    def run(self):
        """Continuously reads JSON objects from the socket until disconnect."""
        print(f"Thread for {self.address} started")
        try:
            while True:
                msg = receive_object(self.connection)
                if not msg: break
                
                print(f"[{self.address}] Received: {msg}")

                if msg["type"] == "connect":
                    self.p_id = msg["player_id"]
                    print(f"[{self.p_id}] Player connected from {self.address}")
                    self.dados.add_player(self.p_id)
                
                elif msg["type"] == "input":
                    p_id = msg["player_id"]
                    keys = msg["keys"]
                    self.dados.handle_input(p_id, keys)
                
                elif msg["type"] == "disconnect":
                    p_id = msg["player_id"]
                    print(f"[{p_id}] Player requested disconnect")
                    break
        except Exception as e:
            print(f"Error handling client {self.address}: {e}")
        finally:
            self.lista_clientes.remover(self.address)
            if self.p_id:
                self.dados.remove_player(self.p_id)
            self.connection.close()
            print(f"Thread for {self.address} terminated")
