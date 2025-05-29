import argparse

from chat import Chat
from chat_ui import ChatUI

parser = argparse.ArgumentParser(description="Distributed Chat Application")
parser.add_argument(
    "-l", "--local",
    action="store_true",
    help="Run on localhost"
)
parser.add_argument(
    "-c", "--console",
    action="store_true",
    help="Run without UI"
)
parser.add_argument(
    "-p", "--port",
    type=int,
    help="Port to run the application on"
)
args = parser.parse_args()

if __name__ == "__main__":
    chat = Chat(args)
    if not args.console:
        ui = ChatUI(chat.node, chat.config)
        ui.run()
    else:
        chat.run()
