import socket
from peer_base import PeerBase, Peer


class Node:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.peer_base = PeerBase()
        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message(self, peer_host: str, peer_port: int, message: str):
        """Sends message to peer"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((peer_host, peer_port))
                message = message + f"|SERVER_PORT:{self.port}"
                s.sendall(message.encode("utf-8"))
            except ConnectionError as e:
                print(f"Can't send message to {peer_host}:{peer_port}: {e}")
                raise

    def receive_messages(self):
        """Listens to messages from peers"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        try:
            while self.is_running:
                try:
                    conn, addr = self.server_socket.accept()
                    with conn:
                        while True:
                            data = conn.recv(1024).decode("utf-8")
                            if not data:
                                break
                            message, server_port = data.split("|")
                            print(f"\n({addr[0]}:{addr[1]}): {message}\n>> ", end="", flush=True)
                            self.peer_base.update_peer(addr[0], int(server_port.split(":")[1]))
                except OSError:
                    raise
        finally:
            if self.server_socket:
                self.server_socket.close()

    def close(self):
        """Closes current node"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
