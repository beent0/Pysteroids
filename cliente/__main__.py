import sys
import socket
import cliente

if __name__ == "__main__":
    # Configurações base
    ip = cliente.SERVER_ADDRESS
    for arg in sys.argv[1:]:
        if "." in arg or "localhost" in arg:
            ip = arg

    # Verifica se o utilizador quer o modo CLI
    if "--cli" in sys.argv[1:]:
        from cliente.interface.cli import InterfaceTexto
        print(f"[CLI] A ligar a {ip}...")
        
        # Cria a ligação necessária para a InterfaceTexto
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, cliente.PORT))
        
        ui = InterfaceTexto(sock)
        ui.show_info()
    else:
        # Modo Pygame normal (Lazy import para não dar erro sem Pygame)
        from cliente.interface.interface import Interface
        ui = Interface(ip, debug="--debug" in sys.argv)
        ui.execute()