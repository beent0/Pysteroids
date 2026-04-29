"""
Helper functions for low-level TCP socket communication.
Implements a length-prefixed protocol for sending JSON objects.
"""
import json

INT_SIZE = 8

def send_int(connection, value: int):
    """Sends a signed 8-byte integer in network byte order."""
    connection.sendall(value.to_bytes(INT_SIZE, byteorder="big", signed=True))

def receive_int(connection):
    """Receives and decodes a signed 8-byte integer. Returns None if connection is closed."""
    data = b""
    while len(data) < INT_SIZE:
        chunk = connection.recv(INT_SIZE - len(data))
        if not chunk: return None
        data += chunk
    return int.from_bytes(data, byteorder='big', signed=True)

def send_object(connection, obj):
    """Serializes a Python dictionary to JSON and sends it prefixed with its byte size."""
    data = json.dumps(obj).encode('utf-8')
    size = len(data)
    send_int(connection, size)
    connection.sendall(data)

def receive_object(connection):
    """Receives a JSON object by first reading the size prefix and then the payload."""
    size = receive_int(connection)
    if size is None: return None
    data = b""
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk: break
        data += chunk
    return json.loads(data.decode('utf-8'))
