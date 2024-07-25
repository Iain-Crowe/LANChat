import os
import requests
import selectors
import signal
import socket
import sys
import threading
from typing import List, Optional, Tuple

running = threading.Event()
running.set()

sel = selectors.DefaultSelector()

def recieve_messages() -> None:
    """
        Target for `recieve_thread`. Awaits messages sent broadcasted from server and prints them.
    """
    while running.is_set():
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                print(message)
        except ConnectionAbortedError:
            break
        except Exception as e:
            if running.is_set():
                print(f"Error receicing message: {e}")
            break

def send_messages() -> None:
    """
        Target for `send_thread`. Reads command line and sends message to server.
    """
    while running.is_set():
        try:
            message = _input()    
            if message:
                client_socket.send(message.encode("utf-8"))
        except ConnectionAbortedError:
            break
        except Exception as e:
            if running.is_set():
                print(f"Error sending message: {e}")
            break

def _input() -> Optional[str]:
    """
        Non-holding version of the built-in `input()`

        Returns a string from the command line on new-line.
    """
    message = None
    events = sel.select(timeout=1)
    for key, _ in events:
        if key.fileobj is sys.stdin:
            message = sys.stdin.readline().strip()
    return message

def discover_server() -> Optional[Tuple[str, int]]:
    """
        Makes API call to server to request IP and Port for socket connection.

        If available, returns tuple containing the IP as a string and port as an
        integer.
    """
    try:
        server_ip = os.getenv("SERVER_IP", "localhost")
        response = requests.get(f"http://{server_ip}:5000/discover")
        data = response.json()
        return data['server_ip'], int(data['server_port'])
    except requests.RequestException as e:
        print(f"Error discovering server: {e}")
        return None

def get_users() -> Optional[Tuple[int, List[str]]]:
    """
        Makes API call to server to request user data.

        If available, returns a tuple containing the number of active users, and a list
        of active users connected to the server.
    """
    try:
        server_ip = os.getenv("SERVER_IP", "localhost")
        response = requests.get(f"http://{server_ip}:5000/users")
        data = response.json()
        return data["total_users"], data["active_users"]
    except requests.RequestException as e:
        print(f"Error fetching user data: {e}")
        return None

def shutdown(signum, frame) -> None:
    """
        Shutdown sequence for client. Halts threads and closes
        the socket connection with server.

        Params - 
            `signum`: unused
            `frame`: unused
    """
    running.clear()
    print("\nShutting down...")
    
    try:
        client_socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print(f"Error shutting down socket: {e}")
    finally:
        client_socket.close()

    sys.exit(0)

if __name__ == "__main__":
    # Signals for shutting down client safely
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Get server IP and data on who is online
    discovery_result = discover_server()
    user_data = get_users()
    if discovery_result:
        # Connect to server via socket
        SERVER, PORT = discovery_result
        ADDRESS: Tuple[str, int] = (SERVER, PORT)
        client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(ADDRESS)

        # Welcome statement with instructions for how to use CLI
        print("Welcome to the LANChat CLI Client (v1.0)")
        print(f"You have connected to {SERVER}:{PORT}...")
        print("To exit the client use 'Ctrl+C'")
        print("To send a chat simply type and press 'ENTER'")
        if user_data: 
            num_users, users = user_data
            print(f"\nThere are {num_users} online:")
            for u in users:    
                print(f"  {u}")
        print()

        # Register selector for use with non-holding input
        sel.register(sys.stdin, selectors.EVENT_READ)

        # Start thread for receiving messages.
        recieve_thread = threading.Thread(target=recieve_messages)
        recieve_thread.start()

        # Start thead for sending messages.
        send_thread = threading.Thread(target=send_messages)
        send_thread.start()

        # Join threads
        recieve_thread.join()
        send_thread.join()
    else:
        # Exit if server is not running.
        print("Server not found.")
        sys.exit(1)