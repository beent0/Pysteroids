"""
Main Server Orchestrator.
Binds to a port and manages the lifecycle of client handler and broadcast threads.
"""
import socket
import servidor
from servidor.gestor.processa_cliente import ProcessaCliente
from servidor.gestor.lista_clientes import ListaClientes
from servidor.gestor.thread_broadcast import ThreadBroadcast
from servidor.dados.dados import Dados

class Maquina:
    """The server 'machine' that coordinates networking and game state."""
    def __init__(self):
        """Initializes the server socket, shared client list, and game data."""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('', servidor.PORT))
        self.lista_clientes = ListaClientes()
        self.dados = Dados()
        
        # Start Broadcast Thread
        self.broadcast = ThreadBroadcast(self.lista_clientes, self.dados)
        self.broadcast.start()

    def execute(self):
        """Main loop: listens for and accepts incoming client connections."""
        self.s.listen(5)
        print(f"Servidor Pysteroids ligado na porta {servidor.PORT}")
        
        while True:
            try:
                connection, address = self.s.accept()
                print(f"Cliente {address} conectado")
                
                # Add to client list for broadcast
                self.lista_clientes.adicionar(address, connection)
                
                # Create thread with shared state
                processa = ProcessaCliente(connection, address, self.lista_clientes, self.dados)
                processa.start()
            except Exception as e:
                print(f"Accept Error: {e}")
                break

if __name__ == "__main__":
    maq = Maquina()
    maq.execute()
