"""
Thread-safe registry for connected clients.
Used by the broadcast thread to send updates to all active sockets.
"""
import threading
from typing import Dict, Tuple
import socket

class ListaClientes:
    """Manages a dictionary of active client connections with mutual exclusion."""
    def __init__(self):
        self._clientes: Dict[Tuple[str, int], socket.socket] = {}
        self._lock = threading.Lock()
        self._nr_clientes = 0

    def adicionar(self, address: Tuple[str, int], connection: socket.socket) -> None:
        """Adds a client address and socket to the registry."""
        with self._lock:
            self._clientes[address] = connection
            self._nr_clientes += 1
            print(f"Client {address} added! Total: {self._nr_clientes}")

    def remover(self, addr: Tuple[str, int]) -> None:
        """Removes a client from the registry by address."""
        with self._lock:
            if addr in self._clientes:
                del self._clientes[addr]
                self._nr_clientes -= 1
                print(f"Client {addr} removed! Total: {self._nr_clientes}")

    def obter_lista(self):
        """Returns a copy of the current client dictionary for iteration."""
        with self._lock:
            return self._clientes.copy()

    def obter_nr_clientes(self) -> int:
        """Returns the total number of connected clients."""
        with self._lock:
            return self._nr_clientes
