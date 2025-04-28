import socket
import re

from peer_base import PeerBase

MESSAGE_REGEX = re.compile(
    r"^SENDER:(?P<username>[^ ]+?) "
    r"(?P<host>[^:]+?):(?P<port>\d+?)"
    r" \| MESSAGE:(?P<message>.*)$",
    re.DOTALL
)


class Node:
    """A class for single node in P2P chat"""

    def __init__(self, host: str = "localhost", port: int = 8000,
                 username: str = "John Doe"):
        if not isinstance(host, str):
            raise ValueError(f"Host must be string, but was:{host} {type(host)}")
        if not isinstance(port, int):
            raise ValueError(f"Port must be integer, but was:{port} {type(port)}")
        if not isinstance(username, str):
            raise ValueError(f"Username must be string, but was:{username} {type(username)}")

        self.host = host
        self.port = port
        self.username = username
        self.peer_base = PeerBase()
        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message(self, peer_host: str, peer_port: int, message: str):
        """Sends message to peer"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((peer_host, peer_port))
                message = f"SENDER:{self.username} {self.host}:{self.port} | MESSAGE:{message}"
                s.sendall(message.encode("utf-8"))
            except ConnectionError as e:
                print(f"Can't send message to {peer_host}:{peer_port}: {e}")
                raise

    def receive_messages(self):
        """Listens to messages from peers"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        while self.is_running:
            try:
                conn, addr = self.server_socket.accept()
                with conn:
                    while True:
                        data = conn.recv(1024).decode("utf-8")
                        if not data:
                            break
                        match = MESSAGE_REGEX.fullmatch(data)
                        groups = match.groupdict()
                        print(f"\n{groups['username']} "
                              f"({groups["host"]}:{groups["port"]}): "
                              f"{groups["message"]}\n>> ",
                              end="", flush=True)
                        self.peer_base.update_peer(
                            groups["host"], int(groups["port"]), groups["username"]
                        )
            except OSError:
                # if app will be closed, this error occurs
                break

        if self.server_socket:
            self.server_socket.close()

    def close(self):
        """Closes current node"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
