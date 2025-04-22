import socket
import sys
from threading import Thread
import argparse

parser = argparse.ArgumentParser(description="Distributed Chat Application")
parser.add_argument("--port", type=int, default=8000, help="Port to run the application on")
args = parser.parse_args()


class Node:
    def __init__(self, host='localhost', port=args.port):
        self.host = host
        self.port = port
        self.known_peers = []
        self.is_running = True
        self.server_socket = None

    @staticmethod
    def send_message(peer_host, peer_port, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((peer_host, peer_port))
                s.sendall(message.encode())
            except ConnectionRefusedError:
                print(f"Can't send message to {peer_host}:{peer_port}")

    def receive_messages(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                            print(f"\n{addr}: {data}")
                except OSError:
                    break
        finally:
            if self.server_socket:
                self.server_socket.close()

    def add_peer(self, peer_host, peer_port):
        """Adds peer to known"""
        if (peer_host, peer_port) not in self.known_peers:
            self.known_peers.append((peer_host, peer_port))
            print(f"Peer {peer_host}:{peer_port} was added.")

    def list_peers(self):
        """Prints all known peers"""
        if len(self.known_peers) == 0:
            print("No available peers")
            return

        for i, peer in enumerate(self.known_peers):
            print(f"{i + 1}. {peer[0]}:{peer[1]}")

    def close(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()


def print_help():
    print("This is a chat. There are available commands:")
    print(" /add <peer_host> <peer_port>  adds new peer to known")
    print()
    print(" /list  prints list of known hosts")
    print()
    print(" /exit  closes this application")
    print()
    print(" If you type just a text, it will be send to all known hosts")


def main():
    node = Node()
    print(f"App starts on {node.host}:{node.port}")

    t = Thread(target=node.receive_messages, daemon=True)
    t.start()

    try:
        while True:
            command = input(">> ")
            if command.startswith("/add"):
                _, host, port = command.split()
                if not host or not port:
                    print("Usage: /add <peer_host> <peer_port>")
                node.add_peer(host, int(port))
            elif command.startswith("/list"):
                node.list_peers()
            elif command.startswith("/help"):
                print_help()
            elif command.startswith("/exit"):
                break
            else:
                if len(node.known_peers) > 0:
                    target_host, target_port = node.known_peers[0]
                    node.send_message(target_host, target_port, command)
                else:
                    print("No available peers")
    finally:
        node.close()
        t.join(timeout=0.5)
        sys.exit(0)


if __name__ == "__main__":
    main()
