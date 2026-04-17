import sys
import cliente
from cliente.interface.interface import Interface

if __name__ == "__main__":
    ip = cliente.SERVER_ADDRESS
    debug = False
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ["--debug", "-d"]:
                debug = True
            elif "." in arg or "localhost" in arg:
                ip = arg
    
    print(f"[CLIENT] Starting. Server: {ip}, Debug: {debug}")
    ui = Interface(ip, debug)
    ui.execute()
