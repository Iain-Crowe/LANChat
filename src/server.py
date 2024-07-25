import os
import signal
import socket
import sys
import threading
from typing import List, Tuple

from flask import Flask, jsonify

from logger import logger

class Server:
    """
        Service class designed to run server upon instantiation.
    """
    def __init__(self) -> None:
        self.SERVER: str = socket.gethostbyname(socket.gethostname())
        self.PORT: int = int(os.environ["SERVER_PORT"])
        self.ADDRESS: Tuple[str, int] = (self.SERVER, self.PORT)
        self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS)
        self.clients: List[socket.socket] = []
        self.client_addresses: List[str] = []
        self.running = True

        signal.signal(signal.SIGINT, self.shudown)
        signal.signal(signal.SIGTERM, self.shudown)

        logger.info("[STARTING] Server is starting...")
        self.start_server()

    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """
            Handler function for clients that connect with the server. Handles the entire life-cycle of
            each client. Handler will notify other clients of connection and disconnection and broadcast
            messages to other clients connected with the server.

            Params -
                `client_socket`: The socket of the client that is used to connect with the server.
                `client_address`: The IP and Port associated with the client.
        """
        # Notify other clients of new connection
        logger.info(f"[NEW CONNECTION] {client_address} connected.")
        host, port = client_address
        self.broadcast(f"[NEW CONNECTION] ({host}:{port}) connected.", client_socket)
        
        # Client main loop
        while self.running:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if message: 
                    message = f"[{host}:{port}] -> {message}"   
                    logger.info(message)
                    self.broadcast(message, client_socket)
                else:
                    break
            except ConnectionResetError as e:
                logger.error(f"[{client_address}] {e}")
                break
        
        # Disconnect client and clean up
        self.broadcast(f"[DISCONNECT] ({host}:{port}) disconnected.", client_socket)
        self.client_addresses.remove(client_address)
        self.clients.remove(client_socket)
        client_socket.close()
        logger.info(f"[DISCONNECT] {client_address} disconnected.")

    def broadcast(self, message: str, sender_socket: socket.socket) -> None:
        """
            Function responsible for broadcasting messages across the whole server excluding
            message originator.

            Params -
                `message`: String containing the message to be broadcasted.
                `sender_socket`: Socket of the sender, so that it can be excluded from broadcast.
        """
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode("utf-8"))
                except BrokenPipeError:
                    continue
    
    def start_flask(self) -> None:
        """
            Target of flask thread. Provides some API endpoints for the clients to get needed information
            from. Ideally, this is handled with sockets as well, but this seemed like the safest approach
            for now...
        """
        logger.info("[FLASK] Starting flask app.")
        app = Flask(__name__)

        @app.route("/discover", methods=["GET"])
        def discover():
            """
                Endpoint for server discovery.

                Returns the server's ip and port.
            """
            return jsonify({"server_ip": self.SERVER, 'server_port': self.PORT})
        
        @app.route("/users", methods=["GET"])
        def get_users():
            """
                Endpoint for telling client about the users connected to server.

                Returns total number of users and a list of client addresses connected.
            """
            response = {
                "total_users": len(self.clients),
                "active_users": self.client_addresses
            }

            return jsonify(response)

        app.run(host="0.0.0.0", port=5000)

    def start_server(self) -> None:
        """
            Responsible for starting up the server and running the main loop.
        """
        self.server.listen()
        logger.info(f"[LISTENING] Server is listening on {self.SERVER}:{self.PORT}")

        threading.Thread(target=self.start_flask, daemon=True).start()
        
        while True:
            client_socket, client_address = self.server.accept()
            self.clients.append(client_socket)
            self.client_addresses.append(client_address)
            thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            thread.start()
            logger.info(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

    def shudown(self, signum, frame) -> None:
        """
            Function to handle the server's shutdown sequence. Halts all loops
            and closes all socket connections.

            Params - 
                `signum`: unused
                `frame`: unused
        """
        logger.info("[SHUTDOWN] Server is shutting down...")
        self.running = False
        self.server.close()
        for client_socket in self.clients:
            client_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    # Run server
    Server()