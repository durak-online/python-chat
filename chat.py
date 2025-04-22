import sys
from threading import Thread
import argparse
from peer_base import Peer
from node import Node

parser = argparse.ArgumentParser(description="Distributed Chat Application")
parser.add_argument("--port", type=int, default=8000, help="Port to run the application on")
args = parser.parse_args()


def print_help():
    print("This is a chat. There are available commands:")
    print("  /add <peer_host> <peer_port>   adds new peer to known")
    print("  /send <peer_host> <message>   sends a message to peer")
    print("  /list   prints list of known peers")
    print("  /clear   clear all known peers")
    print("  /exit   closes this application")


def main():
    node = Node(port=args.port)
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
                node.peer_base.add_peer(Peer(host, int(port)))

            elif command.startswith("/send"):
                _, host, message = command.split(maxsplit=2)
                peer = node.peer_base.get_peer_by_host(host)
                if peer:
                    node.send_message(peer.host, peer.port, message)

            elif command.startswith("/list"):
                node.peer_base.print_peers()

            elif command.startswith("/clear"):
                node.peer_base.clear()

            elif command.startswith("/help"):
                print_help()

            elif command.startswith("/exit"):
                break

            else:
                print("Unknown command: try /help")
    except Exception as e:
        print(e)
    finally:
        node.peer_base.save_peers()
        node.close()
        t.join(timeout=0.5)
        sys.exit(0)


if __name__ == "__main__":
    main()
