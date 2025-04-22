import socket
from peer_base import PeerBase, Peer


class Node:
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.peer_base = PeerBase()
        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def send_message(peer_host, peer_port, message):
        """Sends message to peer"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((peer_host, peer_port))
                s.sendall(message.encode())
            except ConnectionRefusedError:
                print(f"Can't send message to {peer_host}:{peer_port}")

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
                            data = conn.recv(1024).decode('utf-8')
                            if not data:
                                break
                            print(f"\n({addr[0]}:{addr[1]}): {data}\n>> ", end='', flush=True)
                            if not self.peer_base.get_peer_by_host(addr[0]):
                                self.peer_base.add_peer(Peer(addr[0], addr[1]))
                except OSError:
                    break
        finally:
            if self.server_socket:
                self.server_socket.close()

    def close(self):
        """Closes current node"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
