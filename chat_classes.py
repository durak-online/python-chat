import json
import os
from datetime import datetime
from typing import Literal

from contacts import Contact

HISTORY_DIR = "./history"


class Message:
    """A class with message info for UI"""

    def __init__(
            self,
            sender: Contact,
            sent_time: datetime,
            content: str,
            message_type: Literal["text", "file"] = "text"
    ):
        self.sender = sender
        self.sent_time = sent_time
        self.content = content
        self.message_type = message_type

    def to_dict(self):
        """Casts this object to dict for JSON serialization"""
        return {
            "sender": self.sender.to_dict(),
            "sent_time": self.sent_time.strftime("%H:%M:%S"),
            "content": self.content,
            "type": self.message_type
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a message from JSON data"""
        return cls(
            Contact.from_dict(data["sender"]),
            datetime.strptime(data["sent_time"], "%H:%M:%S"),
            data["content"],
            data["type"]
        )


class ChatInfo:
    """Chat info for serialization"""

    def __init__(self, name: str, messages: list[dict]):
        self.chat_name = name
        self.messages = messages

    def to_dict(self):
        """Casts this object to dict for JSON serialization"""
        return {
            "chat_name": self.chat_name,
            "messages": self.messages
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a chat info from JSON data"""
        return cls(data["chat_name"], data["messages"])


class ChatHistory:
    """A class for single chat with messages"""

    def __init__(self, contact: Contact, name: str = ""):
        self.name = name
        self.contact = contact
        self.messages = list[Message]()
        self._save_path = os.path.join(
            HISTORY_DIR,
            f"{contact.host.replace(".", "_")}.json"
        )
        os.makedirs(HISTORY_DIR, exist_ok=True)

    def add_message(self, message: Message):
        """Adds a new message to messages"""
        self.messages.append(message)

    def load_chat(self):
        """Loads chat from file"""
        try:
            with open(self._save_path, "r") as f:
                content = f.read()
                if content.strip():
                    loaded_data = json.loads(content)
                    loaded_info = ChatInfo.from_dict(loaded_data)

                    self.name = loaded_info.chat_name
                    self.messages = [
                        Message.from_dict(item)
                        for item in loaded_info.messages
                    ]
                else:
                    self.name = self.contact.username
                    self.messages = []
        except json.JSONDecodeError:
            print(f"Can't load from '{self._save_path}'")
            self.name = self.contact.username
            self.messages = []
        except FileNotFoundError:
            print(f"File '{self._save_path}' doesn't exist")
            self.name = self.contact.username
            self.messages = []

    def save_chat(self):
        """Saves chat to file"""
        with open(self._save_path, "w") as f:
            messages = [Message.to_dict(msg) for msg in self.messages]
            info = ChatInfo(self.name, messages)
            json.dump(info.to_dict(), f, indent=4, default=str)
