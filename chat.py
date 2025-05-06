import sys
from threading import Thread
import argparse
from peer_base import Peer
from node import Node
from user_config import UserConfig
import socket

parser = argparse.ArgumentParser(description="Distributed Chat Application")
parser.add_argument("-l", "--local", action="store_true", help="Run on localhost")
args = parser.parse_args()


class Chat:
    def __init__(self):
        self.config = UserConfig()
        self.node = self.get_node()
        self.receive_thread = Thread(target=self.node.receive_messages,
                                     daemon=True, args=(self.config.downloads_dir,))

    @staticmethod
    def print_help():
        """Prints help message"""
        print("This is a chat. There are available commands:")
        print("  /add <username> <peer_host> <peer_port>   Adds new peer to known")
        print("  /send <username> <message>   Sends a message to peer")
        print("  /sendfile <username> <path_to_file>   Sends a file to peer")
        print("  /list   Prints list of known peers")
        print("  /clear   Clear all known peers")
        print("  /chname <username>   Edits current username")
        print("  /chport <port>   Edits current port. This will restart server")
        print("  /exit   Closes this application")

    def run(self):
        """Runs chat application"""
        print(f"App starts on {self.node.host}:{self.node.port}")
        self.receive_thread.start()

        try:
            self.chat_cycle()
        except Exception as e:
            print(e)
        finally:
            self.node.peer_base.save_peers()
            self.node.close()
            self.receive_thread.join(timeout=2)
            sys.exit(0)

    def chat_cycle(self):
        """Waits and then executes commands"""
        while True:
            command = input(">> ")

            if command.startswith("/add"):
                self.add_contact(command)
            elif command.startswith("/sendfile"):
                self.send_file(command)
            elif command.startswith("/send"):
                self.send_message(command)
            elif command.startswith("/chname"):
                self.change_name(command)
            elif command.startswith("/chport"):
                self.change_port(command)
            elif command.startswith("/list"):
                self.node.peer_base.print_peers()
            elif command.startswith("/clear"):
                self.node.peer_base.clear()
                print("Erased all contacts")
            elif command.startswith("/help"):
                self.print_help()
            elif command.startswith("/exit"):
                break
            else:
                print("Unknown command: try /help")

    def change_port(self, command: str):
        parts = command.split()
        if len(parts) != 2 or not parts[1].strip().isdigit():
            print("Usage: /chport <new_port>")
            return

        _, port = parts
        self.config.save_config(self.config.username, int(port))
        self.node.peer_base.save_peers()
        self.node.close()
        self.receive_thread.join()
        print("Closed old server")
        self.node = self.get_node()
        self.receive_thread = Thread(target=self.node.receive_messages,
                                     daemon=True, args=(self.config.downloads_dir,))
        self.receive_thread.start()
        print(f"Started new server on {self.node.host}:{self.node.port}")

    def change_name(self, command: str):
        parts = command.split()
        if len(parts) != 2:
            print("Usage: /chname <username_without_spaces>")
            return

        _, username = parts
        self.config.save_config(username, self.node.port)
        print(f"Changed username to {username}")

    def send_message(self, command: str):
        parts = command.split(maxsplit=2)
        if len(parts) != 3:
            print("Usage: /send <username> <message>")
            return

        _, username, message = parts
        peer = self.node.peer_base.get_peer_by_username(username)
        # if user typed IP instead username
        if not peer:
            peer = self.node.peer_base.get_peer_by_host(username)

        if peer:
            self.node.send_message(peer.host, peer.port, message)

    def send_file(self, command: str):
        parts = command.split()
        if len(parts) != 3:
            print("Usage: /sendfile <username> <path_to_file>")
            return

        _, username, path = parts
        peer = self.node.peer_base.get_peer_by_username(username)
        # if user typed IP instead username
        if not peer:
            peer = self.node.peer_base.get_peer_by_host(username)

        if peer:
            self.node.send_file(peer.host, peer.port, path)

    def add_contact(self, command: str):
        parts = command.split()
        if len(parts) != 4:
            print("Usage: /add <username> <peer_host> <peer_port>")
            return

        _, username, host, port = parts
        self.node.peer_base.add_peer(Peer(host, int(port), username))
        print(f"Added {username} to contacts")

    def get_node(self) -> Node:
        """Returns new Node instance, which depends on --local argument"""
        if args.local:
            node = Node(port=self.config.server_port,
                        username=self.config.username)
        else:
            node = Node(host="0.0.0.0", port=self.config.server_port,
                        username=self.config.username)
            public_ip = socket.gethostbyname(socket.gethostname())
            print(f"Your IPv4 in current wifi is {public_ip}. Share it with others")
            print(f"Your username is {node.username}")
        return node


if __name__ == "__main__":
    chat = Chat()
    chat.run()
