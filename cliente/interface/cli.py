import time
import os
from cliente.broadcast_receiver import BroadcastReceiver

class InterfaceTexto:
    """Interface that shows information of the client without running pygame"""

    def __init__(self, connection):
        self.receiver = BroadcastReceiver(connection)
        self.receiver.start()
        self.running = True

    def show_info(self):
        while self.running:
            # Gets the updated state of the receiver
            ships, asteroids, lasers, winner = self.receiver.obter_estado()

            # Clear the console
            os.system('cls' if os.name == 'nt' else 'clear')

            # Display the game state
            print("=== PYSTEROIDS - Text Interface ===")
            print(f"Active players: {len(ships)}")
            print(f"Asteroids in orbit: {len(asteroids)}")

            for p_id, ship in ships.items():
                status = "Alive" if ship["alive"] else "Respawning"
                print(f"Player {p_id}: Score={ship['score']} | Status={status}")

            if winner:
                print(f"\nWinner: Player {winner}")
            
            time.sleep(1)  # Update every second

    def stop(self):
            self.running = False
            self.receiver.running = False