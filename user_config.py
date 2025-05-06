import json
import os

CONFIG_FILE = "config.json"


class UserConfig:
    """A class for user configuration"""

    def __init__(self):
        self.username: str = "JohnDoe"
        self.server_port: int = 8000
        self.downloads_dir = "./chat_downloads"
        os.makedirs(self.downloads_dir, exist_ok=True)
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                username = config["username"]
                server_port = config["server_port"]
                if username:
                    self.username = username
                if server_port:
                    self.server_port = int(server_port)

    def save_config(self, username: str, port: int):
        self.username = username
        self.server_port = port
        with open(CONFIG_FILE, "w") as f:
            json.dump({"username": username, "server_port": port}, f)
